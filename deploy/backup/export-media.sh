#!/usr/bin/env bash
# Exporte les volumes média RH (photos, fichiers uploadés).
#
# Usage local :
#   ./deploy/backup/export-media.sh
#
# Produit : deploy/backups/onip_media_YYYYMMDD_HHMMSS.tar.gz

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$REPO_ROOT/deploy/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT="$BACKUP_DIR/onip_media_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

RH_CONTAINER="${ONIP_RH_CONTAINER:-rh_server}"
if docker ps --format '{{.Names}}' | grep -qx "$RH_CONTAINER"; then
  echo "==> Export média depuis $RH_CONTAINER..."
  docker exec "$RH_CONTAINER" tar czf - -C /app/backend media 2>/dev/null > "$OUTPUT" || true
fi

if [[ ! -s "$OUTPUT" ]]; then
  echo "Aucun média dans le conteneur — export depuis volume Docker..."
  VOLUME="$(docker volume ls --format '{{.Name}}' | grep -E 'rh_media|onip.*media' | head -1 || true)"
  if [[ -n "$VOLUME" ]]; then
    docker run --rm -v "${VOLUME}:/data:ro" -v "$BACKUP_DIR:/backup" alpine \
      tar czf "/backup/onip_media_${TIMESTAMP}.tar.gz" -C /data .
    OUTPUT="$BACKUP_DIR/onip_media_${TIMESTAMP}.tar.gz"
  else
    echo "Aucun volume média trouvé — rien à exporter."
    exit 0
  fi
fi

echo "==> Sauvegarde média : $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
