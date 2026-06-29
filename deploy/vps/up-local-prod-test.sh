#!/usr/bin/env bash
# Test local mode production (DEBUG=0, sans montages code, port 8100 pour tablettes).
#
# Usage :
#   ./deploy/vps/up-local-prod-test.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Créé .env depuis .env.example — ajustez les valeurs si besoin."
fi

docker compose \
  -f docker-compose.yml \
  -f compose/prod.yml \
  -f compose/prod.local.yml \
  --profile rh up -d --build

echo ""
echo "Stack RH prod-test démarrée."
LAN_IP="$(grep -E '^SERVER_LAN_IP=' .env 2>/dev/null | cut -d= -f2 || true)"
LAN_IP="${LAN_IP:-localhost}"
echo "  API tablettes : http://${LAN_IP}:8100"
echo "  Interface web : http://${LAN_IP}:8100/login/"
