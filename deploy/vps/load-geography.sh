#!/usr/bin/env bash
# Charge le référentiel cartographique ONIP (province → village) sur le VPS.
# Usage : bash deploy/vps/load-geography.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml)
[[ -f compose/prod.yml ]] && COMPOSE+=(-f compose/prod.yml)
[[ -f compose/prod.vps.yml ]] && COMPOSE+=(-f compose/prod.vps.yml)
[[ -f compose/prod.expose8100.yml ]] && COMPOSE+=(-f compose/prod.expose8100.yml)
COMPOSE+=(--env-file .env)

CARTO_FILE="/app/datas/Onip_Data_Carto/entites_admin.json"

echo "==> Import géographie ONIP (entites_admin.json)..."
"${COMPOSE[@]}" --profile rh exec -T rh_server ls -la "$CARTO_FILE" 2>/dev/null \
  || echo "    ATTENTION: fichier absent dans le conteneur (volume datas/)"
"${COMPOSE[@]}" --profile rh exec -T -w /app/backend rh_server \
  python manage.py load_geography_from_onip --file "$CARTO_FILE"

echo "==> Synchronisation fiches employé (depuis village)..."
"${COMPOSE[@]}" --profile rh exec -T -w /app/backend rh_server \
  python manage.py sync_home_geography_from_village

echo "==> Comptage..."
"${COMPOSE[@]}" --profile rh exec -T -w /app/backend rh_server \
  python manage.py shell -c "
from employee.models import Province, Territory, Sector, Groupement, Village
print('provinces   :', Province.objects.count())
print('territoires :', Territory.objects.count())
print('secteurs    :', Sector.objects.count())
print('groupements :', Groupement.objects.count())
print('villages    :', Village.objects.count())
"

echo "OK"
