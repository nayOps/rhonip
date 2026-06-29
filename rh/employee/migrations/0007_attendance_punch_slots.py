from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0006_employee_optional_fields'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='attendance',
            name='source',
            field=models.CharField(
                choices=[
                    ('manual', 'Saisie manuelle'),
                    ('fingerprint', 'Empreinte'),
                    ('import', 'Import'),
                ],
                default='manual',
                max_length=20,
                verbose_name='source',
            ),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='direction',
            field=models.CharField(
                blank=True,
                choices=[('IN', 'entrée'), ('OUT', 'sortie')],
                max_length=10,
                null=True,
                verbose_name='direction',
            ),
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.UniqueConstraint(
                fields=('employee', 'date', 'time'),
                name='employee_attendance_unique_punch',
            ),
        ),
    ]
