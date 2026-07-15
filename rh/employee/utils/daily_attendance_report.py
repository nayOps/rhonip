"""Rapport journalier de présence — registre entreprise pour une journée."""

from __future__ import annotations

from datetime import date, time as dt_time
from urllib.parse import urlencode

from django.utils import timezone
from django.utils.translation import gettext as _

from core.models import Organization
from employee.models import Direction, Employee
from employee.utils.attendance_schedule_config import (
    get_work_end,
    get_work_start,
)
from employee.utils.attendance_slots import slot_display_cell
from employee.utils.attendance_stats import (
    WEEKDAY_FULL,
    _day_detail,
    bulk_punches_by_employee,
)
from employee.utils.company_attendance import _morning_punch_on_day
from employee.utils.report_pdf_common import build_pdf_filename, logo_data_uri
from employee.utils.roster import apply_roster_filter

STATUS_BADGE_CLASS = {
    'present': 'present',
    'partial': 'partial',
    'absent': 'absent',
}

REPORT_SLOT_CODES = ('MORNING_IN', 'EVENING_OUT')
REPORT_SLOT_HEADERS = (_('Entrée'), _('Sortie'))
REPORT_STATUS_LABELS = {
    'present': _('PRÉSENT'),
    'partial': _('PARTIEL'),
    'absent': _('ABSENT'),
}


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


def build_daily_attendance_query_string(
    target_date: date | None = None,
    direction_id: int | str | None = None,
) -> str:
    params = {}
    if target_date:
        params['date'] = target_date.isoformat()
    if direction_id:
        params['direction'] = str(direction_id)
    return urlencode(params)


def parse_daily_attendance_filters(
    target_date: str | None = None,
    direction: str | None = None,
) -> dict:
    parsed_date = _parse_date(target_date) or timezone.localdate()
    direction_id = None
    direction_label = ''
    raw_direction = (direction or '').strip()
    if raw_direction:
        try:
            direction_id = int(raw_direction)
            direction_obj = Direction.objects.filter(pk=direction_id).first()
            direction_label = str(direction_obj) if direction_obj else ''
        except (TypeError, ValueError):
            direction_id = None

    return {
        'target_date': parsed_date,
        'target_date_value': parsed_date.isoformat(),
        'direction_id': direction_id,
        'direction_value': str(direction_id) if direction_id else '',
        'direction_label': direction_label,
        'query_string': build_daily_attendance_query_string(parsed_date, direction_id),
    }


def _format_count(value: int) -> str:
    return f'{value:,}'.replace(',', ' ')


def _format_duration(total_minutes: int) -> str:
    if not total_minutes:
        return '—'
    hours, minutes = divmod(total_minutes, 60)
    return f'{hours}h {minutes:02d}m'


def _full_name(employee: Employee) -> str:
    parts = [
        (employee.last_name or '').strip(),
        (employee.middle_name or '').strip(),
        (employee.first_name or '').strip(),
    ]
    label = ' '.join(part for part in parts if part)
    return label or '—'


def _fonction_label(employee: Employee) -> str:
    if employee.designation:
        return employee.designation.name or '—'
    return '—'


def _arrival_sort_key(row: dict):
    punch = row.get('morning_punch_time')
    if punch is None:
        return (1, dt_time.max, row.get('full_name', '').casefold())
    return (0, punch, ())


def _punch_count_on_day(emp_bulk: dict, target_date: date) -> int:
    punch_times = emp_bulk.get(target_date, [])
    return len(punch_times) if punch_times else 0


def _report_status_from_punch_count(punch_count: int) -> tuple[str, str]:
    if punch_count >= 2:
        return 'present', REPORT_STATUS_LABELS['present']
    if punch_count == 1:
        return 'partial', REPORT_STATUS_LABELS['partial']
    return 'absent', REPORT_STATUS_LABELS['absent']


def _has_marked_presence_on_day(emp_bulk: dict, target_date: date) -> bool:
    return _punch_count_on_day(emp_bulk, target_date) >= 1


def _two_slot_values(slots: dict) -> list[dict]:
    values = []
    for index, code in enumerate(REPORT_SLOT_CODES):
        cell = slot_display_cell(slots.get(code), code)
        time_label = cell.get('time', '--:--')
        if time_label == '--:--':
            time_label = '—'
        is_late_entry = index == 0 and cell.get('badge_class') in ('late', 'missed_entry')
        values.append({'time': time_label, 'is_late': is_late_entry})
    return values


def _employees_queryset(direction_id: int | None = None):
    queryset = apply_roster_filter(
        Employee.objects.filter(agent_situation='active').select_related(
            'direction', 'designation', 'service', 'grade'
        )
    ).order_by('last_name', 'first_name', 'middle_name', 'registration_number')
    if direction_id:
        queryset = queryset.filter(direction_id=direction_id)
    return queryset


def _build_rows(employees, target_date: date, bulk_attendance: dict) -> list[dict]:
    rows = []

    for employee in employees:
        emp_bulk = bulk_attendance.get(employee.pk, {})
        punch_count = _punch_count_on_day(emp_bulk, target_date)
        if punch_count < 1:
            continue
        detail = _day_detail(emp_bulk, target_date)
        slots = detail.get('slots', {})
        status, status_label = _report_status_from_punch_count(punch_count)
        rows.append(
            {
                'matricule': employee.registration_number or '—',
                'full_name': _full_name(employee),
                'direction': str(employee.direction) if employee.direction else '—',
                'fonction': _fonction_label(employee),
                'slot_values': _two_slot_values(slots),
                'duration_label': _format_duration(detail.get('worked_minutes', 0)),
                'status': status,
                'status_label': status_label,
                'status_badge_class': STATUS_BADGE_CLASS.get(status, 'absent'),
                'note': detail.get('note', ''),
                'morning_punch_time': _morning_punch_on_day(emp_bulk, target_date),
                'punch_count': punch_count,
            }
        )

    rows.sort(key=_arrival_sort_key)
    for index, row in enumerate(rows, start=1):
        row['numero'] = index
        row['numero_display'] = f'{index:02d}'
    return rows


def build_daily_attendance_report(
    target_date: date | None = None,
    direction_id: int | None = None,
) -> dict:
    target_date = target_date or timezone.localdate()
    employees = list(_employees_queryset(direction_id))
    employee_ids = [employee.pk for employee in employees]
    bulk = bulk_punches_by_employee(employee_ids, target_date, target_date)

    counts = {'present': 0, 'partial': 0, 'absent': 0}
    for employee in employees:
        punch_count = _punch_count_on_day(bulk.get(employee.pk, {}), target_date)
        status, _status_label = _report_status_from_punch_count(punch_count)
        counts[status] += 1

    rows = _build_rows(employees, target_date, bulk)
    attended = counts['present'] + counts['partial']
    effectif = len(employees)
    registered = len(rows)
    presence_rate = round(attended * 1000 / effectif) / 10 if effectif else 0

    generated_at = timezone.localtime()
    organization = Organization.objects.first()
    weekday_label = WEEKDAY_FULL[target_date.weekday()]
    work_start = get_work_start()
    work_end = get_work_end()

    direction_obj = Direction.objects.filter(pk=direction_id).first() if direction_id else None
    direction_label = str(direction_obj) if direction_obj else _('Toutes directions')

    return {
        'title': _('Rapport de présence journalier'),
        'report_title_line1': _('RAPPORT DE PRÉSENCE'),
        'report_title_line2': _('JOURNALIER'),
        'table_section_title': _('Registre des pointages'),
        'target_date': target_date,
        'target_date_value': target_date.isoformat(),
        'report_day_label': target_date.strftime('%d/%m/%Y'),
        'weekday_label': weekday_label,
        'is_weekend': target_date.weekday() >= 5,
        'direction_id': direction_id,
        'direction_label': direction_label,
        'query_string': build_daily_attendance_query_string(target_date, direction_id),
        'rows': rows,
        'slot_headers': list(REPORT_SLOT_HEADERS),
        'schedule_label': f'{work_start.strftime("%H:%M")} – {work_end.strftime("%H:%M")}',
        'total_count': effectif,
        'total_count_display': _format_count(effectif),
        'registered_count': registered,
        'registered_count_display': _format_count(registered),
        'present_count': counts['present'],
        'present_count_display': _format_count(counts['present']),
        'partial_count': counts['partial'],
        'partial_count_display': _format_count(counts['partial']),
        'absent_count': counts['absent'],
        'absent_count_display': _format_count(counts['absent']),
        'attended_count': attended,
        'attended_count_display': _format_count(attended),
        'presence_rate': presence_rate,
        'presence_rate_display': f'{presence_rate:.1f}%',
        'display_from': 1 if registered else 0,
        'display_to': registered,
        'organization': organization,
        'generated_at': generated_at,
        'generated_at_label': generated_at.strftime('%d/%m/%Y à %H:%M'),
        'report_ref': f'REF-RH-PRES-{target_date.strftime("%Y%m%d")}',
        'logo_uri': logo_data_uri(),
        'pdf_filename': build_pdf_filename('presence-journalier', day=target_date),
        'directions': list(
            Direction.objects.order_by('name').values('id', 'name')
        ),
    }


def render_daily_attendance_html(report: dict | None = None, **kwargs) -> str:
    from django.template.loader import render_to_string

    report = report or build_daily_attendance_report(**kwargs)
    return render_to_string('employee/daily_attendance_report_pdf.html', report)


def render_daily_attendance_pdf(**kwargs) -> bytes:
    from employee.utils.html_pdf_renderer import render_html_to_pdf

    report = build_daily_attendance_report(**kwargs)
    html = render_daily_attendance_html(report)
    return render_html_to_pdf(html)
