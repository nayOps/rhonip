"""
Écriture des médias d'enrôlement (base64 → fichiers) et promotion vers FGP Core.
"""
import base64
import hashlib
import re
from pathlib import Path
from typing import Any, Optional

import requests
from django.conf import settings


DOCUMENT_TYPE_MAP = {
    'FICHE_IDENTIFICATION': 'carte_identite',
    'ACTE_NAISSANCE': 'acte_naissance',
    'JUGEMENT_SUPPLETIF': 'autre',
    'CARTE_ELECTEUR': 'carte_identite',
    'CERTIFICAT_NATIONALITE': 'attestation',
    'PASSEPORT': 'passeport',
    'CARTE_ETUDIANT': 'autre',
    'PERMIS_CONDUIRE': 'autre',
    'AUTRE': 'autre',
}


def _media_root() -> Path:
    root = getattr(settings, 'MEDIA_ROOT', None)
    if root is None:
        root = Path(settings.BASE_DIR) / 'media'
    return Path(root)


def strip_data_url(value: str) -> str:
    if not value:
        return ''
    if 'base64,' in value:
        return value.split('base64,', 1)[1]
    return value


def save_base64_file(
    session_id: str,
    category: str,
    name: str,
    data_b64: str,
    ext: str = 'jpg',
) -> tuple[str, str, int]:
    """Retourne (uri file://, sha256 hex, taille octets)."""
    raw = base64.b64decode(strip_data_url(data_b64))
    digest = hashlib.sha256(raw).hexdigest()
    folder = _media_root() / 'enrollments' / session_id / category
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r'[^\w.\-]', '_', name)
    path = folder / f'{safe_name}.{ext}'
    path.write_bytes(raw)
    uri = path.as_uri()
    return uri, digest, len(raw)


def persist_session_attachments(session, registration_number: str, fgp_core_url: str) -> dict[str, Any]:
    """
    Écrit les pièces jointes sur disque et tente POST /api/v1/core/documents/.
    """
    payload = session.payload or {}
    attachments = payload.get('attachments') or []
    results: list[dict[str, Any]] = []
    errors: list[str] = []

    for doc in attachments:
        doc_type = DOCUMENT_TYPE_MAP.get(doc.get('type'), 'autre')
        for page in doc.get('pages') or []:
            image_b64 = page.get('image_base64')
            if not image_b64:
                continue
            mime = (page.get('mime_type') or 'image/jpeg').lower()
            ext = 'png' if 'png' in mime else 'jpg'
            page_id = page.get('id') or 'page'
            try:
                uri, digest, size = save_base64_file(
                    session.session_id,
                    'documents',
                    f'{doc_type}_{page_id}',
                    image_b64,
                    ext=ext,
                )
                body = {
                    'registration_number': registration_number,
                    'document_type': doc_type,
                    'document_uri': uri,
                    'file_size': size,
                    'mime_type': mime,
                }
                headers = {'Content-Type': 'application/json'}
                internal_key = getattr(settings, 'GUICHET_INTERNAL_API_KEY', None)
                if internal_key:
                    headers['X-Guichet-Internal-Key'] = internal_key
                resp = requests.post(
                    f'{fgp_core_url}/api/v1/core/documents/',
                    json=body,
                    headers=headers,
                    timeout=30,
                )
                ok = resp.status_code in (200, 201)
                results.append(
                    {
                        'page_id': page_id,
                        'uri': uri,
                        'hash': digest,
                        'fgp_core': ok,
                        'status': resp.status_code,
                    }
                )
                if not ok:
                    errors.append(f'document {page_id}: HTTP {resp.status_code}')
            except Exception as exc:
                errors.append(f'document {page_id}: {exc}')

    return {'saved': len(results), 'results': results, 'errors': errors}


def persist_session_biometric_files(session) -> dict[str, Any]:
    """Sauvegarde face / empreintes / iris sur disque ; retourne URIs + hash."""
    payload = session.payload or {}
    biometrics = payload.get('biometrics') or {}
    out: dict[str, Any] = {}
    sid = session.session_id

    face = biometrics.get('face') or {}
    for key, field in [('photo', 'image_base64'), ('photo_raw', 'raw_image_base64')]:
        b64 = face.get(field if field != 'photo' else 'image_base64')
        if not b64:
            continue
        try:
            uri, digest, _size = save_base64_file(sid, 'face', key, b64)
            out[f'{key}_uri'] = uri
            out[f'{key}_hash'] = digest
        except Exception:
            pass

    fp = biometrics.get('fingerprints') or {}
    fingers = fp.get('fingers') or []
    fp_uris = []
    for finger in fingers:
        pos = finger.get('position', 'unknown')
        item = {
            'position': pos,
            'status': finger.get('status'),
            'quality': finger.get('quality'),
            'nfiq': finger.get('nfiq'),
            'timestamp': finger.get('timestamp'),
            'template_format': finger.get('format_id'),
        }
        img = finger.get('image_base64')
        if img:
            try:
                uri, digest, _size = save_base64_file(sid, 'fingerprints', str(pos).lower(), img)
                item['uri'] = uri
                item['hash'] = digest
            except Exception:
                pass

        tpl = finger.get('template_base64')
        if tpl:
            try:
                tpl_uri, tpl_hash, _tpl_size = save_base64_file(
                    sid,
                    'fingerprints_templates',
                    f"{str(pos).lower()}_template",
                    tpl,
                    ext='bin',
                )
                item['template_uri'] = tpl_uri
                item['template_hash'] = tpl_hash
            except Exception:
                pass

        fp_uris.append(item)
    if fp_uris:
        out['fingerprints'] = fp_uris
        out['fingerprints_device'] = fp.get('device', 'fap60')
        out['fingerprints_fake'] = fp.get('device') == 'fake-dev' or fp.get('source') == 'fake-dev'

    iris = biometrics.get('iris') or {}
    iris_uris = []
    for eye in iris.get('eyes') or []:
        if eye.get('status') != 'CAPTURED':
            continue
        pos = eye.get('position', 'unknown')
        img = eye.get('image_base64')
        if not img:
            continue
        try:
            uri, digest, _size = save_base64_file(sid, 'iris', str(pos).lower(), img)
            iris_uris.append({'position': pos, 'uri': uri, 'hash': digest})
        except Exception:
            pass
    if iris_uris:
        out['iris'] = iris_uris

    return out


def persist_session_biometrics(session, registration_number: str, fgp_core_url: str, persisted_media: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Promeut les URIs biométriques vers fgp_core/api/v1/core/biometric/ (création ou mise à jour).
    """
    persisted_media = persisted_media or {}
    payload = session.payload or {}
    biometrics = payload.get('biometrics') or {}

    face = biometrics.get('face') or {}
    fp = biometrics.get('fingerprints') or {}
    iris = biometrics.get('iris') or {}
    fp_list = persisted_media.get('fingerprints') or []
    iris_list = persisted_media.get('iris') or []

    body: dict[str, Any] = {
        'registration_number': registration_number,
        'photo_uri': persisted_media.get('photo_uri'),
        'photo_hash': persisted_media.get('photo_hash'),
        'photo_quality': face.get('quality'),
        'fingerprints_uri': fp_list[0]['uri'] if fp_list else None,
        'fingerprints_hash': fp_list[0]['hash'] if fp_list else None,
        'fingerprints_quality': fp.get('quality'),
        'iris_uri': iris_list[0]['uri'] if iris_list else None,
        'iris_hash': iris_list[0]['hash'] if iris_list else None,
        'iris_quality': iris.get('quality'),
    }
    body = {k: v for k, v in body.items() if v not in (None, '')}
    if len(body.keys()) <= 1:
        return {'saved': False, 'status': 'no_data'}

    headers = {'Content-Type': 'application/json'}
    internal_key = getattr(settings, 'GUICHET_INTERNAL_API_KEY', None)
    if internal_key:
        headers['X-Guichet-Internal-Key'] = internal_key

    create_resp = requests.post(
        f'{fgp_core_url}/api/v1/core/biometric/',
        json=body,
        headers=headers,
        timeout=30,
    )
    if create_resp.status_code in (200, 201):
        return {'saved': True, 'status': create_resp.status_code}

    if create_resp.status_code in (400, 409):
        update_resp = requests.patch(
            f'{fgp_core_url}/api/v1/core/biometric/{registration_number}/',
            json=body,
            headers=headers,
            timeout=30,
        )
        return {
            'saved': update_resp.status_code in (200, 202),
            'status': update_resp.status_code,
            'error': update_resp.text if update_resp.status_code not in (200, 202) else None,
        }

    return {'saved': False, 'status': create_resp.status_code, 'error': create_resp.text}


def persist_session_fingerprints(session, registration_number: str, fgp_core_url: str, persisted_media: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Persiste les empreintes détaillées (par doigt) dans fgp_core/api/v1/core/fingerprints/.
    """
    persisted_media = persisted_media or {}
    fingers = persisted_media.get('fingerprints') or []
    if not fingers:
        return {'saved': 0, 'errors': []}

    headers = {'Content-Type': 'application/json'}
    internal_key = getattr(settings, 'GUICHET_INTERNAL_API_KEY', None)
    if internal_key:
        headers['X-Guichet-Internal-Key'] = internal_key

    saved = 0
    errors: list[str] = []
    for finger in fingers:
        position = str(finger.get('position') or 'UNKNOWN').upper()
        body = {
            'registration_number': registration_number,
            'finger_position': position,
            'capture_status': str(finger.get('status') or 'PENDING').upper(),
            'image_uri': finger.get('uri'),
            'image_hash': finger.get('hash'),
            'template_uri': finger.get('template_uri'),
            'template_hash': finger.get('template_hash'),
            'template_format': str(finger.get('template_format') or ''),
            'quality_score': finger.get('quality'),
            'nfiq_score': finger.get('nfiq'),
            'device': persisted_media.get('fingerprints_device'),
            'captured_at': finger.get('timestamp'),
        }
        body = {k: v for k, v in body.items() if v not in (None, '')}
        try:
            resp = requests.post(
                f'{fgp_core_url}/api/v1/core/fingerprints/',
                json=body,
                headers=headers,
                timeout=30,
            )
            if resp.status_code in (200, 201):
                saved += 1
            else:
                errors.append(f'{position}: HTTP {resp.status_code}')
        except Exception as exc:
            errors.append(f'{position}: {exc}')

    return {'saved': saved, 'errors': errors}


def _path_from_file_uri(uri: str) -> Optional[Path]:
    if not uri or not str(uri).startswith('file:'):
        return None
    from urllib.parse import unquote, urlparse

    parsed = urlparse(uri)
    path = unquote(parsed.path)
    if not path:
        return None
    return Path(path)


def load_session_face_photo_base64(session) -> Optional[str]:
    """Photo visage : payload base64 ou fichier persisted_media / disque."""
    payload = session.payload or {}
    face = (payload.get('biometrics') or {}).get('face') or {}
    for key in ('icao_image_base64', 'image_base64'):
        val = face.get(key)
        if val:
            return strip_data_url(str(val))

    persisted = payload.get('persisted_media') or {}
    uri = persisted.get('photo_uri')
    if uri:
        path = _path_from_file_uri(str(uri))
        if path and path.is_file():
            return base64.b64encode(path.read_bytes()).decode('ascii')

    sid = session.session_id
    if sid:
        for candidate in (
            _media_root() / 'enrollments' / sid / 'face' / 'photo.jpg',
            _media_root() / 'enrollments' / sid / 'face' / 'photo.png',
        ):
            if candidate.is_file():
                return base64.b64encode(candidate.read_bytes()).decode('ascii')
    return None


def session_has_face_photo(session) -> bool:
    return load_session_face_photo_base64(session) is not None
