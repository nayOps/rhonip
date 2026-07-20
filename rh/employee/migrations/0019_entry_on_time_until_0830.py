from django.db import migrations


def sync_morning_reference_0830(apps, schema_editor):
    """Entrée à l'heure jusqu'à 08:30 (référence officielle)."""
    AttendanceSchedule = apps.get_model('employee', 'AttendanceSchedule')
    row = AttendanceSchedule.objects.first()
    if not row or not row.slots_config:
        return

    changed = False
    slots = list(row.slots_config)
    for slot in slots:
        if slot.get('code') == 'MORNING_IN' and slot.get('reference') != '08:30':
            slot['reference'] = '08:30'
            changed = True
    if changed:
        row.slots_config = slots
        row.save(update_fields=['slots_config', 'updated_at'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0018_sync_attendance_slot_windows'),
    ]

    operations = [
        migrations.RunPython(sync_morning_reference_0830, noop_reverse),
    ]
