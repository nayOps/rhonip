from datetime import time

from django.db import migrations


NEW_PRESETS = {
    '4_slots': [
        {
            'code': 'MORNING_IN',
            'label': 'Entrée matin',
            'target': '08:00',
            'accept_from': '08:00',
            'accept_until': '10:00',
            'reference': '08:00',
            'ui_header': 'Matin : Entrée 1',
        },
        {
            'code': 'LUNCH_OUT',
            'label': 'Sortie pause',
            'target': '12:00',
            'accept_from': '10:01',
            'accept_until': '12:30',
            'ui_header': 'Matin : Sortie 1',
        },
        {
            'code': 'LUNCH_IN',
            'label': 'Entrée pause',
            'target': '13:00',
            'accept_from': '12:00',
            'accept_until': '14:00',
            'ui_header': 'Après-midi : Entrée 2',
        },
        {
            'code': 'EVENING_OUT',
            'label': 'Sortie soir',
            'target': '16:00',
            'accept_from': '16:00',
            'accept_until': '23:59',
            'reference': '16:00',
            'ui_header': 'Après-midi : Sortie 2',
        },
    ],
    '2_slots': [
        {
            'code': 'MORNING_IN',
            'label': 'Entrée',
            'target': '08:00',
            'accept_from': '08:00',
            'accept_until': '10:00',
            'reference': '08:00',
            'ui_header': 'Entrée',
        },
        {
            'code': 'EVENING_OUT',
            'label': 'Sortie',
            'target': '16:00',
            'accept_from': '16:00',
            'accept_until': '23:59',
            'ui_header': 'Sortie',
        },
    ],
}


def sync_attendance_schedule_windows(apps, schema_editor):
    """Applique les nouvelles fenêtres 8h–10h / 16h–23h59 sur le planning actif."""
    AttendanceSchedule = apps.get_model('employee', 'AttendanceSchedule')
    row = AttendanceSchedule.objects.first()
    if not row:
        return

    preset = row.slot_preset or '2_slots'
    if preset not in NEW_PRESETS:
        preset = '2_slots'
        row.slot_preset = preset

    row.slots_config = NEW_PRESETS[preset]
    row.work_start = time(8, 0)
    row.work_end = time(16, 0)
    row.save(update_fields=['slot_preset', 'slots_config', 'work_start', 'work_end', 'updated_at'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0017_education_fk_references'),
    ]

    operations = [
        migrations.RunPython(sync_attendance_schedule_windows, noop_reverse),
    ]
