#!/usr/bin/env bash
# Seed jour férié 03/08/2026 + clear cache
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'

sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=40 adn@102.68.62.85 bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py shell <<'PY'
from datetime import date
from leave.models import Holiday
from employee.utils.holidays import clear_holiday_cache, is_public_holiday, holiday_name_for_day
from employee.utils.attendance_slots import evaluate_day_slots

DAY = date(2026, 8, 3)
obj, created = Holiday.objects.get_or_create(
    start_dt=DAY,
    end_dt=DAY,
    defaults={'name': 'Jour férié', 'paid': True},
)
if not created and not obj.name:
    obj.name = 'Jour férié'
    obj.save()
clear_holiday_cache()
print('holiday', 'created' if created else 'exists', obj.id, obj.name, obj.start_dt, obj.end_dt)
print('is_public_holiday', is_public_holiday(DAY), holiday_name_for_day(DAY))
r = evaluate_day_slots(DAY, [])
print('evaluate', r.get('status'), r.get('status_label'), r.get('note'))
print('HOLIDAY_SEED_OK')
PY
REMOTE
