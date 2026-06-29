#!/bin/bash

# Script d'installation pour système biométrique
# Compatible Debian/Ubuntu/Kali Linux

echo "================================================"
echo "🔐 Installation Système Biométrique"
echo "================================================"
echo ""

# Vérifier si on est root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Ne lancez pas ce script en tant que root"
    echo "   Le script demandera sudo quand nécessaire"
    exit 1
fi

# Mise à jour des dépôts
echo "📦 Mise à jour des dépôts..."
sudo apt-get update

# Installation des dépendances système
echo ""
echo "📦 Installation des dépendances système..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libusb-1.0-0-dev \
    libopencv-dev \
    python3-opencv \
    v4l-utils \
    build-essential \
    git

# Installation optionnelle de libfprint (si disponible)
echo ""
echo "📦 Installation de libfprint (optionnel)..."
if apt-cache show libfprint-2-dev &> /dev/null; then
    sudo apt-get install -y libfprint-2-dev
    echo "✓ libfprint installé"
else
    echo "⚠️  libfprint non disponible dans les dépôts"
fi

# Permissions USB
echo ""
echo "🔐 Configuration des permissions USB..."
sudo usermod -a -G plugdev $USER

# Créer la règle udev pour les périphériques biométriques
sudo bash -c 'cat > /etc/udev/rules.d/99-biometric.rules << EOF
# Permissions pour périphériques biométriques
SUBSYSTEM=="usb", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="video4linux", GROUP="video", MODE="0660"
EOF'

sudo udevadm control --reload-rules
sudo udevadm trigger

echo "✓ Règles udev créées"
echo "⚠️  Vous devrez peut-être vous déconnecter/reconnecter pour que les permissions prennent effet"

# Installation des dépendances Python
echo ""
echo "📦 Installation des dépendances Python..."
pip3 install -r requirements.txt

# Créer les répertoires nécessaires
echo ""
echo "📁 Création des répertoires..."
mkdir -p data templates

# Rendre les scripts exécutables
echo ""
echo "🔧 Configuration des scripts..."
chmod +x scripts/*.py
chmod +x test_fingerprint.py
chmod +x test_iris.py
chmod +x gui_app.py

# Test des installations
echo ""
echo "🧪 Vérification des installations..."

# Test Python
if python3 -c "import cv2" 2>/dev/null; then
    echo "✓ OpenCV installé"
else
    echo "❌ OpenCV non installé correctement"
fi

if python3 -c "import usb" 2>/dev/null; then
    echo "✓ PyUSB installé"
else
    echo "❌ PyUSB non installé correctement"
fi

if python3 -c "import serial" 2>/dev/null; then
    echo "✓ PySerial installé"
else
    echo "❌ PySerial non installé correctement"
fi

# Liste des caméras
echo ""
echo "📷 Caméras disponibles:"
ls -la /dev/video* 2>/dev/null || echo "   Aucune caméra détectée"

# Liste des ports série
echo ""
echo "📡 Ports série disponibles:"
ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "   Aucun port série détecté"

echo ""
echo "================================================"
echo "✅ Installation terminée!"
echo "================================================"
echo ""
echo "Prochaines étapes:"
echo "  1. Branchez vos périphériques biométriques"
echo "  2. Lancez: python3 scripts/detect_devices.py"
echo "  3. Mettez à jour config.json avec vos IDs"
echo "  4. Testez: python3 test_fingerprint.py"
echo "  5. Testez: python3 test_iris.py"
echo "  6. Interface graphique: python3 gui_app.py"
echo ""
echo "Documentation: README.md"
echo ""

