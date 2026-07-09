"""Rapports PDF — agents inactifs et actifs sans empreinte ni photo."""

from __future__ import annotations

from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext as _

from core.models import Organization
from employee.models import Employee
from employee.services.fingerprint_enrollment import get_enrollment_status
from employee.utils.completed_enrollment_day_report import (
    _format_count,
    _fonction_label,
    _full_name,
    _situation_label,
)
from employee.utils.html_pdf_renderer import render_html_to_pdf
from employee.utils.report_pdf_common import build_pdf_filename, logo_data_uri, photo_data_uri

REPORT_INACTIVE = 'inactive'
REPORT_MISSING_BIOMETRIC = 'missing_biometric'


def _has_photo(employee: Employee) -> bool:
    if not employee.photo:
        return False
    try:
        return bool(employee.photo.name) and employee.photo.storage.exists(employee.photo.name)
    except (ValueError, OSError):
        return False


def _morpho_captured_count(employee: Employee) -> int:
    enrollment = get_enrollment_status(employee)
    return int(enrollment.get('enrolledCount', 0) or 0)


def fetch_inactive_agents() -> list[Employee]:
    return list(
        Employee.objects.filter(agent_situation='inactive')
        .select_related('designation')
        .order_by('last_name', 'first_name', 'middle_name')
    )


def fetch_active_without_photo_and_fingerprints() -> list[Employee]:
    employees = list(
        Employee.objects.filter(agent_situation='active')
        .select_related('designation')
        .order_by('last_name', 'first_name', 'middle_name')
    )
    rows = []
    for employee in employees:
        if _has_photo(employee):
            continue
        if _morpho_captured_count(employee) > 0:
            continue
        rows.append(employee)
    return rows


def _build_rows(employees: list[Employee]) -> list[dict]:
    rows = []
    for employee in employees:
        rows.append(
            {
                'matricule': employee.registration_number,
                'full_name': _full_name(employee),
                'sort_key': _full_name(employee).casefold(),
                'photo_uri': photo_data_uri(employee.photo),
                'statut': _situation_label(employee),
                'fonction': _fonction_label(employee),
            }
        )
    rows.sort(key=lambda r: (r['sort_key'], r['matricule'] or ''))
    for index, row in enumerate(rows, start=1):
        row['numero'] = index
        row['numero_display'] = f'{index:02d}'
    return rows


def _base_report_context(report_kind: str, rows: list[dict], title_lines: tuple[str, str]) -> dict:
    generated_at = timezone.localtime()
    organization = Organization.objects.first()
    total = len(rows)
    return {
        'report_kind': report_kind,
        'is_global_report': True,
        'report_title_line1': title_lines[0],
        'report_title_line2': title_lines[1],
        'table_section_title': title_lines[1],
        'target_date': generated_at.date(),
        'report_day_label': generated_at.strftime('%d/%m/%Y'),
        'period_label': 'État au ' + generated_at.strftime('%d/%m/%Y'),
        'has_period_filter': False,
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
    }


def build_inactive_agents_report() -> dict:
    rows = _build_rows(fetch_inactive_agents())
    report = _base_report_context(
        REPORT_INACTIVE,
        rows,
        (_('RAPPORT DES AGENTS'), _('INACTIFS')),
    )
    report['pdf_filename'] = build_pdf_filename('agents-inactifs', day=timezone.localdate())
    return report


def build_active_missing_biometric_report() -> dict:
    rows = _build_rows(fetch_active_without_photo_and_fingerprints())
    report = _base_report_context(
        REPORT_MISSING_BIOMETRIC,
        rows,
        (_('RAPPORT DES AGENTS ACTIFS'), _('SANS EMPREINTE NI PHOTO')),
    )
    report['pdf_filename'] = build_pdf_filename('agents-sans-biometrie', day=timezone.localdate())
    return report


def render_biometric_gap_pdf(report: dict) -> bytes:
    html = render_to_string('employee/completed_enrollment_day_report_pdf.html', report)
    return render_html_to_pdf(html)


def render_inactive_agents_pdf() -> bytes:
    return render_biometric_gap_pdf(build_inactive_agents_report())


def render_active_missing_biometric_pdf() -> bytes:
    return render_biometric_gap_pdf(build_active_missing_biometric_report())
