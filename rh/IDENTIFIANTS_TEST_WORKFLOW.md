# 🔐 Identifiants pour Tester les Workflows

## 👤 Comptes Utilisateurs Créés

### 🟢 **EMPLOYÉS NORMAUX** (Pour tester le workflow complet)

#### **1. David KALONJI - Développeur**
- **Email** : `david.kalonji@onip.cd`
- **Mot de passe** : `onip2024`
- **Designation** : Développeur
- **Direction** : Direction Technique
- **Rôle** : Employé normal
- **Workflow** : Directeur Technique → Directeur RH → Directeur Général

#### **2. Paul KASENGA - Chef de Projet**
- **Email** : `paul.kasenga@onip.cd`
- **Mot de passe** : `onip2024`
- **Designation** : Chef de Projet
- **Direction** : Direction Technique
- **Rôle** : Employé normal
- **Workflow** : Directeur Technique → Directeur RH → Directeur Général

---

### 🔵 **DIRECTEURS** (Pour tester le workflow directeur)

#### **1. Directeur Technique**
- **Email** : `directeur.technique@onip.cd`
- **Mot de passe** : `onip2024`
- **Designation** : Directeur Technique
- **Direction** : Direction Technique
- **Rôle** : Directeur
- **Workflow** : Directeur RH → Directeur Général (saut du directeur de direction)

#### **2. Directeur RH**
- **Email** : `directeur.rh@onip.cd`
- **Mot de passe** : `onip2024`
- **Designation** : Directeur RH
- **Direction** : Direction des Ressources Humaines
- **Rôle** : Directeur
- **Workflow** : Directeur RH → Directeur Général (saut du directeur de direction)

#### **3. Directeur Général**
- **Email** : `directeur.general@onip.cd`
- **Mot de passe** : `onip2024`
- **Designation** : Directeur Général
- **Direction** : Direction Générale
- **Rôle** : Directeur
- **Workflow** : Directeur RH → Directeur Général (saut du directeur de direction)

---

## 🧪 Scénarios de Test

### **Test 1 : Workflow Congé - Employé Normal**

1. **Se connecter en tant qu'employé normal** :
   - Email : `david.kalonji@onip.cd`
   - Mot de passe : `onip2024`

2. **Créer une demande de congé** :
   - Aller sur `/leave/leave/create/`
   - Remplir le formulaire :
     - Type de congé : Choisir un type
     - Dates : Du [date] au [date]
     - Motif : "Test workflow"
   - Cliquer sur "Enregistrer"

3. **Vérifier les approbations créées** :
   - Le système doit créer 3 approbations :
     - ✅ Directeur Technique (`directeur.technique@onip.cd`)
     - ✅ Directeur RH (`directeur.rh@onip.cd`)
     - ✅ Directeur Général (`directeur.general@onip.cd`)

4. **Se connecter en tant que Directeur Technique** :
   - Email : `directeur.technique@onip.cd`
   - Mot de passe : `onip2024`
   - Aller sur `/action-required/`
   - Voir la demande de congé de David KALONJI
   - Cliquer sur "Approve"

5. **Se connecter en tant que Directeur RH** :
   - Email : `directeur.rh@onip.cd`
   - Mot de passe : `onip2024`
   - Aller sur `/action-required/`
   - Voir la demande de congé de David KALONJI
   - Cliquer sur "Approve"

6. **Se connecter en tant que Directeur Général** :
   - Email : `directeur.general@onip.cd`
   - Mot de passe : `onip2024`
   - Aller sur `/action-required/`
   - Voir la demande de congé de David KALONJI
   - Cliquer sur "Approve"

7. **Vérifier que toutes les approbations sont complètes** :
   - Se connecter en tant qu'admin ou employé
   - Voir le détail du congé
   - Vérifier que les 3 approbations sont "APPROVED"

---

### **Test 2 : Workflow Congé - Directeur**

1. **Se connecter en tant que Directeur Technique** :
   - Email : `directeur.technique@onip.cd`
   - Mot de passe : `onip2024`

2. **Créer une demande de congé** :
   - Aller sur `/leave/leave/create/`
   - Remplir le formulaire
   - Cliquer sur "Enregistrer"

3. **Vérifier les approbations créées** :
   - Le système doit créer **2 approbations seulement** :
     - ✅ Directeur RH (`directeur.rh@onip.cd`)
     - ✅ Directeur Général (`directeur.general@onip.cd`)
   - ⚠️ **Le Directeur Technique ne doit PAS être dans la liste** (car c'est lui qui fait la demande)

4. **Approuver avec Directeur RH puis Directeur Général**

---

### **Test 3 : Workflow Mission - Employé Normal**

1. **Se connecter en tant qu'employé normal** :
   - Email : `paul.kasenga@onip.cd`
   - Mot de passe : `onip2024`

2. **Créer une demande de mission** :
   - Aller sur `/mission/mission/create/`
   - Remplir le formulaire :
     - Nom : "Mission à Kinshasa"
     - Description : "Test workflow mission"
     - Destination : "Kinshasa"
     - Employés : Sélectionner Paul KASENGA
     - Dates : Du [date] au [date]
   - Cliquer sur "Enregistrer"

3. **Vérifier les approbations** :
   - Même workflow que pour le congé (3 approbations)

---

### **Test 4 : Workflow Mission - Directeur**

1. **Se connecter en tant que Directeur RH** :
   - Email : `directeur.rh@onip.cd`
   - Mot de passe : `onip2024`

2. **Créer une demande de mission**

3. **Vérifier les approbations** :
   - 2 approbations seulement (Directeur RH → Directeur Général)

---

## 📋 Checklist de Test

### ✅ **Vérifications à faire** :

- [ ] Un employé normal peut créer un congé
- [ ] Un employé normal peut créer une mission
- [ ] Un directeur peut créer un congé
- [ ] Un directeur peut créer une mission
- [ ] Les approbations sont créées automatiquement
- [ ] Le workflow employé normal a 3 approbations
- [ ] Le workflow directeur a 2 approbations
- [ ] Les approbateurs reçoivent des notifications
- [ ] Les approbateurs voient les demandes dans `/action-required/`
- [ ] Les approbateurs peuvent approuver
- [ ] Les approbateurs peuvent rejeter
- [ ] Les commentaires peuvent être ajoutés
- [ ] L'état des approbations est mis à jour correctement
- [ ] Seuls les approbateurs désignés peuvent approuver

---

## 🔍 URLs Utiles

- **Page de connexion** : `http://localhost:8000/login/`
- **Page d'accueil** : `http://localhost:8000/`
- **Action Required** : `http://localhost:8000/action-required/`
- **Créer un congé** : `http://localhost:8000/leave/leave/create/`
- **Créer une mission** : `http://localhost:8000/mission/mission/create/`
- **Liste des congés** : `http://localhost:8000/leave/leave/`
- **Liste des missions** : `http://localhost:8000/mission/mission/`

---

## 🎯 Résumé des Identifiants

| Rôle | Email | Mot de passe | Workflow |
|------|-------|--------------|----------|
| **Employé Normal** | `david.kalonji@onip.cd` | `onip2024` | 3 étapes |
| **Employé Normal** | `paul.kasenga@onip.cd` | `onip2024` | 3 étapes |
| **Directeur Technique** | `directeur.technique@onip.cd` | `onip2024` | 2 étapes |
| **Directeur RH** | `directeur.rh@onip.cd` | `onip2024` | 2 étapes |
| **Directeur Général** | `directeur.general@onip.cd` | `onip2024` | 2 étapes |
| **Admin** | `admin@onip.cd` | `onip2024` | Tous les accès |

---

## ⚠️ Notes Importantes

1. **Mot de passe** : Tous les comptes utilisent le mot de passe `onip2024`
2. **Workflow automatique** : Les approbations sont créées automatiquement lors de la création d'une demande
3. **Détection du rôle** : Le système détecte automatiquement si l'employé est un directeur en analysant sa designation
4. **Notifications** : Les approbateurs reçoivent des notifications (si le système de notifications est activé)
5. **Sécurité** : Seuls les approbateurs désignés peuvent approuver/rejeter une demande

---

*Document créé le 25 février 2026*
