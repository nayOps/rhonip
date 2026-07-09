#!/usr/bin/env bash
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'

sshpass -e ssh -o StrictHostKeyChecking=no adn@102.68.62.85 bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

echo "==> restart rh_server"
$COMPOSE --profile rh restart rh_server
sleep 20

echo "==> status"
$COMPOSE --profile rh ps rh_server
curl -sS -o /dev/null -w "login %{http_code}\n" http://127.0.0.1:8100/login/
REMOTE
