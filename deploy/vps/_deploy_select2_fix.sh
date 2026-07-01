#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
B='/mnt/c/Users/HYF/Documents/rh-onip'
VPS='adn@102.68.62.85'

files=(
  rh/template/base.html
  rh/static/autocomplete_light/select2.js
  rh/static/assets/js/onip-form-select2.js
  rh/static/assets/js/employee-detail.js
)

for f in "${files[@]}"; do
  sshpass -e scp -o StrictHostKeyChecking=no "$B/$f" "$VPS:~/onip-rh/$f"
done

sshpass -e ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=no "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"
# template/ et static/ sont montés en lecture seule depuis l'hôte (SCP ci-dessus suffit)
$COMPOSE --profile rh exec -T -w /app/backend rh_server sh -c '
cp -f static/autocomplete_light/select2.js staticfiles/autocomplete_light/select2.js
cp -f static/assets/js/onip-form-select2.js staticfiles/assets/js/onip-form-select2.js
cp -f static/assets/js/employee-detail.js staticfiles/assets/js/employee-detail.js
cp -f static/autocomplete_light/i18n/fr.js staticfiles/autocomplete_light/i18n/fr.js
'
$COMPOSE --profile rh restart rh_server
echo "OK deploy select2 fix"
REMOTE
