import base64
import os
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

from django.db import models

from employee.models import Employee

FINGER_POSITION_TO_TABLET = {
    'RIGHT_INDEX': 'Index_Droit',
    'RIGHT_THUMB': 'Pouce_Droit',
    'LEFT_INDEX': 'Index_Gauche',
    'LEFT_THUMB': 'Pouce_Gauche',
    'RIGHT_MIDDLE': 'Majeur_Droit',
    'LEFT_MIDDLE': 'Majeur_Gauche',
    'RIGHT_RING': 'Annulaire_Droit',
    'LEFT_RING': 'Annulaire_Gauche',
    'RIGHT_LITTLE': 'Auriculaire_Droit',
    'LEFT_LITTLE': 'Auriculaire_Gauche',
}

TABLET_FINGER_ALIASES = {
    'index_droit': 'Index_Droit',
    'pouce_droit': 'Pouce_Droit',
    'index_gauche': 'Index_Gauche',
    'pouce_gauche': 'Pouce_Gauche',
    'right_index': 'Index_Droit',
    'right_thumb': 'Pouce_Droit',
    'left_index': 'Index_Gauche',
    'left_thumb': 'Pouce_Gauche',
}

TABLET_TO_REGISTER = {tablet: register for register, tablet in FINGER_POSITION_TO_TABLET.items()}

# Doigts exposés aux tablettes de pointage (matching 1:N).
MATCHING_FINGER_POSITIONS = (
    'RIGHT_INDEX',
    'RIGHT_THUMB',
    'LEFT_INDEX',
)


class FgpFingerprintCapture(models.Model):
    """Lecture seule — table register fgp_core (même PostgreSQL)."""

    id = models.UUIDField(primary_key=True)
    registration_number = models.CharField(max_length=50)
    finger_position = models.CharField(max_length=20)
    capture_status = models.CharField(max_length=20)
    template_uri = models.URLField(blank=True, null=True)
    template_format = models.CharField(max_length=30, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fgp_fingerprints'


def normalize_tablet_finger_name(finger_name):
    if not finger_name:
        return None
    if finger_name in FINGER_POSITION_TO_TABLET.values():
        return finger_name
    key = str(finger_name).strip().replace('-', '_')
    if key in TABLET_FINGER_ALIASES:
        return TABLET_FINGER_ALIASES[key]
    return key.replace('_', ' ').title().replace(' ', '_')


def _media_roots():
    roots = []
    configured = os.getenv('FGP_MEDIA_ROOT', '/app/media')
    if configured:
        roots.append(Path(configured))
    roots.append(Path('/app/media'))
    return roots


def _resolve_template_path(template_uri):
    if not template_uri:
        return None

    parsed = urlparse(template_uri)
    if parsed.scheme == 'file':
        candidates = [Path(unquote(parsed.path))]
    elif parsed.scheme in ('http', 'https'):
        path_part = parsed.path
        if '/media/' in path_part:
            relative = path_part.split('/media/', 1)[1]
            candidates = [root / relative for root in _media_roots()]
        else:
            candidates = []
    else:
        candidates = []

    if parsed.scheme == 'file':
        for root in _media_roots():
            if '/media/' in parsed.path:
                relative = parsed.path.split('/media/', 1)[1]
                candidates.append(root / PurePosixPath(unquote(relative)))
            candidates.append(root / Path(unquote(parsed.path)).name)

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def load_template_base64(template_uri):
    path = _resolve_template_path(template_uri)
    if not path:
        return None
    return base64.b64encode(path.read_bytes()).decode('ascii')


def employees_with_fingerprints():
    return Employee.objects.filter(
        registration_number__isnull=False,
    ).exclude(registration_number='')


def build_matching_index():
    rows = []
    employee_by_matricule = {
        employee.registration_number: employee
        for employee in employees_with_fingerprints()
    }

    captures = FgpFingerprintCapture.objects.filter(
        registration_number__in=employee_by_matricule.keys(),
        finger_position__in=MATCHING_FINGER_POSITIONS,
        capture_status='CAPTURED',
    ).exclude(template_uri__isnull=True).exclude(template_uri='')

    for capture in captures:
        employee = employee_by_matricule.get(capture.registration_number)
        if not employee:
            continue
        finger_name = FINGER_POSITION_TO_TABLET.get(capture.finger_position)
        if not finger_name:
            continue
        fmt = (capture.template_format or '').upper()
        if fmt and not fmt.startswith('MORPHO'):
            continue
        rows.append(
            {
                'employeeId': employee.pk,
                'fingerName': finger_name,
                'registrationNumber': capture.registration_number,
                'fingerPosition': capture.finger_position,
            }
        )
    return rows


def get_template_for_employee_finger(employee_id, finger_name):
    employee = Employee.objects.filter(pk=employee_id).first()
    if not employee or not employee.registration_number:
        return None

    tablet_finger = normalize_tablet_finger_name(finger_name)
    register_position = TABLET_TO_REGISTER.get(tablet_finger)
    if not register_position:
        return None

    capture = FgpFingerprintCapture.objects.filter(
        registration_number=employee.registration_number,
        finger_position=register_position,
        capture_status='CAPTURED',
    ).first()
    if not capture or not capture.template_uri:
        return None

    template_base64 = load_template_base64(capture.template_uri)
    if not template_base64:
        return None

    return {
        'employeeId': employee.pk,
        'fingerName': tablet_finger,
        'template_base64': template_base64,
        'template_format': capture.template_format or '',
    }


def employee_has_fingerprints(employee):
    if not employee.registration_number:
        return False
    return FgpFingerprintCapture.objects.filter(
        registration_number=employee.registration_number,
        capture_status='CAPTURED',
    ).exclude(template_uri__isnull=True).exclude(template_uri='').exists()
