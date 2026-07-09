#!/usr/bin/env bash
# Correctif Select2 formation (study_level, field_of_study, degree) — VPS
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
B='/mnt/c/Users/HYF/OneDrive/Documents/rh-onip'
VPS='adn@102.68.62.85'
REMOTE='~/onip-rh'

files=(
  rh/employee/forms.py
  rh/template/components/education_inline_formset.html
  rh/static/assets/js/onip-form-select2.js
  rh/static/assets/js/employee-detail.js
  rh/static/assets/css/employee-detail.css
  rh/template/base.html
  rh/template/employee/employee.html
)

echo "==> Copie des fichiers vers VPS..."
for f in "${files[@]}"; do
  src="$B/$f"
  if [[ ! -f "$src" ]]; then
    echo "  SKIP (absent): $f"
    continue
  fi
  echo "  -> $f"
  sshpass -e scp -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$src" "$VPS:$REMOTE/$f"
done

echo "==> Sync staticfiles + restart rh_server..."
sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE --profile rh exec -T -w /app/backend rh_server sh -c '
mkdir -p staticfiles/assets/css staticfiles/assets/js
cp -f static/assets/css/employee-detail.css staticfiles/assets/css/employee-detail.css
cp -f static/assets/js/onip-form-select2.js staticfiles/assets/js/onip-form-select2.js
cp -f static/assets/js/employee-detail.js staticfiles/assets/js/employee-detail.js
'

grep -c "ListSelect2" rh/employee/forms.py

$COMPOSE --profile rh restart rh_server
sleep 20
curl -sS -o /dev/null -w "login %{http_code}\n" http://127.0.0.1:8100/login/
curl -sS -o /dev/null -w "onip-form-select2.js %{http_code} %{size_download}\n" "http://127.0.0.1:8100/static/assets/js/onip-form-select2.js?v=20260709-4"
echo "OK deploy education select2 fix"
REMOTE
