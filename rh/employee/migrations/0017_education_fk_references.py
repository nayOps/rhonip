import core.models.fields.model_select_field
from django.db import migrations, models
import django.db.models.deletion


def migrate_education_to_references(apps, schema_editor):
    from employee.utils.education_references import migrate_education_char_to_fk

    migrate_education_char_to_fk(apps=apps)


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('employee', '0016_education_reference_tables'),
    ]

    operations = [
        migrations.RenameField(
            model_name='education',
            old_name='study_level',
            new_name='study_level_legacy',
        ),
        migrations.RenameField(
            model_name='education',
            old_name='degree',
            new_name='degree_legacy',
        ),
        migrations.RenameField(
            model_name='education',
            old_name='field_of_study',
            new_name='field_of_study_legacy',
        ),
        migrations.RenameField(
            model_name='education',
            old_name='institution',
            new_name='institution_legacy',
        ),
        migrations.AddField(
            model_name='education',
            name='study_level_ref',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='employee.studylevel',
                verbose_name="niveau d'étude",
            ),
        ),
        migrations.AddField(
            model_name='education',
            name='degree_ref',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='employee.degree',
                verbose_name='diplôme',
            ),
        ),
        migrations.AddField(
            model_name='education',
            name='field_of_study_ref',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='employee.fieldofstudy',
                verbose_name='domaine',
            ),
        ),
        migrations.AddField(
            model_name='education',
            name='institution_ref',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='employee.institution',
                verbose_name='établissement',
            ),
        ),
        migrations.RunPython(migrate_education_to_references, migrations.RunPython.noop, atomic=False),
        migrations.RemoveField(model_name='education', name='study_level_legacy'),
        migrations.RemoveField(model_name='education', name='degree_legacy'),
        migrations.RemoveField(model_name='education', name='field_of_study_legacy'),
        migrations.RemoveField(model_name='education', name='institution_legacy'),
        migrations.RenameField(
            model_name='education',
            old_name='study_level_ref',
            new_name='study_level',
        ),
        migrations.RenameField(
            model_name='education',
            old_name='degree_ref',
            new_name='degree',
        ),
        migrations.RenameField(
            model_name='education',
            old_name='field_of_study_ref',
            new_name='field_of_study',
        ),
        migrations.RenameField(
            model_name='education',
            old_name='institution_ref',
            new_name='institution',
        ),
    ]
