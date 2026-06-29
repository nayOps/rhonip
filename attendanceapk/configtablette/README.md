# 🔐 Configuration et Test MorphoTablet

## 📋 Vue d'ensemble

Environnement de test simple et direct pour la MorphoTablet 2 **SANS Docker** pour éviter la lenteur.

## 🚀 Démarrage Rapide

### 1. Démarrer le serveur

```bash
cd /home/nayops/Documents/architecture/configtablette
python3 server.py
```

Le serveur démarrera sur le port **8080**.

### 2. Trouver votre adresse IP

```bash
ip addr show | grep 'inet ' | grep -v '127.0.0.1'
```

Exemple de résultat : `192.168.1.100`

### 3. Accéder à l'interface

**Depuis votre PC :**
```
http://localhost:8080
```

**Depuis la MorphoTablet (sur le même réseau Wi-Fi) :**
```
http://[VOTRE_IP]:8080
```

Exemple : `http://192.168.1.100:8080`

---

## 🧪 Tests à Effectuer

### Test 1 : Caméra
1. Ouvrir l'interface
2. Cliquer sur "📷 Démarrer la Caméra"
3. Autoriser l'accès à la caméra si demandé
4. Vérifier que le flux vidéo s'affiche
5. Cliquer sur "📸 Capturer" pour prendre une photo

**✅ Succès si :** La photo s'affiche correctement

### Test 2 : Lecteur d'empreintes
1. Observer la zone "Lecteur d'Empreintes"
2. Noter si la tablette détecte le capteur
3. Placer le doigt sur le capteur MorphoTablet

**📝 Note :** Pour l'instant, l'empreinte est simulée. Le vrai SDK permettra la capture réelle.

### Test 3 : Enregistrement complet
1. Mode "Enregistrement"
2. Entrer un ID employé (ex: 1)
3. Capturer une photo
4. Cliquer sur "✅ Valider"
5. Vérifier le message de succès

**✅ Succès si :** Message "Enregistrement biométrique enregistré avec succès!"

### Test 4 : Pointage
1. Mode "Entrée"
2. Entrer un ID employé
3. Capturer une photo
4. Valider
5. Vérifier que les données sont sauvegardées

**📊 Voir les données :** 
- Ouvrir la console développeur (F12)
- Aller dans l'onglet "Application" → "Local Storage"
- Voir les clés commençant par `morpho_`

---

## 📂 Structure des Fichiers

```
configtablette/
├── index.html       # Interface web principale
├── server.py        # Serveur HTTP simple (Python)
├── README.md        # Ce fichier
└── data/            # Dossier pour sauvegarder les données (créé auto)
```

---

## 🔍 Informations Techniques

### Technologies Utilisées
- **HTML5** : Structure
- **CSS3** : Design responsive
- **JavaScript Vanilla** : Logique (pas de framework)
- **MediaDevices API** : Accès caméra
- **LocalStorage** : Stockage temporaire

### Compatibilité
- ✅ Chrome/Chromium (Recommandé)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Navigateurs Android (WebView)

### Permissions Requises
- 📷 **Caméra** : Pour capturer les photos
- 💾 **LocalStorage** : Pour sauvegarder les données

---

## 🐛 Dépannage

### Problème : "Caméra non disponible"
**Solutions :**
1. Vérifier que la tablette a une caméra
2. Autoriser l'accès à la caméra dans les permissions du navigateur
3. Essayer un autre navigateur (Chrome recommandé)

### Problème : "Impossible d'accéder à l'interface depuis la tablette"
**Solutions :**
1. Vérifier que PC et tablette sont sur le même réseau Wi-Fi
2. Vérifier l'adresse IP du PC : `ip addr show`
3. Désactiver temporairement le pare-feu :
   ```bash
   sudo ufw allow 8080/tcp
   ```
4. Ping de la tablette vers le PC :
   ```bash
   ping [IP_DU_PC]
   ```

### Problème : "Port 8080 déjà utilisé"
**Solution :** Modifier le port dans `server.py` :
```python
PORT = 8081  # ou un autre port libre
```

---

## 📊 Données Capturées

Les données suivantes sont enregistrées localement :

```json
{
  "mode": "checkin|checkout|enroll",
  "employeeId": "123",
  "photo": "data:image/jpeg;base64,...",
  "fingerprintTemplate": "SIMULATED_...",
  "timestamp": "2025-01-21T10:30:00.000Z",
  "location": "MorphoTablet Direct Test"
}
```

### Exporter les données
Ouvrez la console (F12) et tapez :
```javascript
// Voir toutes les données
for (let i = 0; i < localStorage.length; i++) {
    let key = localStorage.key(i);
    if (key.startsWith('morpho_')) {
        console.log(key, JSON.parse(localStorage.getItem(key)));
    }
}

// Exporter en JSON
let allData = [];
for (let i = 0; i < localStorage.length; i++) {
    let key = localStorage.key(i);
    if (key.startsWith('morpho_')) {
        allData.push(JSON.parse(localStorage.getItem(key)));
    }
}
console.log(JSON.stringify(allData, null, 2));
```

---

## 🔄 Prochaines Étapes

### Une fois que ça fonctionne :

1. **✅ Tester sur la tablette** - Vérifier que tout fonctionne
2. **🔌 Intégrer le SDK Morpho** - Capturer les vraies empreintes
3. **🌐 Créer l'API backend** - Sauvegarder en base de données
4. **🐳 Intégrer avec Docker** - Déployer en production
5. **🔒 Sécuriser** - HTTPS, authentification, etc.

---

## 💡 Astuces

### Afficher les logs en temps réel
Le serveur affiche automatiquement toutes les requêtes dans le terminal.

### Tester sur mobile/tablette sans Wi-Fi
Utilisez un **hotspot** depuis votre PC et connectez la tablette.

### Mode développeur sur Android
1. Paramètres → À propos
2. Taper 7 fois sur "Numéro de build"
3. Retour → Options pour développeurs
4. Activer "Débogage USB" et "Inspection USB"

---

## 📞 Support

**Problème ?** Vérifiez :
1. Logs du serveur dans le terminal
2. Console développeur (F12) dans le navigateur
3. Permissions caméra et LocalStorage

**Commande utile pour voir les processus sur le port 8080 :**
```bash
sudo lsof -i :8080
```

---

**Créé le :** 21 Janvier 2025  
**Version :** 1.0.0 - Test Direct

