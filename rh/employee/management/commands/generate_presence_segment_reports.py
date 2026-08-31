from datetime import date

from django.core.management.base import BaseCommand, CommandError

from employee.utils.presence_statistics import generate_presence_segment_reports


class Command(BaseCommand):
    help = 'Génère les PDF statistiques de présence pour tous les segments (hub rapports).'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=0, help='Année (défaut: année courante)')
        parser.add_argument('--month', type=int, default=0, help='Mois 1-12 (défaut: mois courant)')

    def handle(self, *args, **options):
        today = date.today()
        year = int(options['year']) or today.year
        month = int(options['month']) or today.month
        if month < 1 or month > 12:
            raise CommandError('Mois invalide (1-12).')

        results = generate_presence_segment_reports(year=year, month=month, today=today)
        self.stdout.write(f'Période: {month:02d}/{year} — {len(results)} PDF')
        for item in results:
            self.stdout.write(
                f"  {item['filename']} ({item['row_count']} agents) — {item['label']}"
            )
        self.stdout.write(self.style.SUCCESS('OK'))
