"""Import du référentiel cartographique ONIP (province → village)."""
from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.db import transaction


def _clean(value) -> str:
    if value is None:
        return ''
    return str(value).strip()


def resolve_onip_carto_path(path=None) -> Path:
    if path:
        candidate = Path(path)
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f'Fichier introuvable: {candidate}')

    candidates = [
        Path(settings.BASE_DIR).parent.parent / 'datas' / 'Onip_Data_Carto' / 'entites_admin.json',
        Path('/app/datas/Onip_Data_Carto/entites_admin.json'),
        Path(settings.BASE_DIR) / 'datas' / 'Onip_Data_Carto' / 'entites_admin.json',
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        'Référentiel ONIP introuvable. Attendu: datas/Onip_Data_Carto/entites_admin.json'
    )


def _iter_rows(path: Path):
    with path.open(encoding='utf-8') as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    raise ValueError('Format entites_admin.json invalide (liste attendue).')


@transaction.atomic
def load_geography_from_onip(path=None, *, replace: bool = True) -> dict:
    from employee.models import Groupement, Province, Sector, Territory, Village

    data_path = resolve_onip_carto_path(path)
    rows = _iter_rows(data_path)

    if replace:
        Village.objects.all().delete()
        Groupement.objects.all().delete()
        Sector.objects.all().delete()
        Territory.objects.all().delete()
        Province.objects.all().delete()

    provinces: dict[int, Province] = {}
    territories: dict[tuple[int, int], Territory] = {}
    sectors: dict[tuple[int, int], Sector] = {}
    groupements: dict[tuple[int, int], Groupement] = {}
    villages_batch: list[Village] = []
    village_keys: set[tuple[int, str]] = set()

    stats = {
        'source_rows': len(rows),
        'provinces': 0,
        'territories': 0,
        'sectors': 0,
        'groupements': 0,
        'villages': 0,
        'skipped_villages': 0,
    }

    def flush_villages():
        nonlocal villages_batch
        if not villages_batch:
            return
        Village.objects.bulk_create(villages_batch, batch_size=2000)
        stats['villages'] += len(villages_batch)
        villages_batch = []

    for row in rows:
        prov_sid = row.get('province_source_id')
        prov_name = _clean(row.get('province_name'))
        if prov_sid is None or not prov_name:
            continue

        if prov_sid not in provinces:
            province, created = Province.objects.get_or_create(
                source_id=prov_sid,
                defaults={'name': prov_name},
            )
            if not created and province.name != prov_name:
                province.name = prov_name
                province.save(update_fields=['name'])
            provinces[prov_sid] = province
            if created:
                stats['provinces'] += 1

        province = provinces[prov_sid]
        terr_sid = row.get('territoire_source_id')
        terr_name = _clean(row.get('territoire_name'))
        terr_key = (prov_sid, terr_sid)
        if terr_sid is None or not terr_name:
            continue

        if terr_key not in territories:
            territory, created = Territory.objects.get_or_create(
                province=province,
                source_id=terr_sid,
                defaults={
                    'name': terr_name,
                    'type_name': _clean(row.get('territoire_type')),
                },
            )
            territories[terr_key] = territory
            if created:
                stats['territories'] += 1

        territory = territories[terr_key]
        sect_sid = row.get('secteur_source_id')
        sect_name = _clean(row.get('secteur_name'))
        sect_key = (terr_sid, sect_sid)
        if sect_sid is None or not sect_name:
            continue

        if sect_key not in sectors:
            sector, created = Sector.objects.get_or_create(
                territory=territory,
                source_id=sect_sid,
                defaults={
                    'name': sect_name,
                    'type_name': _clean(row.get('secteur_type')),
                },
            )
            sectors[sect_key] = sector
            if created:
                stats['sectors'] += 1

        sector = sectors[sect_key]
        grp_sid = row.get('groupement_source_id')
        grp_name = _clean(row.get('groupement_name'))
        grp_key = (sect_sid, grp_sid)
        if grp_sid is None or not grp_name:
            continue

        if grp_key not in groupements:
            groupement, created = Groupement.objects.get_or_create(
                sector=sector,
                source_id=grp_sid,
                defaults={
                    'name': grp_name,
                    'type_name': _clean(row.get('groupement_type')),
                },
            )
            groupements[grp_key] = groupement
            if created:
                stats['groupements'] += 1

        groupement = groupements[grp_key]
        vill_sid = row.get('village_source_id')
        vill_name = _clean(row.get('village_name'))
        if vill_sid is None or not vill_name:
            continue

        dedupe_key = (groupement.pk, vill_name.casefold())
        if dedupe_key in village_keys:
            stats['skipped_villages'] += 1
            continue
        village_keys.add(dedupe_key)

        villages_batch.append(
            Village(
                source_id=vill_sid,
                groupement=groupement,
                name=vill_name,
                locality_name=_clean(row.get('locality_name')),
                latitude=row.get('latitude'),
                longitude=row.get('longitude'),
            )
        )
        if len(villages_batch) >= 2000:
            flush_villages()

    flush_villages()

    stats['total_provinces'] = Province.objects.count()
    stats['total_territories'] = Territory.objects.count()
    stats['total_sectors'] = Sector.objects.count()
    stats['total_groupements'] = Groupement.objects.count()
    stats['total_villages'] = Village.objects.count()
    stats['source_file'] = str(data_path)
    return stats
