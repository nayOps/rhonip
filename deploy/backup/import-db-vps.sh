#!/usr/bin/env bash
# Restaure un dump PostgreSQL sur le VPS (après démarrage de onip_postgres).
#
# Usage sur le VPS :
#   cd /home/adn/onip-rh
#   ./deploy/backup/import-db-vps.sh deploy/backups/onip_rh_YYYYMMDD_HHMMSS.sql.gz
#
# ATTENTION : écrase la base existante du conteneur onip_postgres.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage : $0 <fichier.sql.gz>" >&2
  exit 1
fi

DUMP_FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [[ ! -f "$DUMP_FILE" ]]; then
  echo "Fichier introuvable : $DUMP_FILE" >&2
  exit 1
fi

if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.env"
  set +a
fi

POSTGRES_DB="${POSTGRES_DB:-onip_db}"
POSTGRES_USER="${POSTGRES_USER:-onip_user}"
CONTAINER="${ONIP_POSTGRES_CONTAINER:-onip_postgres}"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "ERREUR : démarrez d'abord la stack : ./deploy/vps/bootstrap.sh" >&2
  exit 1
fi

echo "==> Restauration de $DUMP_FILE dans $CONTAINER ($POSTGRES_DB)..."
echo "    (écrasement des données actuelles)"
read -r -p "Continuer ? [o/N] " confirm
if [[ "${confirm,,}" != "o" && "${confirm,,}" != "oui" ]]; then
  echo "Annulé."
  exit 0
fi

if [[ "$DUMP_FILE" == *.gz ]]; then
  gunzip -c "$DUMP_FILE" | docker exec -i -e PGCLIENTENCODING=UTF8 "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1
else
  docker exec -i -e PGCLIENTENCODING=UTF8 "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 < "$DUMP_FILE"
fi

echo "==> Restauration terminée."
echo "    Redémarrez RH : docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml restart rh_server rh_worker"
