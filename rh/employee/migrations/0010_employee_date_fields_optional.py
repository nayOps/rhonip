import core.models.fields.date_field
import core.models.fields.model_select_field
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0009_education_geography_onip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='date_of_birth',
            field=core.models.fields.date_field.DateField(
                blank=True, default=None, null=True, verbose_name='date de naissance'
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='date_of_join',
            field=core.models.fields.date_field.DateField(
                blank=True, default=None, null=True, verbose_name="date d'engagement"
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='date_of_issue',
            field=core.models.fields.date_field.DateField(
                blank=True, default=None, null=True, verbose_name='date de délivrance'
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='date_of_expiry',
            field=core.models.fields.date_field.DateField(
                blank=True, default=None, null=True, verbose_name="date d'expiration"
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='status',
            field=core.models.fields.model_select_field.ModelSelect(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='employee.status',
                verbose_name='status',
            ),
        ),
    ]
