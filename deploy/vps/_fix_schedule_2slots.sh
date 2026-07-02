#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
sshpass -e ssh -o StrictHostKeyChecking=no adn@102.68.62.85 bash -s <<'REMOTE'
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE exec -T rh_server python manage.py shell <<'PY'
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
row.slots_config = list(PRESET_2_SLOTS_CONFIG)
row.work_start = time(8, 0)
row.work_end = time(16, 30)
row.save()
clear_attendance_schedule_cache()
s = get_presence_slots()
print("OK", row.slot_preset, s[0]["accept_from"], s[0]["accept_until"], s[1]["accept_from"], s[1]["accept_until"])
PY

$COMPOSE --profile rh restart rh_server
sleep 12
curl -sS -o /dev/null -w "overview:%{http_code}\n" --max-time 20 http://127.0.0.1:8100/login/
REMOTE
