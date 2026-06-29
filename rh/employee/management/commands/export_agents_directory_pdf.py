from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from employee.utils.agents_directory import (
    agents_directory_queryset,
    render_agents_directory_html,
    render_agents_directory_pdf,
)


class Command(BaseCommand):
    help = (
        "Génère un PDF annuaire des agents (prénom, nom, mot de passe, "
        "e-mail professionnel), hors Directeur Général et Directeurs Généraux Adjoints."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='',
            help='Chemin du fichier PDF de sortie (défaut: media/exports/annuaire-agents-YYYYMMDD-HHMMSS.pdf).',
        )
        parser.add_argument(
            '--html-only',
            action='store_true',
            help='Génère uniquement le fichier HTML (sans PDF).',
        )

    def handle(self, *args, **options):
        employees = agents_directory_queryset()
        count = employees.count()
        timestamp = timezone.localtime().strftime('%Y%m%d-%H%M%S')
        default_name = f'annuaire-agents-{timestamp}.pdf'
        output = Path(options['output'] or Path('media') / 'exports' / default_name)
        output.parent.mkdir(parents=True, exist_ok=True)

        if options['html_only']:
            html_path = output.with_suffix('.html')
            html_path.write_text(render_agents_directory_html(), encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f'HTML généré: {html_path} ({count} agents)'))
            return

        pdf_bytes = render_agents_directory_pdf()
        output.write_bytes(pdf_bytes)
        self.stdout.write(self.style.SUCCESS(f'PDF généré: {output} ({count} agents)'))
