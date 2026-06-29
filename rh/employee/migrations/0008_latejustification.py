import core.models.fields.date_field
import core.models.fields.json_field
import core.models.fields.model_select_field
import core.models.fields.time_field
import core.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('employee', '0007_attendance_punch_slots'),
    ]

    operations = [
        migrations.CreateModel(
            name='LateJustification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le/à')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le/à')),
                ('metadata', core.models.fields.json_field.JSONField(blank=True, default=dict, verbose_name='meta')),
                ('date', core.models.fields.date_field.DateField(verbose_name='date du retard')),
                ('delay_minutes', models.PositiveIntegerField(default=0, verbose_name='retard (minutes)')),
                ('morning_punch_time', core.models.fields.time_field.TimeField(blank=True, default=None, null=True, verbose_name="heure d'arrivée")),
                ('reason', models.TextField(verbose_name='motif')),
                ('document', models.FileField(blank=True, default=None, null=True, upload_to=core.utils.upload_directory_file, verbose_name='pièce justificative')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_latejustification_created_by', to=settings.AUTH_USER_MODEL, verbose_name='créé par')),
                ('employee', core.models.fields.model_select_field.ModelSelect(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='late_justifications', to='employee.employee', verbose_name='employé')),
                ('updated_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='employee_latejustification_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='mis à jour par')),
            ],
            options={
                'verbose_name': 'justification de retard',
                'verbose_name_plural': 'justifications de retard',
                'ordering': ('-date', '-id'),
            },
        ),
        migrations.AddConstraint(
            model_name='latejustification',
            constraint=models.UniqueConstraint(fields=('employee', 'date'), name='employee_late_justification_unique_day'),
        ),
    ]
