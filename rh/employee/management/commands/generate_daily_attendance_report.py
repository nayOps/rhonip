from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from employee.utils.daily_attendance_report import (
    build_daily_attendance_report,
    render_daily_attendance_pdf,
)
from employee.utils.report_pdf_common import default_reports_output_dir


class Command(BaseCommand):
    help = 'Génère le rapport PDF de présence journalière pour une date donnée.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            required=True,
            help='Date du rapport (YYYY-MM-DD), ex. 2026-07-09',
        )
        parser.add_argument(
            '--direction',
            default='',
            help='ID direction (optionnel)',
        )
        parser.add_argument(
            '--output',
            default='',
            help='Chemin du fichier PDF de sortie (optionnel)',
        )

    def handle(self, *args, **options):
        try:
            target_date = date.fromisoformat(str(options['date']).strip())
        except ValueError as exc:
            raise CommandError('Date invalide — format attendu YYYY-MM-DD') from exc

        direction_id = None
        raw_direction = str(options.get('direction') or '').strip()
        if raw_direction:
            try:
                direction_id = int(raw_direction)
            except ValueError as exc:
                raise CommandError('direction invalide — entier attendu') from exc

        pdf_bytes = render_daily_attendance_pdf(target_date=target_date, direction_id=direction_id)
        report = build_daily_attendance_report(target_date=target_date, direction_id=direction_id)
        filename = report.get('pdf_filename') or 'rapport-rh-onip-presence-journalier.pdf'
        output = str(options.get('output') or '').strip()
        if output:
            output_path = Path(output)
        else:
            output_path = default_reports_output_dir() / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(pdf_bytes)
        self.stdout.write(self.style.SUCCESS(f'PDF généré : {output_path} ({len(pdf_bytes)} octets)'))
