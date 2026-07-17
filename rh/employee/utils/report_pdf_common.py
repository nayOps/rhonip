"""Utilitaires communs pour les PDF de rapports RH ONIP."""

from __future__ import annotations

import base64
import mimetypes
from datetime import date
from pathlib import Path

from django.conf import settings

from core.models import Organization


def file_to_data_uri(path: Path) -> str | None:
    if not path.is_file():
        return None
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        suffix = path.suffix.lower()
        if suffix in ('.jpg', '.jpeg'):
            mime = 'image/jpeg'
        elif suffix == '.png':
            mime = 'image/png'
        elif suffix == '.gif':
            mime = 'image/gif'
        else:
            return None
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{encoded}'


def logo_data_uri() -> str | None:
    organization = Organization.objects.first()
    if organization and organization.logo:
        try:
            data_uri = file_to_data_uri(Path(organization.logo.path))
            if data_uri:
                return data_uri
        except (ValueError, OSError):
            pass

    for name in ('logo-onip.png', 'logo.png', 'logo.jpg', 'logo.jpeg'):
        static_logo = Path(settings.BASE_DIR) / 'static' / 'assets' / 'images' / 'logo' / name
        data_uri = file_to_data_uri(static_logo)
        if data_uri:
            return data_uri
    return None


def photo_data_uri(photo_field) -> str | None:
    if not photo_field:
        return None
    try:
        return file_to_data_uri(Path(photo_field.path))
    except (ValueError, OSError):
        return None


def build_pdf_filename(
    report_code: str,
    *,
    day: date | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    year: int | None = None,
    month: int | None = None,
) -> str:
    """Convention : rapport-rh-onip-{code}-{dates}.pdf"""
    parts = ['rapport-rh-onip', report_code]
    if year and month:
        parts.append(f'{int(year):04d}-{int(month):02d}')
    elif day:
        parts.append(day.strftime('%Y-%m-%d'))
    elif date_from and date_to:
        parts.append(date_from.strftime('%Y-%m-%d'))
        parts.append(date_to.strftime('%Y-%m-%d'))
    elif date_from:
        parts.append(date_from.strftime('%Y-%m-%d'))
    return '-'.join(parts) + '.pdf'


def default_reports_output_dir() -> Path:
    """Dossier local des PDF générés : deploy/vps/reports à la racine du dépôt."""
    repo_root = Path(settings.BASE_DIR).parent
    output_dir = repo_root / 'deploy' / 'vps' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def list_generated_report_files(limit: int = 40) -> list[dict]:
    """Liste les PDF générés dans deploy/vps/reports (plus récents d'abord)."""
    output_dir = default_reports_output_dir()
    files = sorted(
        output_dir.glob('rapport-rh-onip-*.pdf'),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    items = []
    for path in files[:limit]:
        stat = path.stat()
        items.append(
            {
                'filename': path.name,
                'size_bytes': stat.st_size,
                'size_kb': max(1, round(stat.st_size / 1024)),
                'modified_at': date.fromtimestamp(stat.st_mtime),
                'modified_label': date.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y'),
            }
        )
    return items


def save_report_pdf(pdf_bytes: bytes, filename: str):
    """Enregistre un PDF dans le dossier des rapports générés."""
    output_dir = default_reports_output_dir()
    output_path = output_dir / filename
    output_path.write_bytes(pdf_bytes)
    return output_path
