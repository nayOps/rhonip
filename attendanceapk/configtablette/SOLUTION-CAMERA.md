# 🎥 Solution : Problème d'accès à la Caméra

## 🔍 Problème Identifié

Le **navigateur par défaut d'Android** a des restrictions sur l'accès à la caméra.

---

## ✅ SOLUTION 1 : Installer Chrome (RECOMMANDÉ)

### Sur la MorphoTablet :

1. **Ouvrir Google Play Store**
2. **Rechercher** : `Chrome`
3. **Installer** : Google Chrome
4. **Ouvrir Chrome**
5. **Aller sur** : `http://192.168.100.101:8888/test-camera.html`
6. **Autoriser** l'accès à la caméra quand demandé
7. **Cliquer** sur "TESTER LA CAMÉRA"

**✅ Chrome fonctionne à 99% des cas avec l'accès caméra**

---

## ✅ SOLUTION 2 : Activer HTTPS (Si Chrome pas disponible)

Certains navigateurs exigent HTTPS pour accéder à la caméra.

### Étape 1 : Générer le certificat SSL

```bash
cd /home/nayops/Documents/architecture/configtablette
chmod +x generate-cert.sh
./generate-cert.sh
```

### Étape 2 : Démarrer le serveur HTTPS

```bash
chmod +x server-https.py
python3 server-https.py
```

### Étape 3 : Accéder depuis la tablette

```
https://192.168.100.101:8443/test-camera.html
```

**⚠️ Important :** Vous devrez accepter le certificat auto-signé :
- Cliquez sur "Avancé"
- Puis "Continuer vers le site"

---

## ✅ SOLUTION 3 : Vérifier les Permissions Android

### Sur la MorphoTablet :

1. **Paramètres** → **Applications**
2. Trouver le **Navigateur** que vous utilisez
3. **Permissions** → **Caméra**
4. **Autoriser**

---

## 🔧 Tests de Diagnostic

### Test 1 : Vérifier que Chrome est bien installé
```
Sur la tablette → Chercher l'icône Chrome
```

### Test 2 : Tester avec une autre URL
Essayez ce test externe pour vérifier si la caméra fonctionne :
```
https://www.onlinemictest.com/fr/test-webcam/
```

Si ça marche → Le problème vient de notre code  
Si ça ne marche pas → Le problème vient des permissions Android

---

## 📝 Checklist de Dépannage

- [ ] Chrome est installé sur la tablette
- [ ] Tablette et PC sur le même Wi-Fi
- [ ] URL correcte : `http://192.168.100.101:8888/test-camera.html`
- [ ] Permission caméra accordée au navigateur
- [ ] Popup de demande d'accès apparaît
- [ ] Console de debug affiche des messages

---

## 💡 Si Rien ne Marche

### Vérification Matérielle

**La caméra fonctionne-t-elle en général ?**

Testez avec l'application Caméra native d'Android :
1. Ouvrir l'app **Caméra**
2. Prendre une photo
3. Si ça ne marche pas → Problème matériel

---

## 🆘 Dernière Solution : Application Android Native

Si vraiment le navigateur ne fonctionne pas, nous devrons créer une **application Android native** qui utilise directement le SDK Morpho.

Mais essayons d'abord Chrome ! 🚀

---

**Quelle solution voulez-vous essayer en premier ?**

