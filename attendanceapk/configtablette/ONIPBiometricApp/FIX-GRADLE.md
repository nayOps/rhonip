# 🔧 Fix Gradle - Étapes Simples

## ✅ **Solution : Utiliser Android Studio**

Le plus simple est de laisser Android Studio gérer Gradle automatiquement.

---

## 📱 **Étapes à Suivre**

### **1. Ouvrir Android Studio**

```bash
# Lancer Android Studio
android-studio
```

### **2. Ouvrir le Projet**

1. **File** → **Open**
2. Naviguer vers : `/home/nayops/Documents/architecture/configtablette/ONIPBiometricApp`
3. Cliquer **OK**

### **3. Laisser Android Studio Synchroniser**

**Android Studio va automatiquement :**
- ✅ Télécharger Gradle wrapper
- ✅ Synchroniser les dépendances
- ✅ Résoudre les problèmes de configuration

**Attendre** la fin de la synchronisation (barre de progression en bas)

### **4. Si Erreur de Synchronisation**

**Cliquer sur le lien dans l'erreur :**
- "Sync Now"
- "Try Again"
- "Fix Gradle Version"

Ou manuellement :

**File** → **Project Structure** → **Project**
- **Android Gradle Plugin Version** : `7.4.2`
- **Gradle Version** : `8.2`
- Cliquer **OK**

### **5. Build le Projet**

**Build** → **Rebuild Project**

---

## 🚀 **Méthode Alternative : Ligne de Commande**

Si vous voulez vraiment utiliser la ligne de commande :

### **Installer Gradle System-Wide**

```bash
# Installer Gradle via SDK Manager
sudo apt update
sudo apt install gradle

# Vérifier
gradle --version
```

### **Créer le Wrapper**

```bash
cd /home/nayops/Documents/architecture/configtablette/ONIPBiometricApp

# Générer le wrapper
gradle wrapper --gradle-version 8.2
```

### **Build avec Gradle**

```bash
# Maintenant le wrapper existe
./gradlew clean
./gradlew assembleDebug
```

---

## ⚡ **Solution Rapide : Copier depuis SDK Demo**

Les exemples du SDK ont déjà un wrapper Gradle fonctionnel :

```bash
cd /home/nayops/Documents/architecture/configtablette/ONIPBiometricApp

# Copier le wrapper depuis les exemples du SDK
cp -r ../sdk/Customer_support_package-2.8/Code_Samples/Main_Demo/gradle .
cp ../sdk/Customer_support_package-2.8/Code_Samples/Main_Demo/gradlew .
cp ../sdk/Customer_support_package-2.8/Code_Samples/Main_Demo/gradlew.bat .

# Rendre exécutable
chmod +x gradlew

# Maintenant ça devrait marcher
./gradlew clean
./gradlew assembleDebug
```

---

## 📋 **Checklist**

- [ ] Android Studio ouvert
- [ ] Projet ONIPBiometricApp ouvert
- [ ] Synchronisation Gradle terminée (sans erreur)
- [ ] Build → Rebuild Project réussi
- [ ] Tablette connectée (`adb devices`)
- [ ] Prêt à Run ▶️

---

## 🎯 **Recommandation**

**👉 Utilisez Android Studio** - C'est le plus simple et le plus fiable !

1. Ouvrir Android Studio
2. File → Open → ONIPBiometricApp
3. Attendre la synchronisation
4. Run ▶️

**Tout se fait automatiquement !**

---

## 🆘 **Si Problème dans Android Studio**

### **Erreur : "Gradle sync failed"**

**Solution :**
1. **File** → **Invalidate Caches** → **Invalidate and Restart**
2. Attendre le redémarrage
3. Projet se synchronise automatiquement

### **Erreur : "SDK not found"**

**Solution :**
1. **Tools** → **SDK Manager**
2. **SDK Platforms** : Installer Android 11.0 (API 30)
3. **SDK Tools** : Installer Android SDK Build-Tools
4. Cliquer **Apply** → **OK**

### **Erreur : "Gradle version incompatible"**

**Solution :**
1. **File** → **Project Structure**
2. **Project** → Changer **Gradle Version** à `8.2`
3. **OK**
4. Sync Now

---

**Une fois la synchronisation OK, vous pouvez continuer avec le test sur tablette !** 🚀










