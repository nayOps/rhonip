from django.core.management.base import BaseCommand

from employee.models import Employee
from employee.utils.professional_email import (
    build_professional_email,
    is_alema_olamba,
)


class Command(BaseCommand):
    help = (
        "Génère les e-mails professionnels au format prenom.nom@onip.gouv.cd "
        "pour tous les agents, sauf Alema Olamba."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les e-mails sans modifier la base.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Écrase les e-mails professionnels déjà renseignés.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        stats = {
            'updated': 0,
            'skipped_excluded': 0,
            'skipped_existing': 0,
            'skipped_incomplete': 0,
            'skipped_duplicate': 0,
        }
        seen_emails: dict[str, int] = {}
        updates: list[tuple[Employee, str]] = []

        for employee in Employee.objects.order_by('id'):
            if is_alema_olamba(employee):
                stats['skipped_excluded'] += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Exclu: #{employee.id} {employee.first_name} '
                        f'{employee.middle_name or ""} {employee.last_name}'.strip()
                    )
                )
                continue

            if employee.email_professional and not force:
                stats['skipped_existing'] += 1
                continue

            email = build_professional_email(employee.first_name, employee.last_name)
            if not email:
                stats['skipped_incomplete'] += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Ignoré (nom incomplet): #{employee.id} '
                        f'{employee.first_name} {employee.last_name}'
                    )
                )
                continue

            if email in seen_emails:
                stats['skipped_duplicate'] += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Doublon: #{employee.id} → {email} '
                        f'(déjà attribué à #{seen_emails[email]})'
                    )
                )
                continue

            seen_emails[email] = employee.id
            updates.append((employee, email))
            stats['updated'] += 1

        for employee, email in updates:
            label = (
                f'#{employee.id} {employee.first_name} {employee.last_name} → {email}'
            )
            if dry_run:
                self.stdout.write(f'[dry-run] {label}')
                continue

            employee.email_professional = email
            employee.save(update_fields=['email_professional'])
            self.stdout.write(label)

        if not dry_run and updates:
            self.stdout.write(self.style.SUCCESS('Enregistrement terminé.'))

        self.stdout.write('')
        for key, value in stats.items():
            self.stdout.write(f'{key}: {value}')
