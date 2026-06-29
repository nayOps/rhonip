#!/bin/bash

# Générer un certificat auto-signé pour HTTPS
echo "🔐 Génération d'un certificat SSL auto-signé..."

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=CD/ST=Kinshasa/L=Kinshasa/O=ONIP/CN=192.168.100.101"

echo "✅ Certificat généré!"
echo "📁 Fichiers créés:"
echo "   - cert.pem (certificat)"
echo "   - key.pem (clé privée)"

