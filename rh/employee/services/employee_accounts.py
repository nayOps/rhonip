"""Création des comptes utilisateurs liés aux employés ONIP."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from employee.models import Employee
from employee.utils.professional_email import is_alema_olamba

EMPLOYEE_GROUP_NAME = 'Employés'

EMPLOYEE_PERMISSIONS = (
    'leave.add_leave',
    'leave.view_leave',
    'leave.change_leave',
    'leave.add_earlyleave',
    'leave.view_earlyleave',
    'leave.change_earlyleave',
    'mission.view_mission',
    'employee.view_employee',
    'employee.change_employee',
    'employee.view_latejustification',
    'employee.add_latejustification',
)

EMPLOYEE_PERMISSIONS_REVOKE = (
    'mission.add_mission',
    'mission.change_mission',
)


def ensure_employee_group() -> Group:
    group, _ = Group.objects.get_or_create(name=EMPLOYEE_GROUP_NAME)
    for perm_string in EMPLOYEE_PERMISSIONS:
        app_label, codename = perm_string.split('.')
        try:
            perm = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )
        except Permission.DoesNotExist:
            continue
        group.permissions.add(perm)
    for perm_string in EMPLOYEE_PERMISSIONS_REVOKE:
        app_label, codename = perm_string.split('.')
        try:
            perm = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename,
            )
        except Permission.DoesNotExist:
            continue
        group.permissions.remove(perm)
    return group


def provision_employee_account(
    employee: Employee,
    *,
    group: Group | None = None,
    reset_password: bool = False,
    dry_run: bool = False,
) -> tuple[str, str | None]:
    """
    Crée ou met à jour le compte d'un employé.
    Retourne (statut, email) avec statut in {created, updated, skipped, error}.
    """
    User = get_user_model()
    email = (employee.email_professional or '').strip()
    matricule = (employee.registration_number or '').strip()

    if not email:
        return 'skipped', None
    if not matricule:
        return 'skipped', None

    if dry_run:
        existing = User.objects.filter(employee=employee).exists()
        return ('updated' if existing else 'created'), email

    user = User.objects.filter(employee=employee).first()
    if user is None:
        user = User.objects.filter(email__iexact=email).first()

    if user is None:
        user = User.objects.create_user(
            email=email,
            password=matricule,
            employee=employee,
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        created = True
    else:
        created = False
        user.email = email
        user.username = email
        user.employee = employee
        user.is_active = True
        user.save(update_fields=['email', 'username', 'employee', 'is_active'])
        if reset_password:
            user.set_password(matricule)
            user.save(update_fields=['password'])

    if group is None:
        group = ensure_employee_group()
    user.groups.add(group)

    return ('created' if created else 'updated'), email


def provision_all_employee_accounts(
    *,
    reset_password: bool = False,
    dry_run: bool = False,
) -> dict:
    stats = {
        'created': 0,
        'updated': 0,
        'skipped_excluded': 0,
        'skipped_incomplete': 0,
        'dry_run': dry_run,
    }

    group = None if dry_run else ensure_employee_group()

    for employee in Employee.objects.order_by('id'):
        if is_alema_olamba(employee):
            stats['skipped_excluded'] += 1
            continue

        status, _email = provision_employee_account(
            employee,
            group=group,
            reset_password=reset_password,
            dry_run=dry_run,
        )
        if status in stats:
            stats[status] += 1
        else:
            stats['skipped_incomplete'] += 1

    return stats
