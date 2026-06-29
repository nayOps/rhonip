"""Rapport enregistrement biométrique — agents, photos et empreintes."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.conf import settings
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


def _enrollment_row(employee: Employee) -> dict:
    enrollment = get_enrollment_status(employee)
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
        'status_label': (
            _('Complet') if enrolled_count >= total_fingers and total_fingers > 0
            else _('Partiel') if enrolled_count > 0
            else _('Non enrôlé')
        ),
    }


def biometric_enrollment_queryset():
    return apply_roster_filter(
        Employee.objects.select_related('direction', 'designation', 'service')
    ).order_by('last_name', 'first_name', 'middle_name')


def build_biometric_enrollment_report(filter_status: str = 'all') -> dict:
    rows = []
    complete_count = 0
    partial_count = 0
    none_count = 0

    for employee in biometric_enrollment_queryset():
        row = _enrollment_row(employee)
        if row['is_complete']:
            complete_count += 1
        elif row['has_any']:
            partial_count += 1
        else:
            none_count += 1

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
        'organization': organization,
        'generated_at': generated_at,
        'generated_at_label': generated_at.strftime('%d/%m/%Y à %H:%M'),
        'total_count': len(rows),
        'complete_count': complete_count,
        'partial_count': partial_count,
        'none_count': none_count,
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
