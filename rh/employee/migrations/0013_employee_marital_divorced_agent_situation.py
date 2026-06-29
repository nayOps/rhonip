from django.db import migrations, models


def mark_directory_agents_active(apps, schema_editor):
    from employee.utils.agents_directory import agents_directory_queryset

    Employee = apps.get_model('employee', 'Employee')
    active_ids = list(agents_directory_queryset().values_list('pk', flat=True))
    if active_ids:
        Employee.objects.filter(pk__in=active_ids).update(agent_situation='active')


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0012_employee_country_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='marital_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('maried', 'marié(e)'),
                    ('single', 'célibataire'),
                    ('divorced', 'divorcé(e)'),
                ],
                default=None,
                max_length=12,
                null=True,
                verbose_name='état civil',
            ),
        ),
        migrations.AddField(
            model_name='employee',
            name='agent_situation',
            field=models.CharField(
                choices=[('active', 'actif'), ('inactive', 'inactif')],
                default='inactive',
                max_length=10,
                verbose_name="situation de l'agent",
            ),
        ),
        migrations.RunPython(mark_directory_agents_active, migrations.RunPython.noop),
    ]
