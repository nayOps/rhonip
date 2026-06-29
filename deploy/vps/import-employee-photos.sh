#!/bin/bash
# Importe les photos employés dans le volume media du conteneur RH
set -euo pipefail
cd /home/adn/onip-rh
ARCHIVE="${1:-/home/adn/onip-rh/deploy/backups/onip_employee_photos.tar.gz}"

if [ ! -f "$ARCHIVE" ]; then
  echo "Archive introuvable: $ARCHIVE"
  exit 1
fi

echo "=== extraction dans le volume media ==="
docker cp "$ARCHIVE" onip_rh_server:/tmp/onip_employee_photos.tar.gz
docker exec onip_rh_server bash -c '
  set -e
  mkdir -p /app/backend/media
  tar xzf /tmp/onip_employee_photos.tar.gz -C /app/backend/media
  rm -f /tmp/onip_employee_photos.tar.gz
  echo "jpg count: $(find /app/backend/media -maxdepth 1 -type f -name "*.jpg" | wc -l)"
'

echo ""
echo "=== test URL media ==="
PHOTO=$(docker exec onip_postgres psql -U onip_user -d onip_db -t -A -c "SELECT photo FROM employee_employee WHERE photo IS NOT NULL AND photo <> '' LIMIT 1;")
PHOTO=$(echo "$PHOTO" | tr -d '[:space:]')
echo "photo=$PHOTO"
curl -s -o /dev/null -w "GET /media/$PHOTO => %{http_code}\n" "http://127.0.0.1:8100/media/$PHOTO"
