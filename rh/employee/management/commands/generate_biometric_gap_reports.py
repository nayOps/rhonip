from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from employee.utils.biometric_gap_reports import (
    REPORT_INACTIVE,
    REPORT_MISSING_BIOMETRIC,
    build_active_missing_biometric_report,
    build_inactive_agents_report,
    render_biometric_gap_pdf,
)


class Command(BaseCommand):
    help = 'Génère les rapports PDF inactifs (43) et actifs sans empreinte ni photo (26).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report',
            choices=[REPORT_INACTIVE, REPORT_MISSING_BIOMETRIC, 'all'],
            default='all',
            help='Type de rapport à générer',
        )
        parser.add_argument('--output', default='', help='Chemin PDF (un seul rapport)')

    def handle(self, *args, **options):
        report_type = options['report']
        output = (options.get('output') or '').strip()

        if report_type in (REPORT_INACTIVE, 'all'):
            self._write_report(build_inactive_agents_report(), output if report_type == REPORT_INACTIVE else '')

        if report_type in (REPORT_MISSING_BIOMETRIC, 'all'):
            self._write_report(
                build_active_missing_biometric_report(),
                output if report_type == REPORT_MISSING_BIOMETRIC else '',
            )

    def _write_report(self, report: dict, output: str) -> None:
        pdf_bytes = render_biometric_gap_pdf(report)
        filename = report.get('pdf_filename') or f'rapport-{timezone.localdate():%Y-%m-%d}.pdf'
        output_path = Path(output or filename)
        output_path.write_bytes(pdf_bytes)
        self.stdout.write(
            self.style.SUCCESS(
                f'PDF généré : {output_path} ({len(pdf_bytes)} octets, {report["total_count"]} agents)'
            )
        )
