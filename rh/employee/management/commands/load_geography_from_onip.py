from django.core.management.base import BaseCommand

from employee.utils.onip_geography_import import load_geography_from_onip


class Command(BaseCommand):
    help = (
        'Importe le référentiel géographique ONIP (province → groupement → village) '
        'depuis datas/Onip_Data_Carto/entites_admin.json (dérivé de onip_full.sql).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=None,
            help='Chemin vers entites_admin.json (défaut: datas/Onip_Data_Carto/entites_admin.json).',
        )
        parser.add_argument(
            '--no-replace',
            action='store_true',
            help='Conserve les données existantes et complète le référentiel.',
        )

    def handle(self, *args, **options):
        stats = load_geography_from_onip(
            options.get('file'),
            replace=not options['no_replace'],
        )
        self.stdout.write(self.style.SUCCESS(
            'Import ONIP terminé — '
            f"fichier: {stats['source_file']}, "
            f"lignes source: {stats['source_rows']}, "
            f"provinces: {stats['total_provinces']} (+{stats['provinces']}), "
            f"territoires: {stats['total_territories']} (+{stats['territories']}), "
            f"secteurs: {stats['total_sectors']} (+{stats['sectors']}), "
            f"groupements: {stats['total_groupements']} (+{stats['groupements']}), "
            f"villages: {stats['total_villages']} (+{stats['villages']}, "
            f"ignorés: {stats['skipped_villages']})"
        ))
