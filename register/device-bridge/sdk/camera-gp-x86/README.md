# CameraGP (COM x86)

Le pilote photo GPY / XHY-D500 passe par l’OCX **CameraGP**, enregistré lors de l’installation du SDK :

- Installateur : `CameraGPSDKsetup.exe` (dossier SDK GPY)
- GUID COM : `{8ADCE96D-A045-431F-BC80-447B571167C3}`

## Architecture

| Processus | Plateforme | Port | Rôle |
|-----------|------------|------|------|
| `Fgp.DeviceBridge.Api` | Any CPU (FAP60 x64) | **8765** | API guichet (empreintes + proxy caméra) |
| `Fgp.CameraGp.Bridge` | **x86** | **8766** | OCX COM, preview JPEG, capture visage |

Au démarrage du Device Bridge (`Camera:AutoStartSidecar: true`), le sidecar x86 est lancé automatiquement. Le frontend n’appelle **que** le port **8765** — plus de WebSocket `localhost:9002`.

## Build

```powershell
cd device-bridge
dotnet build Fgp.DeviceBridge.sln
```

La build copie `Fgp.CameraGp.Bridge.exe` dans le dossier de sortie de `Fgp.DeviceBridge.Api`.

## Vérification

```powershell
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/api/v1/devices/camera/status
```
