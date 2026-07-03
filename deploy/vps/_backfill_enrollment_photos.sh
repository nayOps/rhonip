#!/usr/bin/env bash
# Déploie le correctif photo + finalise les sessions FAILED/PENDING avec photo.
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
VPS='adn@102.68.62.85'
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REMOTE_BASE='~/onip-rh/register/backend/enrollment_gateway/apps/enrollment'

echo "=== Copie des fichiers vers le VPS ==="
sshpass -e ssh -o StrictHostKeyChecking=no "$VPS" \
  "mkdir -p $REMOTE_BASE/management/commands"
for f in \
  enrollment_storage.py \
  services.py \
  views.py \
  management/__init__.py \
  management/commands/__init__.py \
  management/commands/backfill_enrollment_photos.py
do
  sshpass -e scp -o StrictHostKeyChecking=no \
    "$ROOT/register/backend/enrollment_gateway/apps/enrollment/$f" \
    "$VPS:$REMOTE_BASE/$f"
done

echo "=== Recréation enrollment (clé API alignée sur .env) ==="
sshpass -e ssh -o StrictHostKeyChecking=no "$VPS" bash -s <<'REMOTE'
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"
$COMPOSE --profile register up -d --force-recreate enrollment_gateway enrollment_worker
sleep 10
GK=$($COMPOSE --profile register exec -T enrollment_gateway printenv GUICHET_INTERNAL_API_KEY | tr -d '\r\n')
RK=$($COMPOSE --profile rh exec -T rh_server printenv GUICHET_INTERNAL_API_KEY | tr -d '\r\n')
echo "gateway_key=${GK:0:20}... rh_key=${RK:0:20}... match=$([ "$GK" = "$RK" ] && echo yes || echo NO)"

echo "=== Backfill sessions FAILED/PENDING avec photo ==="
$COMPOSE --profile register exec -T enrollment_gateway \
  python manage.py backfill_enrollment_photos

echo "=== Re-sync COMPLETED sans photo RH ==="
$COMPOSE --profile register exec -T enrollment_gateway \
  python manage.py backfill_enrollment_photos --resync-completed

echo "=== Vérification ==="
docker exec onip_postgres psql -U onip_user -d onip_db -c "
SELECT count(*) AS non_completed_with_photo
FROM enrollment_sessions
WHERE status <> 'COMPLETED'
  AND payload->'persisted_media'->>'photo_uri' IS NOT NULL;
SELECT count(*) AS rh_with_photo FROM employee_employee WHERE photo IS NOT NULL AND photo <> '';
"
REMOTE

echo "OK"
