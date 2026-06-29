#!/bin/bash
# Corrige les accents corrompus en base (Employ├⌐ → Employé)
set -euo pipefail
cd /home/adn/onip-rh
docker exec onip_rh_server python /app/backend/manage.py fix_text_encoding
echo "=== menus ==="
docker exec onip_postgres psql -U onip_user -d onip_db -c "SELECT id, name FROM core_menu ORDER BY id;"
