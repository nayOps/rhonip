#!/usr/bin/env bash
# Exécution complète sur le VPS : clé guichet + cartographie + rebuild RH
set -euo pipefail

REPO="/home/adn/onip-rh"
[[ -d "$REPO" ]] || REPO="$HOME/rhonip"
cd "$REPO"

COMPOSE=(docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env)
KEY="${GUICHET_INTERNAL_API_KEY:-fgp_guichet_internal_dev}"
RH_PORT="${RH_SERVER_PORT:-8100}"

echo "==> Répertoire: $(pwd)"

if [[ -f .env ]]; then
  if grep -q '^GUICHET_INTERNAL_API_KEY=' .env; then
    sed -i "s|^GUICHET_INTERNAL_API_KEY=.*|GUICHET_INTERNAL_API_KEY=${KEY}|" .env
  else
    echo "GUICHET_INTERNAL_API_KEY=${KEY}" >> .env
  fi
  echo "    $(grep '^GUICHET_INTERNAL_API_KEY=' .env)"
fi

echo "==> git pull (si possible)..."
git pull --ff-only 2>/dev/null || echo "    (git pull ignoré)"

touch .env
for kv in STATIC_URL=/static/ MEDIA_URL=/media/ RH_SSL_REDIRECT=0; do
  key="${kv%%=*}"
  val="${kv#*=}"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
done
echo "    $(grep -E '^(STATIC_URL|MEDIA_URL|RH_SSL_REDIRECT)=' .env)"

echo "==> Import cartographie ONIP..."
if [[ -f deploy/vps/load-geography.sh ]]; then
  bash deploy/vps/load-geography.sh
else
  "${COMPOSE[@]}" --profile rh exec -T -w /app/backend rh_server \
    python manage.py load_geography_from_onip
fi

echo "==> Rebuild / redémarrage rh_server..."
"${COMPOSE[@]}" --profile rh up -d --build rh_server

echo "==> Attente démarrage..."
sleep 18

echo "==> Tests..."
curl -s -o /dev/null -w "    login RH: HTTP %{http_code}\n" "http://127.0.0.1:${RH_PORT}/login/"
curl -s -o /dev/null -w "    static CSS: HTTP %{http_code}\n" "http://127.0.0.1:${RH_PORT}/static/assets/css/main/app.css"
curl -s -o /dev/null -w "    guichet API: HTTP %{http_code}\n" \
  -H "X-Guichet-Internal-Key: ${KEY}" \
  "http://127.0.0.1:${RH_PORT}/api/guichet/employees/?page=1&page_size=1"

"${COMPOSE[@]}" --profile rh exec -T -w /app/backend rh_server python manage.py shell -c "
from employee.models import Province, Village
print('    provinces:', Province.objects.count(), '| villages:', Village.objects.count())
" 2>/dev/null || true

echo ""
echo "OK — guichet local : docker compose --profile register up -d --force-recreate frontend"
