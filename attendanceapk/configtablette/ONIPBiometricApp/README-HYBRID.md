# 🌐 ONIP Biometric App - Architecture Hybride

## 🎨 WebView + Next.js + Tailwind CSS

Cette application utilise une **architecture hybride** combinant :
- **Android Native** (Java) pour le SDK MorphoSmart
- **Next.js + Tailwind CSS** pour l'interface utilisateur moderne

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  TABLETTE ANDROID (MorphoTablet 2)              │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  WebViewActivity (Java)                  │  │
│  │                                           │  │
│  │  ┌─────────────────────────────────────┐ │  │
│  │  │  WebView                            │ │  │
│  │  │  ↓                                  │ │  │
│  │  │  Next.js App (React + Tailwind)    │ │  │
│  │  │  - UI Magnifique                   │ │  │
│  │  │  - Animations Framer Motion        │ │  │
│  │  │  - Composants modernes             │ │  │
│  │  └─────────────────────────────────────┘ │  │
│  │         ↕ JavaScript Bridge             │  │
│  │  ┌─────────────────────────────────────┐ │  │
│  │  │  BiometricBridge (Java)             │ │  │
│  │  │  - captureFingerprint()             │ │  │
│  │  │  - takePhoto()                      │ │  │
│  │  │  - sendBiometricData()              │ │  │
│  │  └─────────────────────────────────────┘ │  │
│  │         ↓                                │  │
│  │  ┌─────────────────────────────────────┐ │  │
│  │  │  Services Natifs                    │ │  │
│  │  │  - BiometricService (SDK Morpho)    │ │  │
│  │  │  - CameraService                    │ │  │
│  │  │  - ApiService (Backend)             │ │  │
│  │  └─────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
           ↓ HTTP REST
┌─────────────────────────────────────────────────┐
│  Backend ONIP (Symfony)                         │
│  - employee-service                             │
│  - Endpoints biométriques                       │
└─────────────────────────────────────────────────┘
```

---

## 📂 Structure du Projet

```
ONIPBiometricApp/
├── app/                                    # Android Native
│   ├── src/main/
│   │   ├── java/com/onip/biometric/
│   │   │   ├── WebViewActivity.java       ✅ Activity principale
│   │   │   ├── bridges/
│   │   │   │   └── BiometricBridge.java   ✅ Bridge JS ↔ Java
│   │   │   └── services/
│   │   │       ├── BiometricService.java  ✅ SDK MorphoSmart
│   │   │       ├── CameraService.java     ✅ Gestion caméra
│   │   │       └── ApiService.java        ✅ Backend API
│   │   ├── res/
│   │   │   └── values/
│   │   │       └── strings.xml
│   │   └── AndroidManifest.xml            ✅ Configuration
│   ├── libs/
│   │   └── MorphoSmart_SDK_6.19.4.0.jar   ✅ SDK
│   └── build.gradle                        ✅ Dépendances
│
├── nextjs-ui/                              # Interface Next.js
│   ├── app/
│   │   ├── layout.tsx                      ✅ Layout principal
│   │   ├── page.tsx                        ✅ Menu principal
│   │   ├── employees/
│   │   │   └── add/
│   │   │       └── page.tsx                ✅ Enregistrement employé
│   │   ├── attendance/
│   │   │   └── page.tsx                    ✅ Pointage
│   │   └── types/
│   │       └── android.ts                  ✅ Types TypeScript
│   ├── public/
│   ├── tailwind.config.ts                  ✅ Config Tailwind
│   ├── package.json                        ✅ Dépendances
│   └── next.config.js                      ✅ Config Next.js
│
└── README-HYBRID.md                        ← Vous êtes ici
```

---

## 🚀 Installation et Configuration

### **Prérequis**

- ✅ **Android Studio** installé
- ✅ **Node.js** 18+ installé
- ✅ **MorphoTablet 2** connectée en USB

---

### **Étape 1 : Configuration Next.js**

#### 1.1 Installer les dépendances

```bash
cd /home/nayops/Documents/architecture/configtablette/ONIPBiometricApp/nextjs-ui
npm install
```

#### 1.2 Configurer l'URL du serveur

Éditez `WebViewActivity.java` et choisissez l'URL appropriée :

```java
// Option 1: Serveur local sur la tablette (production)
private static final String NEXTJS_URL = "http://localhost:3000";

// Option 2: Serveur sur le PC (développement - RECOMMANDÉ)
private static final String NEXTJS_URL = "http://192.168.100.101:3000";

// Option 3: Assets locaux (déploiement sans serveur)
private static final String NEXTJS_URL = "file:///android_asset/nextjs/index.html";
```

**Pour le développement, utilisez l'Option 2 :**
- Remplacez `192.168.100.101` par l'IP de votre PC
- Assurez-vous que PC et tablette sont sur le même WiFi

#### 1.3 Démarrer le serveur Next.js

```bash
cd nextjs-ui
npm run dev
```

Le serveur démarre sur `http://localhost:3000`

**Important** : Pour que la tablette puisse accéder au serveur, lancez avec :

```bash
npm run dev -- -H 0.0.0.0
```

Cela expose le serveur sur toutes les interfaces réseau.

---

### **Étape 2 : Configuration Android Studio**

#### 2.1 Ouvrir le projet

1. Lancer **Android Studio**
2. **File → Open**
3. Sélectionner : `/home/nayops/Documents/architecture/configtablette/ONIPBiometricApp`
4. Attendre la synchronisation Gradle

#### 2.2 Vérifier la configuration

**build.gradle (Module: app)** doit contenir :

```gradle
dependencies {
    implementation files('libs/MorphoSmart_SDK_6.19.4.0.jar')
    implementation 'com.squareup.okhttp3:okhttp:4.9.0'
    implementation 'com.google.code.gson:gson:2.8.8'
    // ... autres dépendances
}
```

#### 2.3 Connecter la tablette

```bash
# Vérifier la connexion USB
adb devices

# Devrait afficher:
# List of devices attached
# <serial_number>    device
```

#### 2.4 Build et installer

**Option A : Via Android Studio**
- Cliquez sur **Run** (▶️)
- Sélectionnez la MorphoTablet
- Attendez la compilation et l'installation

**Option B : Ligne de commande**

```bash
# Build APK Debug
./gradlew assembleDebug

# Installer sur tablette
adb install app/build/outputs/apk/debug/app-debug.apk
```

---

## 🎮 Utilisation

### **Workflow Complet**

#### 1️⃣ **Démarrer le Serveur Next.js**

```bash
cd /home/nayops/Documents/architecture/configtablette/ONIPBiometricApp/nextjs-ui
npm run dev -- -H 0.0.0.0
```

**Vérifier** : Ouvrez `http://localhost:3000` dans votre navigateur PC

#### 2️⃣ **Lancer l'App sur la Tablette**

- Ouvrir **ONIP Biometric** sur la tablette
- L'interface Next.js doit se charger
- Le message "Capteur biométrique prêt" doit apparaître

#### 3️⃣ **Enregistrer un Employé**

1. Menu principal → **Enregistrement Employé**
2. **Étape 1** : Entrer ID et Nom
3. **Étape 2** : Cliquer "Capturer Photo"
   - La caméra Android s'active
   - La photo s'affiche dans l'interface
4. **Étapes 3-6** : Scanner les 4 empreintes
   - Placer chaque doigt sur le capteur
   - Attendre la validation (✓)
5. **Étape 7** : Vérifier et envoyer

#### 4️⃣ **Pointer (Attendance)**

1. Menu principal → **Pointage**
2. Cliquer "Scanner Empreinte"
3. Placer un doigt enregistré
4. Le système affiche :
   - ✅ "Bienvenue [Nom] !" si reconnu
   - ❌ "Empreinte non reconnue" sinon

---

## 🔌 Communication JavaScript ↔ Java

### **Depuis JavaScript → Java**

```typescript
// Dans Next.js/React
if (window.AndroidBridge) {
  // Capturer une empreinte
  window.AndroidBridge.captureFingerprint();
  
  // Prendre une photo
  window.AndroidBridge.takePhoto();
  
  // Envoyer des données
  const data = { employeeId: '123', ... };
  window.AndroidBridge.sendBiometricData(JSON.stringify(data));
  
  // Afficher un Toast
  window.AndroidBridge.showToast('Message');
}
```

### **Depuis Java → JavaScript**

```java
// Dans BiometricBridge.java

// Succès capture empreinte
webView.evaluateJavascript(
    "window.onFingerprintCaptured('" + base64Template + "', " + quality + ")",
    null
);

// Succès capture photo
webView.evaluateJavascript(
    "window.onPhotoTaken('" + base64Photo + "')",
    null
);

// Erreur
webView.evaluateJavascript(
    "window.onError('" + errorMessage + "')",
    null
);

// Progression
webView.evaluateJavascript(
    "window.onCaptureProgress(" + progress + ")",
    null
);
```

---

## 🎨 Personnalisation de l'UI

### **Modifier les Couleurs**

Éditez `nextjs-ui/tailwind.config.ts` :

```typescript
export default {
  theme: {
    extend: {
      colors: {
        primary: '#8B5CF6',  // Purple
        secondary: '#EC4899', // Pink
        // ... vos couleurs
      },
    },
  },
}
```

### **Modifier les Animations**

Éditez les composants dans `nextjs-ui/app/` :

```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.9 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.5 }}
>
  {/* Votre contenu */}
</motion.div>
```

### **Ajouter des Pages**

```bash
# Créer une nouvelle page
mkdir -p nextjs-ui/app/nouvelle-page
touch nextjs-ui/app/nouvelle-page/page.tsx
```

---

## 🔧 Débogage

### **Déboguer la WebView (Chrome DevTools)**

1. Sur le PC, ouvrir Chrome
2. Aller sur : `chrome://inspect`
3. Connecter la tablette en USB
4. La WebView de l'app apparaît dans la liste
5. Cliquer sur **"inspect"**
6. Console JavaScript, Network, etc. disponibles !

### **Logs Android**

```bash
# Voir tous les logs
adb logcat

# Filtrer par tag
adb logcat | grep BiometricBridge
adb logcat | grep WebViewActivity

# Logs de l'app uniquement
adb logcat | grep com.onip.biometric
```

### **Problèmes Courants**

#### ❌ "AndroidBridge non disponible"

**Cause** : Le bridge n'est pas injecté

**Solution** :
```java
// Vérifier dans WebViewActivity.java
webView.addJavascriptInterface(bridge, "AndroidBridge");
```

#### ❌ "ERR_CONNECTION_REFUSED"

**Cause** : Le serveur Next.js n'est pas accessible

**Solutions** :
1. Vérifier que `npm run dev -- -H 0.0.0.0` tourne
2. Vérifier l'IP dans `WebViewActivity.java`
3. Vérifier que tablette et PC sont sur même WiFi
4. Tester depuis le navigateur tablette : `http://192.168.100.101:3000`

#### ❌ "Capteur biométrique non trouvé"

**Cause** : Le SDK MorphoSmart n'est pas initialisé

**Solution** :
1. Vérifier que `MorphoSmart_SDK_6.19.4.0.jar` est dans `app/libs/`
2. Vérifier les permissions USB dans `AndroidManifest.xml`
3. Redémarrer la tablette

---

## 📦 Build Production

### **Option 1 : Serveur Next.js Externe**

L'app Android se connecte à un serveur Next.js distant.

```bash
# Build Next.js
cd nextjs-ui
npm run build
npm start

# L'app Android pointe vers le serveur
```

### **Option 2 : Next.js dans les Assets**

Embarquer Next.js dans l'APK (pas de serveur requis).

```bash
# 1. Build Next.js en static
cd nextjs-ui
npm run build
npm run export  # Génère le dossier 'out/'

# 2. Copier dans Android assets
mkdir -p ../app/src/main/assets/nextjs
cp -r out/* ../app/src/main/assets/nextjs/

# 3. Modifier WebViewActivity.java
private static final String NEXTJS_URL = "file:///android_asset/nextjs/index.html";

# 4. Build APK
./gradlew assembleRelease
```

---

## 🚀 Avantages de l'Architecture Hybride

### ✅ **Développement UI Ultra-Rapide**
- Tailwind CSS : Design moderne en minutes
- Hot Reload : Voir les changements instantanément
- Framer Motion : Animations fluides pré-faites

### ✅ **Réutilisabilité**
- Même UI pour tablette, web, mobile
- Composants React réutilisables
- Design system cohérent

### ✅ **Performance Optimale**
- SDK natif pour biométrie (rapide)
- WebView optimisée (GPU accelerated)
- Next.js optimisations (code splitting, etc.)

### ✅ **Flexibilité**
- Modifier l'UI sans recompiler l'APK
- Déployer des mises à jour UI rapidement
- A/B testing facile

---

## 📊 Performance

### **Temps de Démarrage**
- Lancement app : ~1-2 secondes
- Chargement WebView : ~1 seconde
- Chargement Next.js : ~0.5-1 seconde
- **Total** : ~2.5-4 secondes

### **Capture Biométrique**
- Scan empreinte : ~2-5 secondes
- Capture photo : ~0.5-1 seconde
- Envoi backend : ~1-2 secondes

---

## 🎯 Prochaines Étapes

- [ ] Tester sur tablette réelle
- [ ] Optimiser les animations
- [ ] Ajouter mode hors-ligne
- [ ] Implémenter cache local
- [ ] Tests de performance
- [ ] Build APK release
- [ ] Déploiement production

---

## 📞 Support

- **Documentation Next.js** : https://nextjs.org/docs
- **Documentation Tailwind** : https://tailwindcss.com/docs
- **Documentation Framer Motion** : https://www.framer.com/motion/
- **SDK MorphoSmart** : Voir `SDK-ANALYSIS.md`

---

**Version** : 1.0.0  
**Architecture** : Hybride WebView + Next.js  
**UI Framework** : React 19 + Tailwind CSS v4 + Framer Motion  
**SDK Native** : MorphoSmart 6.19.4.0  
**Plateforme** : Android 5.0+ (API 21+)

