"""Filtres pour l'effectif opérationnel (liste agents / présences / guichet)."""

from django.contrib.auth import get_user_model
from django.db.models import Q

from employee.models import Employee


def _named_agent_q():
    return (
        (Q(first_name__isnull=False) & ~Q(first_name=''))
        | (Q(last_name__isnull=False) & ~Q(last_name=''))
    )


def staff_linked_employee_ids():
    User = get_user_model()
    return User.objects.filter(
        Q(is_staff=True) | Q(is_superuser=True),
        employee__isnull=False,
    ).values_list('employee_id', flat=True)


def apply_roster_filter(queryset):
    """Exclut les comptes admin liés à une fiche et les fiches sans identité."""
    return queryset.exclude(
        pk__in=staff_linked_employee_ids(),
    ).filter(_named_agent_q())


def roster_employees_queryset():
    return apply_roster_filter(Employee.objects.all())
