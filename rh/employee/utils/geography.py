"""Chargement et résolution des entités géographiques (province → village)."""
from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings


def _clean(value):
    if value is None:
        return ''
    return str(value).strip()


def upsert_geography_from_record(record, Province, Territory, Sector, Groupement, Village):
    """Crée la hiérarchie géographique à partir d'un enregistrement dossier (employees.json)."""
    province_name = _clean(record.get('provinceOrigine'))
    if not province_name:
        return None, None, None, None, None

    province, _ = Province.objects.get_or_create(name=province_name)
    territory = sector = groupement = village = None

    territory_name = _clean(record.get('territoire'))
    if territory_name:
        territory, _ = Territory.objects.get_or_create(province=province, name=territory_name)

        sector_name = _clean(record.get('secteur'))
        if sector_name:
            sector, _ = Sector.objects.get_or_create(territory=territory, name=sector_name)

            groupement_name = _clean(record.get('groupement') or record.get('groupementQuartier'))
            if groupement_name:
                groupement, _ = Groupement.objects.get_or_create(
                    sector=sector,
                    name=groupement_name,
                )

        village_name = _clean(record.get('village'))
        if village_name and territory:
            if groupement:
                village, _ = Village.objects.get_or_create(
                    groupement=groupement,
                    name=village_name,
                )
            elif sector:
                groupement, _ = Groupement.objects.get_or_create(
                    sector=sector,
                    name='Non renseigné',
                    defaults={'type_name': ''},
                )
                village, _ = Village.objects.get_or_create(
                    groupement=groupement,
                    name=village_name,
                )

    return province, territory, sector, groupement, village


def load_geography_from_dossier(path=None):
    """Importe provinces / territoires / secteurs / groupements / villages depuis employees.json."""
    from employee.models import Groupement, Province, Territory, Sector, Village

    if path is None:
        path = Path(settings.BASE_DIR) / 'employees.json'
    path = Path(path)
    if not path.exists():
        return {'provinces': 0, 'territories': 0, 'sectors': 0, 'groupements': 0, 'villages': 0, 'records': 0}

    with path.open(encoding='utf-8') as handle:
        payload = json.load(handle)

    records = payload.get('F_Form1') or []
    stats = {
        'provinces': 0,
        'territories': 0,
        'sectors': 0,
        'groupements': 0,
        'villages': 0,
        'records': 0,
    }

    before = (
        Province.objects.count(),
        Territory.objects.count(),
        Sector.objects.count(),
        Groupement.objects.count(),
        Village.objects.count(),
    )

    for record in records:
        if 'nomEnfant' in record:
            continue
        upsert_geography_from_record(record, Province, Territory, Sector, Groupement, Village)
        stats['records'] += 1

    after = (
        Province.objects.count(),
        Territory.objects.count(),
        Sector.objects.count(),
        Groupement.objects.count(),
        Village.objects.count(),
    )
    stats['provinces'] = after[0] - before[0]
    stats['territories'] = after[1] - before[1]
    stats['sectors'] = after[2] - before[2]
    stats['groupements'] = after[3] - before[3]
    stats['villages'] = after[4] - before[4]
    stats['total_provinces'] = after[0]
    stats['total_territories'] = after[1]
    stats['total_sectors'] = after[2]
    stats['total_groupements'] = after[3]
    stats['total_villages'] = after[4]
    return stats


def migrate_employee_geography_text_fields(Employee, Province, Territory, Sector, Groupement, Village):
    """Relie les employés existants aux FK géographiques via metadata ou anciennes valeurs texte."""
    updated = 0
    for employee in Employee.objects.all().iterator():
        meta = employee.metadata or {}
        province_name = _clean(
            getattr(employee, 'home_province_text', None)
            or meta.get('provinceOrigine')
        )
        territory_name = _clean(
            getattr(employee, 'home_territory_text', None)
            or meta.get('territoire')
        )
        sector_name = _clean(
            getattr(employee, 'home_sector_text', None)
            or meta.get('secteur')
        )
        groupement_name = _clean(meta.get('groupement') or meta.get('groupementQuartier'))
        village_name = _clean(
            getattr(employee, 'home_village_text', None)
            or meta.get('village')
        )

        if not any([province_name, territory_name, sector_name, groupement_name, village_name]):
            continue

        record = {
            'provinceOrigine': province_name,
            'territoire': territory_name,
            'secteur': sector_name,
            'groupement': groupement_name,
            'village': village_name,
        }
        province, territory, sector, groupement, village = upsert_geography_from_record(
            record, Province, Territory, Sector, Groupement, Village
        )

        changed = False
        if province and employee.home_province_id != province.pk:
            employee.home_province_id = province.pk
            changed = True
        if territory and employee.home_territory_id != territory.pk:
            employee.home_territory_id = territory.pk
            changed = True
        if sector and employee.home_sector_id != sector.pk:
            employee.home_sector_id = sector.pk
            changed = True
        if groupement and employee.home_groupement_id != groupement.pk:
            employee.home_groupement_id = groupement.pk
            changed = True
        if village and employee.home_village_id != village.pk:
            employee.home_village_id = village.pk
            changed = True

        if changed:
            employee.save(update_fields=[
                'home_province_id',
                'home_territory_id',
                'home_sector_id',
                'home_groupement_id',
                'home_village_id',
            ])
            updated += 1
    return updated


def resolve_geography_fk(payload, Province, Territory, Sector, Groupement, Village):
    """Convertit noms ou ids géographiques en PK pour l'API guichet."""
    data = payload.copy()

    province_val = data.get('home_province')
    territory_val = data.get('home_territory')
    sector_val = data.get('home_sector')
    groupement_val = data.get('home_groupement')
    village_val = data.get('home_village')

    province = territory = sector = groupement = village = None

    if province_val not in (None, ''):
        if isinstance(province_val, int) or (isinstance(province_val, str) and province_val.isdigit()):
            data['home_province'] = int(province_val)
            province = Province.objects.filter(pk=data['home_province']).first()
        else:
            province, _ = Province.objects.get_or_create(name=_clean(province_val))
            data['home_province'] = province.pk

    if territory_val not in (None, '') and province:
        if isinstance(territory_val, int) or (isinstance(territory_val, str) and territory_val.isdigit()):
            data['home_territory'] = int(territory_val)
            territory = Territory.objects.filter(pk=data['home_territory']).first()
        else:
            territory, _ = Territory.objects.get_or_create(province=province, name=_clean(territory_val))
            data['home_territory'] = territory.pk

    if sector_val not in (None, '') and territory:
        if isinstance(sector_val, int) or (isinstance(sector_val, str) and sector_val.isdigit()):
            data['home_sector'] = int(sector_val)
            sector = Sector.objects.filter(pk=data['home_sector']).first()
        else:
            sector, _ = Sector.objects.get_or_create(territory=territory, name=_clean(sector_val))
            data['home_sector'] = sector.pk

    if groupement_val not in (None, '') and sector:
        if isinstance(groupement_val, int) or (isinstance(groupement_val, str) and groupement_val.isdigit()):
            data['home_groupement'] = int(groupement_val)
            groupement = Groupement.objects.filter(pk=data['home_groupement']).first()
        else:
            groupement, _ = Groupement.objects.get_or_create(sector=sector, name=_clean(groupement_val))
            data['home_groupement'] = groupement.pk

    if village_val not in (None, ''):
        if isinstance(village_val, int) or (isinstance(village_val, str) and village_val.isdigit()):
            data['home_village'] = int(village_val)
        elif groupement:
            village, _ = Village.objects.get_or_create(
                groupement=groupement,
                name=_clean(village_val),
            )
            data['home_village'] = village.pk
        elif sector:
            groupement, _ = Groupement.objects.get_or_create(
                sector=sector,
                name='Non renseigné',
                defaults={'type_name': ''},
            )
            village, _ = Village.objects.get_or_create(
                groupement=groupement,
                name=_clean(village_val),
            )
            data['home_village'] = village.pk
            data['home_groupement'] = groupement.pk

    return data
