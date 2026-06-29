"""Bundle empreintes Morpho pour tablettes de pointage."""

from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from employee.models import Employee
from employee.services.fingerprint_tablet import (
    FINGER_POSITION_TO_TABLET,
    FgpFingerprintCapture,
    MATCHING_FINGER_POSITIONS,
    load_template_base64,
)
from employee.utils.roster import apply_roster_filter


def _parse_since(raw: str | None):
    if not raw:
        return None
    text = str(raw).strip()
    if not text:
        return None
    parsed = parse_datetime(text)
    if parsed is None and 'T' not in text:
        parsed = parse_datetime(f'{text}T00:00:00')
    if parsed is None:
        return None
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _employee_row(employee: Employee) -> dict:
    return {
        'employeeId': employee.pk,
        'registrationNumber': employee.registration_number or '',
        'firstName': employee.first_name or '',
        'lastName': employee.last_name or '',
        'middleName': employee.middle_name or '',
        'fullName': employee.full_name(),
    }


def build_fingerprint_bundle(since=None) -> dict:
    since_dt = _parse_since(since) if isinstance(since, str) else since

    employees = list(
        apply_roster_filter(
            Employee.objects.select_related('direction', 'designation')
        ).filter(registration_number__isnull=False)
        .exclude(registration_number='')
        .order_by('last_name', 'first_name')
    )
    matricules = [employee.registration_number for employee in employees]
    employee_by_matricule = {employee.registration_number: employee for employee in employees}

    captures_qs = FgpFingerprintCapture.objects.filter(
        registration_number__in=matricules,
        finger_position__in=MATCHING_FINGER_POSITIONS,
        capture_status='CAPTURED',
    ).exclude(template_uri__isnull=True).exclude(template_uri='')

    if since_dt:
        captures_qs = captures_qs.filter(updated_at__gte=since_dt)

    captures = list(captures_qs.order_by('registration_number', 'finger_position'))

    templates_by_employee: dict[int, list[dict]] = {}
    latest_updated = since_dt

    for capture in captures:
        fmt = (capture.template_format or '').upper()
        if fmt and not fmt.startswith('MORPHO'):
            continue

        employee = employee_by_matricule.get(capture.registration_number)
        if not employee:
            continue

        finger_name = FINGER_POSITION_TO_TABLET.get(capture.finger_position)
        if not finger_name:
            continue

        template_b64 = load_template_base64(capture.template_uri)
        if not template_b64:
            continue

        updated_at = getattr(capture, 'updated_at', None)
        if updated_at and (latest_updated is None or updated_at > latest_updated):
            latest_updated = updated_at

        templates_by_employee.setdefault(employee.pk, []).append(
            {
                'fingerName': finger_name,
                'fingerPosition': capture.finger_position,
                'template_base64': template_b64,
                'template_format': capture.template_format or '',
            }
        )

    employee_rows = []
    for employee in employees:
        fingers = templates_by_employee.get(employee.pk, [])
        if since_dt and not fingers:
            continue
        row = _employee_row(employee)
        row['fingers'] = fingers
        employee_rows.append(row)

    generated_at = timezone.localtime()
    if latest_updated is None:
        latest_updated = generated_at

    return {
        'status': 'success',
        'generatedAt': generated_at.isoformat(),
        'since': since_dt.isoformat() if since_dt else None,
        'version': latest_updated.isoformat() if hasattr(latest_updated, 'isoformat') else str(latest_updated),
        'matchingFingerPositions': list(MATCHING_FINGER_POSITIONS),
        'totalEmployees': len(employee_rows),
        'totalTemplates': sum(len(row.get('fingers') or []) for row in employee_rows),
        'employees': employee_rows,
    }
