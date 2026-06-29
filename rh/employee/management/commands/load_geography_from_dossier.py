from django.core.management.base import BaseCommand

from employee.utils.geography import load_geography_from_dossier


class Command(BaseCommand):
    help = "Charge les données géographiques RDC (province → village) depuis employees.json."

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            dest='file',
            default=None,
            help='Chemin vers employees.json (défaut: BASE_DIR/employees.json)',
        )

    def handle(self, *args, **options):
        stats = load_geography_from_dossier(options.get('file'))
        self.stdout.write(self.style.SUCCESS(
            f"Géographie chargée — dossiers lus: {stats['records']}, "
            f"provinces: {stats.get('total_provinces', 0)}, "
            f"territoires: {stats.get('total_territories', 0)}, "
            f"secteurs: {stats.get('total_sectors', 0)}, "
            f"villages: {stats.get('total_villages', 0)}"
        ))
