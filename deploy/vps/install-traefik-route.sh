#!/usr/bin/env bash
# Installe la route Traefik ONIP dans le stack cpnpr (sans redémarrer Traefik).
# Usage sur le VPS :
#   cd /home/adn/onip-rh && ./deploy/vps/install-traefik-route.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CPNPR_TRAEFIK_DYNAMIC="${CPNPR_TRAEFIK_DYNAMIC:-/home/adn/cpnpr/docker/traefik/config/dynamic}"
SOURCE="$REPO_ROOT/deploy/traefik/onip-rh.yml"
TARGET="$CPNPR_TRAEFIK_DYNAMIC/onip-rh.yml"

if [[ ! -f "$SOURCE" ]]; then
  echo "Fichier source introuvable : $SOURCE" >&2
  exit 1
fi

if [[ ! -d "$CPNPR_TRAEFIK_DYNAMIC" ]]; then
  echo "Répertoire Traefik cpnpr introuvable : $CPNPR_TRAEFIK_DYNAMIC" >&2
  echo "Définissez CPNPR_TRAEFIK_DYNAMIC si le chemin diffère." >&2
  exit 1
fi

cp "$SOURCE" "$TARGET"
echo "Route installée : $TARGET"
echo "Traefik recharge automatiquement (watch=true). Vérifiez : https://rh.onip.gouv.cd"
