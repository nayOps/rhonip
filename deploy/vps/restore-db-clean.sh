#!/usr/bin/env bash
# Restauration propre : recrée onip_db puis importe le dump production.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

DUMP="${1:-deploy/backups/onip_rh_production.sql}"
COMPOSE=(docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml)

source .env 2>/dev/null || true
USER="${POSTGRES_USER:-onip_user}"
DB="${POSTGRES_DB:-onip_db}"

[[ -f "$DUMP" ]] || { echo "Dump introuvable: $DUMP" >&2; exit 1; }

echo "==> Arrêt RH..."
"${COMPOSE[@]}" stop rh_server rh_worker 2>/dev/null || true

echo "==> Recréation base $DB..."
docker exec onip_postgres psql -U "$USER" -d postgres -v ON_ERROR_STOP=1 <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${DB}' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${DB};
CREATE DATABASE ${DB} OWNER ${USER} ENCODING 'UTF8';
SQL

echo "==> Import $DUMP ..."
docker exec -i onip_postgres psql -U "$USER" -d "$DB" -v ON_ERROR_STOP=1 < "$DUMP"

echo "==> Redémarrage RH..."
"${COMPOSE[@]}" start rh_server rh_worker

echo "==> Restauration terminée."
