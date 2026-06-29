# 📱 ONIP Biometric App

Application Android native pour la MorphoTablet 2, dédiée à l'enregistrement biométrique des employés et à la gestion du pointage.

---

## 🎯 Fonctionnalités

### ✅ Enregistrement d'Employé
- Capture photo (caméra frontale 13MP)
- Capture de 4 empreintes digitales :
  - Index Gauche
  - Index Droit
  - Pouce Gauche
  - Pouce Droit
- Envoi sécurisé au backend ONIP

### ✅ Pointage (Attendance)
- Vérification d'empreinte digitale
- Identification automatique de l'employé
- Enregistrement horodaté du pointage
- Affichage du nom de l'employé

---

## 🏗️ Architecture

```
ONIPBiometricApp/
├── app/
│   ├── src/main/
│   │   ├── java/com/onip/biometric/
│   │   │   ├── MainActivity.java                    # Point d'entrée
│   │   │   ├── activities/
│   │   │   │   ├── EmployeeEnrollmentActivity.java # Enregistrement
│   │   │   │   └── AttendanceActivity.java          # Pointage
│   │   │   ├── services/
│   │   │   │   ├── BiometricService.java            # SDK MorphoSmart
│   │   │   │   ├── CameraService.java               # Gestion caméra
│   │   │   │   └── ApiService.java                  # Communication API
│   │   │   ├── models/
│   │   │   │   ├── Employee.java                    # Modèle Employé
│   │   │   │   └── BiometricData.java               # Données biométriques
│   │   │   └── utils/
│   │   ├── res/
│   │   │   ├── layout/                              # Layouts XML
│   │   │   └── values/                              # Strings, colors, etc.
│   │   └── AndroidManifest.xml
│   ├── libs/
│   │   └── MorphoSmart_SDK_6.19.4.0.jar            # SDK empreintes
│   └── build.gradle
└── README.md
```

---

## 🔧 Installation et Configuration

### 1️⃣ Prérequis

- **Android Studio** 4.0+ (ou dernière version)
- **JDK** 8+
- **MorphoTablet 2** (MPH-MB001A)
- **SDK Android** API 21+ (Android 5.0+)

### 2️⃣ Importer le SDK MorphoSmart

```bash
# Copier le JAR du SDK dans le dossier libs
cp ../sdk/Customer_support_package-2.8/Code_Samples/Main_Demo/MorphoSmart_SDK_6.19.4.0/MorphoSmart_SDK_6.19.4.0.jar app/libs/
```

### 3️⃣ Configuration du Backend

Modifier l'URL du backend dans `ApiService.java` :

```java
private static final String API_BASE_URL = "http://192.168.100.101:8000/api";
```

Remplacer par l'adresse IP de votre serveur backend ONIP.

### 4️⃣ Build et Installation

#### Option A : Avec Android Studio

1. Ouvrir Android Studio
2. File → Open → Sélectionner le dossier `ONIPBiometricApp`
3. Attendre la synchronisation Gradle
4. Connecter la MorphoTablet en USB
5. Run → Run 'app'

#### Option B : En Ligne de Commande

```bash
# Build l'APK
./gradlew assembleDebug

# Installer sur la tablette
adb install app/build/outputs/apk/debug/app-debug.apk
```

---

## 📱 Utilisation

### Enregistrement d'un Employé

1. Ouvrir l'application
2. Cliquer sur **"Enregistrement Employé"**
3. Entrer l'ID de l'employé (NIN)
4. **Étape 1 : Photo**
   - Positionner le visage face à la caméra
   - Cliquer sur "Capturer"
   - Confirmer ou reprendre
5. **Étape 2-5 : Empreintes**
   - Placer chaque doigt sur le capteur quand demandé
   - Attendre la validation (bip sonore)
   - Passer au doigt suivant
6. **Confirmation**
   - Vérifier les données
   - Cliquer sur "Envoyer"
   - Attendre la confirmation du serveur

### Pointage

1. Ouvrir l'application
2. Cliquer sur **"Pointage"**
3. Placer un doigt enregistré sur le capteur
4. Attendre la vérification (1-2 secondes)
5. Confirmation affichée :
   - ✅ "Bienvenue [Nom] ! Pointage enregistré."
   - ❌ "Empreinte non reconnue"

---

## 🔌 API Endpoints

### 📤 Enregistrement Biométrique

**POST** `/api/biometric/enroll`

**Body (multipart/form-data):**
```
employeeId: string
photo: file (JPEG)
fingerprint_0: string (Base64)
fingerprint_1: string (Base64)
fingerprint_2: string (Base64)
fingerprint_3: string (Base64)
fingerIndex_0: int
fingerIndex_1: int
fingerIndex_2: int
fingerIndex_3: int
```

**Response:**
```json
{
  "success": true,
  "message": "Employé enregistré avec succès"
}
```

### 🔍 Vérification d'Empreinte

**POST** `/api/biometric/verify`

**Body (JSON):**
```json
{
  "fingerprint": "base64_encoded_template",
  "timestamp": 1705876543210
}
```

**Response:**
```json
{
  "matched": true,
  "employee": {
    "id": "123",
    "firstName": "Jean",
    "lastName": "Dupont",
    "department": "IT",
    "position": "Developer"
  }
}
```

### ⏰ Pointage

**POST** `/api/biometric/checkin`

**Body (JSON):**
```json
{
  "fingerprint": "base64_encoded_template",
  "action": "checkin",
  "timestamp": 1705876543210
}
```

**Response:**
```json
{
  "success": true,
  "message": "Pointage enregistré pour Jean Dupont",
  "employee_name": "Jean Dupont",
  "timestamp": "2025-01-21 14:30:00"
}
```

---

## 🧪 Tests

### Test du Capteur d'Empreintes

1. Ouvrir l'app démo du SDK :
   ```bash
   adb install ../sdk/Customer_support_package-2.8/Demo_APK/Main_Demo_2.8.apk
   ```
2. Lancer "Main Demo"
3. Aller dans "Fingerprint Sensor"
4. Tester "Capture" et "Verify"

### Test de la Caméra

1. Utiliser l'application Caméra native d'Android
2. Prendre une photo de test
3. Vérifier la qualité (résolution 13MP)

### Test de Connectivité Backend

```bash
# Depuis la tablette, tester l'accès à l'API
curl -X GET http://192.168.100.101:8000/api/health
```

---

## 🐛 Dépannage

### Problème : "Périphérique USB non trouvé"

**Solutions :**
1. Vérifier que le capteur est sous tension
2. Redémarrer l'application
3. Vérifier les permissions USB dans AndroidManifest.xml

### Problème : "Erreur réseau"

**Solutions :**
1. Vérifier que la tablette et le serveur sont sur le même réseau
2. Pinger le serveur :
   ```bash
   ping 192.168.100.101
   ```
3. Vérifier que le backend est démarré
4. Vérifier l'URL dans `ApiService.java`

### Problème : "Caméra non accessible"

**Solutions :**
1. Vérifier les permissions dans Paramètres → Apps → ONIP Biometric → Permissions
2. Accorder la permission Caméra
3. Redémarrer l'application

### Problème : "Empreinte de mauvaise qualité"

**Solutions :**
1. Nettoyer le capteur avec un chiffon doux
2. Nettoyer le doigt (pas d'humidité, pas de saleté)
3. Appuyer fermement mais sans écraser
4. Centrer le doigt sur le capteur

---

## 📚 Documentation Technique

### SDK MorphoSmart

- **Version** : 6.19.4.0
- **Documentation** : `../sdk/Customer_support_package-2.8/Documentation/`
- **Exemples** : `../sdk/Customer_support_package-2.8/Code_Samples/`

### Classes Principales

#### BiometricService

Gère toutes les opérations liées au capteur d'empreintes digitales.

**Méthodes principales :**
- `initialize()` : Initialiser le périphérique USB
- `captureFingerprint(callback)` : Capturer une empreinte
- `verifyFingerprint(template, callback)` : Vérifier une empreinte
- `close()` : Fermer le périphérique

#### CameraService

Gère la caméra pour la capture de photos.

**Méthodes principales :**
- `open(cameraId)` : Ouvrir la caméra (0=arrière, 1=avant)
- `takePhoto(callback)` : Prendre une photo
- `switchCamera()` : Changer de caméra
- `close()` : Fermer la caméra

#### ApiService

Gère la communication avec le backend ONIP.

**Méthodes principales :**
- `enrollEmployee(...)` : Enregistrer un employé
- `verifyFingerprint(...)` : Vérifier une empreinte
- `recordCheckIn(...)` : Enregistrer un pointage

---

## 🚀 Prochaines Étapes

- [ ] Créer les activités Android complètes
- [ ] Implémenter les layouts XML
- [ ] Ajouter les ressources (strings, colors, drawables)
- [ ] Tester sur la tablette réelle
- [ ] Implémenter la gestion des erreurs
- [ ] Ajouter des animations et feedback UX
- [ ] Implémenter le mode hors-ligne avec synchronisation
- [ ] Ajouter des logs et analytics

---

## 📞 Support

- **Documentation** : `SDK-ANALYSIS.md`
- **Backend API** : `../../onip-si/apps/employee-service/`
- **Issues** : Contacter l'équipe de développement ONIP

---

**Version** : 1.0.0  
**Date** : Janvier 2025  
**Plateforme** : Android 5.0+ (API 21+)  
**Matériel** : MorphoTablet 2 (MPH-MB001A)

