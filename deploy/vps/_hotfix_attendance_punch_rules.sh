#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS='adn@102.68.62.85'

FILES=(
  rh/employee/utils/attendance_slots.py
  rh/employee/utils/attendance_schedule_config.py
  rh/employee/services/attendance_punch.py
  rh/employee/tests_attendance_punch.py
)

for f in "${FILES[@]}"; do
  sshpass -e scp -o StrictHostKeyChecking=no "$ROOT/$f" "$VPS:~/onip-rh/$f"
done

# rh/api n'est pas monté en volume sur le VPS : copie directe dans le conteneur
sshpass -e scp -o StrictHostKeyChecking=no "$ROOT/rh/api/views/attendance_device.py" "$VPS:/tmp/attendance_device.py"

sshpass -e ssh -o StrictHostKeyChecking=no "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"
$COMPOSE --profile rh cp /tmp/attendance_device.py rh_server:/app/backend/api/views/attendance_device.py
$COMPOSE --profile rh restart rh_server
sleep 8
$COMPOSE --profile rh exec -T rh_server python manage.py shell -c "
from employee.models import AttendanceSchedule
from employee.utils.attendance_schedule_config import (
    clear_attendance_schedule_cache,
    preset_slots,
    serialize_slot,
)
row = AttendanceSchedule.objects.first()
if row and row.slot_preset == AttendanceSchedule.PRESET_2_SLOTS:
    row.slots_config = [serialize_slot(slot) for slot in preset_slots('2_slots')]
    row.work_start = __import__('datetime').time(8, 0)
    row.work_end = __import__('datetime').time(16, 0)
    row.save()
    clear_attendance_schedule_cache()
    print('schedule_synced_2_slots')
else:
    print('schedule_skip', getattr(row, 'slot_preset', None))
"
$COMPOSE --profile rh exec -T rh_server python manage.py test employee.tests_attendance_punch -v 1
echo DEPLOY_OK
REMOTE
