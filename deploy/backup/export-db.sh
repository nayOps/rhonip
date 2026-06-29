#!/usr/bin/env bash
# Exporte la base PostgreSQL ONIP locale (agents, comptes, paie, présences…).
# Les fichiers générés restent HORS GitHub (voir deploy/backups/.gitignore).
#
# Usage (PC local, WSL ou Git Bash) :
#   cd rh-onip
#   ./deploy/backup/export-db.sh
#
# Produit : deploy/backups/onip_rh_YYYYMMDD_HHMMSS.sql.gz

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$REPO_ROOT/deploy/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT="$BACKUP_DIR/onip_rh_production.sql.gz"
OUTPUT_SQL="$BACKUP_DIR/onip_rh_production.sql"

mkdir -p "$BACKUP_DIR"

# Charger .env si présent
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
  echo "ERREUR : conteneur '$CONTAINER' non démarré." >&2
  echo "Lancez d'abord : docker compose --profile rh up -d" >&2
  exit 1
fi

echo "==> Export PostgreSQL ($POSTGRES_DB) depuis $CONTAINER..."
docker exec "$CONTAINER" pg_dump \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  | gzip > "$OUTPUT"

SIZE="$(du -h "$OUTPUT" | cut -f1)"
gunzip -c "$OUTPUT" > "$OUTPUT_SQL"
echo "==> Sauvegarde créée : $OUTPUT ($SIZE)"
echo "==> Dump GitHub      : $OUTPUT_SQL"
