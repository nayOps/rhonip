# FAP60 SDK — Intégration FGP / Device Bridge

> Référence consolidée à partir du manuel API FAP60 (v1.0.02) et de l’intégration actuelle dans `device-bridge/`.  
> Voir aussi : [Sprint 0 — Guichet](sprint-0-guichet.md), [OpenAPI Device Bridge](device-bridge.openapi.yaml).

---

## Sommaire

1. [Vue d’ensemble](#1-vue-densemble)
2. [Prérequis système](#2-prérequis-système)
3. [Contenu du SDK et DLL](#3-contenu-du-sdk-et-dll)
4. [Deux familles d’API](#4-deux-familles-dapi)
5. [Ce que FGP utilise aujourd’hui](#5-ce-que-fgp-utilise-aujourdhui)
6. [Licence algorithme (zzAuth / zzInit)](#6-licence-algorithme-zzauth--zzinit)
7. [API Device (FAP60-02.dll)](#7-api-device-fap60-02dll)
8. [API Algorithme (fingerprint.dll)](#8-api-algorithme-fingerprintdll)
9. [Codes position des doigts](#9-codes-position-des-doigts)
10. [Codes d’erreur](#10-codes-derreur)
11. [Configuration FGP](#11-configuration-fgp)
12. [Dépannage](#12-dépannage)

---

## 1. Vue d’ensemble

Le SDK FAP60 fournit :

- **Capture matérielle** : images plateau, découpe par doigt, vidéo live, rouleau, calibration.
- **Traitement biométrique** : NFIQ, extraction de minuties (ANSI / ISO), comparaison, recherche 1:N, compression WSQ/JPEG2000.

Dans FGP, le poste guichet Windows exécute un **Device Bridge** (.NET 8) qui encapsule les appels P/Invoke ; le frontend et Django ne chargent jamais les DLL directement.

```
Navigateur (Next.js)
    → fingerprint_service :8010 (optionnel)
    → Device Bridge :8765 (Windows, poste guichet)
        → FAP60-02.dll      (device)
        → fingerprint.dll   (algorithme + licence)
        → DLL dépendantes   (CS_FAP, MXLicenseAPI, VC++ runtime, …)
```

---

## 2. Prérequis système

| Élément | Exigence |
|--------|----------|
| OS | Windows 10+ (32 ou 64 bits) |
| Outils dev | Visual Studio 2015+ / .NET 8 pour le bridge |
| CPU | Intel Core i5 ou équivalent |
| RAM | 8 Go minimum |
| Interface PC | Port série virtuel (selon driver fournisseur) |
| Bridge FGP | .NET 8, mode `fap60`, dossier SDK x64 complet |

---

## 3. Contenu du SDK et DLL

Structure officielle du kit :

| Chemin | Description |
|--------|-------------|
| `/include` | Fichiers `.h` |
| `/bin/bin32` | Bibliothèques 32 bits |
| `/bin/bin64` | Bibliothèques 64 bits |
| `/samplecode/Cplusplus` | Démo |
| `/Doc` | Manuel API |

### DLL et rôles

| Fichier | Rôle |
|---------|------|
| **FAP60-02.dll** | Driver / API device : open, capture, video, calibration |
| **fingerprint.dll** | Algorithme : licence, NFIQ, minuties, segmentation, compression |
| CS_FAP.dll | Dépendance |
| CsImgDll.dll | Dépendance |
| MXDev.dll | Dépendance device |
| **MXLicenseAPI.dll** | Gestion licence (lié à `zzAuth` / fichiers d’auth) |
| mxRollFinger.dll | Capture rouleau |
| devrun.dll | Runtime device |
| mfc140.dll, mfc140u.dll | Runtime MFC |
| msvcp140.dll, vcruntime140.dll | Runtime Visual C++ |

**Important :** copier **toutes** les DLL de `bin/Bin64` (ou `FAP60Demo/Bin64`) vers `device-bridge/sdk/fap60-x64/`, pas seulement trois fichiers. Un SDK incomplet provoque des erreurs obscures à l’exécution.

Scripts fournis :

```cmd
cd device-bridge\scripts
verify-fap60-sdk.cmd    REM compare bridge vs FAP60Demo\Bin64
copy-fap60-sdk.cmd      REM copie depuis Demo\Bin64 (prioritaire)
copy-fap60-sdk.ps1 -Force
```

### Alignement bridge ↔ FAP60Demo (vérifié sur poste guichet)

| Élément | Device Bridge | FAP60Demo |
|---------|---------------|-----------|
| **Dossier DLL** | `device-bridge/sdk/fap60-x64` | `...\FAP60Demo\Bin64` |
| **Config** | `appsettings` → `Fingerprint:SdkPath` | Répertoire de `FAP60Demo.exe` |
| **FAP60-02.dll** | Identique (même hash MD5) | ✓ |
| **fingerprint.dll** | Identique (même hash MD5) | ✓ |
| **MXOpenSSLDll.dll** | Peut manquer si copie ancienne | Présent dans Demo\Bin64 |
| **license.dat** | Optionnel dans `fap60-x64` | Souvent implicite via `zzInit(null,0)` depuis Bin64 |

Le bridge **ne charge pas** le dossier de la démo automatiquement : il utilise **`SdkPath`** (copie locale). Pour test strict, pointer temporairement :

```json
"SdkPath": "C:\\Users\\HYF\\Documents\\sdk\\FAP60 Windows CSharp SDKV2.0.14C-2025091817\\FAP60 Windows CSharp SDKV2.0.14C-2025091817\\samplecode\\FAP60Demo\\Bin64"
```

---

## 4. Deux familles d’API

| Famille | DLL | Initialisation | Usage typique |
|---------|-----|----------------|---------------|
| **Device** | `FAP60-02.dll` | `mxOpenDevice` / `closeDevice` | Capture, aperçu live, calibration |
| **Algorithme** | `fingerprint.dll` | **`zzInit` (licence obligatoire)** puis `zzFree` | NFIQ, minuties ISO/ANSI, ABIS, segmentation |

La démo C# (`FAP60Demo`) appelle **`zzInit(null, 0)` avant `mxOpenDevice`**. En pratique, cela ne fonctionne que si un **fichier ou bloc de licence valide** est déjà présent sur la machine ; sinon `zzInit` renvoie **-100004** (fichier d’autorisation introuvable).

**Capture d’images** : principalement API Device (`captureImage` / `captureImage_old`, `captureVideo`).  
**Qualité NFIQ / templates** : API Algorithme (`zzGetQualityNFIQScore`, `zzFingerprintFeatureExtract`, etc.) — nécessite `zzInit` réussi.

---

## 5. Ce que FGP utilise aujourd’hui

Implémentation : `device-bridge/src/Fgp.DeviceBridge.Api/Modules/Fap60/`.

| Fonction SDK | Wrapper bridge | Endpoint / usage |
|--------------|----------------|------------------|
| `zzInit` / `zzFree` | `Fap60Native` | À l’**open** / **close** device (si licence configurée) |
| `mxOpenDevice` | `Fap60FingerprintModule.OpenAsync` | `POST …/fingerprint/open` |
| `closeDevice` | `CloseAsync` | `POST …/fingerprint/close` |
| `captureImage_old` | `CaptureAsync` | `POST …/fingerprint/capture` |
| `captureVideo` | `GetPreviewFrameAsync` | `POST …/fingerprint/preview` |
| `mxCancleCapture` / `cancleCapture` | `CancelCapture` | Entre tentatives de capture |
| `zzGetQualityNFIQScore` | `Fap60ImageHelper.GetNfiq` | Après capture réussie |
| `getDeviceSN`, `getFirmwareVersion` | Open | Logs / health |

**Non encore intégré** (évolutions possibles) :

- `captureImage` (nom officiel, vs `_old` utilisé par la démo)
- `calibrationDevice`
- `captureRollImage` / `zzGetRollFinger`
- `zzFingerprintFeatureExtract` / `_Position` (templates ISO pour ABIS)
- `zzAuth` (obtention licence en ligne)

### Paramètres capture (alignés démo)

| Paramètre | Valeur FGP / démo |
|-----------|-------------------|
| `captureType` | `0` gauche 4, `1` droite 4, `3` deux pouces, `4` un doigt |
| `nMissNum` | Nombre de doigts absents (cases décochées) |
| `unTimeOutMs` | **15 000 ms par tentative** SDK ; budget total configurable (ex. 60 s) |
| `o_CaptureStatus` | Tableau **sortie** 10 entiers, initialisé à **0** |
| Retry | Boucle jusqu’au budget total (comme `FAP60Form._GetImage`) |

### Mapping doigts (bridge ↔ SDK)

| Position logique (bridge) | Index `g_CaptureType` (démo) |
|---------------------------|------------------------------|
| left_index | 0 |
| left_middle | 1 |
| left_ring | 2 |
| left_little | 3 |
| left_thumb | 4 |
| right_thumb | 5 |
| right_index | 6 |
| right_middle | 7 |
| right_ring | 8 |
| right_little | 9 |

Ordre buffer petites images (main gauche 4) : `left_little` → `left_ring` → `left_middle` → `left_index`.

---

## 6. Licence algorithme (zzAuth / zzInit)

### Flux officiel

1. **`zzAuth`** — contacte le serveur de licence (IP/port/user/key) et reçoit `szAuthInfo` (données liées au PC, max ~1080 octets).
2. **`zzInit(szLicenseData, iLicenseDataLen)`** — charge ces données (ou un fichier licence équivalent).
3. Utiliser les fonctions algorithme (NFIQ, extract, match, …).
4. **`zzFree`** — libération à la fermeture.

### Erreur courante FGP

| Code | Signification doc |
|------|-------------------|
| **-100004** | **Authorization file not found** (fichier d’autorisation introuvable) |

Cause : `zzInit(null, 0)` sans fichier licence sur le poste ni données issues de `zzAuth`.

### Configuration bridge (implémentée)

Fichier : `device-bridge/src/Fgp.DeviceBridge.Api/appsettings.Development.json`

| Clé | Description |
|-----|-------------|
| `LicenseFilePath` | Fichier licence (`license.dat` relatif à `SdkPath` ou chemin absolu) |
| `RequireAlgorithmLicense` | `true` = échec Open si pas de licence ; `false` = mode dégradé (capture sans NFIQ) |
| `TryLicenseServerOnMissingFile` | Appelle `zzAuth` si fichier absent et identifiants renseignés |
| `CacheLicenseFromServer` | Sauve `fingerprint.license` après `zzAuth` réussi |
| `LicenseServer` | IP, port, UserId, Password (doc §4.2.1) |

Exemple avec fichier local :

```json
{
  "Fingerprint": {
    "Mode": "fap60",
    "SdkPath": "C:\\...\\device-bridge\\sdk\\fap60-x64",
    "LicenseFilePath": "license.dat",
    "RequireAlgorithmLicense": true
  }
}
```

Exemple serveur licence :

```json
{
  "TryLicenseServerOnMissingFile": true,
  "LicenseServer": {
    "Ip": "183.129.171.153",
    "Port": 1902,
    "UserId": "VOTRE_ID",
    "Password": "VOTRE_CLE"
  }
}
```

- Copier `license.dat` dans `device-bridge/sdk/fap60-x64/` (voir [README-LICENCE.md](../device-bridge/sdk/fap60-x64/README-LICENCE.md)).
- **Ne pas committer** les fichiers licence.

### Mode dégradé (sans licence algo)

```json
"RequireAlgorithmLicense": false
```

OpenDevice + capture + preview OK ; NFIQ non calculé (journal : « mode dégradé »).

---

## 7. API Device (FAP60-02.dll)

### Ouverture / fermeture

```c
void* mxOpenDevice(int *errCode);           // C# : errCode[0] si échec
int closeDevice(CsFapHandle pHandle);
```

### Capture

| Fonction | Description |
|----------|-------------|
| `captureVideo` | Image plateau améliorée (aperçu live). `captureType` : 0=L4, 1=R4, 3=pouces, 4=single |
| `captureImage` / `captureImage_old` | Capture finale + découpe petites images 300×400 |
| `cancleCapture` / `mxCancleCapture` | Annulation capture en cours |
| `calibrationDevice` | Calibration capteur (callback) |
| `captureRollImage` | Capture rouleau |

**captureImage** — paramètres :

- `captureType` : 0 gauche 4, 1 droite 4, 3 deux pouces, 4 single  
- `nMissNum` : doigts manquants  
- `unTimeOutMs` : timeout **par appel**  
- `save_ori_img_buf` / `save_enh_img_buf` : 1600×1500 (démo)  
- `save_small_image_buf` : buffer découpé  
- `o_CaptureStatus` : **sortie** — état des doigts après découpe  

### Divers

| Fonction | Description |
|----------|-------------|
| `getSdkVersion` | Version SDK |
| `getFirmwareVersion` | Firmware lecteur |
| `getDeviceSN` | Numéro de série |
| `getDriverVersion` | Version driver |
| `mxGetMessageText` | Texte d’erreur à partir du code |

---

## 8. API Algorithme (fingerprint.dll)

> Toutes ces fonctions supposent **`zzInit` réussi**.

### Licence & version

| Fonction | Rôle |
|----------|------|
| `zzAuth` | Récupération données licence (serveur) |
| `zzInit` / `zzFree` | Init / fin bibliothèque |
| `zzGetVersion` | Version algorithme |

### Qualité & segmentation

| Fonction | Rôle |
|----------|------|
| `zzGetQualityNFIQScore` | Score NFIQ 1–5 |
| `zzGetQualityScore` | Score qualité 0–100 |
| `zzCalcFingerArea` | % zone utile |
| `zzFingerSegment` | Segmentation multi-doigts |
| `zzSingleFingerSegment` | Segmentation un doigt |

### Minuties & formats

| Fonction | Rôle |
|----------|------|
| `zzFingerprintFeatureExtract` | Extraction feature (format 2–6 : ANSI/ISO) |
| `zzFingerprintFeatureExtract_Position` | Extraction + code position doigt (table §9) |
| `zzFingerprintFeatureMatchResult` | 1:1 |
| `zzFingerprintFeatureMatchScore` | Score 0–100 |
| `zzFingerprintFeatureSearch` | 1:N |
| `zzMergeFeatureRecord` | Fusion enregistrements |

### Compression

| Fonction | Rôle |
|----------|------|
| `zzCompress` / `zzDecompress` | WSQ / JPEG2000 |
| `zzGetFIR_Ratio_*` / `zzDecompressFromFIR_*` | FIR ISO/ANSI |

### Rouleau

| Fonction | Rôle |
|----------|------|
| `zzGetRollFinger` | Assemblage capture rouleau |

---

## 9. Codes position des doigts

Standard utilisé par `zzFingerprintFeatureExtract_Position` et la doc §4.2.28 :

| Position | Code |
|----------|------|
| Unknown finger | 0 |
| Right thumb | 1 |
| Right index finger | 2 |
| Right middle finger | 3 |
| Right ring finger | 4 |
| Right little finger | 5 |
| Left thumb | 6 |
| Left index finger | 7 |
| Left middle finger | 8 |
| Left ring finger | 9 |
| Left little finger | 10 |

Le bridge FGP utilise des identifiants texte (`left_index`, `right_thumb`, …) mappés vers ces codes pour l’ABIS / OSIA.

---

## 10. Codes d’erreur

### Algorithme (fingerprint.dll) — extraits

| Code | Description |
|------|-------------|
| -100000 | Initialization failed |
| -100001 | Uninitialized |
| -100002 | Authorization expired |
| -100003 | Incorrect authorization code length |
| **-100004** | **Authorization file not found** |
| -100005 | Authorization code verification failed |
| -100006 | Image check failed |
| -100010 | Fingerprint feature extraction failed |
| -100031 | Multifinger segment failed |
| -100032 | Edge finger |
| -101004 | Living algorithm — no authorization file |

### Driver (FAP60-02.dll) — extraits

| Code | Description |
|------|-------------|
| 0 | Succès |
| -6 | Open device failure |
| -9 | Timeout |
| -11 | Loading data failed, cannot capture |
| -25 | Cancel capture image |
| **-26** | **Capture image timeout** |
| **-100032** | **Edge finger** — doigts trop en bord du capteur ; repositionner au **centre** du plateau |
| -600013 | Pas la main gauche détectée |
| -600014 | Pas la main droite détectée |
| -600013 | Not left hand detected |
| -600014 | Not right hand detected |
| -600025 | User cancelled capture |

---

## 11. Configuration FGP

### Device Bridge

Fichier : `device-bridge/src/Fgp.DeviceBridge.Api/appsettings.Development.json`

```json
{
  "Fingerprint": {
    "Mode": "fap60",
    "SdkPath": "C:\\Users\\...\\device-bridge\\sdk\\fap60-x64"
  },
  "Cors": {
    "AllowedOrigins": ["http://localhost:3000"]
  }
}
```

### Frontend (poste guichet)

- `NEXT_PUBLIC_USE_DEVICE_BRIDGE_DIRECT=true` — appels directs `http://127.0.0.1:8765`
- `NEXT_PUBLIC_DEVICE_BRIDGE_URL=http://127.0.0.1:8765`

### Démarrage

```cmd
cd device-bridge\scripts
start-device-bridge.cmd
```

Santé : `GET http://127.0.0.1:8765/health`  
Probe : `device-bridge\scripts\probe-devices.cmd`

---

## 12. Dépannage

| Symptôme | Cause probable | Action |
|----------|----------------|--------|
| `zzInit (-100004)` | Pas de fichier / données licence | Fournir `LicenseFilePath` ou exécuter `zzAuth` ; copier SDK Bin64 complet |
| `capture image timeout` (-26) | Doigts mal placés, capteur sale, ou pas de preview | Tester **FAP60Demo** (Video + Capture) sur le même PC ; calibration |
| Open OK, SN `n/a` | SDK partiel ou device non identifié | Vérifier driver Windows + toutes les DLL |
| Aperçu vide | `captureVideo` échoue ou device fermé | Open device ; vérifier logs bridge |
| 400 capture, 1 tentative | Ancien bridge (timeout 60 s unique) | Rebuild bridge : 15 s × N tentatives |
| Frontend 503 | Bridge arrêté ou mauvaise URL | Bridge local 8765 + `USE_DEVICE_BRIDGE_DIRECT` |

### Checklist avant capture

1. Toutes les DLL `Bin64` dans `sdk/fap60-x64/`
2. Licence algo configurée (**ou** mode sans NFIQ si politique métier l’accepte)
3. Bridge redémarré après changement C# / DLL
4. **Open device** → aperçu live visible
5. Doigts plaqués sur le plateau selon mode (L4 / R4 / pouces)
6. Attendre fin de capture (plusieurs tentatives de 15 s possibles)

---

## Références projet

| Document | Lien |
|----------|------|
| Guichet Sprint 0 | [sprint-0-guichet.md](sprint-0-guichet.md) |
| OpenAPI bridge | [device-bridge.openapi.yaml](device-bridge.openapi.yaml) |
| Code bridge FAP60 | `device-bridge/src/Fgp.DeviceBridge.Api/Modules/Fap60/` |
| Démo fabricant | `FAP60 Windows CSharp SDK…/samplecode/FAP60Demo/` |
| Manuel source | `FAP60 Windows CSharp SDK…/Doc/` (fournisseur) |

---

*Dernière mise à jour : intégration guichet FGP — licence zzInit, capture retry, preview live.*
