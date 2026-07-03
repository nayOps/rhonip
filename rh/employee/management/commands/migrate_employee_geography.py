from django.core.management.base import BaseCommand

from employee.models import Employee, Province, Territory, Sector, Groupement, Village
from employee.utils.geography import migrate_employee_geography_text_fields


class Command(BaseCommand):
    help = (
        "Relie les employés aux entités géographiques via metadata "
        "(provinceOrigine, territoire, secteur, village)."
    )

    def handle(self, *args, **options):
        updated = migrate_employee_geography_text_fields(
            Employee, Province, Territory, Sector, Groupement, Village,
        )
        self.stdout.write(self.style.SUCCESS(f'Employés mis à jour : {updated}'))
