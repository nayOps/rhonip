import os

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from employee.models import Attendance, Employee
from employee.utils.roster import apply_roster_filter
from employee.services.attendance_punch import (
    PunchRejectedError,
    build_day_evaluation,
    import_attendance_payload,
    serialize_attendance_record,
    serialize_employee_for_tablet,
)
from employee.services.fingerprint_tablet import (
    build_matching_index,
    get_template_for_employee_finger,
)
from employee.services.fingerprint_enrollment import get_enrollment_status, import_enrollment_payload
from employee.utils.fingerprint_bundle import build_fingerprint_bundle


def _check_device_key(request):
    expected_key = os.getenv('ATTENDANCE_DEVICE_API_KEY', '')
    if not expected_key:
        return None
    provided = request.headers.get('X-Attendance-Device-Key', '')
    if provided != expected_key:
        return Response({'status': 'forbidden', 'message': 'Clé appareil invalide.'}, status=status.HTTP_403_FORBIDDEN)
    return None


class AttendanceDeviceAPI(APIView):
    """API tablette / APK — compatible attendanceapk (POST + GET /api/attendance)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        denied = _check_device_key(request)
        if denied:
            return denied

        queryset = Attendance.objects.select_related('employee').order_by('-date', '-time')
        employee_id = request.GET.get('employeeId') or request.GET.get('employee_id')
        punch_date = request.GET.get('date')

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if punch_date:
            queryset = queryset.filter(date=punch_date)

        data = [serialize_attendance_record(record) for record in queryset[:500]]
        return Response({'status': 'success', 'total': len(data), 'data': data})

    def post(self, request):
        denied = _check_device_key(request)
        if denied:
            return denied

        payload = request.data
        if not payload:
            return Response(
                {'status': 'error', 'message': 'Aucune donnée JSON reçue.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = import_attendance_payload(payload, source='fingerprint')
        except PunchRejectedError as exc:
            return Response({'status': 'error', 'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({'status': 'error', 'message': str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({'status': 'error', 'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        day_evaluation = result['day_evaluation']
        assigned_slot = result.get('assigned_slot') or {}
        employee = result['employee']

        record = serialize_attendance_record(result['attendance'], day_evaluation=day_evaluation)
        message = 'Pointage enregistré.' if result['created'] else 'Pointage déjà enregistré à cette heure.'

        return Response(
            {
                'status': 'success',
                'message': message,
                'data': record,
                'employeeName': employee.full_name(),
                'assignedSlot': assigned_slot,
                'dayEvaluation': day_evaluation,
            },
            status=status.HTTP_200_OK,
        )


class TabletEmployeeDataAPI(APIView):
    """Liste des employés pour l'APK tablette — GET /api/data."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        denied = _check_device_key(request)
        if denied:
            return denied

        employees = apply_roster_filter(
            Employee.objects.select_related('designation', 'direction')
        ).order_by('last_name', 'first_name')

        data = [serialize_employee_for_tablet(employee) for employee in employees]
        return Response({'status': 'success', 'total': len(data), 'data': data})


class TabletFingerprintMatchingAPI(APIView):
    """Index empreintes tablette — GET /api/fingerprints/matching."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        denied = _check_device_key(request)
        if denied:
            return denied

        data = build_matching_index()
        return Response({'status': 'success', 'total': len(data), 'data': data})


class TabletFingerprintBundleAPI(APIView):
    """Bundle empreintes Morpho — GET /api/fingerprints/bundle."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        denied = _check_device_key(request)
        if denied:
            return denied

        since = request.GET.get('since')
        bundle = build_fingerprint_bundle(since=since)
        return Response(bundle)


class TabletFingerprintBinaryAPI(APIView):
    """Template binaire — GET /api/fingerprints/<employee_id>/<finger>."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, employee_id, finger_name):
        denied = _check_device_key(request)
        if denied:
            return denied

        payload = get_template_for_employee_finger(employee_id, finger_name)
        if not payload:
            return Response(
                {'status': 'error', 'message': f'Aucune empreinte pour {employee_id}/{finger_name}.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                'status': 'success',
                'employeeId': payload['employeeId'],
                'fingerName': payload['fingerName'],
                'template_base64': payload['template_base64'],
                'template_format': payload.get('template_format', ''),
            }
        )


class TabletEmployeeDayStatusAPI(APIView):
    """Statut journalier 4 plages — GET /api/attendance/day-status/<employee_id>."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, employee_id):
        denied = _check_device_key(request)
        if denied:
            return denied

        employee = Employee.objects.filter(pk=employee_id).first()
        if not employee:
            return Response({'status': 'error', 'message': 'Employé introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                'status': 'success',
                'employeeId': employee.pk,
                'employeeName': employee.full_name(),
                'dayEvaluation': build_day_evaluation(employee),
            }
        )


class TabletFingerprintEnrollAPI(APIView):
    """Enrôlement empreinte Morpho depuis tablette — POST /api/fingerprints/enroll."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        denied = _check_device_key(request)
        if denied:
            return denied

        payload = request.data
        if not payload:
            return Response(
                {'status': 'error', 'message': 'Aucune donnée JSON reçue.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = import_enrollment_payload(payload)
        except ValueError as exc:
            return Response({'status': 'error', 'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({'status': 'error', 'message': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                'status': 'success',
                'message': 'Empreinte enregistrée.',
                'data': result,
            },
            status=status.HTTP_200_OK,
        )


class TabletFingerprintEnrollStatusAPI(APIView):
    """Statut enrôlement 10 doigts — GET /api/fingerprints/enroll/status/<employee_id>."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, employee_id):
        denied = _check_device_key(request)
        if denied:
            return denied

        employee = Employee.objects.filter(pk=employee_id).first()
        if not employee:
            return Response({'status': 'error', 'message': 'Employé introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': 'success', **get_enrollment_status(employee)})
