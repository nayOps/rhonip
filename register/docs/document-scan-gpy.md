# Scan de documents — intégration GPY

## Prérequis

1. **GPYScan** (port **9002**) — `start-gpy-service.cmd` ou `CameraGPSDK.exe`
2. **Ou** Device Bridge + sidecar COM — `start-device-bridge.cmd` (8765 → 8766)

## Parcours guichet

1. Étape **Documents** dans l'enrôlement
2. Choisir **type de pièce** + **structure** (page unique, recto/verso, multipages, multipages R/V)
3. **Nouveau document** ou démarrage du scanner (crée un brouillon)
4. **Scanner la page** (recto, verso, ou page N selon la structure)
5. **Terminer ce document** quand toutes les pages du dossier sont capturées
6. Répéter pour une autre pièce (acte, passeport, etc.)
7. **Suivant**

### Structures

| Mode | Comportement |
|------|----------------|
| Page unique | 1 scan → document terminé automatiquement |
| Recto + verso | 2 scans (recto puis verso) → document terminé |
| Plusieurs pages | N scans → **Terminer ce document** manuellement |
| Multipages recto/verso | Alternance recto/verso (ou choix manuel) → terminer quand complet (min. 2 pages) |

## API Device Bridge

```http
POST /api/v1/devices/camera/capture-document
Content-Type: application/json

{ "auto_cut": true }
```

Réponse : `image_base64` (JPEG), comme la photo visage mais sans `CaptureFace`.

## Webcam générique (sans XHY)

- Mode **GPYScan 9002** : capture depuis l'aperçu canvas (pas de découpage constructeur)
- Mode **COM** : refusé si `CAM_Open` → -1 (Logitech/HP)

## Import fichier

Bouton **Importer image ou PDF** — toujours disponible sans scanner.

## Suite (optionnel)

- Fusion PDF (`AddPDFImageFile` / `Convert2PDF`) côté sidecar
- Persistance gateway `modality/document/{session_id}/`
- Caméra secondaire (`GetSecondCameraID`) pour document dessous
