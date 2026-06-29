#!/bin/bash

# Script de démarrage rapide pour le test MorphoTablet
# Usage: ./START.sh

clear

echo "======================================================================"
echo "    🔐 MorphoTablet - Environnement de Test Direct"
echo "======================================================================"
echo ""

# Trouver l'IP
IP=$(ip addr show | grep -E 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1 | head -1)

echo "✓ IP détectée: $IP"
echo ""
echo "📱 ACCÈS À L'INTERFACE:"
echo "----------------------------------------------------------------------"
echo "  Depuis ce PC:"
echo "    👉 http://localhost:8888"
echo ""
echo "  Depuis la MorphoTablet (même réseau Wi-Fi):"
echo "    👉 http://$IP:8888"
echo ""
echo "======================================================================"
echo ""
echo "🚀 Démarrage du serveur..."
echo ""

# Démarrer le serveur Python
python3 server.py

