# RH App V2 - Application Android Fluide et Stable

Application Android native pour la MorphoTablet 2, dédiée à la gestion des présences et à l'enregistrement des employés avec empreintes digitales.

## 🎯 Objectifs

- **Fluidité** : Marquer la présence de manière fluide, sans interruption
- **Stabilité** : Pas d'erreurs aléatoires (capteur, données, matching)
- **Design** : Interface magnifique adaptée à une tablette
- **Performance** : Matching rapide et optimisé

## 🏗️ Architecture

### Structure du Projet

```
rhApp-v2/
├── app/
│   ├── src/main/
│   │   ├── java/com/onip/rh/
│   │   │   ├── RHApplication.java          # Application globale (singleton)
│   │   │   ├── activities/
│   │   │   │   ├── LoadingActivity.java    # Écran de démarrage
│   │   │   │   ├── HomeActivity.java       # Menu principal
│   │   │   │   ├── AttendanceActivity.java # Marquer présence
│   │   │   │   ├── AuthActivity.java       # Authentification
│   │   │   │   └── EmployeeEnrollmentActivity.java # Enregistrement (stub)
│   │   │   ├── services/
│   │   │   │   ├── DeviceManager.java      # Gestion MorphoDevice (retry)
│   │   │   │   ├── DataManager.java        # Gestion données (cache + retry)
│   │   │   │   └── AttendanceService.java  # Enregistrement présences
│   │   │   ├── models/
│   │   │   │   └── Employee.java           # Modèle employé
│   │   │   ├── utils/
│   │   │   │   ├── ConfigManager.java      # Configuration backend
│   │   │   │   └── RetryHelper.java        # Retry automatique
│   │   │   └── fingerprint/
│   │   │       └── FingerprintProcessObserver.java # Callbacks SDK
│   │   └── res/
│   │       ├── layout/                     # Layouts XML
│   │       ├── drawable/                   # Drawables (glassmorphisme, tricolore)
│   │       └── values/                      # Colors, strings, styles
│   └── libs/
│       └── MorphoSmart_SDK_6.19.4.0.jar    # SDK MorphoSmart
```

## 🚀 Fonctionnalités

### 1. Écran de Démarrage (LoadingActivity)
- Initialisation MorphoDevice avec retry automatique (3 tentatives)
- Chargement des employés depuis le backend
- Chargement des templates d'empreintes
- Barre de progression avec messages de statut
- Navigation automatique vers HomeActivity

### 2. Menu Principal (HomeActivity)
- 2 grandes cartes glassmorphiques :
  - **Marquer Présence** → AttendanceActivity
  - **Enregistrer Employé** → AuthActivity (authentification requise)
- Affichage du statut système (capteur, données, nombre d'employés)

### 3. Marquer Présence (AttendanceActivity)
- Capture automatique d'empreinte
- Matching optimisé avec arrêt anticipé (score >= 75)
- Vérification des doigts prioritaires : Index_Droit, Pouce_Droit, Index_Gauche
- Vérification de présence complète (2 présences/jour max)
- Retry automatique en cas d'échec (2 secondes)
- Retour automatique après succès (3 secondes)

### 4. Authentification (AuthActivity)
- Capture d'empreinte
- Vérification du rôle `super_admin`
- Navigation vers formulaire d'enregistrement si succès

## 🔧 Solutions de Stabilité

### 1. DeviceManager
- **Retry automatique** : 3 tentatives avec backoff exponentiel
- **Vérification de connexion** : Méthode `checkConnection()`
- **Gestion d'erreurs** : Try-catch avec logs détaillés

### 2. DataManager
- **Retry automatique** : 3 tentatives pour chaque requête
- **Chargement parallèle** : Employés et templates en même temps
- **Gestion d'erreurs** : Continue même si une partie échoue

### 3. RHApplication
- **Cache** : Validité de 5 minutes
- **Vérification d'expiration** : `needsDataRefresh()`
- **État global** : `isReady()` pour vérifier device + données

### 4. RetryHelper
- **Backoff exponentiel** : Délai augmente à chaque tentative
- **Configurable** : Nombre de tentatives et délai initial

## 🎨 Design System

### Couleurs RDC Officielles
- **Bleu** : `#0095c9` (principal)
- **Jaune** : `#fff24b` (accents)
- **Rouge** : `#db3832` (alertes)

### Composants
- **Glassmorphisme** : Cartes semi-transparentes (`#80FFFFFF`)
- **Barre tricolore** : Toujours visible en haut
- **Boutons** : Grands (min 60dp hauteur), flat design
- **Typographie** : Cooper Hewitt (ou Roboto fallback)

## 📱 Configuration Backend

Par défaut :
- **IP** : `192.168.1.73`
- **Port** : `8082` (corrigé pour correspondre au backend Docker)

Modifiable via `ConfigManager` (SharedPreferences).

## 🔌 API Endpoints Utilisés

- `GET /api/data` - Récupérer tous les employés
- `GET /api/fingerprints/matching` - Récupérer tous les templates
- `GET /api/fingerprints/{employeeId}/{fingerName}` - Récupérer un template binaire
- `GET /api/attendance` - Récupérer l'historique des présences
- `POST /api/attendance` - Enregistrer une présence

## 🛠️ Build et Installation

### Prérequis
- Android Studio 4.0+
- JDK 8+
- MorphoTablet 2 (MPH-MB001A)
- SDK Android API 21+

### Build
```bash
cd configtablette/rhApp-v2
./gradlew assembleDebug
```

L'APK sera générée dans : `app/build/outputs/apk/debug/rh-app-v2.apk`

### Installation
```bash
adb install app/build/outputs/apk/debug/rh-app-v2.apk
```

## 📊 Améliorations par rapport à V1

| Aspect | V1 | V2 | Amélioration |
|--------|----|----|--------------|
| **Stabilité capteur** | Instable | Retry automatique | ✅ Stable |
| **Chargement données** | Parfois échoue | Retry + cache | ✅ Fiable |
| **Matching** | Lent, parfois échoue | Optimisé, arrêt anticipé | ✅ Rapide |
| **Gestion erreurs** | Basique | Complète avec retry | ✅ Robuste |
| **Design** | Basique | Glassmorphisme + tricolore | ✅ Magnifique |
| **Fluidité** | Interruptions | Retry auto, retour auto | ✅ Fluide |

## 🚧 À Implémenter

- [ ] `EmployeeEnrollmentActivity` : Formulaire d'enregistrement complet (3 étapes)
- [ ] Gestion des erreurs réseau plus avancée
- [ ] Mode hors-ligne avec synchronisation
- [ ] Logs et analytics

## 📝 Notes Techniques

- **SDK MorphoSmart** : Version 6.19.4.0
- **Min SDK** : 21 (Android 5.0+)
- **Target SDK** : 30
- **Compile SDK** : 30

## 🔍 Debugging

Les logs sont préfixés avec les tags suivants :
- `RHApplication` : Application globale
- `DeviceManager` : Gestion du capteur
- `DataManager` : Chargement des données
- `LoadingActivity` : Écran de démarrage
- `AttendanceActivity` : Marquer présence
- `AuthActivity` : Authentification

---

**Version** : 1.0.0  
**Date** : Décembre 2025  
**Plateforme** : Android 5.0+ (API 21+)  
**Matériel** : MorphoTablet 2 (MPH-MB001A)

