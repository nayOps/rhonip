# SDK Iris — reference guichet

Le bridge utilise le dossier **Iris Device Server** installe sur le poste :

- Par defaut : `C:\Users\HYF\Documents\sdk\iris\bin`
- Config : `Iris:BinPath` dans `appsettings.json`

## Lecteur guichet (JD5)

Modele courant : **JD5** / **IRIS-SCANNER** (USB `VID_1234` / `PID_0101`).

- Pilote Windows : **USB Video** (`usbvideo`) — pas besoin de `JD7Driver\install.bat`.
- Service HTTP : `启用HTTP服务.bat` (admin, une fois).
- Test UI native : `DeviceUI.exe` dans `iris\bin`.

## Lecteur JD7 (autre materiel)

Uniquement si l'ID USB est `VID_2285` / `PID_2F11` :

- `iris\bin\drivers\JD7Driver\install.bat` (admin)

## Fichiers requis

- `IrisDeviceServer.exe`
- `device_server.json` (port TCP **50218** ; HTTP souvent **50219**)
- DLL et configs `device_config_*.json`

Le bridge demarre `IrisDeviceServer.exe` si `Iris:AutoStartServer` = true.

Verification :

```powershell
.\scripts\verify-iris-sdk.ps1
.\scripts\check-iris-server.ps1
```
