#!/usr/bin/env bash
# Bootstrap ONIP RH sur le VPS (isolation complète de cpnpr/Présidence).
#
# Usage :
#   cd /home/adn/onip-rh
#   ./deploy/vps/bootstrap.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "==> Vérification Docker..."
docker info >/dev/null

echo "==> Vérification réseau proxy (cpnpr)..."
if ! docker network inspect proxy >/dev/null 2>&1; then
  echo "ERREUR : le réseau Docker 'proxy' n'existe pas." >&2
  echo "Démarrez d'abord le stack cpnpr (Traefik Présidence)." >&2
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "==> Génération .env depuis .env.prod.example..."
  bash deploy/env-gen.sh .env.prod.example .env
  echo ""
  echo "IMPORTANT : éditez .env et remplacez les valeurs __A_DEFINIR__ avant de continuer."
  echo "Puis relancez : ./deploy/vps/bootstrap.sh"
  exit 0
fi

echo "==> Installation route Traefik ONIP..."
bash deploy/vps/install-traefik-route.sh

echo "==> Build et démarrage stack RH (production VPS)..."
docker compose \
  -f docker-compose.yml \
  -f compose/prod.yml \
  -f compose/prod.vps.yml \
  --profile rh up -d --build

BACKUP_DIR="$REPO_ROOT/deploy/backups"
LATEST_DUMP="$REPO_ROOT/deploy/backups/onip_rh_production.sql"
if [[ ! -f "$LATEST_DUMP" ]]; then
  LATEST_DUMP="$(ls -t "$BACKUP_DIR"/onip_rh_*.sql.gz 2>/dev/null | head -1 || true)"
fi
if [[ -n "$LATEST_DUMP" && -f "$LATEST_DUMP" ]]; then
  echo ""
  read -r -p "Restaurer la sauvegarde $LATEST_DUMP ? [o/N] " restore
  if [[ "${restore,,}" == "o" || "${restore,,}" == "oui" ]]; then
    bash deploy/backup/import-db-vps.sh "$LATEST_DUMP"
  fi
fi

echo ""
echo "==> Déploiement terminé."
echo "    URL : https://rh.onip.gouv.cd"
echo "    Logs : docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml logs -f rh_server"
echo ""
echo "    NE PAS exécuter 'docker compose down -v' sur cpnpr."
