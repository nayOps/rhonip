#!/usr/bin/env bash
# Installation initiale ONIP RH sur VPS (isolé de la stack Présidence cpnpr).
# Usage (sur le VPS, en tant qu'adn) :
#   git clone git@github.com:ORG/rh-onip.git /home/adn/onip-rh
#   cd /home/adn/onip-rh
#   cp deploy/vps/env.prod.template .env
#   nano .env
#   bash deploy/vps/install.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

CPNPR_TRAEFIK_DYNAMIC="${CPNPR_TRAEFIK_DYNAMIC:-/home/adn/cpnpr/docker/traefik/config/dynamic}"
ONIP_DOMAIN="${ONIP_DOMAIN:-rh.onip.gouv.cd}"

echo "==> Vérification réseau Traefik (proxy)..."
if ! docker network inspect proxy >/dev/null 2>&1; then
  echo "ERREUR: le réseau Docker 'proxy' est absent. La stack cpnpr/Traefik doit tourner."
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "ERREUR: fichier .env manquant. Copiez deploy/vps/env.prod.template vers .env"
  exit 1
fi

echo "==> Route Traefik ONIP..."
if [[ -d "$CPNPR_TRAEFIK_DYNAMIC" ]]; then
  install -m 644 deploy/traefik/onip-rh.yml "$CPNPR_TRAEFIK_DYNAMIC/onip-rh.yml"
  echo "    Copié → $CPNPR_TRAEFIK_DYNAMIC/onip-rh.yml"
else
  echo "ATTENTION: dossier Traefik introuvable ($CPNPR_TRAEFIK_DYNAMIC)"
  echo "    Copiez manuellement deploy/traefik/onip-rh.yml"
fi

echo "==> Build et démarrage (profils rh + prod)..."
docker compose --profile rh --profile prod up -d --build

echo "==> État des conteneurs ONIP..."
docker compose --profile rh --profile prod ps

echo ""
echo "Terminé."
echo "  - URL RH : https://${ONIP_DOMAIN}"
echo "  - Vérifiez le DNS : ${ONIP_DOMAIN} → IP publique du VPS"
echo "  - Ne jamais exécuter 'docker compose down -v' sur cpnpr (Présidence)."
