#!/usr/bin/env bash
# Génère un .env à partir d'un template en remplaçant les placeholders secrets.
# Usage : ./deploy/env-gen.sh .env.prod.example .env

set -euo pipefail

TEMPLATE_FILE="${1:-.env.prod.example}"
OUTPUT_FILE="${2:-.env}"

if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "Template introuvable : $TEMPLATE_FILE" >&2
  exit 1
fi

cp "$TEMPLATE_FILE" "$OUTPUT_FILE"

generate_password() {
  local base
  base="$(openssl rand -hex 16)"
  echo "${base}@*"
}

while grep -q "__PASSWORD__" "$OUTPUT_FILE"; do
  pw="$(generate_password)"
  sed -i "0,/__PASSWORD__/s//${pw}/" "$OUTPUT_FILE"
done

while grep -q "__SECRET__" "$OUTPUT_FILE"; do
  secret="$(openssl rand -hex 32)"
  sed -i "0,/__SECRET__/s//${secret}/" "$OUTPUT_FILE"
done

echo "Fichier généré : $OUTPUT_FILE"
echo "Vérifiez RH_ALLOWED_HOSTS, RH_CSRF_TRUSTED_ORIGINS et KEYCLOAK_* avant le déploiement."
