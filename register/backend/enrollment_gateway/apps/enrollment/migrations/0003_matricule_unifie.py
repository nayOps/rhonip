from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0002_enrollmentsession_modality_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enrollmentsession',
            old_name='nin',
            new_name='registration_number',
        ),
        migrations.RenameField(
            model_name='enrollmentreceipt',
            old_name='nin',
            new_name='registration_number',
        ),
        migrations.RemoveField(
            model_name='enrollmentsession',
            name='extensions_status',
        ),
        migrations.RemoveField(
            model_name='enrollmentsession',
            name='fgp_core_status',
        ),
        migrations.AddField(
            model_name='enrollmentsession',
            name='employee_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
