# 🎯 Guide de Test - APK de Présence

## 📱 Installation et Test

### 1. Installation de l'APK
```bash
adb install app/build/outputs/apk/debug/presence.apk
```

### 2. Vérification des Services
- **Backend Python**: http://192.168.1.73:8082/api/data
- **Frontend Next.js**: http://192.168.1.73:3001

### 3. Test de la Logique d'Alternance

#### Scénario 1: Premier employé (John Doe)
1. **Première empreinte** → Doit marquer "Arrivée"
2. **Deuxième empreinte** (même employé) → Doit marquer "Départ"
3. **Troisième empreinte** (même employé) → Doit marquer "Arrivée"

#### Scénario 2: Deuxième employé (alema)
1. **Première empreinte** → Doit marquer "Arrivée"
2. **Deuxième empreinte** (même employé) → Doit marquer "Départ"

#### Scénario 3: Mélange d'employés
1. **John Doe** → Arrivée
2. **alema** → Arrivée
3. **John Doe** → Départ
4. **alema** → Départ

## 🔍 Vérification des Logs

### Logs Android
```bash
adb logcat | grep FingerprintTest
```

### Logs Backend
```bash
# Voir les présences enregistrées
curl -s http://192.168.1.73:8082/api/attendance | jq '.data[]'

# Voir les employés
curl -s http://192.168.1.73:8082/api/data | jq '.data[] | {id, firstName, lastName, biometricEnrolled}'
```

## 🎯 Points de Vérification

### ✅ Reconnaissance Correcte
- L'APK doit reconnaître le bon employé
- Les logs doivent montrer: "✓ Correspondance simulée avec employé ID X"

### ✅ Alternance Arrivée/Départ
- Premier scan = Arrivée
- Deuxième scan (même employé) = Départ
- Troisième scan (même employé) = Arrivée

### ✅ Gestion des Erreurs
- Si pas de correspondance: "❌ Empreinte non reconnue"
- Si erreur réseau: Message d'erreur détaillé

## 🚨 Problèmes Connus et Solutions

### Problème: Mauvaise reconnaissance
**Solution**: Vérifier que l'employé a `biometricEnrolled: true`

### Problème: Pas d'alternance
**Solution**: Vérifier les logs pour voir la logique de détermination

### Problème: Erreur réseau
**Solution**: Vérifier que le backend Python est démarré

## 📊 Vérification des Données

### Backend Python
```bash
# Vérifier les employés
curl -s http://192.168.1.73:8082/api/data | jq '.data[] | {id, firstName, lastName, biometricEnrolled}'

# Vérifier les présences
curl -s http://192.168.1.73:8082/api/attendance | jq '.data[] | {employeeId, type, date, time}'
```

### Frontend Next.js
- Ouvrir http://192.168.1.73:3001
- Vérifier que les employés apparaissent
- Vérifier que les présences sont enregistrées

## 🎯 Résultats Attendus

1. **Reconnaissance**: L'APK reconnaît correctement les employés
2. **Alternance**: Arrivée → Départ → Arrivée pour le même employé
3. **Persistance**: Les données sont sauvegardées dans le backend
4. **Interface**: Le frontend affiche les présences en temps réel





