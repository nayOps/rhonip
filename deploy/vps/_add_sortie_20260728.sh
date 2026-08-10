#!/usr/bin/env bash
# Ajoute une sortie 16:30 le 28/07/2026 pour tous les agents ayant un pointage
# ce jour-là mais sans sortie (EVENING_OUT) déjà enregistrée.
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'

sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=40 adn@102.68.62.85 bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py shell <<'PY'
from datetime import date, time, datetime
from collections import defaultdict
from employee.models import Attendance, Employee
from employee.utils.attendance_slots import evaluate_day_slots

DAY = date(2026, 7, 28)
OUT_TIME = time(16, 30)

def as_time(v):
    if isinstance(v, time):
        return v
    if isinstance(v, datetime):
        return v.time()
    s = str(v).strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            pass
    return None

qs = Attendance.objects.filter(date=DAY).select_related('employee').order_by('employee_id', 'time')
by_emp = defaultdict(list)
for a in qs:
    by_emp[a.employee_id].append(a)

created = skipped_has_out = skipped_conflict = 0
details = []
for eid, punches in by_emp.items():
    emp = punches[0].employee
    times = [t for t in (as_time(p.time) for p in punches) if t]
    if not times:
        continue
    detail = evaluate_day_slots(DAY, times)
    eo = (detail.get('slots') or {}).get('EVENING_OUT') or {}
    if eo.get('punch_time'):
        skipped_has_out += 1
        continue
    # Avoid unique constraint (employee, date, time)
    if Attendance.objects.filter(employee=emp, date=DAY, time=OUT_TIME).exists():
        skipped_conflict += 1
        details.append(f"CONFLICT {emp.registration_number} already has {OUT_TIME}")
        continue
    Attendance.objects.create(
        employee=emp,
        date=DAY,
        time=OUT_TIME,
        direction='OUT',
        source='manual',
    )
    created += 1
    details.append(f"OK {emp.registration_number} +OUT {OUT_TIME.strftime('%H:%M')} (had {[t.strftime('%H:%M') for t in times]})")

print(f"employees_with_punches={len(by_emp)}")
print(f"created_out={created}")
print(f"skipped_has_out={skipped_has_out}")
print(f"skipped_conflict={skipped_conflict}")
for line in details[:30]:
    print(line)
if len(details) > 30:
    print(f"... +{len(details)-30} more")

# spot check
still_missing = 0
for eid, punches in by_emp.items():
    times = [t for t in (as_time(p.time) for p in Attendance.objects.filter(employee_id=eid, date=DAY)) if t]
    detail = evaluate_day_slots(DAY, times)
    eo = (detail.get('slots') or {}).get('EVENING_OUT') or {}
    if times and not eo.get('punch_time'):
        still_missing += 1
print(f"still_missing_out_after={still_missing}")
print("SORTIE_28_OK")
PY
REMOTE
