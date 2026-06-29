"""Résolution du N+1 (responsable hiérarchique) par direction."""

from django.apps import apps
from django.contrib.auth import get_user_model


def _designation_name(employee):
    if not employee or not employee.designation:
        return ''
    return (employee.designation.name or '').lower()


def is_direction_leader(employee):
    name = _designation_name(employee)
    return 'directeur' in name or 'sous-directeur' in name or 'sous directeur' in name


def resolve_direction_director(employee):
    """Directeur de la direction de l'employé (hors sous-directeurs)."""
    if not employee or not employee.direction:
        return None
    User = get_user_model()
    return (
        User.objects.filter(
            is_active=True,
            employee__direction=employee.direction,
            employee__designation__name__icontains='Directeur',
        )
        .exclude(employee__designation__name__icontains='Sous-directeur')
        .exclude(employee__designation__name__icontains='Sous directeur')
        .select_related('employee')
        .first()
    )


def resolve_rh_director():
    User = get_user_model()
    return (
        User.objects.filter(
            is_active=True,
            employee__designation__name__icontains='Directeur RH',
        )
        .select_related('employee')
        .first()
    )


def resolve_n_plus_one(employee):
    """
    N+1 pour validation d'une demande agent :
    - employé normal → directeur de sa direction ;
    - directeur / sous-directeur → directeur RH.
    """
    if not employee:
        return None
    if is_direction_leader(employee):
        return resolve_rh_director()
    director = resolve_direction_director(employee)
    if director and employee.pk and getattr(director, 'employee_id', None) == employee.pk:
        return resolve_rh_director()
    return director or resolve_rh_director()
