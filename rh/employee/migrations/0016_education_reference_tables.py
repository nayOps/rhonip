from django.conf import settings
from django.db import migrations, models
import core.models.fields.json_field
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


def seed_education_references(apps, schema_editor):
    from employee.utils.education_references import seed_all_references

    seed_all_references(apps=apps)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0015_attendance_schedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le/à')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le/à')),
                ('metadata', core.models.fields.json_field.JSONField(blank=True, default=dict, verbose_name='meta')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='code')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='libellé')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ordre')),
                ('is_system', models.BooleanField(default=True, verbose_name='système')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_created_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='créé par',
                )),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    on_update=True,
                    related_name='%(app_label)s_%(class)s_updated_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='mis à jour par',
                )),
            ],
            options={
                'verbose_name': "niveau d'étude",
                'verbose_name_plural': "niveaux d'étude",
                'ordering': ('sort_order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le/à')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le/à')),
                ('metadata', core.models.fields.json_field.JSONField(blank=True, default=dict, verbose_name='meta')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='code')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='libellé')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ordre')),
                ('is_system', models.BooleanField(default=True, verbose_name='système')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_created_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='créé par',
                )),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    on_update=True,
                    related_name='%(app_label)s_%(class)s_updated_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='mis à jour par',
                )),
            ],
            options={
                'verbose_name': 'diplôme',
                'verbose_name_plural': 'diplômes',
                'ordering': ('sort_order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='FieldOfStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le/à')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le/à')),
                ('metadata', core.models.fields.json_field.JSONField(blank=True, default=dict, verbose_name='meta')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='code')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='libellé')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ordre')),
                ('is_system', models.BooleanField(default=True, verbose_name='système')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_created_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='créé par',
                )),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    on_update=True,
                    related_name='%(app_label)s_%(class)s_updated_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='mis à jour par',
                )),
            ],
            options={
                'verbose_name': 'domaine de formation',
                'verbose_name_plural': 'domaines de formation',
                'ordering': ('sort_order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le/à')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le/à')),
                ('metadata', core.models.fields.json_field.JSONField(blank=True, default=dict, verbose_name='meta')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='code')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='libellé')),
                ('institution_type', models.CharField(
                    choices=[('public', 'Publique'), ('private', 'Privée'), ('other', 'Autre')],
                    default='other',
                    max_length=20,
                    verbose_name='type',
                )),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='ordre')),
                ('is_system', models.BooleanField(default=True, verbose_name='système')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    related_name='%(app_label)s_%(class)s_created_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='créé par',
                )),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(
                    default=django_currentuser.middleware.get_current_authenticated_user,
                    null=True,
                    on_delete=models.deletion.CASCADE,
                    on_update=True,
                    related_name='%(app_label)s_%(class)s_updated_by',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='mis à jour par',
                )),
            ],
            options={
                'verbose_name': 'établissement',
                'verbose_name_plural': 'établissements',
                'ordering': ('sort_order', 'name'),
            },
        ),
        migrations.RunPython(seed_education_references, migrations.RunPython.noop),
    ]
