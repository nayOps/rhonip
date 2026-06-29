from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware
from datetime import time

from employee.utils.attendance_schedule_config import PRESET_4_SLOTS_CONFIG


def create_default_schedule(apps, schema_editor):
    AttendanceSchedule = apps.get_model('employee', 'AttendanceSchedule')
    if not AttendanceSchedule.objects.exists():
        AttendanceSchedule.objects.create(
            slot_preset='4_slots',
            slots_config=PRESET_4_SLOTS_CONFIG,
            work_start=time(8, 0),
            work_end=time(16, 0),
            lunch_break_min_minutes=50,
            lunch_break_max_minutes=70,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0014_remove_employee_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='créé le/à')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='mis à jour le/à')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='meta')),
                (
                    'slot_preset',
                    models.CharField(
                        choices=[
                            ('2_slots', '2 plages (entrée / sortie)'),
                            ('4_slots', '4 plages (matin, pause, après-midi)'),
                        ],
                        default='4_slots',
                        max_length=20,
                        verbose_name='modèle de plages',
                    ),
                ),
                ('slots_config', models.JSONField(blank=True, default=list, verbose_name='configuration des plages')),
                ('work_start', models.TimeField(default=time(8, 0), verbose_name='début de journée')),
                ('work_end', models.TimeField(default=time(16, 0), verbose_name='fin de journée')),
                ('lunch_break_min_minutes', models.PositiveSmallIntegerField(default=50, verbose_name='pause déjeuner min (min)')),
                ('lunch_break_max_minutes', models.PositiveSmallIntegerField(default=70, verbose_name='pause déjeuner max (min)')),
                (
                    'created_by',
                    django_currentuser.db.models.fields.CurrentUserField(
                        default=django_currentuser.middleware.get_current_authenticated_user,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='employee_attendanceschedule_created_by',
                        to='core.user',
                        verbose_name='créé par',
                    ),
                ),
                (
                    'updated_by',
                    django_currentuser.db.models.fields.CurrentUserField(
                        default=django_currentuser.middleware.get_current_authenticated_user,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        on_update=True,
                        related_name='employee_attendanceschedule_updated_by',
                        to='core.user',
                        verbose_name='mis à jour par',
                    ),
                ),
            ],
            options={
                'verbose_name': 'planning des plages de présence',
                'verbose_name_plural': 'plannings des plages de présence',
            },
        ),
        migrations.RunPython(create_default_schedule, migrations.RunPython.noop),
    ]
