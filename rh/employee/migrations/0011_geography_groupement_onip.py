# Generated manually for ONIP geography hierarchy (groupement level)

import core.models.fields.cascade_model_select_field
import core.models.fields.json_field
import core.models.fields.model_select_field
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


def migrate_villages_to_groupement(apps, schema_editor):
    Village = apps.get_model('employee', 'Village')
    Groupement = apps.get_model('employee', 'Groupement')
    Sector = apps.get_model('employee', 'Sector')

    for village in Village.objects.select_related('territory', 'sector').iterator():
        sector = village.sector
        if not sector:
            sector, _ = Sector.objects.get_or_create(
                territory_id=village.territory_id,
                name='Non renseigné',
                defaults={'type_name': ''},
            )
        groupement, _ = Groupement.objects.get_or_create(
            sector_id=sector.pk,
            name='Non renseigné',
            defaults={'type_name': ''},
        )
        village.groupement_id = groupement.pk
        village.save(update_fields=['groupement_id'])


def migrate_employee_home_groupement(apps, schema_editor):
    Employee = apps.get_model('employee', 'Employee')
    Village = apps.get_model('employee', 'Village')

    for employee in Employee.objects.exclude(home_village_id=None).iterator():
        village = Village.objects.filter(pk=employee.home_village_id).select_related('groupement').first()
        if village and village.groupement_id and employee.home_groupement_id != village.groupement_id:
            employee.home_groupement_id = village.groupement_id
            employee.save(update_fields=['home_groupement_id'])


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0010_employee_date_fields_optional'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='village',
            name='uniq_village_per_territory_sector',
        ),
        migrations.RemoveConstraint(
            model_name='territory',
            name='uniq_territory_per_province',
        ),
        migrations.RemoveConstraint(
            model_name='sector',
            name='uniq_sector_per_territory',
        ),
        migrations.AddField(
            model_name='province',
            name='source_id',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='identifiant source'),
        ),
        migrations.AddField(
            model_name='territory',
            name='source_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='identifiant source'),
        ),
        migrations.AddField(
            model_name='territory',
            name='type_name',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='type'),
        ),
        migrations.AddField(
            model_name='sector',
            name='source_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='identifiant source'),
        ),
        migrations.AddField(
            model_name='sector',
            name='type_name',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='province',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='nom'),
        ),
        migrations.AlterField(
            model_name='territory',
            name='name',
            field=models.CharField(max_length=200, verbose_name='nom'),
        ),
        migrations.AlterField(
            model_name='sector',
            name='name',
            field=models.CharField(max_length=200, verbose_name='nom'),
        ),
        migrations.CreateModel(
            name='Groupement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le/à')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le/à')),
                ('metadata', core.models.fields.json_field.JSONField(blank=True, default=dict, verbose_name='meta')),
                ('source_id', models.IntegerField(blank=True, null=True, verbose_name='identifiant source')),
                ('name', models.CharField(max_length=200, verbose_name='nom')),
                ('type_name', models.CharField(blank=True, default='', max_length=20, verbose_name='type')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='créé par')),
                ('sector', core.models.fields.model_select_field.ModelSelect(on_delete=django.db.models.deletion.CASCADE, to='employee.sector', verbose_name='secteur')),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='mis à jour par')),
            ],
            options={
                'verbose_name': 'groupement',
                'verbose_name_plural': 'groupements',
                'ordering': ('sector__name', 'name'),
            },
        ),
        migrations.AddField(
            model_name='village',
            name='groupement',
            field=core.models.fields.model_select_field.ModelSelect(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='employee.groupement',
                verbose_name='groupement',
            ),
        ),
        migrations.AddField(
            model_name='village',
            name='source_id',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='identifiant source'),
        ),
        migrations.AddField(
            model_name='village',
            name='locality_name',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='localité'),
        ),
        migrations.AddField(
            model_name='village',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='latitude'),
        ),
        migrations.AddField(
            model_name='village',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='longitude'),
        ),
        migrations.AlterField(
            model_name='village',
            name='name',
            field=models.CharField(max_length=200, verbose_name='nom'),
        ),
        migrations.RunPython(migrate_villages_to_groupement, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='village',
            name='sector',
        ),
        migrations.RemoveField(
            model_name='village',
            name='territory',
        ),
        migrations.AlterField(
            model_name='village',
            name='groupement',
            field=core.models.fields.model_select_field.ModelSelect(
                on_delete=django.db.models.deletion.CASCADE,
                to='employee.groupement',
                verbose_name='groupement',
            ),
        ),
        migrations.AlterModelOptions(
            name='village',
            options={'ordering': ('name',), 'verbose_name': 'village', 'verbose_name_plural': 'villages'},
        ),
        migrations.AddField(
            model_name='employee',
            name='home_groupement',
            field=core.models.fields.cascade_model_select_field.CascadeModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='employee.groupement',
                verbose_name="groupement d'origine",
            ),
        ),
        migrations.RunPython(migrate_employee_home_groupement, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='territory',
            constraint=models.UniqueConstraint(fields=('province', 'source_id'), name='uniq_territory_source_per_province'),
        ),
        migrations.AddConstraint(
            model_name='sector',
            constraint=models.UniqueConstraint(fields=('territory', 'source_id'), name='uniq_sector_source_per_territory'),
        ),
        migrations.AddConstraint(
            model_name='groupement',
            constraint=models.UniqueConstraint(fields=('sector', 'source_id'), name='uniq_groupement_source_per_sector'),
        ),
        migrations.AddConstraint(
            model_name='village',
            constraint=models.UniqueConstraint(fields=('groupement', 'name'), name='uniq_village_per_groupement'),
        ),
        migrations.AddIndex(
            model_name='village',
            index=models.Index(fields=['name'], name='employee_village_name_idx'),
        ),
    ]
