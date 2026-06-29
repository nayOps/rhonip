#!/usr/bin/env bash
# A lancer SUR le VPS apres : ssh adn@102.68.62.85
#   cd /home/adn/onip-rh && bash deploy/vps/fix-guichet-key-manual.sh

set -euo pipefail

KEY="${GUICHET_INTERNAL_API_KEY:-fgp_guichet_internal_dev}"
RH_PORT="${RH_SERVER_PORT:-8100}"

for d in /home/adn/onip-rh /home/adn/rhonip ~/onip-rh ~/rhonip; do
  if [[ -f "$d/.env" ]]; then
    cd "$d"
    break
  fi
done

if [[ ! -f .env ]]; then
  echo "ERREUR: .env introuvable. cd vers le clone onip-rh puis relancez."
  exit 1
fi

echo "==> Repertoire : $(pwd)"
echo "==> Avant :"
grep '^GUICHET_INTERNAL_API_KEY=' .env || true

if grep -q '^GUICHET_INTERNAL_API_KEY=' .env; then
  sed -i "s|^GUICHET_INTERNAL_API_KEY=.*|GUICHET_INTERNAL_API_KEY=${KEY}|" .env
else
  echo "GUICHET_INTERNAL_API_KEY=${KEY}" >> .env
fi

echo "==> Apres :"
grep '^GUICHET_INTERNAL_API_KEY=' .env

COMPOSE=( -f docker-compose.yml )
[[ -f compose/prod.yml ]] && COMPOSE+=( -f compose/prod.yml )
[[ -f compose/prod.vps.yml ]] && COMPOSE+=( -f compose/prod.vps.yml )

echo "==> Redemarrage rh_server..."
docker compose "${COMPOSE[@]}" --env-file .env --profile rh up -d --force-recreate rh_server

echo "==> Attente 15 s..."
sleep 15

HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "X-Guichet-Internal-Key: ${KEY}" \
  "http://127.0.0.1:${RH_PORT}/api/guichet/employees/?page=1&page_size=1")

echo "==> Test guichet : HTTP ${HTTP}"
if [[ "$HTTP" == "200" ]]; then
  echo "OK — retournez sur le PC guichet et lancez :"
  echo "  docker compose --profile register up -d --force-recreate frontend"
else
  echo "ERREUR — logs : docker logs rh_server --tail 50"
  exit 1
fi
