#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
: "${GITHUB_TOKEN:?GITHUB_TOKEN required}"

sed 's/\r$//' "$(dirname "$0")/_vps_git_pull_now.sh" | \
  timeout 240 sshpass -e ssh -o StrictHostKeyChecking=no adn@102.68.62.85 \
  "GITHUB_TOKEN='${GITHUB_TOKEN}' bash -s"

sshpass -e ssh -o StrictHostKeyChecking=no adn@102.68.62.85 bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
bash deploy/vps/sync-staticfiles.sh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"
echo "==> generate presence segment PDFs (aout 2026)"
$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py generate_presence_segment_reports --year 2026 --month 8
echo "==> PDF count"
ls -1 deploy/vps/reports/rapport-rh-onip-statistiques-presence-2026-08-*.pdf 2>/dev/null | wc -l
ls -lh deploy/vps/reports/rapport-rh-onip-statistiques-presence-2026-08-*.pdf 2>/dev/null | head -15
REMOTE

echo "DEPLOY_SEGMENT_REPORTS_OK"
