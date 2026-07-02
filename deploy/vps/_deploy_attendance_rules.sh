#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
B='/mnt/c/Users/HYF/Documents/rh-onip'
VPS='adn@102.68.62.85'

files=(
  rh/employee/utils/attendance_schedule_config.py
  rh/employee/utils/attendance_slots.py
  rh/employee/utils/attendance_stats.py
  rh/template/employee/includes/company_attendance_registry.html
  rh/template/components/employee_attendance_panel.html
  rh/static/assets/css/company-attendance.css
  rh/static/assets/css/employee-detail.css
)

for f in "${files[@]}"; do
  sshpass -e scp -o StrictHostKeyChecking=no "$B/$f" "$VPS:~/onip-rh/$f"
done

sshpass -e ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=no "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE --profile rh exec -T -w /app/backend rh_server sh -c '
cp -f static/assets/css/company-attendance.css staticfiles/assets/css/company-attendance.css
cp -f static/assets/css/employee-detail.css staticfiles/assets/css/employee-detail.css
'

$COMPOSE --profile rh exec -T rh_server python manage.py shell -c "
from datetime import time
from employee.models import AttendanceSchedule
from employee.utils.attendance_schedule_config import (
    PRESET_2_SLOTS_CONFIG,
    clear_attendance_schedule_cache,
    get_presence_slots,
)

row = AttendanceSchedule.objects.first()
if not row:
    row = AttendanceSchedule()
row.slot_preset = AttendanceSchedule.PRESET_2_SLOTS
row.slots_config = PRESET_2_SLOTS_CONFIG
row.work_start = time(8, 0)
row.work_end = time(16, 30)
row.save()
clear_attendance_schedule_cache()
slots = get_presence_slots()
print('preset', row.slot_preset)
print('entry', slots[0]['accept_from'], '-', slots[0]['accept_until'])
print('exit', slots[1]['accept_from'], '-', slots[1]['accept_until'])
"

chmod +x rh/docker/backend/server-entrypoint.sh
$COMPOSE --profile rh cp rh/docker/backend/server-entrypoint.sh rh_server:/app/docker/backend/server-entrypoint.sh
$COMPOSE --profile rh restart rh_server
sleep 15

echo "=== verify ==="
$COMPOSE exec -T rh_server grep -c "missed_entry" /app/backend/employee/utils/attendance_slots.py
curl -sS -o /dev/null -w "overview %{http_code} %{time_total}s\n" --max-time 20 http://127.0.0.1:8100/employee/attendance/overview/
$COMPOSE --profile rh ps rh_server
REMOTE
