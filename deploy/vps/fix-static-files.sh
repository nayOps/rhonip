#!/usr/bin/env bash
# Corrige le service des fichiers statiques (CSS/JS) sur le VPS.
set -euo pipefail

REPO="/home/adn/onip-rh"
[[ -d "$REPO" ]] || REPO="$HOME/rhonip"
cd "$REPO"

COMPOSE=(docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env)
RH_PORT="${RH_SERVER_PORT:-8100}"

echo "==> Répertoire: $(pwd)"

touch .env
for kv in \
  STATIC_URL=/static/ \
  MEDIA_URL=/media/ \
  RH_SSL_REDIRECT=0 \
  WHITENOISE_USE_FINDERS=1; do
  key="${kv%%=*}"
  val="${kv#*=}"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
done
echo "    $(grep -E '^(STATIC_URL|MEDIA_URL|RH_SSL_REDIRECT|WHITENOISE_USE_FINDERS)=' .env)"

if [ ! -f rh/static/assets/css/main/app.css ]; then
  echo "ERREUR: rh/static/assets/css/main/app.css absent sur l'hôte"
  echo "       git pull ou copiez le dossier rh/static/"
  exit 1
fi

echo "==> git pull..."
git pull --ff-only 2>/dev/null || echo "    (git pull ignoré)"

echo "==> Rebuild rh_server (no-cache pour forcer collectstatic dans l'image)..."
"${COMPOSE[@]}" --profile rh build --no-cache rh_server
"${COMPOSE[@]}" --profile rh up -d --force-recreate rh_server

echo "==> Attente démarrage..."
sleep 25

echo "==> Diagnostic conteneur..."
"${COMPOSE[@]}" --profile rh exec -T -w /app/backend rh_server python manage.py shell -c "
from django.conf import settings
import os
print('STATIC_URL:', settings.STATIC_URL)
print('WHITENOISE_USE_FINDERS:', settings.WHITENOISE_USE_FINDERS)
root = str(settings.STATIC_ROOT)
src = str(settings.STATICFILES_DIRS[0])
for label, path, rel in (
    ('static source', src, 'assets/css/main/app.css'),
    ('staticfiles', root, 'assets/css/main/app.css'),
):
    print(label + ':', os.path.isfile(os.path.join(path, rel)))
print('staticfiles count:', sum(len(files) for _, _, files in os.walk(root)))
"

echo "==> Tests HTTP..."
CSS_CODE="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${RH_PORT}/static/assets/css/main/app.css")"
JS_CODE="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${RH_PORT}/static/assets/js/bootstrap.js")"
echo "    app.css  → HTTP ${CSS_CODE}"
echo "    bootstrap.js → HTTP ${JS_CODE}"

HREF="$(curl -s "http://127.0.0.1:${RH_PORT}/login/" | grep -o 'href="[^"]*app\.css"' | head -1 || true)"
echo "    login href: ${HREF:-NON TROUVÉ}"

if [ "$CSS_CODE" = "200" ] && [ "$JS_CODE" = "200" ]; then
  echo ""
  echo "OK — Rechargez http://102.68.62.85:${RH_PORT}/login/ avec Ctrl+F5"
else
  echo ""
  echo "ERREUR — Voir les logs:"
  echo "  ${COMPOSE[*]} --profile rh logs rh_server --tail 60"
  exit 1
fi
