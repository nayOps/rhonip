# FGP Device Bridge

Service Windows local qui expose les périphériques biométriques (FAP60, iris, scanner, signature, imprimante) via HTTP.

## Prérequis

- **.NET 8 SDK** : https://dotnet.microsoft.com/download/dotnet/8.0  
- Lecteur FAP60 branché (USB)
- Pilotes / VC++ Redistributable x64 si la DLL refuse de charger

## Démarrage + test matériel

**Terminal 1** (laisse ouvert) — si PowerShell bloque les `.ps1`, utilisez `.cmd` :

```cmd
cd c:\Users\HYF\Documents\sdk\fgp\fgp\device-bridge\scripts
start-device-bridge.cmd
```

Ou PowerShell (autoriser pour cette session seulement) :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start-device-bridge.ps1
```

**Terminal 2** (test reconnaissance) :

```cmd
probe-devices.cmd
```

API : `http://127.0.0.1:8765`

- `GET /health` — état SDK / modules  
- `POST /api/v1/devices/fingerprint/probe` — ouvre le FAP60, lit le n° de série, referme

## Configuration

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DEVICE_BRIDGE_URL` | — | (côté Django) URL du bridge |
| `Fingerprint__Mode` | `mock` | `mock` ou `fap60` |
| `Fingerprint__SdkPath` | — | Dossier contenant `FAP60-02.dll`, `fingerprint.dll` |

Copier les DLL depuis `sdk/FAP60.../Bin64/` vers `device-bridge/sdk/` pour le mode `fap60`.

## Endpoints (Sprint 0)

- `GET /health`
- `POST /api/v1/devices/fingerprint/open`
- `POST /api/v1/devices/fingerprint/close`
- `POST /api/v1/devices/fingerprint/capture`

Voir `docs/device-bridge.openapi.yaml`.
