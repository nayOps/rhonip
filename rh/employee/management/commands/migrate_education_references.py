from django.core.management.base import BaseCommand

from employee.models import Education
from employee.utils.education_references import seed_all_references


class Command(BaseCommand):
    help = "Réapplique le seed des référentiels formation et peut re-mapper les valeurs legacy si présentes."

    def add_arguments(self, parser):
        parser.add_argument(
            '--seed-only',
            action='store_true',
            help='Ne fait que recharger les listes système.',
        )

    def handle(self, *args, **options):
        seed_all_references()
        self.stdout.write(self.style.SUCCESS('Référentiels formation rechargés.'))

        if options['seed_only']:
            return

        legacy_fields = (
            ('study_level_legacy', 'study_level'),
            ('degree_legacy', 'degree'),
            ('field_of_study_legacy', 'field_of_study'),
            ('institution_legacy', 'institution'),
        )
        if not any(hasattr(Education, legacy) for legacy, _target in legacy_fields):
            self.stdout.write('Aucun champ legacy à migrer.')
            return

        from employee.utils.education_references import migrate_education_char_to_fk
        from django.apps import apps

        migrate_education_char_to_fk(apps=apps)
        self.stdout.write(self.style.SUCCESS('Migration legacy terminée.'))
