# Intégration iris — Iris Device Server (guichet Windows)

SDK matériel : `C:\Users\HYF\Documents\sdk\iris\` (JD5, JD7, M02/M06, etc.).

## Architecture guichet

```
Navigateur (Next.js) → Device Bridge :8765 → Iris Device Server HTTP :50219 → lecteur JD5
                    ↘ enrollment_gateway :8001 (PATCH modality/iris)
```

Le service **biometric_service** (Docker, port 8003) reste pour le dev Linux ; sur le poste guichet Windows, le flux officiel passe par le **Device Server** natif.

## Prérequis matériel (JD5 — guichet courant)

Lecteur **JD5** / **IRIS-SCANNER** : USB `VID_1234` / `PID_0101` (pilote Windows **USB Video**, pas de driver JD7).

1. Activer le service HTTP : `iris\bin\启用HTTP服务.bat` (admin, une fois).
2. **Port HTTP** : souvent **50219** (Postman / bridge) ; le TCP **50218** peut être ouvert sans HTTP — le bridge détecte automatiquement le bon port.
3. Démarrer **IrisDeviceServer.exe** depuis `iris\bin\` (un seul processus).
4. **Ouvrir lecteur** dans l’UI FGP ou via `POST /api/v1/devices/iris/open`.

### JD7 uniquement (autre matériel)

Si l’ID USB est `VID_2285` / `PID_2F11` : `iris\bin\drivers\JD7Driver\install.bat` (admin).

Test rapide :

```powershell
cd fgp\fgp\device-bridge\scripts
.\check-iris-server.ps1
```

Page de test locale : ouvrir `iris\bin\device_server.html` (preview live + capture).

## Device Bridge (intégration native)

Le module iris est **intégré dans le Device Bridge** (`8765`), comme FAP60 :

- `IrisDeviceModule` — proxy HTTP vers le serveur SDK
- `IrisDeviceServerHostedService` — démarre `IrisDeviceServer.exe` si le port est fermé
- Santé dans `GET /health` → module `iris`

```powershell
cd fgp\device-bridge\scripts
.\verify-iris-sdk.ps1
.\start-device-bridge.ps1
.\probe-devices.ps1
```

`appsettings.json` (guichet réel) :

```json
"Iris": {
  "Mode": "device",
  "BaseUrl": "http://127.0.0.1:50219",
  "BinPath": "C:\\Users\\HYF\\Documents\\sdk\\iris\\bin",
  "AutoStartServer": true
}
```

Sans matériel (tests UI) : `"Mode": "mock"`.

### API bridge

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/devices/iris/status` | HTTP + `device/Model` / `device/Status` |
| GET | `/api/v1/devices/iris/preview/live` | Images `image/living/{left,right}.bmp` |
| POST | `/api/v1/devices/iris/capture` | Body `{ "eye": "both"|"left"|"right", "timeout_seconds": 30 }` |
| POST | `/api/v1/devices/iris/open` | Ouvre le lecteur (`device/Open`) |
| POST | `/api/v1/devices/iris/stop` | Arrêt capture en cours |
| POST | `/api/v1/devices/iris/close` | Fermeture device (`device/Close`) |
| POST | `/api/v1/devices/iris/probe` | Diagnostic (health + status + stop) |

Capture : proxy vers `POST /device/Capture` (mode enrôlement `mode:1`, `eye:3` = les deux yeux), puis récupération `image/captured/left.bmp` et `right.bmp`.

## Frontend

- `frontend/src/services/iris-api.ts` — appels bridge
- `frontend/src/lib/iris-enrollment-utils.ts` — règles métier (cas d’enrôlement)
- `IrisCapture.tsx` — preview live, tous les cas ci-dessous, sauvegarde gateway
- Page `/analyse` — libellé **Lecteur iris (JD5)**

### Cas d’enrôlement iris (UI)

| Cas | Action |
|-----|--------|
| Standard | Capturer les 2 yeux |
| Un œil | Capture d’un côté + aveugle / absent / endommagé sur l’autre |
| Aucune capture | « Les 2 — Aveugle / Absent / Endommagé » ou signalement œil par œil |
| Échec | Réessayer, réinitialiser, ou signaler non capturable |
| Reprise | Recapturer un œil déjà capturé ; modifier un signalement |

Statuts par œil : `CAPTURED`, `BLIND`, `MISSING`, `DAMAGED`, `FAILED`, `PENDING`.  
Validation : les **2 yeux** doivent être capturés **ou** signalés (pas de `PENDING` / `FAILED`).

Variables :

- `NEXT_PUBLIC_DEVICE_BRIDGE_URL=http://127.0.0.1:8765`
- `NEXT_PUBLIC_API_URL=http://localhost:8001`

À la validation de l’étape iris : `PATCH /api/v1/enrolments/sessions/modality/iris/{session_id}/`.

## Dépannage

| Symptôme | Cause probable | Action |
|----------|----------------|--------|
| **`errcode=16777231`** (0x0100000F) | Lecteur **fermé** ou capture sans matériel prêt | **Ouvrir lecteur**, un seul `IrisDeviceServer.exe` |
| **`errcode=16777219`** (0x01000003) | **Aucun lecteur** / ouverture impossible | USB JD5, fermer `DeviceUI.exe` en double, **Ouvrir lecteur** |
| `model` vide | Lecteur non ouvert | `DeviceUI.exe` ou bouton Ouvrir lecteur ; `device/Model` → `"JD5"` |
| Port 50219 fermé | Device Server non lancé | Démarrer serveur iris (bridge ou `iris\bin`) |
| Capture OK, images vides | Timeout trop court | Augmenter `timeout_seconds` |
| Bridge « mock » | `Iris:Mode` = mock | Passer à `device` quand le serveur tourne |
| CORS / réseau | Bridge arrêté | `start-device-bridge.cmd` |

Vérification rapide (PowerShell) :

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:50219/device/Model" -Method POST -Body "{}" -ContentType "text/plain"
Invoke-WebRequest -Uri "http://127.0.0.1:50219/device/Status" -Method POST -Body "{}" -ContentType "text/plain"
```

Attendu : `"model": "JD5"` et `"status": 2` (ouvert). Si `status: 1` et `model` vide → Ouvrir lecteur avant le parcours FGP.

Postman : `iris/doc/IrisDeviceServer.postman_collection.json` (variable `IP` = `127.0.0.1:50219`).
