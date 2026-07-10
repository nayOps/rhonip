from django.core.management.base import BaseCommand
from django.db import transaction

from employee.models import Education
from employee.models.education_references import Degree, FieldOfStudy, Institution, StudyLevel
from employee.utils.education_references import resolve_reference, seed_all_references

FIELD_MODELS = (
    ('study_level', StudyLevel),
    ('field_of_study', FieldOfStudy),
    ('degree', Degree),
    ('institution', Institution),
)


class Command(BaseCommand):
    help = (
        "Réaligne les FK formation sur les référentiels canoniques "
        "(alias catalog) et supprime les doublons non utilisés."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--prune',
            action='store_true',
            help='Supprime les entrées non-système sans formation liée.',
        )

    def handle(self, *args, **options):
        seed_all_references()
        self.stdout.write('Référentiels système rechargés.')

        remapped = 0
        with transaction.atomic():
            for education in Education.objects.select_related(
                'study_level', 'field_of_study', 'degree', 'institution',
            ).iterator():
                updates = {}
                for field_name, model in FIELD_MODELS:
                    current = getattr(education, field_name)
                    if not current:
                        continue
                    canonical = resolve_reference(model, current.name, create_if_missing=False)
                    if canonical is None:
                        canonical = resolve_reference(model, current.name, create_if_missing=True)
                    if canonical and canonical.pk != current.pk:
                        updates[field_name] = canonical
                        remapped += 1
                if updates:
                    for field_name, value in updates.items():
                        setattr(education, field_name, value)
                    education.save(update_fields=list(updates.keys()))

        self.stdout.write(self.style.SUCCESS(f'Formations réalignées: {remapped} champ(s) mis à jour.'))

        if not options['prune']:
            return

        pruned = 0
        for field_name, model in FIELD_MODELS:
            for row in model.objects.filter(is_system=False):
                if not Education.objects.filter(**{field_name: row}).exists():
                    row.delete()
                    pruned += 1
        self.stdout.write(self.style.SUCCESS(f'Doublons supprimés: {pruned}.'))
