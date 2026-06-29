# ONIP ICAO Face Quality Assistant (webcam)

Microservice Python local pour le **guidage temps réel** et la **validation finale** des photos d'identité capturées par webcam (Logitech, etc.). Il ne remplace pas la certification matérielle GPY/XHY-D500.

## Prérequis : Python 3.10+

Si vous voyez *Python was not found* :

1. Installer depuis [python.org/downloads](https://www.python.org/downloads/) (3.10 ou 3.12).
2. Cocher **Add python.exe to PATH** à l’installation.
3. Désactiver les alias Store : **Paramètres → Applications → Alias d’exécution d’applications** → désactiver `python.exe` et `python3.exe`.
4. Fermer et rouvrir PowerShell, puis vérifier : `py -3 --version`

## Démarrage

Depuis `fgp/fgp` (recommandé — pas de blocage ExecutionPolicy) :

```cmd
scripts\start-icao-face-service.cmd
```

Ou PowerShell (si les scripts `.ps1` sont autorisés) :

```powershell
.\scripts\start-icao-face-service.ps1
```

Si PowerShell affiche *running scripts is disabled* :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Ou lancement ponctuel :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-icao-face-service.ps1
```

- URL : `http://127.0.0.1:50270` (évite le port 50220, souvent réservé par Windows/Hyper-V)
- Santé : `GET /health`
- WebSocket temps réel : `ws://127.0.0.1:50270/face/ws`
- Validation finale : `POST /face/quality-check` (multipart `image`)
- **Capture complète** : `POST /face/process-capture` — photo brute + recadrage ICAO 7:9 + SHA-256 + qualité

## Frontend

Variable optionnelle :

```env
NEXT_PUBLIC_ICAO_FACE_SERVICE_URL=http://127.0.0.1:50270
```

Dans l'étape **Photo**, mode **Webcam navigateur** :

1. Démarrer la webcam → flux WebSocket (~4 fps) vers le service
2. **Overlay live** : landmarks, mesh (contour), bbox, ligne des yeux, axe du visage, cadre ICAO 7:9
3. Messages de guidage (position, yeux, éclairage…)
4. Capture autorisée quand statut `READY` (score live ≥ 82 par défaut)
5. **Capture automatique** après 12 frames `READY` consécutives (~3,4 s) — désactivable par case à cocher
6. `process-capture` : conserve **photo_originale** (brute) + génère **photo_icao** (recadrage sans étirement)
7. Analyse finale sur l'image ICAO → `ACCEPTED` (≥ 90), `REVIEW` (75–89), `REJECTED` (< 75)
8. **Suivant** bloqué tant que le statut n'est pas `ACCEPTED` (REVIEW et REJECTED → reprendre la photo)

### Seuils (variables d'environnement)

| Variable | Défaut |
|----------|--------|
| `ICAO_SCORE_ACCEPTED` | 90 |
| `ICAO_SCORE_REVIEW` | 75 |
| `ICAO_REALTIME_READY_SCORE` | 82 |
| `ICAO_AUTO_CAPTURE_STABLE_FRAMES` | 12 |

Exposés aussi via `GET /health` → `thresholds`.

Le mode **GPY** (COM / WebSocket 9002) n'utilise pas ce service.

## Décision production

L'assistant webcam peut être évalué en parallèle du matériel certifié. Si les scores et rejets sont satisfaisants sur le terrain, ONIP pourra l'envisager en production ; sinon, conserver XHY-D500 + SDK GPY.
