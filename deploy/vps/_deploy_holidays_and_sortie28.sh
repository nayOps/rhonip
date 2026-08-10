#!/usr/bin/env bash
# Deploy fériés + sortie 28/07 + seed 03/08 sur VPS
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# Prefer OneDrive path when run from WSL/Git Bash
if [ -d "/mnt/c/Users/HYF/OneDrive/Documents/rh-onip" ]; then
  LOCAL="/mnt/c/Users/HYF/OneDrive/Documents/rh-onip"
else
  LOCAL="$ROOT"
fi
VPS='adn@102.68.62.85'
REMOTE='onip-rh'

echo "==> Sync holiday / attendance code"
sshpass -e rsync -avz \
  -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20' \
  "$LOCAL/rh/employee/utils/" \
  "$VPS:~/$REMOTE/rh/employee/utils/"

sshpass -e scp -o StrictHostKeyChecking=no -o ConnectTimeout=20 \
  "$LOCAL/rh/leave/models/holiday.py" \
  "$VPS:~/$REMOTE/rh/leave/models/holiday.py"

sshpass -e scp -o StrictHostKeyChecking=no -o ConnectTimeout=20 \
  "$LOCAL/rh/core/context.py" \
  "$VPS:~/$REMOTE/rh/core/context.py"

sshpass -e rsync -avz \
  -e 'ssh -o StrictHostKeyChecking=no' \
  "$LOCAL/rh/template/employee/includes/company_attendance_registry.html" \
  "$LOCAL/rh/template/components/employee_attendance_panel.html" \
  "$LOCAL/rh/template/employee/daily_attendance_report_pdf.html" \
  "$VPS:~/$REMOTE/rh/template/tmp_holiday_templates/"

sshpass -e ssh -o StrictHostKeyChecking=no "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
mkdir -p rh/template/employee/includes rh/template/components rh/template/employee
cp -f rh/template/tmp_holiday_templates/company_attendance_registry.html rh/template/employee/includes/ 2>/dev/null || true
cp -f rh/template/tmp_holiday_templates/employee_attendance_panel.html rh/template/components/ 2>/dev/null || true
cp -f rh/template/tmp_holiday_templates/daily_attendance_report_pdf.html rh/template/employee/ 2>/dev/null || true
REMOTE

# Better: rsync templates with relative paths
sshpass -e rsync -avz -e 'ssh -o StrictHostKeyChecking=no' \
  "$LOCAL/rh/template/employee/includes/company_attendance_registry.html" \
  "$VPS:~/$REMOTE/rh/template/employee/includes/company_attendance_registry.html"
sshpass -e rsync -avz -e 'ssh -o StrictHostKeyChecking=no' \
  "$LOCAL/rh/template/components/employee_attendance_panel.html" \
  "$VPS:~/$REMOTE/rh/template/components/employee_attendance_panel.html"
sshpass -e rsync -avz -e 'ssh -o StrictHostKeyChecking=no' \
  "$LOCAL/rh/template/employee/daily_attendance_report_pdf.html" \
  "$VPS:~/$REMOTE/rh/template/employee/daily_attendance_report_pdf.html"

sshpass -e rsync -avz -e 'ssh -o StrictHostKeyChecking=no' \
  "$LOCAL/rh/static/assets/css/company-attendance.css" \
  "$LOCAL/rh/static/assets/css/employee-detail.css" \
  "$VPS:~/$REMOTE/rh/static/assets/css/"

echo "==> Restart RH + sync static + seed + sortie"
sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"
$COMPOSE --profile rh up -d --force-recreate rh_server
sleep 25
if [ -x deploy/vps/sync-staticfiles.sh ]; then
  bash deploy/vps/sync-staticfiles.sh || true
fi
echo DEPLOY_CODE_OK
REMOTE

bash "$LOCAL/deploy/vps/_seed_holiday_20260803.sh"
bash "$LOCAL/deploy/vps/_add_sortie_20260728.sh"
echo ALL_DONE
