#!/usr/bin/env bash
# Prépare le push GitHub : export BD + vérifie les fichiers clés.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "==> Export base de données..."
if [[ -f deploy/backup/export-db.sh ]]; then
  bash deploy/backup/export-db.sh
  # Copie vers le nom fixe versionné
  LATEST="$(ls -t deploy/backups/onip_rh_*.sql.gz 2>/dev/null | head -1 || true)"
  if [[ -n "$LATEST" ]]; then
    gunzip -c "$LATEST" > deploy/backups/onip_rh_production.sql
    echo "==> Dump GitHub : deploy/backups/onip_rh_production.sql"
  fi
else
  echo "Lancez : .\\deploy\\backup\\export-db.ps1 (Windows)"
fi

echo ""
echo "==> Fichiers prêts pour GitHub :"
echo "  - Code : rh/, register/, compose/, deploy/, attendanceapk/"
echo "  - Dump : deploy/backups/onip_rh_production.sql"
echo "  - Exclus : .env, agents/, node_modules/, build/"
echo ""
if command -v git >/dev/null 2>&1; then
  git status -sb 2>/dev/null || echo "(git non initialisé — en attente de votre remote GitHub)"
fi
