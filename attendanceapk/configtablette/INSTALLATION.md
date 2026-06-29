# Guide d'Installation - Attendance et Enroll

## 📱 Installation des Applications

### Prérequis
- Android Debug Bridge (ADB) installé
- Tablette MorphoTablet 2 connectée via USB
- Mode développeur activé sur la tablette

### Installation ATTENDANCE

```bash
cd /home/nayops/Documents/architecture/configtablette/attendance
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/attendance.apk
```

### Installation ENROLL

```bash
cd /home/nayops/Documents/architecture/configtablette/enroll
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/enroll.apk
```

## 🔧 Configuration Backend

Les deux applications partagent la même configuration backend via `ConfigManager` :

- **IP par défaut** : `192.168.1.74`
- **Port par défaut** : `8082`

### Modification de la configuration

Si une erreur de connexion se produit au démarrage, un formulaire de configuration apparaît automatiquement permettant de modifier l'IP et le port du backend.

## 🚀 Utilisation

### Application ATTENDANCE

1. Lancer l'application
2. Attendre le chargement (initialisation capteur + données)
3. Cliquer sur "Capturer"
4. Placer le doigt sur le capteur
5. L'application fait automatiquement :
   - Capture de l'empreinte
   - Matching avec les employés
   - Vérification de la présence
   - Enregistrement automatique
   - Retour automatique après 3 secondes

### Application ENROLL

1. Lancer l'application
2. Attendre le chargement (initialisation capteur + données)
3. **Authentification** : Placer le doigt super_admin
4. Si authentification réussie → Formulaire d'enregistrement (à implémenter)

## 🐛 Dépannage

### Erreur "SDK location not found"
```bash
# Créer local.properties avec le chemin du SDK Android
echo "sdk.dir=/path/to/android/sdk" > local.properties
```

### Erreur "Connexion refusée"
- Vérifier que le backend Docker est démarré
- Vérifier l'IP et le port dans le formulaire de configuration
- Vérifier la connexion réseau

### Erreur "Capteur non disponible"
- Vérifier que la tablette est bien connectée
- Redémarrer l'application
- Vérifier les permissions USB

## 📊 Logs

Les logs sont préfixés avec les tags suivants :
- `AttendanceApplication` / `EnrollApplication` : Application globale
- `DeviceManager` : Gestion du capteur
- `DataManager` : Chargement des données
- `LoadingActivity` : Écran de démarrage
- `AttendanceActivity` : Marquer présence
- `AuthActivity` : Authentification

Pour voir les logs :
```bash
adb logcat | grep -E "AttendanceApplication|EnrollApplication|DeviceManager|DataManager|LoadingActivity|AttendanceActivity|AuthActivity"
```


