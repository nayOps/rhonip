#!/bin/bash
# Script pour donner les permissions USB aux lecteurs biométriques

echo "🔐 Configuration des permissions USB..."

# Permissions temporaires pour cette session
echo "Permissions temporaires (session actuelle):"
sudo chmod 666 /dev/bus/usb/003/007  # Aratek
sudo chmod 666 /dev/video2            # Iris

echo "✅ Permissions temporaires appliquées!"

# Créer règle udev permanente
echo ""
echo "📝 Création de règle udev permanente..."
sudo tee /etc/udev/rules.d/99-biometric.rules > /dev/null << 'EOF'
# Lecteur d'empreintes Aratek
SUBSYSTEM=="usb", ATTR{idVendor}=="28ed", ATTR{idProduct}=="1063", MODE="0666", GROUP="plugdev"

# Lecteur d'iris Sunplus
SUBSYSTEM=="usb", ATTR{idVendor}=="1bcf", ATTR{idProduct}=="0b15", MODE="0666", GROUP="plugdev"

# Tous les périphériques vidéo
SUBSYSTEM=="video4linux", GROUP="video", MODE="0660"
EOF

echo "✅ Règle udev créée: /etc/udev/rules.d/99-biometric.rules"

# Recharger les règles
echo ""
echo "🔄 Rechargement des règles udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "Note: Les règles permanentes seront actives au prochain branchement."
echo "      Les permissions temporaires sont actives maintenant."

