#!/bin/bash
# Installation rapide avec --break-system-packages pour Kali

echo "📦 Installation des dépendances Python..."
pip3 install --break-system-packages pyusb pyserial opencv-python numpy pillow scipy scikit-image colorama tqdm

echo "✅ Installation terminée!"

