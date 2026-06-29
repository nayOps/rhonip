#!/bin/bash
# Démarre le guichet register (FGP) sur le VPS — profil register + rh déjà actif
set -euo pipefail
cd /home/adn/onip-rh

set_port() { grep -q "^$1=" .env && sed -i "s/^$1=.*/$1=$2/" .env || echo "$1=$2" >> .env; }
set_port FGP_CORE_PORT 8200
set_port ENROLLMENT_GATEWAY_PORT 8201
set_port FGP_FRONTEND_PORT 8300
set_port FINGERPRINT_SERVICE_PORT 8210

COMPOSE="-f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml"
[ -f compose/prod.expose8100.yml ] && COMPOSE="$COMPOSE -f compose/prod.expose8100.yml"
[ -f compose/prod.fix-timeout.yml ] && COMPOSE="$COMPOSE -f compose/prod.fix-timeout.yml"

echo "=== Démarrage register (build peut prendre plusieurs minutes) ==="
docker compose $COMPOSE --env-file .env --profile rh --profile register up -d --build \
  fgp_core enrollment_gateway enrollment_worker fingerprint_service frontend fgp_nginx

echo ""
echo "=== État des services ==="
docker compose $COMPOSE --profile rh --profile register ps

echo ""
echo "=== URLs (LAN) ==="
IP="${SERVER_LAN_IP:-102.68.62.85}"
echo "  Guichet register : http://${IP}:${FGP_FRONTEND_PORT:-8300}"
echo "  API gateway      : http://${IP}:${ENROLLMENT_GATEWAY_PORT:-8201}"
echo "  FGP core         : http://${IP}:${FGP_CORE_PORT:-8200}"
echo "  RH (référence)   : http://${IP}:${RH_SERVER_PORT:-8100}"
