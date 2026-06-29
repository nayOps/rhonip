# Sprint 0 — Guichet Windows (empreintes FAP60)

> Documentation SDK complète : **[fap60-sdk-integration.md](fap60-sdk-integration.md)** (API Device/Algo, licence, erreurs, dépannage).

## Architecture

```
Navigateur (Next.js) → Device Bridge :8765 → FAP60 DLL | Iris Device Server :50218
                    ↘ enrollment_gateway :8001 (modality_status)
                    ↘ fingerprint_service :8010 (optionnel / legacy Docker)
```

## Démarrage

### 1. Device Bridge (Windows, sur le poste guichet)

```powershell
cd fgp\device-bridge\src\Fgp.DeviceBridge.Api
dotnet run
```

Vérifier : http://127.0.0.1:8765/health

Mode mock par défaut (`appsettings.json` → `Fingerprint:Mode` = `mock`).

Pour le matériel réel : copier **toutes** les DLL `Bin64` dans `device-bridge/sdk/fap60-x64/`, placer `license.dat` (voir [README-LICENCE.md](../device-bridge/sdk/fap60-x64/README-LICENCE.md)), puis :

```json
"Fingerprint": { "Mode": "fap60", "SdkPath": "C:\\chemin\\vers\\sdk\\fap60-x64" }
```

### 2. Stack Docker

```powershell
cd fgp
docker compose up -d postgres redis fgp_core enrollment_gateway extensions_service fingerprint_service frontend
```

Service iris (Linux/dev uniquement) :

```powershell
docker compose --profile dev-biometric up -d biometric_service
```

### Iris (guichet Windows)

Voir **[iris-sdk-integration.md](iris-sdk-integration.md)**.

1. Iris Device Server sur **50219** (`sdk/iris/bin`, lecteur **JD5** / IRIS-SCANNER).
2. Bridge : `Iris:Mode` = `device` dans `appsettings.json`.
3. Étape workflow **iris** → bridge `8765` + `PATCH modality/iris/{session_id}`.

```powershell
.\device-bridge\scripts\check-iris-server.ps1
```

### 3. Frontend

http://localhost:3000 — étape empreintes appelle `fingerprint_service` si disponible, sinon message d’erreur explicite.

## Persistance gateway (workflow 4-4-2)

1. À l’étape **empreintes**, création session `POST /api/v1/enrolments/sessions/` avec `auto_process: false`.
2. À **Suivant** (10 doigts traités), `PATCH .../modality/fingerprint/{session_id}/` avec gabarits FAP60 (`template_base64`, NFIQ, statuts).
3. À la fin **vérification**, `POST .../sessions/submit/{session_id}/` lance le traitement async (validation + ABIS).

Variables frontend : `NEXT_PUBLIC_API_URL=http://localhost:8001` (enrollment_gateway).

## Enrôlement dégradé

Si le bridge est indisponible, l’opérateur peut ignorer les empreintes (bouton « Continuer sans empreintes ») : `modality_status.fingerprint` = `skipped`, validation gateway sans exiger `fingerprints` dans le payload.
