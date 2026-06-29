#!/bin/bash
# Corrige CSRF 403 sur http://IP:8100 puis redémarre rh_server
set -euo pipefail
cd /home/adn/onip-rh

echo "=== .env CSRF/SSL ==="
grep -q '^RH_SSL_REDIRECT=' .env && sed -i 's/^RH_SSL_REDIRECT=.*/RH_SSL_REDIRECT=0/' .env || echo 'RH_SSL_REDIRECT=0' >> .env
grep -q '^SERVER_LAN_IP=' .env && sed -i 's/^SERVER_LAN_IP=.*/SERVER_LAN_IP=102.68.62.85/' .env || echo 'SERVER_LAN_IP=102.68.62.85' >> .env
sed -i 's|^RH_CSRF_TRUSTED_ORIGINS=.*|RH_CSRF_TRUSTED_ORIGINS=https://rh.onip.gouv.cd,http://rh.onip.gouv.cd,http://102.68.62.85:8100,http://102.68.62.85|' .env
grep -E '^(RH_SSL|RH_CSRF|SERVER_LAN)' .env

SETTINGS=/home/adn/onip-rh/rh/payday/settings.py
if ! grep -q '_build_csrf_trusted_origins' "$SETTINGS"; then
  echo "WARN: settings.py local pas à jour — git pull ou copier rh/payday/settings.py"
fi

COMPOSE_FILES="-f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml"
if [ -f compose/prod.fix-timeout.yml ]; then
  COMPOSE_FILES="$COMPOSE_FILES -f compose/prod.fix-timeout.yml"
fi

docker compose $COMPOSE_FILES --env-file .env --profile rh up -d --build rh_server
echo "Attente démarrage (60s)..."
sleep 60

echo ""
echo "=== Django settings ==="
docker exec onip_rh_server python /app/backend/manage.py shell -c "
from django.conf import settings
print('CSRF_COOKIE_SECURE', settings.CSRF_COOKIE_SECURE)
print('CSRF_TRUSTED_ORIGINS', settings.CSRF_TRUSTED_ORIGINS)
print('SECURE_SSL_REDIRECT', settings.SECURE_SSL_REDIRECT)
print('SECURE_PROXY_SSL_HEADER', getattr(settings, 'SECURE_PROXY_SSL_HEADER', None))
"

echo ""
echo "=== POST login test ==="
rm -f /tmp/cj_fix /tmp/login_fix.html /tmp/post_fix.html
curl -sL -c /tmp/cj_fix -b /tmp/cj_fix http://102.68.62.85:8100/login/ -o /tmp/login_fix.html
TOKEN=$(python3 -c "import re; print(re.search(r'name=\"csrfmiddlewaretoken\" value=\"([^\"]+)\"', open('/tmp/login_fix.html').read()).group(1))")
curl -sL -c /tmp/cj_fix -b /tmp/cj_fix -X POST http://102.68.62.85:8100/login/ \
  -H 'Referer: http://102.68.62.85:8100/login/' \
  -H 'Origin: http://102.68.62.85:8100' \
  --data-urlencode "csrfmiddlewaretoken=$TOKEN" \
  --data-urlencode 'username=admin@onip.local' \
  --data-urlencode 'password=OnipAdmin2025!' \
  -o /tmp/post_fix.html -w 'POST %{http_code} redirect:%{redirect_url}\n'
grep -oE '<title>[^<]+</title>|CSRF|Interdit|403' /tmp/post_fix.html | head -3 || true
