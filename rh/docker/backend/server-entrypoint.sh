#!/bin/sh
set -e

until cd /app/backend
do
    echo "Waiting for server volume..."
done

until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

echo "==> collectstatic..."
python manage.py collectstatic --noinput --clear

CSS_FILE="/app/backend/staticfiles/assets/css/main/app.css"
SRC_CSS="/app/backend/static/assets/css/main/app.css"
if [ ! -f "$CSS_FILE" ] && [ -f "$SRC_CSS" ]; then
    echo "WARN: staticfiles vide, copie de secours depuis static/"
    mkdir -p /app/backend/staticfiles
    cp -a /app/backend/static/. /app/backend/staticfiles/
fi

if [ ! -f "$CSS_FILE" ] && [ ! -f "$SRC_CSS" ]; then
    echo "ERREUR: CSS introuvable (staticfiles et static/)"
    ls -la /app/backend/static/assets/css/main/ 2>&1 || true
    exit 1
fi

echo "==> static OK: $(find /app/backend/staticfiles -type f 2>/dev/null | wc -l) fichiers"

exec gunicorn payday.wsgi --bind 0.0.0.0:8000 --workers 2 --timeout 120 --graceful-timeout 30
