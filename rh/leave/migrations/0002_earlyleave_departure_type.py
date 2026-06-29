from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='earlyleave',
            name='departure_type',
            field=models.CharField(
                choices=[
                    ('personal', 'Personnel'),
                    ('medical', 'Médical'),
                    ('administrative', 'Administratif'),
                    ('official', 'Mission / officiel'),
                    ('other', 'Autre'),
                ],
                default='personal',
                max_length=20,
                verbose_name='type de départ',
            ),
        ),
    ]
