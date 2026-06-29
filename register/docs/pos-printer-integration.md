# Impression ticket — POS-SDK

## SDK

`C:\Users\HYF\Documents\sdk\POS-SDK\SDK\POS_SDK.dll` (x86)

## Architecture

```
Next.js → Device Bridge :8765 → Fgp.PosPrinter.Bridge :8767 → POS_SDK.dll → imprimante thermique
```

## Installation guichet

PowerShell (préfixe `.\` obligatoire) :

```powershell
cd c:\Users\HYF\Documents\sdk\fgp\fgp\device-bridge\scripts
.\copy-pos-sdk.cmd
.\build-pos-sidecar.cmd
.\start-device-bridge.cmd
```

Invite de commandes classique : les mêmes noms sans `.\`.

Après `build-pos-sidecar`, le log doit afficher **« Sidecar POS HTTP prêt »**. Si vous voyez **« Sidecar POS arrêté »**, relancez `.\build-pos-sidecar.cmd` (copie complète du runtime x86) puis redémarrez le bridge.

`appsettings.Development.json` :

```json
"Printer": {
  "Mode": "pos",
  "Connection": "SP-USB1",
  "PortType": "usb"
}
```

Autres connexions : `COM1:9600,N,8,1` (com), `192.168.x.x:9100` (net).

## Frontend

Étape **Récépissé** → **Imprimer ticket POS** (QR = numéro de session).

Fallback : **Imprimer (navigateur)**.

## API

- `GET /api/v1/devices/printer/status`
- `POST /api/v1/devices/printer/print-receipt`
- `POST /api/v1/devices/printer/test`
