#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
B='/mnt/c/Users/HYF/Documents/rh-onip'
VPS='adn@102.68.62.85'

sshpass -e scp -o StrictHostKeyChecking=no \
  "$B/rh/employee/forms.py" \
  "$B/rh/static/assets/css/onip-forms.css" \
  "$VPS:~/onip-rh/rh/employee/forms.py" \
  "$VPS:~/onip-rh/rh/static/assets/css/onip-forms.css" 2>/dev/null || {
  sshpass -e scp -o StrictHostKeyChecking=no "$B/rh/employee/forms.py" "$VPS:~/onip-rh/rh/employee/forms.py"
  sshpass -e scp -o StrictHostKeyChecking=no "$B/rh/static/assets/css/onip-forms.css" "$VPS:~/onip-rh/rh/static/assets/css/onip-forms.css"
}

sshpass -e ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=no "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"
$COMPOSE --profile rh cp rh/employee/forms.py rh_server:/app/backend/employee/forms.py
$COMPOSE --profile rh exec -T -w /app/backend rh_server sh -c '
cp -f static/assets/css/onip-forms.css staticfiles/assets/css/onip-forms.css
'
$COMPOSE --profile rh restart rh_server
echo OK locked fields deploy
REMOTE
