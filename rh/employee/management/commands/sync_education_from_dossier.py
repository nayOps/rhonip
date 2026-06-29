from django.core.management.base import BaseCommand

from employee.models import Education, Employee


class Command(BaseCommand):
    help = "Remplit les formations depuis metadata (niveauEtude, domaineEtude) du dossier agents."

    def handle(self, *args, **options):
        updated = 0
        created = 0
        for employee in Employee.objects.all().iterator():
            meta = employee.metadata or {}
            study_level = (meta.get('niveauEtude') or '').strip() or None
            field_of_study = (meta.get('domaineEtude') or '').strip() or None
            if not study_level and not field_of_study:
                continue

            education = Education.objects.filter(employee=employee).order_by('id').first()
            if education:
                changed = False
                if study_level and education.study_level != study_level:
                    education.study_level = study_level
                    changed = True
                if field_of_study and education.field_of_study != field_of_study:
                    education.field_of_study = field_of_study
                    changed = True
                if changed:
                    education.save(update_fields=['study_level', 'field_of_study'])
                    updated += 1
            else:
                Education.objects.create(
                    employee=employee,
                    study_level=study_level,
                    field_of_study=field_of_study,
                    degree=study_level,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Formations synchronisées — créées: {created}, mises à jour: {updated}"
        ))
