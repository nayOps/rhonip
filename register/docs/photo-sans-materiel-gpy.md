# Photo d'identité sans caméra XHY-D500 (GPY)

## Problème

Le SDK **CameraGP** en mode COM (`CheckDevice`, `CAM_Open` code **-1**) n'accepte que le matériel constructeur (XHY-D500 / GPY). Une **Logitech C930c** ou **HP 5MP** ne sera jamais ouverte par l'OCX — ce n'est pas un bug d'intégration FGP.

## Solutions qui fonctionnent aujourd'hui

### 1. Webcam navigateur (recommandé)

1. Ouvrir l'enrôlement → étape **Photo**
2. Choisir **Webcam navigateur** (sélectionné par défaut)
3. **Démarrer webcam** → autoriser la caméra dans Chrome/Edge
4. **Prendre la photo** → **Suivant**

Aucun Device Bridge ni GPYScan requis.

### 2. GPYScan (port 9002) + aperçu live

Si `CameraGPSDK.exe` / GPYScan tourne :

1. Mode **GPY (WS ✓)**
2. **Démarrer caméra GPY**
3. Attendre l'aperçu live (1–2 s)
4. **Capturer** — l'image est prise depuis le **canvas** (flux affiché), pas via `CaptureFace` XHY

### 3. Importer une photo

JPEG/PNG existant → analyse qualité → enregistrement gateway.

## Solution production (matériel certifié)

- Brancher **XHY-D500** en USB
- `device-bridge\scripts\start-device-bridge.cmd`
- Mode **GPY (COM ✓)** — sidecar x86 + OCX

## Ce qui ne résout pas le problème

| Action | Pourquoi |
|--------|----------|
| Réinstaller le SDK seul | OCX inchangé sans XHY |
| Amcap / « 高拍仪测试 » sur le Bureau | Outil DirectShow générique, pas CameraGP certifié |
| Forcer COM sur Logitech | Refus matériel (-1) par design constructeur |
