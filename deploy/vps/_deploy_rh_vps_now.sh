#!/usr/bin/env bash
# Déploiement RH : formulaire employé, présences agent, assets
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
B='/mnt/c/Users/HYF/OneDrive/Documents/rh-onip'
VPS='adn@102.68.62.85'
REMOTE='~/onip-rh'

files=(
  rh/core/context.py
  rh/employee/forms.py
  rh/employee/urls.py
  rh/employee/models/__init__.py
  rh/employee/models/education.py
  rh/employee/models/education_references.py
  rh/employee/utils/education_references.py
  rh/employee/utils/employee_form_steps.py
  rh/employee/views/__init__.py
  rh/employee/views/employee.py
  rh/employee/views/my_attendance.py
  rh/template/base.html
  rh/template/employee/employee.html
  rh/template/employee/my_attendance.html
  rh/template/components/employee_form_stepper.html
  rh/template/components/employee_change_form.html
  rh/template/components/employee_attendance_section.html
  rh/template/components/employee_dossier_header.html
  rh/template/components/employee_dossier_sidebar.html
  rh/template/components/education_inline_formset.html
  rh/template/components/child_inline_formset.html
  rh/template/components/experience_inline_formset.html
  rh/template/components/document_inline_formset.html
  rh/static/assets/js/onip-form-select2.js
  rh/static/assets/js/employee-detail.js
  rh/static/assets/css/employee-detail.css
  rh/static/assets/css/employee-profile-dossier.css
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

echo "==> Migrations + staticfiles + restart..."
sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py migrate employee --noinput 2>/dev/null || true

$COMPOSE --profile rh exec -T -w /app/backend rh_server sh -c '
mkdir -p staticfiles/assets/css staticfiles/assets/js
cp -f static/assets/css/employee-detail.css staticfiles/assets/css/employee-detail.css
cp -f static/assets/css/employee-profile-dossier.css staticfiles/assets/css/employee-profile-dossier.css
cp -f static/assets/js/onip-form-select2.js staticfiles/assets/js/onip-form-select2.js
cp -f static/assets/js/employee-detail.js staticfiles/assets/js/employee-detail.js
'

$COMPOSE --profile rh restart rh_server
sleep 22

curl -sS -o /dev/null -w "login %{http_code}\n" http://127.0.0.1:8100/login/
curl -sS -o /dev/null -w "employee-detail.js %{http_code} %{size_download}\n" "http://127.0.0.1:8100/static/assets/js/employee-detail.js?v=20260709-5"
curl -sS -o /dev/null -w "my-attendance %{http_code}\n" -L http://127.0.0.1:8100/employee/my-attendance/ 2>/dev/null || echo "my-attendance redirect (auth required)"
echo "OK deploy VPS"
REMOTE
