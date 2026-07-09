from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from employee.utils.completed_enrollment_day_report import (
    build_completed_enrollment_global_report,
    render_completed_enrollment_global_pdf,
)


class Command(BaseCommand):
    help = 'Génère le rapport PDF global des agents ACTIF 10/10 sur une période.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period-from',
            required=True,
            help='Début de période (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--period-to',
            required=True,
            help='Fin de période (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--output',
            default='',
            help='Chemin du fichier PDF de sortie (optionnel)',
        )

    def handle(self, *args, **options):
        try:
            period_from = date.fromisoformat(str(options['period_from']).strip())
            period_to = date.fromisoformat(str(options['period_to']).strip())
        except ValueError as exc:
            raise CommandError('Période invalide — format attendu YYYY-MM-DD') from exc

        if period_from > period_to:
            period_from, period_to = period_to, period_from

        report = build_completed_enrollment_global_report(period_from, period_to)
        pdf_bytes = render_completed_enrollment_global_pdf(period_from, period_to)
        default_name = report.get('pdf_filename', 'rapport-rh-onip-enregistrement-global.pdf')
        output = options.get('output') or default_name
        output_path = Path(output)
        output_path.write_bytes(pdf_bytes)
        self.stdout.write(
            self.style.SUCCESS(
                f'PDF généré : {output_path} ({len(pdf_bytes)} octets, {report["total_count"]} agents)'
            )
        )
