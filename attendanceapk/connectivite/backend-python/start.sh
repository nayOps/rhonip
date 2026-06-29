#!/bin/bash

echo "🐍 Installation des dépendances Python..."
pip3 install -r requirements.txt

echo "🚀 Démarrage du serveur de test..."
python3 server.py
