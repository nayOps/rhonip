from django.core.management.base import BaseCommand

from employee.models import Education, Employee
from employee.utils.education_references import resolve_reference


class Command(BaseCommand):
    help = "Synchronise les formations depuis metadata (niveauEtude, domaineEtude) du dossier agents."

    def handle(self, *args, **options):
        from employee.models.education_references import FieldOfStudy, StudyLevel

        updated = 0
        created = 0
        for employee in Employee.objects.all().iterator():
            meta = employee.metadata or {}
            study_level_raw = (meta.get('niveauEtude') or '').strip() or None
            field_of_study_raw = (meta.get('domaineEtude') or meta.get('domaine') or '').strip() or None
            if not study_level_raw and not field_of_study_raw:
                continue

            study_level = resolve_reference(StudyLevel, study_level_raw) if study_level_raw else None
            field_of_study = resolve_reference(FieldOfStudy, field_of_study_raw) if field_of_study_raw else None

            education = Education.objects.filter(employee=employee).order_by('id').first()
            if education:
                changed = False
                if study_level and education.study_level_id != study_level.pk:
                    education.study_level = study_level
                    changed = True
                if field_of_study and education.field_of_study_id != field_of_study.pk:
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
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Formations synchronisées — créées: {created}, mises à jour: {updated}"
        ))
