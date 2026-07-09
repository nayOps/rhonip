"""Aligne les positions RH (designation) sur le fichier de paie de référence."""
from __future__ import annotations

from pathlib import Path

from django.db import transaction

from employee.models import Designation, Employee
from employee.utils.agents_paie import default_agents_paie_path, load_agents_paie_file


def resolve_designation(fonction: str) -> tuple[Designation | None, bool]:
    fonction = (fonction or '').strip()
    if not fonction:
        return None, False
    existing = Designation.objects.filter(name__iexact=fonction).first()
    if existing:
        return existing, False
    return Designation.objects.create(name=fonction), True


def sync_employee_positions_from_paie(
    path: Path | None = None,
    *,
    dry_run: bool = False,
) -> dict:
    source = path or default_agents_paie_path()
    if not source.is_file():
        raise FileNotFoundError(f'Fichier introuvable: {source}')

    payload = load_agents_paie_file(source)
    agents = payload.get('agents') or []

    stats = {
        'source': str(source),
        'payroll_agents': len(agents),
        'updated': 0,
        'already_ok': 0,
        'missing_in_rh': 0,
        'empty_fonction': 0,
        'designations_created': 0,
        'dry_run': dry_run,
        'changes': [],
    }

    if dry_run:
        for row in agents:
            niu = str(row.get('niu') or '').strip()
            fonction = (row.get('fonction') or '').strip()
            if not niu:
                continue
            if not fonction:
                stats['empty_fonction'] += 1
                continue
            employee = Employee.objects.filter(registration_number=niu).first()
            if employee is None:
                stats['missing_in_rh'] += 1
                continue
            current = (employee.designation.name if employee.designation_id else '').strip()
            if current.casefold() == fonction.casefold():
                stats['already_ok'] += 1
            else:
                stats['updated'] += 1
                stats['changes'].append({
                    'matricule': niu,
                    'name': employee.full_name(),
                    'before': current or '—',
                    'after': fonction,
                })
        return stats

    with transaction.atomic():
        for row in agents:
            niu = str(row.get('niu') or '').strip()
            fonction = (row.get('fonction') or '').strip()
            if not niu:
                continue
            if not fonction:
                stats['empty_fonction'] += 1
                continue

            employee = Employee.objects.filter(registration_number=niu).first()
            if employee is None:
                stats['missing_in_rh'] += 1
                continue

            current = (employee.designation.name if employee.designation_id else '').strip()
            if current.casefold() == fonction.casefold():
                stats['already_ok'] += 1
                continue

            before = current or '—'
            designation, created = resolve_designation(fonction)
            if created:
                stats['designations_created'] += 1

            employee.designation = designation
            employee.save(update_fields=['designation'])
            stats['updated'] += 1
            stats['changes'].append({
                'matricule': niu,
                'name': employee.full_name(),
                'before': before,
                'after': fonction,
            })

    return stats
