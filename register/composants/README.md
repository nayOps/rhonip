# 🔐 Système Biométrique - Iris & Empreintes

Solution complète pour interfacer avec des lecteurs biométriques **sans SDK propriétaire**.

## 📦 Composants supportés

### Lecteur d'empreintes
- Communication USB directe
- Support libfprint (Linux)
- Protocoles série personnalisés
- Extraction et comparaison de minuties

### Lecteur d'iris
- Capture via caméra USB/webcam
- Détection et segmentation de l'iris
- Extraction de features (Gabor wavelets)
- Comparaison par distance de Hamming

## 🚀 Installation

### 1. Dépendances système (Linux/Kali)

```bash
# Pour libusb et libfprint
sudo apt-get update
sudo apt-get install -y libusb-1.0-0-dev libfprint-2-dev python3-dev

# Pour OpenCV
sudo apt-get install -y libopencv-dev python3-opencv

# Permissions USB (pour éviter sudo)
sudo usermod -a -G plugdev $USER
echo 'SUBSYSTEM=="usb", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-biometric.rules
sudo udevadm control --reload-rules
```

### 2. Dépendances Python

```bash
pip install -r requirements.txt
```

## 🎯 Utilisation rapide

### Détecter vos périphériques
```bash
python scripts/detect_devices.py
```

### Interface graphique de test
```bash
python gui_app.py
```

### Tests individuels
```bash
# Test lecteur d'empreintes
python test_fingerprint.py

# Test lecteur d'iris
python test_iris.py
```

## 📁 Structure du projet

```
composants/
├── modules/
│   ├── fingerprint/          # Lecteur d'empreintes
│   │   ├── usb_reader.py     # Communication USB directe
│   │   ├── serial_reader.py  # Communication série
│   │   └── matcher.py        # Comparaison d'empreintes
│   ├── iris/                 # Lecteur d'iris
│   │   ├── camera.py         # Capture caméra
│   │   ├── segmentation.py   # Détection iris
│   │   └── matcher.py        # Comparaison iris
│   └── database/             # Stockage des templates
│       └── db_manager.py
├── scripts/
│   ├── detect_devices.py     # Détection USB/Série
│   └── capture_usb_traffic.py # Debug protocole USB
├── gui_app.py                # Interface graphique
├── test_fingerprint.py       # Test empreintes
├── test_iris.py              # Test iris
└── requirements.txt
```

## 🔧 Configuration

Éditez `config.json` pour adapter à votre matériel:

```json
{
  "fingerprint": {
    "vendor_id": "0x0000",  # Votre VID USB
    "product_id": "0x0000", # Votre PID USB
    "serial_port": "/dev/ttyUSB0"
  },
  "iris": {
    "camera_index": 0
  }
}
```

## 📖 Guides détaillés

### Comment trouver les IDs de vos périphériques
```bash
# Lister les périphériques USB
lsusb

# Informations détaillées
lsusb -v -d VENDOR_ID:PRODUCT_ID

# Monitorer le traffic USB
sudo usbmon
```

### Reverse-engineering du protocole
1. Installez le driver officiel sur une VM Windows
2. Capturez le trafic USB avec Wireshark
3. Analysez les commandes envoyées
4. Reproduisez avec pyusb

## 🆘 Dépannage

### Erreur "Access denied" sur USB
```bash
sudo chmod 666 /dev/bus/usb/XXX/YYY
# ou ajoutez une règle udev permanente
```

### libfprint ne détecte pas le lecteur
Votre lecteur n'est peut-être pas supporté. Utilisez l'approche USB directe.

### Caméra iris non détectée
```bash
# Lister les caméras
ls -la /dev/video*
v4l2-ctl --list-devices
```

## 📝 Licence

MIT License - Utilisez librement pour vos projets.

