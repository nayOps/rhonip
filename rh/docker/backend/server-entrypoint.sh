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

CSS_FILE="/app/backend/staticfiles/assets/css/main/app.css"
SRC_CSS="/app/backend/static/assets/css/main/app.css"

echo "==> collectstatic..."
if [ -f "$CSS_FILE" ]; then
    echo "==> static deja present, skip collectstatic"
else
    python manage.py collectstatic --noinput
fi

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

WORKERS="${GUNICORN_WORKERS:-4}"
THREADS="${GUNICORN_THREADS:-2}"
TIMEOUT="${GUNICORN_TIMEOUT:-90}"
WORKER_CLASS="${GUNICORN_WORKER_CLASS:-gthread}"

echo "==> gunicorn workers=${WORKERS} class=${WORKER_CLASS} threads=${THREADS} timeout=${TIMEOUT}"

exec gunicorn payday.wsgi --bind 0.0.0.0:8000 \
  --workers "$WORKERS" \
  --worker-class "$WORKER_CLASS" \
  --threads "$THREADS" \
  --timeout "$TIMEOUT" \
  --graceful-timeout 30 \
  --max-requests 1000 \
  --max-requests-jitter 100
