#!/usr/bin/env bash
# Aligne la cle guichet RH / register (valeur dev par defaut).
# Usage local : bash deploy/vps/align-guichet-key.sh
# Usage VPS   : ssh adn@102.68.62.85 "cd /home/adn/onip-rh && bash deploy/vps/align-guichet-key.sh"

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DEV_KEY="${GUICHET_INTERNAL_API_KEY:-fgp_guichet_internal_dev}"
RH_PORT="${RH_SERVER_PORT:-8100}"

if [[ ! -f .env ]]; then
  echo "ERREUR: .env absent dans $ROOT"
  exit 1
fi

if grep -q '^GUICHET_INTERNAL_API_KEY=' .env; then
  sed -i "s|^GUICHET_INTERNAL_API_KEY=.*|GUICHET_INTERNAL_API_KEY=${DEV_KEY}|" .env
else
  echo "GUICHET_INTERNAL_API_KEY=${DEV_KEY}" >> .env
fi

echo "==> GUICHET_INTERNAL_API_KEY=${DEV_KEY}"

COMPOSE=( -f docker-compose.yml )
[[ -f compose/prod.yml ]] && COMPOSE+=( -f compose/prod.yml )
[[ -f compose/prod.vps.yml ]] && COMPOSE+=( -f compose/prod.vps.yml )
[[ -f compose/prod.expose8100.yml ]] && COMPOSE+=( -f compose/prod.expose8100.yml )

echo "==> Redemarrage rh_server (applique la nouvelle cle)..."
docker compose "${COMPOSE[@]}" --env-file .env --profile rh up -d --force-recreate rh_server

echo "==> Attente demarrage RH..."
sleep 12

echo "==> Test API guichet..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "X-Guichet-Internal-Key: ${DEV_KEY}" \
  "http://127.0.0.1:${RH_PORT}/api/guichet/employees/?page=1&page_size=1")

echo "    HTTP ${HTTP_CODE}"
if [[ "$HTTP_CODE" != "200" ]]; then
  echo "ERREUR: attendu HTTP 200 — verifiez les logs : docker logs rh_server --tail 40"
  exit 1
fi

echo ""
echo "OK — sur le poste guichet Windows :"
echo "  GUICHET_INTERNAL_API_KEY=${DEV_KEY}"
echo "  docker compose --profile register up -d --force-recreate frontend"
