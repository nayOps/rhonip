# 📊 Analyse du SDK MorphoTablet

## 📦 Contenu du SDK

### 🎯 Composants Principaux

1. **MorphoSmart SDK 6.19.4.0** 👆
   - Localisation : `SDKs/MorphoSmart_SDK_6.19.4.0/`
   - Fichier JAR : `Code_Samples/Main_Demo/MorphoSmart_SDK_6.19.4.0/MorphoSmart_SDK_6.19.4.0.jar`
   - **Fonction** : SDK pour la capture et la vérification d'empreintes digitales
   - **Plateforme** : Android

2. **MobIris SDK 1.2.10** 👁️
   - Localisation : `SDKs/MobIris_SDK_1.2.10/`
   - **Fonction** : SDK pour la capture d'iris
   - Contient : `.so` natifs, headers `.h`, documentation

3. **Exemples de Code Complets** 💻
   - `Main_Demo` : Application démo complète avec tous les périphériques
   - `IrisSensor_Demo` : Démonstration capteur d'iris
   - `Multi_SIM_Demo` : Démonstration multi-SIM

4. **Documentation** 📖
   - Guide de programmation CSP
   - Guide de description CSP
   - Guide de personnalisation
   - Manuel opérateur (PDF)

---

## 🔑 APIs Essentielles

### 1️⃣ **API Empreintes Digitales (MorphoSmart SDK)**

#### Classe Principale : `MorphoDevice`

**Initialisation :**
```java
import com.morpho.android.usb.USBManager;
import com.morpho.morphosmart.sdk.MorphoDevice;

// Initialiser le gestionnaire USB (wakeLock TOUJOURS true sur MorphoTablet)
USBManager.getInstance().initialize(context, "com.morpho.morphosample.USB_ACTION", true);

// Créer l'instance du périphérique
MorphoDevice morphoDevice = new MorphoDevice();
Integer nbUsbDevice = new Integer(0);

// Énumérer les périphériques USB
int ret = morphoDevice.initUsbDevicesNameEnum(nbUsbDevice);

if (ret == ErrorCodes.MORPHO_OK && nbUsbDevice == 1) {
    String sensorName = morphoDevice.getUsbDeviceName(0);
    ret = morphoDevice.openUsbDevice(sensorName, 0);
}
```

**Capture d'Empreinte :**
```java
import com.morpho.morphosmart.sdk.*;

// Paramètres de capture
int timeout = 30; // secondes
int acquisitionThreshold = 0;
int fingerNumber = 1; // Nombre de doigts à capturer
TemplateType templateType = TemplateType.MORPHO_PK_ISO_FMR;
TemplateFVPType templateFVPType = TemplateFVPType.MORPHO_NO_PK_FVP;
int maxSizeTemplate = 512;
EnrollmentType enrollType = EnrollmentType.ONE_ACQUISITIONS;
LatentDetection latentDetection = LatentDetection.LATENT_DETECT_ENABLE;
Coder coderChoice = Coder.MORPHO_DEFAULT_CODER;

int detectMode = DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue()
                | DetectionMode.MORPHO_FORCE_FINGER_ON_TOP_DETECT_MODE.getValue();

TemplateList templateList = new TemplateList();

// Callbacks pour feedback visuel
int callbackCmd = CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue()
                | CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue()
                | CallbackMask.MORPHO_CALLBACK_CODEQUALITY.getValue()
                | CallbackMask.MORPHO_CALLBACK_DETECTQUALITY.getValue();

// Capturer
int result = morphoDevice.capture(
    timeout, 
    acquisitionThreshold, 
    0, // advancedSecurityLevelsRequired
    fingerNumber, 
    templateType, 
    templateFVPType, 
    maxSizeTemplate, 
    enrollType,
    latentDetection, 
    coderChoice, 
    detectMode, 
    templateList, 
    callbackCmd, 
    observerCallback
);

if (result == ErrorCodes.MORPHO_OK) {
    // Récupérer le template capturé
    Template template = templateList.getTemplate(0);
    byte[] templateData = template.getTemplate();
    
    // Sauvegarder ou envoyer au backend
    saveToBackend(templateData);
}
```

**Vérification d'Empreinte :**
```java
// Pour vérifier une empreinte contre une référence
int result = morphoDevice.verify(
    referenceTemplate,
    timeout,
    matchingThreshold,
    // ... autres paramètres
);

if (result == ErrorCodes.MORPHO_OK) {
    // Match réussi !
}
```

**Fermeture :**
```java
morphoDevice.cancelLiveAcquisition();
morphoDevice.closeDevice();
morphoDevice = null;
```

---

### 2️⃣ **API Caméra (Android Standard)**

Le SDK utilise l'API Android standard pour la caméra.

**Exemple de Capture Photo :**
```java
import android.hardware.Camera;

// Ouvrir la caméra (0 = arrière, 1 = avant)
Camera camera = Camera.open(0);

// Configurer les paramètres
Camera.Parameters params = camera.getParameters();
params.setPictureSize(1920, 1080); // Résolution
params.setJpegQuality(100); // Qualité JPEG
params.setRotation(0); // Rotation si nécessaire

// Pour caméra frontale
if (facing == Camera.CameraInfo.CAMERA_FACING_FRONT) {
    camera.setDisplayOrientation(180);
    params.setRotation(180);
    params.setPictureSize(1600, 1200);
}

camera.setParameters(params);

// Prendre une photo
camera.takePicture(null, null, new Camera.PictureCallback() {
    @Override
    public void onPictureTaken(byte[] data, Camera camera) {
        // data contient l'image JPEG
        File photoFile = new File("/sdcard/photo.jpg");
        FileOutputStream fos = new FileOutputStream(photoFile);
        fos.write(data);
        fos.close();
        
        // Redémarrer le preview
        camera.startPreview();
    }
});
```

---

## 🏗️ Architecture Recommandée pour l'Application ONIP

### Structure de l'Application Android

```
ONIPBiometricApp/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/onip/biometric/
│   │   │   │   ├── MainActivity.java
│   │   │   │   ├── activities/
│   │   │   │   │   ├── EmployeeEnrollmentActivity.java
│   │   │   │   │   ├── AttendanceActivity.java
│   │   │   │   ├── services/
│   │   │   │   │   ├── BiometricService.java (Wrapper pour MorphoSmart SDK)
│   │   │   │   │   ├── CameraService.java
│   │   │   │   │   ├── ApiService.java (Communication avec backend)
│   │   │   │   ├── models/
│   │   │   │   │   ├── Employee.java
│   │   │   │   │   ├── BiometricData.java
│   │   │   │   ├── utils/
│   │   │   │   │   ├── NetworkUtils.java
│   │   │   │   │   ├── StorageUtils.java
│   │   │   ├── res/
│   │   │   │   ├── layout/
│   │   │   │   ├── values/
│   │   │   ├── AndroidManifest.xml
│   ├── libs/
│   │   ├── MorphoSmart_SDK_6.19.4.0.jar
│   ├── build.gradle
├── build.gradle
├── settings.gradle
```

---

## 📋 Workflow Complet : Enregistrement Employé

### Étape 1 : Capture Photo
```java
public class EmployeeEnrollmentActivity extends Activity {
    
    private Camera camera;
    private byte[] capturedPhoto;
    
    public void captureEmployeePhoto() {
        camera = Camera.open(1); // Caméra frontale
        // Configuration...
        
        camera.takePicture(null, null, new Camera.PictureCallback() {
            @Override
            public void onPictureTaken(byte[] data, Camera camera) {
                capturedPhoto = data;
                showPhotoPreview(data);
                moveToFingerprintCapture();
            }
        });
    }
}
```

### Étape 2 : Capture Empreintes (4 doigts)
```java
private void captureFingerprintSequence() {
    // Capturer 4 empreintes en séquence
    String[] fingers = {"Index Gauche", "Index Droit", "Pouce Gauche", "Pouce Droit"};
    byte[][] fingerprintTemplates = new byte[4][];
    
    for (int i = 0; i < 4; i++) {
        showInstructions("Placez votre " + fingers[i] + " sur le capteur");
        fingerprintTemplates[i] = captureFingerprint(i);
    }
    
    // Une fois toutes les empreintes capturées
    sendToBackend(capturedPhoto, fingerprintTemplates);
}

private byte[] captureFingerprint(int fingerIndex) {
    TemplateList templateList = new TemplateList();
    
    int result = morphoDevice.capture(
        30, // timeout
        0,  // threshold
        0,  // security level
        1,  // fingerNumber
        TemplateType.MORPHO_PK_ISO_FMR,
        TemplateFVPType.MORPHO_NO_PK_FVP,
        512, // maxSize
        EnrollmentType.ONE_ACQUISITIONS,
        LatentDetection.LATENT_DETECT_ENABLE,
        Coder.MORPHO_DEFAULT_CODER,
        DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue(),
        templateList,
        CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue(),
        observer
    );
    
    if (result == ErrorCodes.MORPHO_OK) {
        return templateList.getTemplate(0).getTemplate();
    }
    
    return null;
}
```

### Étape 3 : Envoi au Backend
```java
import okhttp3.*;
import org.json.JSONObject;

public class ApiService {
    
    private static final String API_URL = "https://rh.onip.local/api";
    private OkHttpClient client = new OkHttpClient();
    
    public void enrollEmployee(byte[] photo, byte[][] fingerprints, String employeeId) {
        try {
            // Créer le corps multipart
            MultipartBody.Builder builder = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("employeeId", employeeId)
                .addFormDataPart("photo", "photo.jpg",
                    RequestBody.create(MediaType.parse("image/jpeg"), photo));
            
            // Ajouter les empreintes
            for (int i = 0; i < fingerprints.length; i++) {
                String encodedFingerprint = Base64.encodeToString(fingerprints[i], Base64.DEFAULT);
                builder.addFormDataPart("fingerprint_" + i, encodedFingerprint);
            }
            
            RequestBody requestBody = builder.build();
            
            Request request = new Request.Builder()
                .url(API_URL + "/biometric/enroll")
                .post(requestBody)
                .build();
            
            Response response = client.newCall(request).execute();
            
            if (response.isSuccessful()) {
                showSuccess("Employé enregistré avec succès !");
            }
            
        } catch (Exception e) {
            showError("Erreur : " + e.getMessage());
        }
    }
}
```

---

## 🎯 Workflow Complet : Pointage

### Vérification d'Empreinte
```java
public class AttendanceActivity extends Activity {
    
    public void checkIn() {
        showMessage("Placez votre doigt sur le capteur");
        
        // Capturer l'empreinte
        byte[] capturedFingerprint = captureFingerprint(0);
        
        if (capturedFingerprint != null) {
            // Envoyer au backend pour vérification
            verifyAndCheckIn(capturedFingerprint);
        }
    }
    
    private void verifyAndCheckIn(byte[] fingerprint) {
        try {
            String encodedFingerprint = Base64.encodeToString(fingerprint, Base64.DEFAULT);
            
            JSONObject json = new JSONObject();
            json.put("fingerprint", encodedFingerprint);
            json.put("action", "checkin");
            json.put("timestamp", System.currentTimeMillis());
            
            RequestBody body = RequestBody.create(
                MediaType.parse("application/json"),
                json.toString()
            );
            
            Request request = new Request.Builder()
                .url(API_URL + "/biometric/verify")
                .post(body)
                .build();
            
            Response response = client.newCall(request).execute();
            
            if (response.isSuccessful()) {
                JSONObject result = new JSONObject(response.body().string());
                
                if (result.getBoolean("matched")) {
                    String employeeName = result.getString("employee_name");
                    showSuccess("Bienvenue " + employeeName + " !\nPointage enregistré.");
                } else {
                    showError("Empreinte non reconnue");
                }
            }
            
        } catch (Exception e) {
            showError("Erreur : " + e.getMessage());
        }
    }
}
```

---

## 📚 Fichiers de Référence du SDK

### Exemples à Étudier

1. **Capture d'Empreintes** :
   - `Code_Samples/Main_Demo/cbm_demo/src/main/java/com/morpho/cbm_demo/CbmCaptureFragment.java`
   - Montre comment initialiser le périphérique, capturer et sauvegarder

2. **Vérification d'Empreintes** :
   - `Code_Samples/Main_Demo/cbm_demo/src/main/java/com/morpho/cbm_demo/CbmVerifyFragment.java`
   - Montre comment comparer une empreinte capturée avec une référence

3. **Caméra** :
   - `Code_Samples/Main_Demo/camera_demo/src/main/java/com/morpho/camera_demo/CameraMainActivity.java`
   - Exemple complet de capture photo avec preview

4. **Gestion USB** :
   - Tous les exemples montrent comment gérer correctement l'USB

---

## 🔧 Configuration Requise

### build.gradle (Module app)

```gradle
android {
    compileSdkVersion 28
    
    defaultConfig {
        applicationId "com.onip.biometric"
        minSdkVersion 21
        targetSdkVersion 28
        versionCode 1
        versionName "1.0"
    }
    
    packagingOptions {
        exclude 'META-INF/DEPENDENCIES'
        exclude 'META-INF/LICENSE'
        exclude 'META-INF/NOTICE'
    }
}

dependencies {
    implementation fileTree(dir: 'libs', include: ['*.jar'])
    implementation files('libs/MorphoSmart_SDK_6.19.4.0.jar')
    
    // HTTP Client
    implementation 'com.squareup.okhttp3:okhttp:4.9.0'
    
    // JSON
    implementation 'org.json:json:20210307'
    
    // UI
    implementation 'androidx.appcompat:appcompat:1.3.1'
    implementation 'com.google.android.material:material:1.4.0'
}
```

### AndroidManifest.xml

```xml
<manifest>
    <!-- Permissions -->
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    
    <uses-feature android:name="android.hardware.camera" />
    <uses-feature android:name="android.hardware.usb.host" />
    
    <application>
        <!-- Activities -->
        <activity android:name=".MainActivity" />
        <activity android:name=".activities.EmployeeEnrollmentActivity" />
        <activity android:name=".activities.AttendanceActivity" />
    </application>
</manifest>
```

---

## 🚀 Prochaines Étapes

1. ✅ **Analyse SDK** - TERMINÉ
2. ⏭️ **Créer Projet Android Studio**
3. ⏭️ **Intégrer MorphoSmart SDK**
4. ⏭️ **Développer Interface Enregistrement Employé**
5. ⏭️ **Développer Interface Pointage**
6. ⏭️ **Connecter au Backend ONIP**
7. ⏭️ **Tests sur Tablette Réelle**
8. ⏭️ **Déploiement**

---

## 📞 Support

- Documentation : `Documentation/MorphoTablet_CSP_Programming_Guide.html`
- Exemples APK : `Demo_APK/Main_Demo_2.8.apk`
- Code Source : `Code_Samples/Main_Demo/`

---

**Date d'Analyse** : {{ date }}  
**Version SDK** : MorphoSmart 6.19.4.0  
**Plateforme** : Android (Min SDK 21)

