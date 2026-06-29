from django.core.management.base import BaseCommand, CommandError

from employee.services.import_agents_paie import import_agents_paie


class Command(BaseCommand):
    help = "Importe la liste de paie ONIP (dossier agents/) vers Employee et PayrollLine."

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            dest='file',
            default='',
            help='Chemin vers Liste_Paie_ONIP_*.json (défaut: /app/agents/ ou ../agents/)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule sans écrire en base.',
        )
        parser.add_argument(
            '--no-update',
            action='store_true',
            help='Ne met pas à jour les employés déjà existants.',
        )

    def handle(self, *args, **options):
        path = options['file'] or None
        try:
            stats = import_agents_paie(
                path=path,
                update_existing=not options['no_update'],
                dry_run=options['dry_run'],
            )
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc

        for key, value in stats.items():
            self.stdout.write(f'{key}: {value}')
