from datetime import date, datetime, time

from django.utils.dateparse import parse_datetime

from employee.models import Attendance, Employee
from employee.utils.attendance_schedule_config import get_total_slots
from employee.utils.attendance_slots import (
    PunchRejectedError,
    _coerce_time,
    evaluate_day_slots,
    validate_punch_allowed,
)

__all__ = [
    'PunchRejectedError',
    'build_day_evaluation',
    'import_attendance_payload',
    'record_punch',
    'resolve_employee_from_payload',
    'serialize_attendance_record',
    'serialize_employee_for_tablet',
]


def _parse_punch_datetime(payload):
    raw_time = payload.get('time')
    raw_date = payload.get('date')

    if raw_time:
        if isinstance(raw_time, datetime):
            return raw_time.replace(microsecond=0)
        text = str(raw_time).strip()
        parsed = parse_datetime(text)
        if parsed:
            return parsed.replace(microsecond=0)
        for fmt in ('%Y-%m-%d %H:%M:%S', '%H:%M:%S', '%H:%M'):
            try:
                if fmt.startswith('%Y'):
                    return datetime.strptime(text, fmt)
                base_date = raw_date or date.today().isoformat()
                return datetime.strptime(f'{base_date} {text}', '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue

    if raw_date:
        base = date.fromisoformat(str(raw_date))
        return datetime.combine(base, time(8, 0))

    return datetime.now().replace(microsecond=0)


def resolve_employee_from_payload(payload):
    employee_id = payload.get('employeeId') or payload.get('employee_id')
    registration_number = payload.get('registrationNumber') or payload.get('matricule')

    if employee_id:
        return Employee.objects.filter(pk=employee_id).first()

    if registration_number:
        return Employee.objects.filter(registration_number=str(registration_number)).first()

    return None


def record_punch(employee, punched_at, source='fingerprint'):
    if isinstance(punched_at, datetime):
        punch_date = punched_at.date()
        punch_time = punched_at.time().replace(microsecond=0)
    else:
        raise TypeError('punched_at must be a datetime')

    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=punch_date,
        time=punch_time,
        defaults={'source': source},
    )
    return attendance, created


def _day_punch_times(employee, day):
    return list(
        Attendance.objects.filter(employee=employee, date=day)
        .order_by('time')
        .values_list('time', flat=True)
    )


def build_day_evaluation(employee, day=None):
    day = day or date.today()
    punch_times = _day_punch_times(employee, day)
    evaluation = evaluate_day_slots(day, punch_times)
    slots = evaluation.get('slots') or {}

    slot_summary = []
    for code, slot in slots.items():
        slot_summary.append(
            {
                'code': code,
                'label': str(slot.get('label', code)),
                'punchTime': slot.get('punch_label', '—'),
                'status': slot.get('status', 'missing'),
            }
        )

    return {
        'dayStatus': evaluation.get('status'),
        'dayStatusLabel': str(evaluation.get('status_label', '')),
        'validatedSlots': evaluation.get('validated_slots', 0),
        'totalSlots': evaluation.get('total_slots', get_total_slots(day)),
        'missingSlots': [str(label) for label in evaluation.get('missing_slots', [])],
        'note': evaluation.get('note', ''),
        'slots': slot_summary,
    }


def import_attendance_payload(payload, source='fingerprint'):
    employee = resolve_employee_from_payload(payload)
    if not employee:
        raise ValueError('Employé introuvable pour ce pointage.')

    punched_at = _parse_punch_datetime(payload)
    punch_date = punched_at.date()
    punch_time = punched_at.time().replace(microsecond=0)
    existing = _day_punch_times(employee, punch_date)

    rejection = validate_punch_allowed(punch_date, punch_time, existing)
    if rejection:
        raise PunchRejectedError(rejection)

    attendance, created = record_punch(employee, punched_at, source=source)
    day_evaluation = build_day_evaluation(employee, punched_at.date())

    assigned_slot = None
    punch_time = punched_at.time()
    for slot in day_evaluation.get('slots', []):
        slot_time = slot.get('punchTime', '—')
        if slot_time != '—' and slot_time == punch_time.strftime('%H:%M'):
            assigned_slot = slot
            break

    return {
        'attendance': attendance,
        'created': created,
        'employee': employee,
        'punched_at': punched_at,
        'day_evaluation': day_evaluation,
        'assigned_slot': assigned_slot,
    }


def serialize_attendance_record(record, day_evaluation=None):
    punch_time = _coerce_time(record.time)
    punch_dt = datetime.combine(record.date, punch_time)
    payload = {
        'id': record.pk,
        'employeeId': record.employee_id,
        'date': record.date.isoformat(),
        'time': punch_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'type': 'punch',
        'fingerprintUsed': record.source == 'fingerprint',
        'status': 'present',
        'timestamp': punch_dt.isoformat(),
    }
    if day_evaluation:
        payload['dayEvaluation'] = day_evaluation
    return payload


def serialize_employee_for_tablet(employee):
    from employee.services.fingerprint_tablet import employee_has_fingerprints

    return {
        'id': employee.pk,
        'nin': employee.registration_number or '',
        'firstName': employee.first_name or '',
        'lastName': employee.last_name or '',
        'middleName': employee.middle_name or '',
        'email': employee.email or '',
        'phoneNumber': str(employee.mobile_number or employee.telephone_number or ''),
        'jobTitle': str(employee.designation) if employee.designation else '',
        'department': str(employee.direction) if employee.direction else '',
        'photoPath': employee.photo.url if employee.photo else '',
        'fingerprintTemplate': '',
        'fingerprintFinger': '',
        'biometricEnrolled': employee_has_fingerprints(employee),
        'numberOfChildren': employee.child_set.count(),
        'role': 'employee',
    }
