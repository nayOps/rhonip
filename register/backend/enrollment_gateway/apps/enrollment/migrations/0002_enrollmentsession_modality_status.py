from django.db import migrations, models


def seed_modality_status(apps, schema_editor):
    EnrollmentSession = apps.get_model('enrollment', 'EnrollmentSession')
    default = {
        'fingerprint': 'pending',
        'iris': 'pending',
        'document': 'pending',
        'signature': 'pending',
    }
    for session in EnrollmentSession.objects.filter(modality_status={}):
        session.modality_status = default
        session.save(update_fields=['modality_status'])


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollmentsession',
            name='modality_status',
            field=models.JSONField(default=dict, help_text='Statut par modalité biométrique (fingerprint, iris, ...)'),
        ),
        migrations.RunPython(seed_modality_status, migrations.RunPython.noop),
    ]
