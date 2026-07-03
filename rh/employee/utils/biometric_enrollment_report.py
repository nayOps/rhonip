"""Rapport enregistrement biométrique — agents, photos et empreintes."""

from __future__ import annotations

from datetime import date, datetime, time
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _

from core.models import Organization
from employee.models import Employee
from employee.services.fingerprint_enrollment import get_enrollment_status
from employee.services.fingerprint_tablet import FINGER_POSITION_TO_TABLET
from employee.utils.roster import apply_roster_filter

FINGER_LABELS_FR = {
    'RIGHT_THUMB': _('Pouce droit'),
    'RIGHT_INDEX': _('Index droit'),
    'RIGHT_MIDDLE': _('Majeur droit'),
    'RIGHT_RING': _('Annulaire droit'),
    'RIGHT_LITTLE': _('Auriculaire droit'),
    'LEFT_THUMB': _('Pouce gauche'),
    'LEFT_INDEX': _('Index gauche'),
    'LEFT_MIDDLE': _('Majeur gauche'),
    'LEFT_RING': _('Annulaire gauche'),
    'LEFT_LITTLE': _('Auriculaire gauche'),
}

FILTER_CHOICES = (
    ('all', _('Tous les agents')),
    ('complete', _('Enrôlement complet (10/10)')),
    ('partial', _('Enrôlement partiel')),
    ('none', _('Sans empreinte')),
)

SITUATION_FILTER_CHOICES = (
    ('all', _('Tous')),
    ('active', _('Actif')),
    ('inactive', _('Inactif')),
)


def _parse_date(value) -> date | None:
    if not value:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _format_enrollment_date(value) -> str:
    if not value:
        return '—'
    if isinstance(value, datetime):
        value = timezone.localtime(value)
        return value.strftime('%d/%m/%Y')
    if isinstance(value, date):
        return value.strftime('%d/%m/%Y')
    return '—'


def _date_range_bounds(date_from: date | None, date_to: date | None) -> tuple[datetime | None, datetime | None]:
    tz = timezone.get_current_timezone()
    start_dt = None
    end_dt = None
    if date_from:
        start_dt = timezone.make_aware(datetime.combine(date_from, time.min), tz)
    if date_to:
        end_dt = timezone.make_aware(datetime.combine(date_to, time.max), tz)
    return start_dt, end_dt


def _registration_numbers_for_date_range(date_from: date | None, date_to: date | None) -> set[str]:
    if not date_from and not date_to:
        return set()

    start_dt, end_dt = _date_range_bounds(date_from, date_to)
    conditions = ["capture_status = 'CAPTURED'"]
    params: list = []
    if start_dt:
        conditions.append('COALESCE(captured_at, updated_at, created_at) >= %s')
        params.append(start_dt)
    if end_dt:
        conditions.append('COALESCE(captured_at, updated_at, created_at) <= %s')
        params.append(end_dt)

    sql = f"""
        SELECT DISTINCT registration_number
        FROM fgp_fingerprints
        WHERE {' AND '.join(conditions)}
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return {row[0] for row in cursor.fetchall() if row[0]}


def _fetch_enrollment_date_map(registration_numbers) -> dict[str, dict]:
    numbers = [number for number in registration_numbers if number]
    if not numbers:
        return {}

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT registration_number,
                   MIN(COALESCE(captured_at, updated_at, created_at)),
                   MAX(COALESCE(captured_at, updated_at, created_at))
            FROM fgp_fingerprints
            WHERE capture_status = 'CAPTURED'
              AND registration_number = ANY(%s)
            GROUP BY registration_number
            """,
            [numbers],
        )
        rows = cursor.fetchall()

    result = {}
    for registration_number, first_at, last_at in rows:
        result[registration_number] = {
            'first_at': first_at,
            'last_at': last_at,
            'first_label': _format_enrollment_date(first_at),
            'last_label': _format_enrollment_date(last_at),
        }
    return result


def _date_range_label(date_from: date | None, date_to: date | None) -> str:
    if date_from and date_to:
        return f'{_format_enrollment_date(date_from)} – {_format_enrollment_date(date_to)}'
    if date_from:
        return _('À partir du %(date)s') % {'date': _format_enrollment_date(date_from)}
    if date_to:
        return _('Jusqu’au %(date)s') % {'date': _format_enrollment_date(date_to)}
    return ''


def _logo_file_uri() -> str | None:
    organization = Organization.objects.first()
    if organization and organization.logo:
        logo_path = Path(organization.logo.path)
        if logo_path.is_file():
            return logo_path.as_uri()

    static_logo = Path(settings.BASE_DIR) / 'static' / 'assets' / 'images' / 'logo' / 'logo.svg'
    if static_logo.is_file():
        return static_logo.as_uri()
    return None


def _photo_file_uri(employee: Employee) -> str | None:
    if not employee.photo:
        return None
    try:
        photo_path = Path(employee.photo.path)
    except (ValueError, OSError):
        return None
    if photo_path.is_file():
        return photo_path.as_uri()
    return None


def _finger_label(position: str) -> str:
    return str(FINGER_LABELS_FR.get(position, FINGER_POSITION_TO_TABLET.get(position, position)))


def _enrollment_row(employee: Employee, enrollment_dates: dict | None = None) -> dict:
    enrollment = get_enrollment_status(employee)
    dates = (enrollment_dates or {}).get(employee.registration_number, {})
    fingers = []
    for finger in enrollment.get('fingers', []):
        position = finger.get('fingerPosition', '')
        captured = finger.get('morphoReady') and finger.get('status') == 'CAPTURED'
        fingers.append(
            {
                'position': position,
                'label': _finger_label(position),
                'captured': captured,
                'status': finger.get('status', 'PENDING'),
            }
        )

    enrolled_count = enrollment.get('enrolledCount', 0)
    total_fingers = enrollment.get('totalFingers', 10)

    return {
        'employee': employee,
        'photo_uri': _photo_file_uri(employee),
        'photo_url': employee.photo.url if employee.photo else '',
        'enrollment': enrollment,
        'fingers': fingers,
        'enrolled_count': enrolled_count,
        'total_fingers': total_fingers,
        'is_complete': enrolled_count >= total_fingers and total_fingers > 0,
        'has_any': enrolled_count > 0,
        'agent_situation': employee.agent_situation,
        'agent_situation_label': employee.get_agent_situation_display(),
        'is_active': employee.agent_situation == 'active',
        'status_label': (
            _('Complet') if enrolled_count >= total_fingers and total_fingers > 0
            else _('Partiel') if enrolled_count > 0
            else _('Non enrôlé')
        ),
        'first_enrolled_label': dates.get('first_label', '—'),
        'last_enrolled_label': dates.get('last_label', '—'),
    }


def _filter_employees_by_search(queryset, query):
    query = (query or '').strip()
    if not query:
        return queryset

    for term in query.split():
        queryset = queryset.filter(
            Q(registration_number__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(middle_name__icontains=term)
            | Q(designation__name__icontains=term)
            | Q(direction__name__icontains=term)
            | Q(service__name__icontains=term)
        )
    return queryset.distinct()


def parse_report_filters(
    filter_status: str | None = None,
    situation_filter: str | None = None,
    search_query: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    valid_filters = {code for code, _ in FILTER_CHOICES}
    valid_situations = {code for code, _ in SITUATION_FILTER_CHOICES}
    status = (filter_status or 'all').strip()
    situation = (situation_filter or 'all').strip()
    if status not in valid_filters:
        status = 'all'
    if situation not in valid_situations:
        situation = 'all'

    parsed_from = _parse_date(date_from)
    parsed_to = _parse_date(date_to)
    if parsed_from and parsed_to and parsed_from > parsed_to:
        parsed_from, parsed_to = parsed_to, parsed_from

    return {
        'filter_status': status,
        'situation_filter': situation,
        'search_query': (search_query or '').strip(),
        'date_from': parsed_from,
        'date_to': parsed_to,
        'date_from_value': parsed_from.isoformat() if parsed_from else '',
        'date_to_value': parsed_to.isoformat() if parsed_to else '',
    }


REPORT_PAGE_SIZE = 10


def build_report_query_string(
    filter_status: str = 'all',
    situation_filter: str = 'all',
    search_query: str = '',
    date_from: date | str | None = None,
    date_to: date | str | None = None,
    page: int | None = None,
) -> str:
    from urllib.parse import urlencode

    params = {
        'filter': filter_status,
        'situation': situation_filter,
    }
    if search_query:
        params['q'] = search_query
    if date_from:
        params['date_from'] = date_from.isoformat() if hasattr(date_from, 'isoformat') else str(date_from)
    if date_to:
        params['date_to'] = date_to.isoformat() if hasattr(date_to, 'isoformat') else str(date_to)
    if page and page > 1:
        params['page'] = page
    return urlencode(params)


def paginate_report_rows(rows, request, page_size: int = REPORT_PAGE_SIZE) -> dict:
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        page = 1

    total = len(rows)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, total_pages)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    page_numbers = list(range(max(1, page - 1), min(total_pages, page + 2) + 1))
    query = request.GET.copy()

    def _page_query(target_page: int) -> str:
        query['page'] = target_page
        return query.urlencode()

    return {
        'items': rows[start_index:end_index],
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': total_pages,
        'start': start_index + 1 if total else 0,
        'end': min(end_index, total),
        'page_numbers': page_numbers,
        'prev_query': _page_query(page - 1) if page > 1 else '',
        'next_query': _page_query(page + 1) if page < total_pages else '',
        'page_links': [{'num': num, 'query': _page_query(num)} for num in page_numbers],
    }


def biometric_enrollment_queryset(
    situation_filter: str = 'all',
    search_query: str = '',
    date_from: date | None = None,
    date_to: date | None = None,
):
    queryset = apply_roster_filter(
        Employee.objects.select_related('direction', 'designation', 'service')
    ).order_by('last_name', 'first_name', 'middle_name')
    if situation_filter == 'active':
        queryset = queryset.filter(agent_situation='active')
    elif situation_filter == 'inactive':
        queryset = queryset.filter(agent_situation='inactive')
    queryset = _filter_employees_by_search(queryset, search_query)
    if date_from or date_to:
        registration_numbers = _registration_numbers_for_date_range(date_from, date_to)
        queryset = queryset.filter(registration_number__in=registration_numbers)
    return queryset


def build_biometric_enrollment_report(
    filter_status: str = 'all',
    situation_filter: str = 'all',
    search_query: str = '',
    date_from: date | str | None = None,
    date_to: date | str | None = None,
) -> dict:
    filters = parse_report_filters(filter_status, situation_filter, search_query, date_from, date_to)
    filter_status = filters['filter_status']
    situation_filter = filters['situation_filter']
    search_query = filters['search_query']
    date_from = filters['date_from']
    date_to = filters['date_to']

    employees = list(
        biometric_enrollment_queryset(situation_filter, search_query, date_from, date_to)
    )
    enrollment_dates = _fetch_enrollment_date_map(
        employee.registration_number for employee in employees
    )

    rows = []
    complete_count = 0
    partial_count = 0
    none_count = 0
    active_count = 0
    inactive_count = 0

    for employee in employees:
        row = _enrollment_row(employee, enrollment_dates)
        if row['is_complete']:
            complete_count += 1
        elif row['has_any']:
            partial_count += 1
        else:
            none_count += 1
        if row['is_active']:
            active_count += 1
        else:
            inactive_count += 1

        if filter_status == 'complete' and not row['is_complete']:
            continue
        if filter_status == 'partial' and not (row['has_any'] and not row['is_complete']):
            continue
        if filter_status == 'none' and row['has_any']:
            continue
        rows.append(row)

    organization = Organization.objects.first()
    generated_at = timezone.localtime()

    return {
        'title': _('Rapport enregistrement biométrique'),
        'rows': rows,
        'filter_status': filter_status,
        'filter_choices': FILTER_CHOICES,
        'filter_tabs': [
            {
                'code': code,
                'label': label,
                'query': build_report_query_string(
                    code,
                    situation_filter,
                    search_query,
                    date_from=date_from,
                    date_to=date_to,
                ),
            }
            for code, label in FILTER_CHOICES
        ],
        'situation_filter': situation_filter,
        'situation_filter_choices': SITUATION_FILTER_CHOICES,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'date_from_value': filters['date_from_value'],
        'date_to_value': filters['date_to_value'],
        'date_range_label': _date_range_label(date_from, date_to),
        'has_date_filter': bool(date_from or date_to),
        'clear_search_query': build_report_query_string(
            filter_status,
            situation_filter,
            '',
            date_from=date_from,
            date_to=date_to,
        ),
        'clear_dates_query': build_report_query_string(
            filter_status,
            situation_filter,
            search_query,
        ),
        'query_string': build_report_query_string(
            filter_status,
            situation_filter,
            search_query,
            date_from=date_from,
            date_to=date_to,
        ),
        'organization': organization,
        'generated_at': generated_at,
        'generated_at_label': generated_at.strftime('%d/%m/%Y à %H:%M'),
        'total_count': len(rows),
        'complete_count': complete_count,
        'partial_count': partial_count,
        'none_count': none_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'logo_uri': _logo_file_uri(),
        'report_ref': f'REF-RH-BIO-{generated_at:%Y%m%d}',
    }


def render_biometric_enrollment_html(report: dict | None = None) -> str:
    report = report or build_biometric_enrollment_report()
    return render_to_string('employee/biometric_enrollment_report_pdf.html', report)


def render_biometric_enrollment_pdf(report: dict | None = None) -> bytes:
    from xhtml2pdf import pisa

    html = render_biometric_enrollment_html(report)
    buffer = BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, encoding='utf-8')
    if result.err:
        raise RuntimeError('La génération du PDF a échoué.')
    return buffer.getvalue()
