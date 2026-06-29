from django.core.management.base import BaseCommand

from employee.services.employee_accounts import provision_all_employee_accounts


class Command(BaseCommand):
    help = (
        "Crée les comptes utilisateurs pour les agents (e-mail pro + mot de passe = matricule). "
        "Exclut Alema Olamba."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule sans écrire en base.',
        )
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='Réinitialise le mot de passe au matricule pour les comptes existants.',
        )

    def handle(self, *args, **options):
        stats = provision_all_employee_accounts(
            reset_password=options['reset_password'],
            dry_run=options['dry_run'],
        )
        for key, value in stats.items():
            self.stdout.write(f'{key}: {value}')
