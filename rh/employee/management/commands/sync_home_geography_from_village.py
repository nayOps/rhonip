from django.core.management.base import BaseCommand

from employee.models import Employee


class Command(BaseCommand):
    help = (
        "Recopie province/territoire/secteur/groupement depuis home_village "
        "quand ces champs sont vides sur la fiche employé."
    )

    def handle(self, *args, **options):
        updated = 0
        qs = Employee.objects.filter(home_village_id__isnull=False).select_related(
            'home_village__groupement__sector__territory__province',
        )
        for employee in qs.iterator(chunk_size=500):
            village = employee.home_village
            if not village or not village.groupement_id:
                continue
            groupement = village.groupement
            sector = groupement.sector
            territory = sector.territory
            province = territory.province
            changes = {}
            if employee.home_province_id != province.pk:
                changes['home_province_id'] = province.pk
            if employee.home_territory_id != territory.pk:
                changes['home_territory_id'] = territory.pk
            if employee.home_sector_id != sector.pk:
                changes['home_sector_id'] = sector.pk
            if employee.home_groupement_id != groupement.pk:
                changes['home_groupement_id'] = groupement.pk
            if changes:
                Employee.objects.filter(pk=employee.pk).update(**changes)
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Employés mis à jour : {updated}'))
