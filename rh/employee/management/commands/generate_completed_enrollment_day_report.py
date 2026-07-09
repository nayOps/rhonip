from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from employee.utils.completed_enrollment_day_report import (
    build_completed_enrollment_day_report,
    render_completed_enrollment_day_pdf,
)


class Command(BaseCommand):
    help = 'Génère le rapport PDF des enrollments complets pour une journée donnée.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            required=True,
            help='Date du rapport (YYYY-MM-DD), ex. 2026-06-22',
        )
        parser.add_argument(
            '--period-from',
            default='',
            help='Début de période pour la dernière capture (YYYY-MM-DD, optionnel)',
        )
        parser.add_argument(
            '--period-to',
            default='',
            help='Fin de période pour la dernière capture (YYYY-MM-DD, optionnel)',
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

        period_from = None
        period_to = None
        raw_from = str(options.get('period_from') or '').strip()
        raw_to = str(options.get('period_to') or '').strip()
        if raw_from:
            try:
                period_from = date.fromisoformat(raw_from)
            except ValueError as exc:
                raise CommandError('period-from invalide — format attendu YYYY-MM-DD') from exc
        if raw_to:
            try:
                period_to = date.fromisoformat(raw_to)
            except ValueError as exc:
                raise CommandError('period-to invalide — format attendu YYYY-MM-DD') from exc

        pdf_bytes = render_completed_enrollment_day_pdf(target_date, period_from, period_to)
        default_name = build_completed_enrollment_day_report(
            target_date, period_from, period_to
        ).get('pdf_filename', f'rapport-rh-onip-enregistrement-journalier-{target_date:%Y-%m-%d}.pdf')
        output = options.get('output') or default_name
        output_path = Path(output)
        output_path.write_bytes(pdf_bytes)
        self.stdout.write(self.style.SUCCESS(f'PDF généré : {output_path} ({len(pdf_bytes)} octets)'))
