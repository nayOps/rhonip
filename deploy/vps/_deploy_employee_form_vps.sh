#!/usr/bin/env bash
# Déploiement complet formulaire employé (stepper + référentiels formation) sur VPS
set -euo pipefail
export SSHPASS='ADNKinshasa**2024'
B='/mnt/c/Users/HYF/OneDrive/Documents/rh-onip'
VPS='adn@102.68.62.85'
REMOTE='~/onip-rh'

files=(
  rh/employee/forms.py
  rh/employee/urls.py
  rh/employee/models/__init__.py
  rh/employee/models/education.py
  rh/employee/models/education_references.py
  rh/employee/utils/education_references.py
  rh/employee/utils/employee_form_steps.py
  rh/employee/choices/education_catalog.py
  rh/employee/views/__init__.py
  rh/employee/views/employee.py
  rh/employee/views/my_attendance.py
  rh/employee/migrations/0016_education_reference_tables.py
  rh/employee/migrations/0017_education_fk_references.py
  rh/employee/management/commands/migrate_education_references.py
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
  rh/static/assets/css/onip-forms.css
  rh/static/autocomplete_light/select2.js
  rh/core/views/base/list.py
)

echo "==> Copie des fichiers vers VPS..."
for f in "${files[@]}"; do
  src="$B/$f"
  if [[ ! -f "$src" ]]; then
    echo "  SKIP (absent): $f"
    continue
  fi
  echo "  -> $f"
  sshpass -e scp -o StrictHostKeyChecking=no "$src" "$VPS:$REMOTE/$f"
done

echo "==> Migrations + redémarrage sur VPS..."
sshpass -e ssh -o StrictHostKeyChecking=no "$VPS" bash -s <<'REMOTE'
set -euo pipefail
cd ~/onip-rh
COMPOSE="docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml -f compose/prod.expose8100.yml --env-file .env"

echo "--- migrations avant ---"
$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py showmigrations employee | tail -5

echo "--- migrate ---"
$COMPOSE --profile rh exec -T -w /app/backend rh_server python manage.py migrate employee --noinput

echo "--- sync staticfiles ---"
$COMPOSE --profile rh exec -T -w /app/backend rh_server sh -c '
mkdir -p staticfiles/assets/css staticfiles/assets/js staticfiles/autocomplete_light
cp -f static/assets/css/employee-detail.css staticfiles/assets/css/employee-detail.css
cp -f static/assets/css/employee-profile-dossier.css staticfiles/assets/css/employee-profile-dossier.css
cp -f static/assets/css/onip-forms.css staticfiles/assets/css/onip-forms.css
cp -f static/assets/js/onip-form-select2.js staticfiles/assets/js/onip-form-select2.js
cp -f static/assets/js/employee-detail.js staticfiles/assets/js/employee-detail.js
cp -f static/autocomplete_light/select2.js staticfiles/autocomplete_light/select2.js
'

echo "--- restart rh_server ---"
$COMPOSE --profile rh restart rh_server
sleep 20

echo "--- tests ---"
curl -sS -o /dev/null -w "login %{http_code}\n" http://127.0.0.1:8100/login/
curl -sS -o /dev/null -w "employee-detail.css %{http_code} %{size_download}\n" http://127.0.0.1:8100/static/assets/css/employee-detail.css
curl -sS -o /dev/null -w "employee-detail.js %{http_code} %{size_download}\n" http://127.0.0.1:8100/static/assets/js/employee-detail.js
curl -sS -o /dev/null -w "onip-form-select2.js %{http_code} %{size_download}\n" http://127.0.0.1:8100/static/assets/js/onip-form-select2.js
echo "OK"
REMOTE
