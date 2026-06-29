#!/usr/bin/env bash
# Diagnostic référentiel géographique + test API guichet cascade
set -euo pipefail
cd /home/adn/onip-rh

COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"
KEY="${GUICHET_INTERNAL_API_KEY:-fgp_guichet_internal_dev}"

echo "==> Comptages base"
$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py shell -c "
from employee.models import Province, Territory, Sector, Groupement, Village
print('provinces   :', Province.objects.count())
print('territoires :', Territory.objects.count())
print('secteurs    :', Sector.objects.count())
print('groupements :', Groupement.objects.count())
print('villages    :', Village.objects.count())
p = Province.objects.order_by('name').first()
if p:
    print('exemple province:', p.id, p.name)
    t = Territory.objects.filter(province_id=p.id).first()
    if t:
        print('  territoire:', t.id, t.name)
        s = Sector.objects.filter(territory_id=t.id).first()
        if s:
            print('    secteur:', s.id, s.name)
            g = Groupement.objects.filter(sector_id=s.id).first()
            if g:
                print('      groupement:', g.id, g.name)
"

if [[ -n "${1:-}" ]]; then
  PROV_ID="$1"
else
  PROV_ID=$($COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py shell -c \
    "from employee.models import Province; print(Province.objects.order_by('id').values_list('id', flat=True).first() or '')" | tr -d '\r')
fi

if [[ -n "$PROV_ID" ]]; then
  echo ""
  echo "==> API guichet cascade (province_id=$PROV_ID)"
  curl -s -H "X-Guichet-Internal-Key: $KEY" \
    "http://127.0.0.1:8100/api/guichet/geography/?level=territory&province_id=$PROV_ID" | head -c 400
  echo ""
fi
