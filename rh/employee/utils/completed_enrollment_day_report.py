"""Rapport journalier — agents ACTIF avec enrôlement complet 10/10 (empreintes tablette)."""

from __future__ import annotations

from datetime import date, datetime, time
from urllib.parse import urlencode

from django.db import connection
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _

from core.models import Organization
from employee.models import Employee
from employee.services.fingerprint_enrollment import get_enrollment_status
from employee.utils.report_pdf_common import build_pdf_filename, logo_data_uri, photo_data_uri


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


def build_enrollment_day_query_string(
    target_date: date | None = None,
    period_from: date | None = None,
    period_to: date | None = None,
) -> str:
    params = {}
    if target_date:
        params['date'] = target_date.isoformat()
    if period_from:
        params['period_from'] = period_from.isoformat()
    if period_to:
        params['period_to'] = period_to.isoformat()
    return urlencode(params)


def parse_enrollment_day_filters(
    target_date: str | None = None,
    period_from: str | None = None,
    period_to: str | None = None,
) -> dict:
    parsed_date = _parse_date(target_date) or timezone.localdate()
    parsed_from = _parse_date(period_from)
    parsed_to = _parse_date(period_to)
    if parsed_from and parsed_to and parsed_from > parsed_to:
        parsed_from, parsed_to = parsed_to, parsed_from
    return {
        'target_date': parsed_date,
        'period_from': parsed_from,
        'period_to': parsed_to,
        'target_date_value': parsed_date.isoformat(),
        'period_from_value': parsed_from.isoformat() if parsed_from else '',
        'period_to_value': parsed_to.isoformat() if parsed_to else '',
        'query_string': build_enrollment_day_query_string(parsed_date, parsed_from, parsed_to),
    }


def _full_name(employee: Employee) -> str:
    parts = [
        (employee.last_name or '').strip(),
        (employee.middle_name or '').strip(),
        (employee.first_name or '').strip(),
    ]
    label = ' '.join(p for p in parts if p)
    return label or '—'


def _situation_label(employee: Employee) -> str:
    if employee.agent_situation == 'active':
        return 'ACTIF'
    if employee.agent_situation == 'inactive':
        return 'INACTIF'
    return str(employee.get_agent_situation_display() or '—').upper()


def _fonction_label(employee: Employee) -> str:
    if employee.designation:
        return employee.designation.name or '—'
    return '—'


def _is_complete_enrollment(employee: Employee) -> bool:
    enrollment = get_enrollment_status(employee)
    enrolled_count = enrollment.get('enrolledCount', 0)
    total_fingers = enrollment.get('totalFingers', 10)
    return enrolled_count >= total_fingers and total_fingers > 0


def _fetch_matricules_in_period(
    period_from: date | None = None,
    period_to: date | None = None,
) -> set[str]:
    """Matricules ayant au moins une capture dans la période."""
    if not period_from and not period_to:
        return set()

    tz = timezone.get_current_timezone()
    params: list = []
    conditions = ["capture_status = 'CAPTURED'", "registration_number IS NOT NULL", "trim(registration_number) <> ''"]
    if period_from:
        start_dt = timezone.make_aware(datetime.combine(period_from, time.min), tz)
        conditions.append('COALESCE(captured_at, updated_at, created_at) >= %s')
        params.append(start_dt)
    if period_to:
        end_dt = timezone.make_aware(datetime.combine(period_to, time.max), tz)
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


def _fetch_matricules_last_capture_on_day(
    target_date: date,
    period_from: date | None = None,
    period_to: date | None = None,
) -> list[str]:
    """Matricules ACTIF 10/10 dont la dernière capture (dans la période) tombe ce jour."""
    tz = timezone.get_current_timezone()
    day_start = timezone.make_aware(datetime.combine(target_date, time.min), tz)
    day_end = timezone.make_aware(datetime.combine(target_date, time.max), tz)

    period_start = None
    period_end = None
    if period_from:
        period_start = timezone.make_aware(datetime.combine(period_from, time.min), tz)
    if period_to:
        period_end = timezone.make_aware(datetime.combine(period_to, time.max), tz)

    params: list = []
    period_conditions = ''
    if period_start:
        period_conditions += ' AND COALESCE(captured_at, updated_at, created_at) >= %s'
        params.append(period_start)
    if period_end:
        period_conditions += ' AND COALESCE(captured_at, updated_at, created_at) <= %s'
        params.append(period_end)

    sql = f"""
        WITH period_caps AS (
            SELECT registration_number,
                   COALESCE(captured_at, updated_at, created_at) AS cap_at
            FROM fgp_fingerprints
            WHERE capture_status = 'CAPTURED'
              AND registration_number IS NOT NULL
              AND trim(registration_number) <> ''
              {period_conditions}
        ),
        last_caps AS (
            SELECT registration_number, max(cap_at) AS last_at
            FROM period_caps
            GROUP BY registration_number
        )
        SELECT lc.registration_number
        FROM last_caps lc
        JOIN employee_employee ee ON ee.registration_number = lc.registration_number
        WHERE ee.agent_situation = 'active'
          AND lc.last_at >= %s
          AND lc.last_at <= %s
        ORDER BY lc.registration_number
    """
    params.extend([day_start, day_end])

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        matricules = [row[0] for row in cursor.fetchall() if row[0]]

    if not matricules:
        return []

    employees = {
        e.registration_number: e
        for e in Employee.objects.filter(registration_number__in=matricules).select_related('designation')
    }
    return [
        matricule
        for matricule in matricules
        if matricule in employees and _is_complete_enrollment(employees[matricule])
    ]


def _fetch_complete_active_agents_global(
    period_from: date | None = None,
    period_to: date | None = None,
) -> list[Employee]:
    """Tous les agents ACTIF 10/10 ayant capturé au moins une empreinte dans la période."""
    matricules = _fetch_matricules_in_period(period_from, period_to)
    if not matricules:
        return []

    employees = list(
        Employee.objects.filter(
            agent_situation='active',
            registration_number__in=matricules,
        )
        .select_related('designation')
        .order_by('last_name', 'first_name', 'middle_name')
    )
    return [employee for employee in employees if _is_complete_enrollment(employee)]


def _fetch_complete_active_agents_for_day(
    target_date: date,
    period_from: date | None = None,
    period_to: date | None = None,
) -> list[Employee]:
    matricules = _fetch_matricules_last_capture_on_day(target_date, period_from, period_to)
    if not matricules:
        return []

    employees = list(
        Employee.objects.filter(registration_number__in=matricules)
        .select_related('designation')
        .order_by('last_name', 'first_name', 'middle_name')
    )
    return employees


def _format_count(value: int) -> str:
    return f'{value:,}'.replace(',', ' ')


def _build_rows(employees: list[Employee]) -> list[dict]:
    rows = []
    for employee in employees:
        rows.append(
            {
                'matricule': employee.registration_number,
                'full_name': _full_name(employee),
                'sort_key': _full_name(employee).casefold(),
                'photo_uri': photo_data_uri(employee.photo),
                'photo_url': employee.photo.url if employee.photo else '',
                'statut': _situation_label(employee),
                'fonction': _fonction_label(employee),
            }
        )

    rows.sort(key=lambda r: (r['sort_key'], r['matricule'] or ''))
    for index, row in enumerate(rows, start=1):
        row['numero'] = index
        row['numero_display'] = f'{index:02d}'
    return rows


def build_completed_enrollment_global_report(
    period_from: date | None = None,
    period_to: date | None = None,
) -> dict:
    employees = _fetch_complete_active_agents_global(period_from, period_to)
    rows = _build_rows(employees)
    generated_at = timezone.localtime()
    organization = Organization.objects.first()

    period_label = ''
    if period_from and period_to:
        period_label = f'{period_from.strftime("%d/%m/%Y")} – {period_to.strftime("%d/%m/%Y")}'
    elif period_from:
        period_label = _('À partir du %(date)s') % {'date': period_from.strftime('%d/%m/%Y')}
    elif period_to:
        period_label = _('Jusqu’au %(date)s') % {'date': period_to.strftime('%d/%m/%Y')}

    total = len(rows)
    return {
        'is_global_report': True,
        'target_date': generated_at.date(),
        'target_date_value': generated_at.date().isoformat(),
        'report_day_label': generated_at.strftime('%d/%m/%Y'),
        'period_from': period_from,
        'period_to': period_to,
        'period_from_value': period_from.isoformat() if period_from else '',
        'period_to_value': period_to.isoformat() if period_to else '',
        'period_label': period_label or '—',
        'has_period_filter': bool(period_from or period_to),
        'query_string': build_enrollment_day_query_string(None, period_from, period_to),
        'rows': rows,
        'total_count': total,
        'total_count_display': _format_count(total),
        'active_count': total,
        'active_count_display': _format_count(total),
        'display_from': 1 if total else 0,
        'display_to': total,
        'organization': organization,
        'generated_at': generated_at,
        'generated_at_label': generated_at.strftime('%d/%m/%Y à %H:%M'),
        'logo_uri': logo_data_uri(),
        'pdf_filename': build_pdf_filename(
            'enregistrement-global',
            date_from=period_from,
            date_to=period_to,
        ),
    }


def build_completed_enrollment_day_report(
    target_date: date | None = None,
    period_from: date | None = None,
    period_to: date | None = None,
) -> dict:
    target_date = target_date or timezone.localdate()
    employees = _fetch_complete_active_agents_for_day(target_date, period_from, period_to)
    rows = _build_rows(employees)
    generated_at = timezone.localtime()
    organization = Organization.objects.first()

    period_label = ''
    if period_from and period_to:
        period_label = f'{period_from.strftime("%d/%m/%Y")} – {period_to.strftime("%d/%m/%Y")}'
    elif period_from:
        period_label = _('À partir du %(date)s') % {'date': period_from.strftime('%d/%m/%Y')}
    elif period_to:
        period_label = _('Jusqu’au %(date)s') % {'date': period_to.strftime('%d/%m/%Y')}

    total = len(rows)
    return {
        'is_global_report': False,
        'target_date': target_date,
        'target_date_value': target_date.isoformat(),
        'report_day_label': target_date.strftime('%d/%m/%Y'),
        'period_from': period_from,
        'period_to': period_to,
        'period_from_value': period_from.isoformat() if period_from else '',
        'period_to_value': period_to.isoformat() if period_to else '',
        'period_label': period_label or '—',
        'has_period_filter': bool(period_from or period_to),
        'query_string': build_enrollment_day_query_string(target_date, period_from, period_to),
        'rows': rows,
        'total_count': total,
        'total_count_display': _format_count(total),
        'active_count': total,
        'active_count_display': _format_count(total),
        'display_from': 1 if total else 0,
        'display_to': total,
        'organization': organization,
        'generated_at': generated_at,
        'generated_at_label': generated_at.strftime('%d/%m/%Y à %H:%M'),
        'logo_uri': logo_data_uri(),
        'pdf_filename': build_pdf_filename('enregistrement-journalier', day=target_date),
    }


def render_completed_enrollment_day_html(
    report: dict | None = None,
    target_date: date | None = None,
    period_from: date | None = None,
    period_to: date | None = None,
) -> str:
    report = report or build_completed_enrollment_day_report(target_date, period_from, period_to)
    return render_to_string('employee/completed_enrollment_day_report_pdf.html', report)


def render_completed_enrollment_global_pdf(
    period_from: date | None = None,
    period_to: date | None = None,
) -> bytes:
    from employee.utils.html_pdf_renderer import render_html_to_pdf

    report = build_completed_enrollment_global_report(period_from, period_to)
    html = render_to_string('employee/completed_enrollment_day_report_pdf.html', report)
    return render_html_to_pdf(html)


def render_completed_enrollment_day_pdf(
    target_date: date | None = None,
    period_from: date | None = None,
    period_to: date | None = None,
) -> bytes:
    from employee.utils.html_pdf_renderer import render_html_to_pdf

    report = build_completed_enrollment_day_report(target_date, period_from, period_to)
    html = render_completed_enrollment_day_html(report)
    return render_html_to_pdf(html)
