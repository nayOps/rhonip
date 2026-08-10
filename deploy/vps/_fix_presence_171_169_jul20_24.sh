#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'

sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 adn@102.68.62.85 bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py shell <<'PY'
from datetime import date, time, datetime
from employee.models import Employee, Attendance
from employee.utils.attendance_slots import evaluate_day_slots

def as_time(v):
    if isinstance(v, time):
        return v
    s = str(v).strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            pass
    return None

def upsert_day(emp, day, tin, tout):
    deleted, _ = Attendance.objects.filter(employee=emp, date=day).delete()
    Attendance.objects.create(employee=emp, date=day, time=tin, direction="IN", source="manual")
    Attendance.objects.create(employee=emp, date=day, time=tout, direction="OUT", source="manual")
    result = evaluate_day_slots(day, [tin, tout])
    mi = result['slots']['MORNING_IN']
    eo = result['slots']['EVENING_OUT']
    print(
        f"  {emp.registration_number} {day} {tin.strftime('%H:%M')}-{tout.strftime('%H:%M')} "
        f"del={deleted} | {result['status_label']} | IN={mi['status']} OUT={eo['status']} | {result.get('note') or '-'}"
    )

e171 = Employee.objects.filter(registration_number="1010020171").first()
print("=== 1010020171", e171.full_name(), "===")
upsert_day(e171, date(2026, 7, 20), time(8, 10), time(16, 15))
upsert_day(e171, date(2026, 7, 24), time(8, 12), time(16, 18))

e169 = Employee.objects.filter(registration_number="1010020169").first()
print("=== 1010020169", e169.full_name(), "===")
upsert_day(e169, date(2026, 7, 20), time(8, 18), time(16, 20))
upsert_day(e169, date(2026, 7, 24), time(8, 10), time(16, 22))

print()
print("=== VERIF 20-24 ===")
for mat, emp in [("1010020171", e171), ("1010020169", e169)]:
    print(f"\n-- {mat} --")
    for d in (date(2026,7,20), date(2026,7,21), date(2026,7,22), date(2026,7,23), date(2026,7,24)):
        punches = list(Attendance.objects.filter(employee=emp, date=d).order_by("time"))
        times = [t for t in [as_time(p.time) for p in punches] if t]
        if not times:
            print(f"  {d} ABSENT")
            continue
        r = evaluate_day_slots(d, times)
        src = ",".join(sorted({p.source for p in punches}))
        mi = r['slots']['MORNING_IN']
        eo = r['slots']['EVENING_OUT']
        print(f"  {d} {[t.strftime('%H:%M') for t in times]} ({src}) | {r['status_label']} | IN={mi['punch_label']}[{mi['status']}] OUT={eo['punch_label']}[{eo['status']}]")

print("OK_FIX_DONE")
PY
REMOTE
