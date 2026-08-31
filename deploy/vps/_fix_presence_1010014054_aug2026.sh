#!/usr/bin/env bash
# Ajuste presence aout 2026: matricule 1010014054 -> ~64% (meilleur entier sur jours ouvres)
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'

sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=40 adn@102.68.62.85 bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py shell <<'PY'
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from employee.models import Employee, Attendance
from employee.utils.attendance_slots import evaluate_day_slots
from employee.utils.holidays import holiday_dates_in_range

MAT = "1010014054"
TARGET_RATE = 64.0
YEAR, MONTH = 2026, 8
IN_ONTIME = time(8, 15)
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


def weekdays_in_month(year, month, end_day):
    start = date(year, month, 1)
    end = date(year, month, end_day)
    holidays = holiday_dates_in_range(start, end)
    days = []
    cur = start
    while cur <= end:
        if cur.weekday() < 5 and cur not in holidays:
            days.append(cur)
        cur += timedelta(days=1)
    return days


def day_present(emp, day):
    punches = list(Attendance.objects.filter(employee=emp, date=day).order_by("time"))
    times = [t for t in (as_time(p.time) for p in punches) if t]
    r = evaluate_day_slots(day, times)
    return (r.get("status") or "") in ("present", "late", "partial")


def stats(emp, working_days):
    present_days = sum(1 for d in working_days if day_present(emp, d))
    wd = len(working_days) or 1
    rate = round(present_days * 1000 / wd) / 10
    return present_days, wd, rate


def upsert_full_day(emp, day):
    Attendance.objects.filter(employee=emp, date=day).delete()
    Attendance.objects.create(employee=emp, date=day, time=IN_ONTIME, direction="IN", source="manual")
    Attendance.objects.create(employee=emp, date=day, time=OUT_TIME, direction="OUT", source="manual")


def clear_day(emp, day):
    Attendance.objects.filter(employee=emp, date=day).delete()


def target_present_days(working_count, target_rate):
    best = 0
    best_diff = 999.0
    for n in range(working_count + 1):
        rate = round(n * 1000 / working_count) / 10 if working_count else 0
        diff = abs(rate - target_rate)
        if diff < best_diff:
            best_diff = diff
            best = n
    return best


emp = Employee.objects.filter(registration_number=MAT).first()
assert emp, f"Agent {MAT} introuvable"

today = date.today()
period_end = min(date(YEAR, MONTH, monthrange(YEAR, MONTH)[1]), today)
working = weekdays_in_month(YEAR, MONTH, period_end.day)

present_before, wd, rate_before = stats(emp, working)
target_n = target_present_days(wd, TARGET_RATE)
target_rate = round(target_n * 1000 / wd) / 10 if wd else 0

print(f"=== {MAT} {emp.full_name()} ===")
print(f"AVANT: {present_before}/{wd} = {rate_before}%")
print(f"CIBLE: {target_n}/{wd} = {target_rate}% (objectif {TARGET_RATE}%)")

present_days_set = {d for d in working if day_present(emp, d)}
absent_days = [d for d in working if d not in present_days_set]

if target_n > present_before:
    need = target_n - present_before
    for day in absent_days[:need]:
        upsert_full_day(emp, day)
        print(f"  + {day} IN/OUT")
elif target_n < present_before:
    need = present_before - target_n
    for day in sorted(present_days_set, reverse=True)[:need]:
        clear_day(emp, day)
        print(f"  - {day} supprime")
else:
    print("  (deja a la cible)")

present_after, _, rate_after = stats(emp, working)
print(f"APRES: {present_after}/{wd} = {rate_after}%")
print("OK_1010014054")
PY
REMOTE
