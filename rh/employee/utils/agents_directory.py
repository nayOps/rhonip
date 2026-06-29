"""Annuaire PDF des agents ONIP (hors direction générale)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from core.models import Organization
from employee.models import Employee
from employee.utils.roster import apply_roster_filter

LEADERSHIP_DESIGNATION_Q = (
    Q(designation__name__iexact='DIRECTEUR GENERAL')
    | Q(designation__name__iexact='Directeur Général')
    | Q(designation__name__iexact='DIRECTEUR GENERAL ADJOINT')
    | Q(designation__name__iexact='Directeur Adjoint')
    | Q(designation__name__icontains='Directeur Général Adjoint')
)


def agents_directory_queryset():
    return (
        apply_roster_filter(
            Employee.objects.select_related('direction')
        )
        .exclude(LEADERSHIP_DESIGNATION_Q)
        .order_by('last_name', 'first_name', 'middle_name')
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


def build_agents_directory_context() -> dict:
    employees = list(agents_directory_queryset())
    organization = Organization.objects.first()
    return {
        'employees': employees,
        'organization': organization,
        'generated_at': timezone.localtime(),
        'total_count': len(employees),
        'logo_uri': _logo_file_uri(),
    }


def render_agents_directory_html() -> str:
    return render_to_string(
        'employee/agents_directory_pdf.html',
        build_agents_directory_context(),
    )


def render_agents_directory_pdf() -> bytes:
    from xhtml2pdf import pisa

    html = render_agents_directory_html()
    buffer = BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, encoding='utf-8')
    if result.err:
        raise RuntimeError('La génération du PDF a échoué.')
    return buffer.getvalue()
