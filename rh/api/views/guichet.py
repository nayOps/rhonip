"""
API guichet interne — création / mise à jour employé depuis register.
Alignée sur employee.models.Employee (+ inlines).
"""
import base64
import os

from django.core.files.base import ContentFile
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import model_serializer_factory
from employee.utils.guichet_form import employee_to_guichet_form
from employee.choices.countries import COUNTRY_NAMES
from employee.utils.geography import resolve_geography_fk
from employee.utils.roster import apply_roster_filter
from employee.models import (
    Agreement,
    Branch,
    Child,
    Designation,
    Direction,
    Document,
    Education,
    Employee,
    Experience,
    Grade,
    Groupement,
    Province,
    Sector,
    Service,
    SubDirection,
    Territory,
    Village,
)

FK_MODELS = {
    'agreement': Agreement,
    'designation': Designation,
    'grade': Grade,
    'direction': Direction,
    'sub_direction': SubDirection,
    'service': Service,
    'branch': Branch,
}

INLINE_KEYS = ('children', 'educations', 'experiences', 'employee_documents')
FILE_KEYS = ('photo_base64', 'appointment_letter_base64', 'appointment_letter_name')


def _check_guichet_key(request):
    expected_key = os.getenv('GUICHET_INTERNAL_API_KEY', '')
    provided_key = request.headers.get('X-Guichet-Internal-Key', '')
    if expected_key and provided_key != expected_key:
        return Response({'status': 'forbidden'}, status=status.HTTP_403_FORBIDDEN)
    return None


def _resolve_fk(Model, value):
    if value is None or value == '':
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    name = str(value).strip()
    if not name:
        return None
    obj, _ = Model.objects.get_or_create(name=name)
    return obj.pk


def _decode_base64(value):
    if not value:
        return None
    raw = str(value)
    if ',' in raw:
        raw = raw.split(',', 1)[1]
    return base64.b64decode(raw)


def _save_file_field(instance, field_name, b64_value, filename):
    content = _decode_base64(b64_value)
    if not content:
        return
    getattr(instance, field_name).save(filename, ContentFile(content), save=True)


def _normalize_employee_payload(data):
    payload = data.copy()
    for field, model in FK_MODELS.items():
        if field in payload:
            payload[field] = _resolve_fk(model, payload.get(field))
    for date_field in (
        'date_of_birth',
        'date_of_join',
        'onip_start_date',
        'date_of_issue',
        'date_of_expiry',
    ):
        if payload.get(date_field) == '':
            payload[date_field] = None
    for text_field in (
        'registration_number',
        'social_security_number',
        'first_name',
        'last_name',
        'middle_name',
        'place_of_birth',
        'citizenship',
        'home_country',
        'identity_number',
        'place_of_issue',
        'appointment_number',
        'spouse',
        'telephone_number',
        'mobile_number',
        'email_professional',
        'email',
        'physical_address',
        'emergency_contact',
        'emergency_phone',
        'relationship',
        'emergency_information',
        'refering_doctor',
        'refering_doctor_phone',
        'refering_doctor_email',
        'payment_account',
        'payer_name',
        'comment',
    ):
        if payload.get(text_field) == '':
            payload[text_field] = None
    for choice_field in ('gender', 'marital_status', 'payment_method', 'type_of_identity'):
        if payload.get(choice_field) == '':
            payload[choice_field] = None
    payload = resolve_geography_fk(payload, Province, Territory, Sector, Groupement, Village)
    return payload


def _extract_inline_payload(data):
    inline_data = {}
    for key in INLINE_KEYS:
        if key in data:
            inline_data[key] = data.pop(key)
    file_data = {}
    for key in FILE_KEYS:
        if key in data:
            file_data[key] = data.pop(key)
    return inline_data, file_data


def _sync_children(employee, rows):
    if rows is None:
        return
    Child.objects.filter(employee=employee).delete()
    for row in rows or []:
        name = (row.get('full_name') or '').strip()
        if not name:
            continue
        Child.objects.create(
            employee=employee,
            full_name=name,
            date_of_birth=row.get('date_of_birth') or None,
        )


def _sync_educations(employee, rows):
    if rows is None:
        return
    from employee.models.education_references import Degree, FieldOfStudy, Institution, StudyLevel
    from employee.utils.education_references import resolve_reference

    Education.objects.filter(employee=employee).delete()
    for row in rows or []:
        institution_raw = (row.get('institution') or '').strip()
        degree_raw = (row.get('degree') or '').strip()
        study_level_raw = (row.get('study_level') or row.get('niveauEtude') or '').strip()
        field_raw = (row.get('field_of_study') or row.get('domaine') or row.get('domaineEtude') or '').strip()
        if not any((institution_raw, degree_raw, study_level_raw, field_raw)):
            continue
        Education.objects.create(
            employee=employee,
            institution=resolve_reference(Institution, institution_raw) if institution_raw else None,
            degree=resolve_reference(Degree, degree_raw) if degree_raw else None,
            study_level=resolve_reference(StudyLevel, study_level_raw) if study_level_raw else None,
            field_of_study=resolve_reference(FieldOfStudy, field_raw) if field_raw else None,
            start_date=row.get('start_date') or None,
            end_date=row.get('end_date') or None,
        )


def _sync_experiences(employee, rows):
    if rows is None:
        return
    Experience.objects.filter(employee=employee).delete()
    for row in rows or []:
        organization = (row.get('organization') or '').strip()
        position = (row.get('position') or '').strip()
        if not organization and not position:
            continue
        exp = Experience.objects.create(
            employee=employee,
            organization=organization or None,
            position=position or None,
            start_date=row.get('start_date') or None,
            end_date=row.get('end_date') or None,
        )
        photo_b64 = row.get('photo_base64')
        if photo_b64:
            _save_file_field(
                exp,
                'photo',
                photo_b64,
                row.get('photo_name') or f'{organization or "experience"}.jpg',
            )


def _sync_documents(employee, rows):
    if rows is None:
        return
    Document.objects.filter(employee=employee).delete()
    for row in rows or []:
        name = (row.get('name') or '').strip()
        file_b64 = row.get('file_base64') or row.get('document_base64')
        if not name or not file_b64:
            continue
        doc = Document(employee=employee, name=name)
        filename = row.get('file_name') or f'{name}.pdf'
        content = _decode_base64(file_b64)
        if content:
            doc.document.save(filename, ContentFile(content), save=False)
        doc.save()


def _sync_inlines(employee, inline_data):
    _sync_children(employee, inline_data.get('children'))
    _sync_educations(employee, inline_data.get('educations'))
    _sync_experiences(employee, inline_data.get('experiences'))
    _sync_documents(employee, inline_data.get('employee_documents'))


class GuichetEmployeeRefs(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        forbidden = _check_guichet_key(request)
        if forbidden:
            return forbidden

        return Response(
            {
                'directions': list(Direction.objects.values('id', 'name')),
                'sub_directions': list(
                    SubDirection.objects.values('id', 'name', 'direction_id')
                ),
                'services': list(Service.objects.values('id', 'name', 'sub_direction_id')),
                'grades': list(Grade.objects.values('id', 'name')),
                'agreements': list(Agreement.objects.values('id', 'name')),
                'designations': list(Designation.objects.values('id', 'name')),
                'branches': list(Branch.objects.values('id', 'name')),
                'provinces': list(Province.objects.order_by('name').values('id', 'name')),
                'countries': [{'id': name, 'name': name} for name in COUNTRY_NAMES],
            }
        )


def _parse_int_param(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _village_payload(village):
    groupement = village.groupement
    sector = groupement.sector
    territory = sector.territory
    province = territory.province
    return {
        'id': village.id,
        'name': village.name,
        'label': f'{village.name} — {territory.name}, {province.name}',
        'province_id': province.id,
        'territory_id': territory.id,
        'sector_id': sector.id,
        'groupement_id': groupement.id,
    }


class GuichetGeography(APIView):
    """Référentiel géographique ONIP pour le guichet register (cascade + recherche village)."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        forbidden = _check_guichet_key(request)
        if forbidden:
            return forbidden

        level = (request.query_params.get('level') or '').strip().lower()
        q = (request.query_params.get('q') or '').strip()
        province_id = _parse_int_param(request.query_params.get('province_id'))
        territory_id = _parse_int_param(request.query_params.get('territory_id'))
        sector_id = _parse_int_param(request.query_params.get('sector_id'))
        groupement_id = _parse_int_param(request.query_params.get('groupement_id'))

        if level == 'province':
            qs = Province.objects.all().order_by('name')
            if q:
                qs = qs.filter(name__icontains=q)
            return Response({'results': list(qs.values('id', 'name')[:100])})

        if level == 'territory':
            if not province_id:
                return Response({'results': []})
            qs = Territory.objects.filter(province_id=province_id).order_by('name')
            if q:
                qs = qs.filter(name__icontains=q)
            return Response({
                'results': [
                    {'id': row['id'], 'name': row['name'], 'province_id': province_id}
                    for row in qs.values('id', 'name')[:200]
                ],
            })

        if level == 'sector':
            if not territory_id:
                return Response({'results': []})
            qs = Sector.objects.filter(territory_id=territory_id).order_by('name')
            if q:
                qs = qs.filter(name__icontains=q)
            return Response({
                'results': [
                    {'id': row['id'], 'name': row['name'], 'territory_id': territory_id}
                    for row in qs.values('id', 'name')[:200]
                ],
            })

        if level == 'groupement':
            if not sector_id:
                return Response({'results': []})
            qs = Groupement.objects.filter(sector_id=sector_id).order_by('name')
            if q:
                qs = qs.filter(name__icontains=q)
            return Response({
                'results': [
                    {'id': row['id'], 'name': row['name'], 'sector_id': sector_id}
                    for row in qs.values('id', 'name')[:300]
                ],
            })

        if level == 'village':
            qs = Village.objects.select_related(
                'groupement__sector__territory__province',
            )
            if groupement_id:
                qs = qs.filter(groupement_id=groupement_id)
                if q:
                    qs = qs.filter(name__icontains=q)
                rows = [_village_payload(v) for v in qs.order_by('name')[:100]]
                return Response({'results': rows})

            if len(q) < 2:
                return Response({'results': []})

            qs = qs.filter(name__icontains=q)
            if sector_id:
                qs = qs.filter(groupement__sector_id=sector_id)
            elif territory_id:
                qs = qs.filter(groupement__sector__territory_id=territory_id)
            elif province_id:
                qs = qs.filter(groupement__sector__territory__province_id=province_id)

            rows = [_village_payload(v) for v in qs.order_by('name')[:50]]
            return Response({'results': rows})

        return Response(
            {'error': 'Paramètre level requis: province, territory, sector, groupement, village'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GuichetEmployeeUpsert(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        forbidden = _check_guichet_key(request)
        if forbidden:
            return forbidden

        raw = request.data.copy()
        employee_id = raw.pop('employee_id', None)
        inline_data, file_data = _extract_inline_payload(raw)
        data = _normalize_employee_payload(raw)
        matricule = (data.get('registration_number') or '').strip() or None
        data['registration_number'] = matricule

        existing = None
        if employee_id:
            existing = Employee.objects.filter(pk=employee_id).first()
        if not existing and matricule:
            existing = Employee.objects.filter(registration_number=matricule).first()

        serializer_cls = model_serializer_factory(Employee, depth=0)

        if existing:
            serializer = serializer_cls(existing, data=data, partial=True)
            action = 'updated'
        else:
            serializer = serializer_cls(data=data, partial=True)
            action = 'created'

        if not serializer.is_valid():
            return Response(
                {'status': 'unsuccessful', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        matricule = instance.registration_number

        photo_b64 = file_data.get('photo_base64')
        if photo_b64:
            _save_file_field(
                instance,
                'photo',
                photo_b64,
                f'{matricule}_photo.jpg',
            )

        letter_b64 = file_data.get('appointment_letter_base64')
        if letter_b64:
            letter_name = file_data.get('appointment_letter_name') or f'{matricule}_nomination.pdf'
            _save_file_field(instance, 'appointment_letter', letter_b64, letter_name)

        _sync_inlines(instance, inline_data)

        output = model_serializer_factory(Employee)(instance)
        return Response(
            {'status': action, 'data': output.data},
            status=status.HTTP_201_CREATED if action == 'created' else status.HTTP_200_OK,
        )


class GuichetEmployeeLookup(APIView):
    """Préremplissage guichet register à partir du matricule / NIU."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        forbidden = _check_guichet_key(request)
        if forbidden:
            return forbidden

        matricule = (request.query_params.get('registration_number') or '').strip()
        if not matricule:
            return Response(
                {'status': 'unsuccessful', 'errors': {'registration_number': 'required'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee = (
            Employee.objects.filter(registration_number=matricule)
            .select_related(
                'designation',
                'branch',
                'direction',
                'sub_direction',
                'service',
                'grade',
                'agreement',
            )
            .first()
        )
        if not employee:
            return Response({'status': 'not_found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'status': 'ok', 'data': employee_to_guichet_form(employee)})


class GuichetEmployeeList(APIView):
    """Liste agents RH pour le guichet register (recherche multi-champs)."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        forbidden = _check_guichet_key(request)
        if forbidden:
            return forbidden

        query = (request.query_params.get('q') or '').strip()
        try:
            page = max(int(request.query_params.get('page', 1)), 1)
        except ValueError:
            page = 1
        try:
            page_size = min(max(int(request.query_params.get('page_size', 25)), 1), 100)
        except ValueError:
            page_size = 25

        qs = apply_roster_filter(
            Employee.objects.select_related(
                'designation',
                'branch',
                'direction',
                'grade',
            )
        ).order_by('registration_number')

        if query:
            qs = qs.filter(
                Q(registration_number__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(middle_name__icontains=query)
                | Q(payer_name__icontains=query)
                | Q(payment_account__icontains=query)
                | Q(telephone_number__icontains=query)
                | Q(mobile_number__icontains=query)
                | Q(email__icontains=query)
                | Q(email_professional__icontains=query)
                | Q(physical_address__icontains=query)
                | Q(designation__name__icontains=query)
                | Q(payroll_lines__full_name__icontains=query)
                | Q(payroll_lines__fonction__icontains=query)
                | Q(metadata__nom_postnom__icontains=query)
            ).distinct()

        total = qs.count()
        start = (page - 1) * page_size
        rows = qs[start : start + page_size]

        return Response(
            {
                'status': 'ok',
                'count': total,
                'page': page,
                'page_size': page_size,
                'results': [employee_to_guichet_form(employee) for employee in rows],
            }
        )
