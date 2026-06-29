"""Import liste de paie ONIP (dossier agents/) vers Employee + PayrollLine."""
from __future__ import annotations

import json
import re
from pathlib import Path


def parse_nom_postnom(full_name: str) -> tuple[str, str | None, str | None]:
    """
    Décompose « NOM POSTNOM PRENOM » (convention courante RDC, majuscules).
    - 1 mot  → nom
    - 2 mots → nom, prénom
    - 3+     → nom, post-nom(s), prénom
    """
    parts = [p for p in re.split(r'\s+', (full_name or '').strip()) if p]
    if not parts:
        return '', None, None
    if len(parts) == 1:
        return parts[0], None, None
    if len(parts) == 2:
        return parts[0], None, parts[1]
    return parts[0], ' '.join(parts[1:-1]), parts[-1]


def period_code_from_label(periode: str) -> str:
    """Ex. « MAI 2026 » → « MAI_2026 »."""
    slug = re.sub(r'[^A-Za-z0-9]+', '_', (periode or '').strip().upper())
    return slug.strip('_') or 'PAIE'


def load_agents_paie_file(path: Path) -> dict:
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)


def default_agents_paie_path() -> Path:
    candidates = (
        Path('/app/agents/Liste_Paie_ONIP_Mai2026.json'),
        Path(__file__).resolve().parents[3] / 'agents' / 'Liste_Paie_ONIP_Mai2026.json',
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]
