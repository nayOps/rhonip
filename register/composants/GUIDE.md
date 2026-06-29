# Guide d'utilisation - Système Biométrique

## 🚀 Démarrage rapide

### 1. Installation

```bash
chmod +x install.sh
./install.sh
```

### 2. Détection des périphériques

```bash
python3 scripts/detect_devices.py
```

Ce script va détecter:
- Tous les périphériques USB connectés
- Les ports série disponibles
- Les caméras disponibles

### 3. Configuration

Éditez `config.json` avec les IDs de vos périphériques:

```json
{
  "fingerprint": {
    "usb": {
      "vendor_id": "0x1234",  ← VID de votre lecteur
      "product_id": "0x5678"  ← PID de votre lecteur
    },
    "serial": {
      "port": "/dev/ttyUSB0",  ← Port série
      "baudrate": 9600
    }
  },
  "iris": {
    "camera_index": 0  ← Index de votre caméra
  }
}
```

## 📖 Utilisation détaillée

### Lecteur d'empreintes

#### USB Direct

```python
from modules.fingerprint import USBFingerprintReader

# Créer le lecteur
reader = USBFingerprintReader()

# Connecter
if reader.connect():
    # Initialiser
    reader.initialize_sensor()
    
    # Capturer une empreinte
    image = reader.capture_fingerprint(timeout=15)
    
    # Extraire le template
    template = reader.extract_template(image)
    
    # Sauvegarder l'image
    reader.save_image(image, "empreinte.png")
    
    # Déconnecter
    reader.disconnect()
```

#### Série (capteurs R30x, etc.)

```python
from modules.fingerprint import SerialFingerprintReader

# Créer le lecteur
reader = SerialFingerprintReader(port="/dev/ttyUSB0", baudrate=57600)

# Connecter
if reader.connect():
    # Vérifier le mot de passe
    reader.verify_password(0x00000000)
    
    # Enregistrer une empreinte
    template = reader.enroll_fingerprint()
    
    # Vérifier une empreinte
    if reader.verify_fingerprint():
        print("Empreinte reconnue!")
```

#### Comparaison d'empreintes

```python
from modules.fingerprint import FingerprintMatcher

# Créer le matcher
matcher = FingerprintMatcher(threshold=0.4)

# Comparer deux templates
is_match, score = matcher.compare_templates(template1, template2)

print(f"Match: {is_match}, Score: {score:.2%}")

# Rechercher dans une base de données
database = [template1, template2, template3]
match_idx, score = matcher.match(template_test, database)
```

### Lecteur d'iris

#### Capture

```python
from modules.iris import IrisCamera

# Créer la caméra
camera = IrisCamera(camera_index=0)

# Ouvrir
if camera.connect():
    # Capturer un iris
    capture = camera.capture_iris(timeout=30, preview=True)
    
    if capture:
        # Accéder aux données
        full_frame = capture['full_frame']
        eye_region = capture['eye_region']
        
        # Sauvegarder
        camera.save_image(eye_region, "iris.jpg")
```

#### Segmentation

```python
from modules.iris import IrisSegmentation

# Créer le segmenteur
segmenter = IrisSegmentation(min_radius=30, max_radius=120)

# Segmenter l'iris
segmentation = segmenter.segment_iris(eye_region)

if segmentation:
    # Vérifier la qualité
    quality = segmenter.check_quality(segmentation, eye_region)
    
    if quality['valid']:
        # Normaliser l'iris
        normalized = segmenter.normalize_iris(eye_region, segmentation)
        
        # Visualiser
        vis = segmenter.visualize_segmentation(eye_region, segmentation)
```

#### Comparaison d'iris

```python
from modules.iris import IrisMatcher

# Créer le matcher
matcher = IrisMatcher(threshold=0.35)

# Encoder les iris normalisés
template1 = matcher.encode_iris(normalized1)
template2 = matcher.encode_iris(normalized2)

# Comparer
is_match, score = matcher.compare_templates(template1, template2)

print(f"Match: {is_match}, Score: {score:.2%}")
```

### Base de données

```python
from modules.database import BiometricDatabase

# Créer/ouvrir la base de données
db = BiometricDatabase('biometric_data.db')
db.connect()

# Ajouter un utilisateur
user_id = db.add_user("John Doe")

# Ajouter une empreinte
fp_id = db.add_fingerprint(user_id, template, finger_index=1, quality_score=85)

# Ajouter un iris
iris_id = db.add_iris(user_id, template, eye='left', quality_score=0.92)

# Récupérer les données
fingerprints = db.get_fingerprints(user_id)
iris_list = db.get_iris(user_id)

# Statistiques
stats = db.get_statistics()
print(f"Utilisateurs: {stats['users']}")

db.disconnect()
```

## 🎯 Cas d'usage complets

### Enregistrement d'un utilisateur

```python
from modules.fingerprint import USBFingerprintReader, FingerprintMatcher
from modules.iris import IrisCamera, IrisSegmentation, IrisMatcher
from modules.database import BiometricDatabase

# Connecter à la base
db = BiometricDatabase()
db.connect()

# Créer l'utilisateur
user_id = db.add_user("Alice")

# Enregistrer empreinte
with USBFingerprintReader() as fp_reader:
    print("Placez votre doigt...")
    image = fp_reader.capture_fingerprint()
    template = fp_reader.extract_template(image)
    db.add_fingerprint(user_id, template)

# Enregistrer iris
with IrisCamera() as camera:
    segmenter = IrisSegmentation()
    matcher = IrisMatcher()
    
    print("Regardez la caméra...")
    capture = camera.capture_iris()
    
    segmentation = segmenter.segment_iris(capture['eye_region'])
    normalized = segmenter.normalize_iris(capture['eye_region'], segmentation)
    template = matcher.encode_iris(normalized)
    
    db.add_iris(user_id, template, eye='left')

db.disconnect()
print("Utilisateur enregistré!")
```

### Authentification

```python
def authenticate_user():
    """Authentifie un utilisateur par empreinte ou iris"""
    
    db = BiometricDatabase()
    db.connect()
    
    # Capturer l'empreinte
    with USBFingerprintReader() as reader:
        image = reader.capture_fingerprint()
        template = reader.extract_template(image)
    
    # Comparer avec la base
    matcher = FingerprintMatcher()
    all_fingerprints = db.get_all_fingerprints()
    
    for fp_data in all_fingerprints:
        is_match, score = matcher.compare_templates(template, fp_data['template'])
        
        if is_match:
            user = db.get_user(fp_data['user_id'])
            db.disconnect()
            return user['name']
    
    db.disconnect()
    return None

# Utilisation
user = authenticate_user()
if user:
    print(f"Bienvenue, {user}!")
else:
    print("Authentification échouée")
```

## 🔧 Reverse-engineering du protocole USB

Si votre lecteur ne fonctionne pas avec les commandes génériques:

### 1. Capturer le trafic

```bash
# Lister les périphériques
python3 scripts/capture_usb_traffic.py list

# Monitorer un périphérique
python3 scripts/capture_usb_traffic.py monitor 0x1234 0x5678 30

# Envoyer une commande
python3 scripts/capture_usb_traffic.py send 0x1234 0x5678 '01 02 03 04'
```

### 2. Analyser avec Wireshark

Sur Windows (avec driver officiel):
1. Installez USBPcap
2. Capturez le trafic USB pendant l'utilisation du lecteur
3. Analysez les commandes envoyées
4. Reproduisez avec Python

### 3. Adapter le code

Modifiez `modules/fingerprint/usb_reader.py`:

```python
def initialize_sensor(self):
    # Vos commandes spécifiques
    init_commands = [
        b'\x01\x00\x00\x00',  # Commande 1
        b'\x02\x00\x00\x00',  # Commande 2
    ]
    
    for cmd in init_commands:
        self.send_command(cmd)
        response = self.read_response()
```

## 🐛 Dépannage

### Erreur "Access denied" USB

```bash
# Temporaire
sudo chmod 666 /dev/bus/usb/XXX/YYY

# Permanent (règle udev)
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1234", ATTR{idProduct}=="5678", MODE="0666"' | sudo tee /etc/udev/rules.d/99-my-device.rules
sudo udevadm control --reload-rules
```

### Port série occupé

```bash
# Vérifier qui utilise le port
sudo lsof /dev/ttyUSB0

# Permissions
sudo chmod 666 /dev/ttyUSB0
# ou
sudo usermod -a -G dialout $USER
```

### Caméra non détectée

```bash
# Lister les caméras
v4l2-ctl --list-devices

# Tester la caméra
ffplay /dev/video0
```

### OpenCV ne trouve pas la caméra

Essayez différents backends:

```python
camera = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Linux
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows
```

## 📚 Ressources

### Documentation des protocoles

- **R30x (série)**: Protocole standard pour capteurs d'empreintes
- **ZFM (série)**: Format de template commun
- **HID**: Beaucoup de lecteurs USB utilisent HID
- **Iris**: Algorithmes Daugman, Wildes

### Bibliothèques alternatives

- **python-fprint**: Interface Python pour libfprint
- **pyfingerprint**: Bibliothèque pour capteurs série
- **iris-recognition**: Implémentations open-source

### Outils utiles

- **lsusb**: Lister périphériques USB
- **usbview**: Visualiser arbre USB
- **Wireshark + USBPcap**: Capturer trafic USB
- **v4l-utils**: Outils Video4Linux

## 💡 Conseils

1. **Testez d'abord la détection**: `detect_devices.py`
2. **Commencez simple**: Testez la connexion avant la capture
3. **Documentez vos commandes**: Si vous faites du reverse-engineering
4. **Qualité des captures**: Bon éclairage pour iris, doigt propre pour empreintes
5. **Sécurité**: Chiffrez les templates en production

## 🤝 Contribution

Ce projet est conçu pour être extensible. Pour ajouter le support d'un nouveau lecteur:

1. Créez un nouveau fichier dans `modules/fingerprint/` ou `modules/iris/`
2. Héritez des classes de base
3. Implémentez les méthodes spécifiques
4. Testez avec les scripts de test
5. Documentez le protocole

## 📞 Support

Pour des questions ou problèmes:
1. Vérifiez la section Dépannage
2. Consultez les logs des scripts de test
3. Utilisez `debug: true` dans config.json

