#!/usr/bin/env python3
"""
Restaure les fichiers tablet_enroll depuis:
1) fichiers existants ailleurs sous /app/media (hash SHA256)
2) sessions enrollments (fingerprints_templates/*.bin)
"""
import base64
import hashlib
import os
import re
import shutil
from collections import defaultdict
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payday.settings')
import django
django.setup()

from django.db import connection

MEDIA = Path(os.getenv('FGP_MEDIA_ROOT', '/app/media'))
TABLET_ROOT = MEDIA / 'tablet_enroll'

FINGER_FILE = {
    'RIGHT_INDEX': 'right_index.bin',
    'RIGHT_THUMB': 'right_thumb.bin',
    'LEFT_INDEX': 'left_index.bin',
    'LEFT_THUMB': 'left_thumb.bin',
    'RIGHT_MIDDLE': 'right_middle.bin',
    'LEFT_MIDDLE': 'left_middle.bin',
    'RIGHT_RING': 'right_ring.bin',
    'LEFT_RING': 'left_ring.bin',
    'RIGHT_LITTLE': 'right_little.bin',
    'LEFT_LITTLE': 'left_little.bin',
}

POSITION_ALIASES = {
    'right_index': 'RIGHT_INDEX',
    'right_thumb': 'RIGHT_THUMB',
    'left_index': 'LEFT_INDEX',
    'left_thumb': 'LEFT_THUMB',
    'right_middle': 'RIGHT_MIDDLE',
    'left_middle': 'LEFT_MIDDLE',
    'right_ring': 'RIGHT_RING',
    'left_ring': 'LEFT_RING',
    'right_little': 'RIGHT_LITTLE',
    'left_little': 'LEFT_LITTLE',
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def build_hash_index(media: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    if not media.is_dir():
        return index
    for path in media.rglob('*.bin'):
        try:
            if path.is_file() and path.stat().st_size > 0:
                index[sha256_file(path)].append(path)
        except OSError:
            continue
    return index


def guess_position_from_name(name: str) -> str | None:
    key = name.lower().replace('-', '_')
    key = re.sub(r'(_template|\.bin)$', '', key)
    return POSITION_ALIASES.get(key)


def scan_enrollment_templates() -> list[tuple[str, Path]]:
    """Retourne (position, path) — matricule résolu via hash DB plus tard."""
    found = []
    enroll = MEDIA / 'enrollments'
    if not enroll.is_dir():
        return found
    for path in enroll.rglob('*.bin'):
        pos = guess_position_from_name(path.stem)
        if pos:
            found.append((pos, path))
    templates = MEDIA / 'enrollments'
    for path in templates.rglob('*template*.bin'):
        pos = guess_position_from_name(path.stem)
        if pos:
            found.append((pos, path))
    return found


def load_db_rows():
    with connection.cursor() as c:
        c.execute(
            """
            SELECT registration_number, finger_position, template_uri, template_hash
            FROM fgp_fingerprints
            WHERE capture_status = 'CAPTURED'
            ORDER BY registration_number, finger_position
            """
        )
        return c.fetchall()


def target_path(matricule: str, position: str) -> Path:
    fname = FINGER_FILE.get(position, f'{position.lower()}.bin')
    return TABLET_ROOT / matricule / fname


def main():
    TABLET_ROOT.mkdir(parents=True, exist_ok=True)
    hash_index = build_hash_index(MEDIA)
    print('hash_index_files', sum(len(v) for v in hash_index.values()))

    restored_hash = 0
    restored_existing = 0
    already_ok = 0
    still_missing = 0
    missing_samples = []

    rows = load_db_rows()
    for matricule, position, template_uri, template_hash in rows:
        dest = target_path(matricule, position)
        if dest.is_file() and dest.stat().st_size > 0:
            already_ok += 1
            continue

        source = None
        if template_hash and template_hash in hash_index:
            for candidate in hash_index[template_hash]:
                if candidate.resolve() == dest.resolve():
                    continue
                source = candidate
                break

        if source is None and template_uri:
            uri_path = template_uri.replace('file://', '')
            p = Path(uri_path)
            if p.is_file() and p.stat().st_size > 0:
                source = p

        if source is None:
            still_missing += 1
            if len(missing_samples) < 10:
                missing_samples.append((matricule, position, template_hash))
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != dest.resolve():
            shutil.copy2(source, dest)
        if template_hash:
            restored_hash += 1
        else:
            restored_existing += 1

    print('already_ok', already_ok)
    print('restored_hash', restored_hash)
    print('restored_existing', restored_existing)
    print('still_missing', still_missing)
    print('missing_samples', missing_samples)

    # Stats bundle
    from employee.utils.fingerprint_bundle import build_fingerprint_bundle
    bundle = build_fingerprint_bundle()
    with_f = sum(1 for e in bundle['employees'] if e.get('fingers'))
    print('bundle_with_fingers', with_f)
    print('bundle_totalTemplates', bundle.get('totalTemplates'))


if __name__ == '__main__':
    main()
