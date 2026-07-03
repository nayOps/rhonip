#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
: "${GITHUB_TOKEN:?GITHUB_TOKEN requis}"
VPS='adn@102.68.62.85'

sshpass -e ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=no "$VPS" bash -s <<REMOTE
set -euo pipefail
cd ~/onip-rh
REMOTE_URL="https://nayOps:${GITHUB_TOKEN}@github.com/nayOps/rhonip.git"

echo "== git pull =="
git fetch "\$REMOTE_URL" main
git reset --hard FETCH_HEAD
git log -1 --oneline

COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

echo "== copie modules pointage =="
\$COMPOSE --profile rh cp rh/employee/utils/attendance_slots.py rh_server:/app/backend/employee/utils/attendance_slots.py
\$COMPOSE --profile rh cp rh/employee/utils/attendance_schedule_config.py rh_server:/app/backend/employee/utils/attendance_schedule_config.py
\$COMPOSE --profile rh cp rh/employee/services/attendance_punch.py rh_server:/app/backend/employee/services/attendance_punch.py
\$COMPOSE --profile rh cp rh/api/views/attendance_device.py rh_server:/app/backend/api/views/attendance_device.py

echo "== restart rh_server =="
\$COMPOSE --profile rh restart rh_server

sleep 8
echo "== tests règles pointage =="
\$COMPOSE --profile rh exec -T rh_server python manage.py test employee.tests_attendance_punch -v 1

echo OK
REMOTE
