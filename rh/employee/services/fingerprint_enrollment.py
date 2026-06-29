import base64
import hashlib
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from django.db import connection, transaction

from employee.models import Employee
from employee.services.fingerprint_tablet import (
    FINGER_POSITION_TO_TABLET,
    TABLET_TO_REGISTER,
    normalize_tablet_finger_name,
)

MORPHO_TEMPLATE_FORMAT = 'MORPHO_PK_ISO_FMR'
MORPHO_DEVICE = 'morpho_tablet'

ALL_FINGER_POSITIONS = tuple(FINGER_POSITION_TO_TABLET.keys())


def _media_root():
    return Path(os.getenv('FGP_MEDIA_ROOT', '/app/media'))


def _ensure_fgp_biometric(registration_number):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO fgp_biometric (registration_number)
            VALUES (%s)
            ON CONFLICT (registration_number) DO NOTHING
            """,
            [registration_number],
        )


def _resolve_finger_position(finger_name):
    if finger_name in FINGER_POSITION_TO_TABLET:
        return finger_name
    tablet = normalize_tablet_finger_name(finger_name)
    register = TABLET_TO_REGISTER.get(tablet)
    if register:
        return register
    return str(finger_name or '').strip().upper().replace(' ', '_')


def get_enrollment_status(employee):
    if not employee.registration_number:
        return {'employeeId': employee.pk, 'fingers': [], 'enrolledCount': 0, 'totalFingers': 10}

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT finger_position, capture_status, template_uri, device, template_format
            FROM fgp_fingerprints
            WHERE registration_number = %s
            ORDER BY finger_position
            """,
            [employee.registration_number],
        )
        rows = cursor.fetchall()

    enrolled = {}
    for position, status, template_uri, device, template_format in rows:
        enrolled[position] = {
            'fingerPosition': position,
            'fingerName': FINGER_POSITION_TO_TABLET.get(position, position),
            'status': status,
            'hasTemplate': bool(template_uri),
            'device': device or '',
            'templateFormat': template_format or '',
            'morphoReady': bool(template_uri)
            and (
                (template_format or '').upper().startswith('MORPHO')
                or (device or '') == MORPHO_DEVICE
            ),
        }

    fingers = []
    enrolled_count = 0
    for position in ALL_FINGER_POSITIONS:
        item = enrolled.get(position) or {
            'fingerPosition': position,
            'fingerName': FINGER_POSITION_TO_TABLET.get(position, position),
            'status': 'PENDING',
            'hasTemplate': False,
            'device': '',
            'templateFormat': '',
            'morphoReady': False,
        }
        if item.get('morphoReady') and item.get('status') == 'CAPTURED':
            enrolled_count += 1
        fingers.append(item)

    return {
        'employeeId': employee.pk,
        'registrationNumber': employee.registration_number,
        'enrolledCount': enrolled_count,
        'totalFingers': len(ALL_FINGER_POSITIONS),
        'fingers': fingers,
    }


def save_fingerprint_template(employee, finger_name, template_bytes, template_format=None, quality_score=None):
    if not employee.registration_number:
        raise ValueError("Cet employé n'a pas de matricule (registration_number).")

    finger_position = _resolve_finger_position(finger_name)
    if finger_position not in FINGER_POSITION_TO_TABLET:
        raise ValueError(f'Position de doigt invalide: {finger_name}')

    if not template_bytes:
        raise ValueError('Template empreinte vide.')

    media_root = _media_root()
    rel_dir = Path('tablet_enroll') / employee.registration_number
    target_dir = media_root / rel_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f'{finger_position.lower()}.bin'
    target_path = target_dir / filename
    target_path.write_bytes(template_bytes)

    template_hash = hashlib.sha256(template_bytes).hexdigest()
    template_uri = f'file://{target_path.as_posix()}'
    captured_at = datetime.now(timezone.utc)
    fmt = template_format or MORPHO_TEMPLATE_FORMAT

    with transaction.atomic():
        _ensure_fgp_biometric(employee.registration_number)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO fgp_fingerprints (
                    id, registration_number, finger_position, capture_status,
                    template_uri, template_hash, template_format,
                    quality_score, device, captured_at, created_at, updated_at
                )
                VALUES (%s, %s, %s, 'CAPTURED', %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (registration_number, finger_position)
                DO UPDATE SET
                    capture_status = 'CAPTURED',
                    template_uri = EXCLUDED.template_uri,
                    template_hash = EXCLUDED.template_hash,
                    template_format = EXCLUDED.template_format,
                    quality_score = EXCLUDED.quality_score,
                    device = EXCLUDED.device,
                    captured_at = EXCLUDED.captured_at,
                    updated_at = NOW()
                """,
                [
                    str(uuid.uuid4()),
                    employee.registration_number,
                    finger_position,
                    template_uri,
                    template_hash,
                    fmt,
                    quality_score,
                    MORPHO_DEVICE,
                    captured_at,
                ],
            )

    return {
        'employeeId': employee.pk,
        'registrationNumber': employee.registration_number,
        'fingerPosition': finger_position,
        'fingerName': FINGER_POSITION_TO_TABLET[finger_position],
        'templateFormat': fmt,
        'templateSize': len(template_bytes),
        'device': MORPHO_DEVICE,
    }


def import_enrollment_payload(payload):
    employee_id = payload.get('employeeId') or payload.get('employee_id')
    if not employee_id:
        raise ValueError('employeeId requis.')

    employee = Employee.objects.filter(pk=employee_id).first()
    if not employee:
        raise ValueError('Employé introuvable.')

    finger_name = payload.get('fingerPosition') or payload.get('fingerName') or payload.get('finger_position')
    template_b64 = payload.get('template_base64') or payload.get('templateBase64')
    if not finger_name or not template_b64:
        raise ValueError('fingerPosition et template_base64 sont requis.')

    try:
        template_bytes = base64.b64decode(template_b64)
    except Exception as exc:
        raise ValueError('template_base64 invalide.') from exc

    quality = payload.get('quality_score') or payload.get('qualityScore')
    if quality is not None:
        try:
            quality = float(quality)
        except (TypeError, ValueError):
            quality = None

    saved = save_fingerprint_template(
        employee,
        finger_name,
        template_bytes,
        template_format=payload.get('template_format') or payload.get('templateFormat'),
        quality_score=quality,
    )
    saved['enrollment'] = get_enrollment_status(employee)
    return saved
