# Séparation des Applications - Attendance et Enroll

## 📁 Structure

Deux applications Android distinctes ont été créées :

```
configtablette/
├── attendance/          # Application 1 : Marquer Présence
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/onip/attendance/
│   │   │   │   ├── AttendanceApplication.java
│   │   │   │   ├── activities/
│   │   │   │   │   ├── LoadingActivity.java
│   │   │   │   │   └── AttendanceActivity.java
│   │   │   │   ├── services/
│   │   │   │   │   ├── DeviceManager.java
│   │   │   │   │   ├── DataManager.java
│   │   │   │   │   └── AttendanceService.java
│   │   │   │   ├── models/
│   │   │   │   │   └── Employee.java
│   │   │   │   ├── utils/
│   │   │   │   │   ├── ConfigManager.java
│   │   │   │   │   └── RetryHelper.java
│   │   │   │   └── fingerprint/
│   │   │   │       └── FingerprintProcessObserver.java
│   │   │   └── res/
│   │   └── libs/        # SDK MorphoSmart
│   └── build.gradle
│
└── enroll/              # Application 2 : Enregistrer Employé
    ├── app/
    │   ├── src/main/
    │   │   ├── java/com/onip/enroll/
    │   │   │   ├── EnrollApplication.java
    │   │   │   ├── activities/
    │   │   │   │   ├── LoadingActivity.java
    │   │   │   │   ├── AuthActivity.java
    │   │   │   │   └── EmployeeEnrollmentActivity.java (stub)
    │   │   │   ├── services/
    │   │   │   │   ├── DeviceManager.java
    │   │   │   │   └── DataManager.java
    │   │   │   ├── models/
    │   │   │   │   └── Employee.java
    │   │   │   ├── utils/
    │   │   │   │   ├── ConfigManager.java
    │   │   │   │   └── RetryHelper.java
    │   │   │   └── fingerprint/
    │   │   │       └── FingerprintProcessObserver.java
    │   │   └── res/
    │   └── libs/        # SDK MorphoSmart
    └── build.gradle
```

## 🎯 Application ATTENDANCE

### Objectif
Application dédiée uniquement à la marque de présence.

### Flux
1. **LoadingActivity** : Initialise le capteur et charge les données
2. **AttendanceActivity** : Capture empreinte → Matching → Enregistrement présence

### Fonctionnalités
- ✅ Capture automatique d'empreinte
- ✅ Matching optimisé (Index_Droit, Pouce_Droit, Index_Gauche)
- ✅ Vérification présence complète (2 max/jour)
- ✅ Enregistrement automatique
- ✅ Retry automatique en cas d'échec
- ✅ Retour automatique après succès

### APK
- Nom : `attendance.apk`
- Package : `com.onip.attendance`

## 🎯 Application ENROLL

### Objectif
Application dédiée uniquement à l'enregistrement des nouveaux employés.

### Flux
1. **LoadingActivity** : Initialise le capteur et charge les données
2. **AuthActivity** : Authentification super_admin
3. **EmployeeEnrollmentActivity** : Formulaire 3 étapes (stub - à implémenter)

### Fonctionnalités
- ✅ Authentification super_admin obligatoire
- ⏳ Formulaire 3 étapes (à implémenter)
- ⏳ Capture multiple d'empreintes (à implémenter)
- ⏳ Vérification doublons (à implémenter)

### APK
- Nom : `enroll.apk`
- Package : `com.onip.enroll`

## 🔧 Composants Partagés

Les deux applications partagent les mêmes composants de base :
- **Models** : `Employee.java`
- **Utils** : `ConfigManager.java`, `RetryHelper.java`
- **Services** : `DeviceManager.java`, `DataManager.java`
- **Fingerprint** : `FingerprintProcessObserver.java`
- **Resources** : Drawables, styles, couleurs RDC

## 🚀 Build

### Attendance
```bash
cd configtablette/attendance
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/attendance.apk
```

### Enroll
```bash
cd configtablette/enroll
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/enroll.apk
```

## 📝 Notes

- Les deux applications partagent la même configuration backend (IP/Port via `ConfigManager`)
- Chaque application a son propre `Application` class pour gérer les données globales
- Les layouts et ressources sont adaptés pour chaque application
- `EmployeeEnrollmentActivity` est un stub à implémenter complètement

## ✅ Statut

- ✅ Structure créée
- ✅ Fichiers communs copiés et adaptés
- ✅ Applications créées
- ✅ LoadingActivity adaptés
- ✅ AndroidManifest créés
- ✅ **Compilation réussie pour les deux applications**
- ✅ **APK générés : attendance.apk et enroll.apk**
- ⏳ EmployeeEnrollmentActivity (stub - à implémenter)
- ⏳ Tests sur tablette

## 🎉 Compilation Réussie

Les deux applications compilent avec succès :

```bash
# Attendance
cd attendance && ./gradlew assembleDebug
# ✅ BUILD SUCCESSFUL
# APK: app/build/outputs/apk/debug/attendance.apk

# Enroll
cd enroll && ./gradlew assembleDebug
# ✅ BUILD SUCCESSFUL
# APK: app/build/outputs/apk/debug/enroll.apk
```

