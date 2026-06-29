"""Génération des adresses e-mail professionnelles ONIP."""
from __future__ import annotations

import re
import unicodedata

PROFESSIONAL_EMAIL_DOMAIN = 'onip.gouv.cd'


def _slugify_name_part(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value)
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]', '', ascii_text.lower())


def build_professional_email(first_name: str, last_name: str) -> str | None:
    prenom = _slugify_name_part(first_name or '')
    nom = _slugify_name_part(last_name or '')
    if not prenom or not nom:
        return None
    return f'{prenom}.{nom}@{PROFESSIONAL_EMAIL_DOMAIN}'


def is_alema_olamba(employee) -> bool:
    """Exclut l'agent Alema Olamba (post-nom + nom)."""
    last = (employee.last_name or '').strip().upper()
    if last != 'OLAMBA':
        return False
    middle = (employee.middle_name or '').strip().upper()
    first = (employee.first_name or '').strip().upper()
    return middle == 'ALEMA' or first == 'ALEMA'
