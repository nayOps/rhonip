from django.db import migrations, models

import employee.choices.countries


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0011_geography_groupement_onip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='citizenship',
            field=models.CharField(
                blank=True,
                choices=employee.choices.countries.COUNTRY_CHOICES,
                default=employee.choices.countries.DEFAULT_COUNTRY,
                max_length=100,
                null=True,
                verbose_name='nationalité',
            ),
        ),
        migrations.AlterField(
            model_name='employee',
            name='home_country',
            field=models.CharField(
                blank=True,
                choices=employee.choices.countries.COUNTRY_CHOICES,
                default=employee.choices.countries.DEFAULT_COUNTRY,
                max_length=100,
                null=True,
                verbose_name="pays d'origine",
            ),
        ),
    ]
