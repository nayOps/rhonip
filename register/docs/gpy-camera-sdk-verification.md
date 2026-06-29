# SDK caméra GPY (CameraGP) — vérification

> Dossier source : `C:\Users\HYF\Documents\sdk\gpy`  
> Matériel associé : caméra type **XHY-D500** (config `GPYScanOFFICESET.ini` dans Documents)

## Contenu vérifié

| Élément | Chemin | Statut |
|--------|--------|--------|
| Archive SDK | `gpy/SDK/32位SDK_English(1).zip` (~65 Mo) | Présent |
| Installateur | `gpy/SDK/_extracted/CameraGPSDKsetup.exe` | Présent |
| Démo HTML + WebSocket | `gpy/SDK/_extracted/Sample/html/` | Présent |
| Démo C# ActiveX | `gpy/SDK/_extracted/Sample/Other Developments/C#/testOcx/` | Présent |
| OCX / interop | `Interop.CameraGPOcxLib.dll`, `AxInterop.CameraGPOcxLib.dll` | Présent (x86) |
| Config poste | `C:\Users\HYF\Documents\GPYScanOFFICESET.ini` | Résolution 1920×1080, auto-exposure |

Le dossier `gpy/3D` est vide sur ce poste.

## Architecture du SDK (comme FAP60 → bridge)

Ce n’est **pas** une DLL appelée directement depuis Next.js. Deux modes :

### 1. Navigateur moderne (Chrome / Edge) — recommandé guichet

1. Installer **`CameraGPSDKsetup.exe`** sur le poste Windows.
2. Un **service local WebSocket** écoute sur **`ws://localhost:9002`**.
3. Le front se connecte comme les exemples :
   - `Sample/html/js/WsUtil.js` — flux vidéo sur `<canvas>`
   - `Sample/html/js/OcxUtil.js` — `StartCam`, `CaptureImage`, `CaptureFace`, etc.
4. La photo arrive en **Base64** (`GetPicBase64:` dans les messages WS, callback type `5` dans `axCam_Ocx.js`).

Fichiers de référence à ouvrir dans le navigateur (après install) :

- `newEaxmpleOneSimple.html` — démarrage minimal
- `newEaxmpleOne.html` / `newEaxmpleTwo.html` — fonctions avancées (visage, second capteur)

### 2. Internet Explorer — ActiveX (legacy)

- CLSID : `D5BD5B4A-4FC0-4869-880B-27EE9869D706`
- Objet : `axCam_Ocx` — non utilisable sur Edge/Chrome actuels.

### 3. Intégration native C# / VB / Delphi

- Projet `testOcx` : `axCameraGPOcx1.GetDevCount()`, `CAM_Open`, `CaptureImage`, `CaptureFace`, etc.

## API utiles pour photo d’identité FGP

| Action | JS (non-IE) | Remarque |
|--------|-------------|----------|
| Init | `WsInit(w, h, …)` → `ws://localhost:9002` | Après service installé |
| Liste caméras | callback `GetDevName` | `camidMain` |
| Résolutions | `GetDeviceResolution` | Choisir max ou 1920×1080 |
| Aperçu | `StartCam(camId, w, h)` | Frames binaires → canvas |
| Photo | `CaptureImage(0)` | Base64 via WS |
| Visage ICAO | `InitFaceCheck()` puis `CaptureFace()` | Détection / recadrage intégrés SDK |
| Fermer | `CloseCam()` | Libérer la caméra |

Commandes WS visage (extrait `WsUtil.js`) :

- `0xef 0x78` — activer/désactiver face check
- `0xef 0x79` — capture visage

## Différence avec l’implémentation actuelle FGP

| | Webcam navigateur (`PhotoCapture.tsx`) | SDK GPY |
|--|----------------------------------------|---------|
| Pilote | `getUserMedia` | Service CameraGP + caméra XHY |
| Qualité / visage | Heuristiques locales | `CaptureFace`, `FaceDoubleOK`, etc. |
| Prérequis | Permission navigateur | **Installateur + service port 9002** |
| Alignement FAP60 | Même poste guichet | Même pattern que bridge 8765 → module dédié ou client WS |

## Checklist installation poste guichet

1. Exécuter `CameraGPSDKsetup.exe` (x86, VC++ redist fourni dans `InstallFail/` si besoin).
2. **Lancer l’application GPYScan / CameraGP** (barre des tâches) — c’est elle qui ouvre le **port 9002**.
3. Brancher la caméra XHY-D500 (USB).
4. Vérifier : `powershell -File fgp/scripts/check-gpy-ws.ps1` → `[OK] Port 9002 en écoute`.
5. Test navigateur : `Sample/html/newEaxmpleOneSimple.html` dans Edge — aperçu live + capture.
6. Optionnel : `GPYScanOFFICESET.ini` dans Documents (exposition, miroir, qualité JPEG).

### Erreur fréquente : caméra OK mais `WebSocket localhost:9002 failed`

| Symptôme | Cause |
|----------|--------|
| Caméra visible dans Windows | Pilote USB OK |
| WS port 9002 échoue | **Service CameraGP non démarré** (pas installé ou app GPYScan fermée) |

**Ce n’est pas** un bug du frontend FGP : le pont WebSocket doit tourner avant Next.js.

### Autre erreur : `localhost:8001 ERR_CONNECTION_REFUSED`

`enrollment_gateway` n’est pas démarré — indépendant de la caméra. Lancer Docker ou le gateway Django sur le port 8001.

## Intégration FGP (comme FAP60 / iris)

```
PhotoCapture → camera-api.ts → Device Bridge :8765 → Sidecar x86 :8766 → OCX COM CameraGP
                                                      ↓
                                    enrollment_gateway PATCH modality/face/{session_id}/
```

| Fichier | Rôle |
|---------|------|
| `device-bridge/.../Fgp.CameraGp.Bridge` | Sidecar x86, OCX, preview JPEG, `CaptureFace` |
| `device-bridge/.../CameraGpProxyModule.cs` | Proxy HTTP vers 8766 |
| `device-bridge/.../CameraGpSidecarHostedService.cs` | Auto-start sidecar + attente `/health` |
| `frontend/src/services/camera-api.ts` | API bridge 8765 |
| `frontend/src/components/biometrics/PhotoCapture.tsx` | GPY via bridge (pas de WS 9002 requis) |
| `frontend/src/services/enrollment-session-api.ts` | `saveFaceBiometrics` → gateway |

**Pas besoin** du port WebSocket 9002 ni de GPYScan pour le guichet FGP (mode COM).

### Vérification

```powershell
cd fgp\device-bridge\scripts
.\start-device-bridge.ps1
.\verify-camera-gp.ps1
```

Build sidecar (nécessite MSBuild .NET Framework pour COM) :

```powershell
dotnet build device-bridge\Fgp.DeviceBridge.sln
# ou Visual Studio : projet Fgp.CameraGp.Bridge (x86)
```

Endpoints :

- `GET http://127.0.0.1:8765/api/v1/devices/camera/status`
- `POST http://127.0.0.1:8765/api/v1/devices/camera/capture`
- `PATCH http://localhost:8001/api/v1/enrolments/sessions/modality/face/{session_id}/`

## Test rapide sans FGP

```text
1. Installer CameraGPSDKsetup.exe depuis gpy/SDK/_extracted/
2. Ouvrir : file:///.../gpy/SDK/_extracted/Sample/html/newEaxmpleOneSimple.html
3. Si « Connection successful » et vidéo → SDK OK
4. Sinon : service non démarré, caméra occupée, ou pilote manquant
```
