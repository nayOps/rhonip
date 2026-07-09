"""Service d'import agents/ → Employee + PayrollPeriod + PayrollLine."""
from __future__ import annotations

from pathlib import Path

from django.db import transaction

from employee.models import Designation, Employee, PayrollLine, PayrollPeriod
from employee.utils.agents_paie import (
    default_agents_paie_path,
    load_agents_paie_file,
    parse_nom_postnom,
    period_code_from_label,
)
from employee.services.sync_positions_from_paie import resolve_designation


def import_agents_paie(
    path: Path | None = None,
    *,
    update_existing: bool = True,
    dry_run: bool = False,
) -> dict:
    source = path or default_agents_paie_path()
    if not source.is_file():
        raise FileNotFoundError(f'Fichier introuvable: {source}')

    payload = load_agents_paie_file(source)
    metadata = payload.get('metadata') or {}
    agents = payload.get('agents') or []
    periode_label = metadata.get('periode') or 'PAIE'
    period_code = period_code_from_label(periode_label)

    stats = {
        'source': str(source),
        'period_code': period_code,
        'employees_created': 0,
        'employees_updated': 0,
        'employees_skipped': 0,
        'payroll_lines': 0,
        'designations_created': 0,
        'dry_run': dry_run,
    }

    if dry_run:
        stats['would_import'] = len(agents)
        return stats

    with transaction.atomic():
        period, _ = PayrollPeriod.objects.update_or_create(
            code=period_code,
            defaults={
                'label': periode_label,
                'bank': metadata.get('banque'),
                'institution': metadata.get('institution'),
                'effectifs': metadata.get('effectifs') or len(agents),
                'metadata': {
                    'totaux': metadata.get('totaux_officiels_document') or {},
                    'ministere': metadata.get('ministere'),
                    'province': metadata.get('province'),
                },
            },
        )

        PayrollLine.objects.filter(period=period).delete()

        for row in agents:
            niu = str(row.get('niu') or '').strip()
            if not niu:
                stats['employees_skipped'] += 1
                continue

            full_name = (row.get('nom_postnom') or '').strip()
            fonction = (row.get('fonction') or '').strip()
            last_name, middle_name, first_name = parse_nom_postnom(full_name)

            designation = None
            if fonction:
                designation, created = resolve_designation(fonction)
                if created:
                    stats['designations_created'] += 1

            employee = Employee.objects.filter(registration_number=niu).first()
            payroll_snapshot = {
                'periode': periode_label,
                'period_code': period_code,
                'niu': niu,
                'fonction': fonction,
                'base': row.get('base'),
                'prime': row.get('prime'),
                'logement': row.get('logement'),
                'ipr': row.get('ipr'),
                'cpa': row.get('cpa'),
                'montant_net': row.get('montant_net'),
                'ftc': row.get('ftc'),
                'net_a_payer': row.get('net_a_payer'),
            }

            if employee is None:
                employee = Employee.objects.create(
                    registration_number=niu,
                    last_name=last_name or full_name or niu,
                    middle_name=middle_name,
                    first_name=first_name,
                    gender='male',
                    marital_status='single',
                    payment_method='bank',
                    payer_name=metadata.get('banque') or 'SOFIBANQUE',
                    designation=designation,
                    metadata={
                        'import_source': 'agents_paie',
                        'nom_postnom': full_name,
                        'payroll': {period_code: payroll_snapshot},
                    },
                )
                stats['employees_created'] += 1
            elif update_existing:
                changed = False
                if not employee.first_name and first_name:
                    employee.first_name = first_name
                    changed = True
                if not employee.middle_name and middle_name:
                    employee.middle_name = middle_name
                    changed = True
                if not employee.last_name and last_name:
                    employee.last_name = last_name
                    changed = True
                if fonction:
                    if designation is None:
                        designation, created = resolve_designation(fonction)
                        if created:
                            stats['designations_created'] += 1
                    if employee.designation_id != designation.id:
                        employee.designation = designation
                        changed = True
                if not employee.payer_name:
                    employee.payer_name = metadata.get('banque') or 'SOFIBANQUE'
                    changed = True
                meta = employee.metadata or {}
                meta.setdefault('import_source', 'agents_paie')
                if full_name:
                    meta['nom_postnom'] = full_name
                payroll_meta = meta.get('payroll') or {}
                payroll_meta[period_code] = payroll_snapshot
                meta['payroll'] = payroll_meta
                employee.metadata = meta
                changed = True
                if changed:
                    employee.save()
                    stats['employees_updated'] += 1
                else:
                    stats['employees_skipped'] += 1
            else:
                stats['employees_skipped'] += 1

            PayrollLine.objects.create(
                period=period,
                employee=employee,
                line_number=row.get('n') or 0,
                registration_number=niu,
                full_name=full_name,
                fonction=fonction or None,
                base=int(row.get('base') or 0),
                prime=int(row.get('prime') or 0),
                logement=int(row.get('logement') or 0),
                ipr=int(row.get('ipr') or 0),
                cpa=int(row.get('cpa') or 0),
                montant_net=int(row.get('montant_net') or 0),
                ftc=int(row.get('ftc') or 0),
                net_a_payer=int(row.get('net_a_payer') or 0),
            )
            stats['payroll_lines'] += 1

    return stats
