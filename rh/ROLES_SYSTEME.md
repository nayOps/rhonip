# 👥 Rôles dans le Système - Définitions Complètes

## 📋 Vue d'Ensemble

Le système Payday ONIP utilise plusieurs niveaux de rôles pour gérer les accès et les workflows d'approbation :

1. **Types d'utilisateurs Django** (niveau système)
2. **Designations** (positions organisationnelles)
3. **Rôles dans les workflows** (logique métier)
4. **Groupes Django** (permissions groupées)

---

## 1️⃣ TYPES D'UTILISATEURS DJANGO

### 🔴 **Superutilisateur (Superuser)**

**Définition** : Utilisateur avec tous les droits dans le système.

**Caractéristiques** :
- `is_superuser = True`
- `is_staff = True`
- Accès complet à toutes les fonctionnalités
- Peut voir et modifier toutes les données
- Accès à l'interface d'administration Django
- Peut créer/modifier/supprimer n'importe quel objet
- **Pas de filtrage** : Voit toutes les données de tous les employés

**Utilisation** :
- Administrateurs système
- Support technique
- Gestionnaires de haut niveau

**Exemple** :
- Email : `admin@onip.cd`
- Nombre actuel : 1

---

### 🟡 **Staff (Personnel)**

**Définition** : Utilisateur avec accès privilégié mais pas superutilisateur.

**Caractéristiques** :
- `is_staff = True`
- `is_superuser = False`
- Accès à l'interface d'administration Django
- Peut voir toutes les données (pas de filtrage automatique)
- Permissions définies par groupes ou permissions individuelles
- Utilisé pour les directeurs et gestionnaires

**Utilisation** :
- Directeurs
- Gestionnaires RH
- Responsables de services

**Exemple** :
- Directeur RH : `directeur.rh@onip.cd`
- Directeur Technique : `directeur.technique@onip.cd`
- Nombre actuel : 11

---

### 🟢 **Utilisateur Normal**

**Définition** : Employé standard sans privilèges spéciaux.

**Caractéristiques** :
- `is_staff = False`
- `is_superuser = False`
- **Filtrage automatique** : Voit seulement ses propres données
- Accès limité aux fonctionnalités selon permissions
- Peut créer des demandes (congés, missions)
- Peut voir ses propres données

**Utilisation** :
- Employés standards
- Personnel opérationnel

**Exemple** :
- Développeur : `david.kalonji@onip.cd`
- Chef de Projet : `paul.kasenga@onip.cd`
- Nombre actuel : 2

---

## 2️⃣ DESIGNATIONS (Positions Organisationnelles)

Les designations définissent la position hiérarchique d'un employé dans l'organisation. Elles sont utilisées pour déterminer les workflows d'approbation.

### 🏢 **Niveau Direction**

#### **Directeur Général**
- **Définition** : Responsable de la direction générale de l'organisation
- **Hiérarchie** : Niveau le plus élevé
- **Rôle dans workflow** : Approbateur final pour tous les workflows
- **Direction** : Direction Générale
- **Workflow** : Approuve en dernière instance

#### **Directeur RH (Ressources Humaines)**
- **Définition** : Responsable de la direction des ressources humaines
- **Hiérarchie** : Niveau direction
- **Rôle dans workflow** : Approbateur pour tous les workflows (congés, missions)
- **Direction** : Direction des Ressources Humaines
- **Workflow** : Approuve après le directeur de direction (pour employés) ou en première instance (pour directeurs)

#### **Directeur Technique**
- **Définition** : Responsable de la direction technique
- **Hiérarchie** : Niveau direction
- **Rôle dans workflow** : Approbateur pour les employés de sa direction
- **Direction** : Direction Technique
- **Workflow** : Première approbation pour les employés de la Direction Technique

#### **Directeur Financier**
- **Définition** : Responsable de la direction financière
- **Hiérarchie** : Niveau direction
- **Rôle dans workflow** : Approbateur pour les employés de sa direction
- **Direction** : Direction Financière
- **Workflow** : Première approbation pour les employés de la Direction Financière

---

### 🏛️ **Niveau Sous-Direction**

#### **Sous-directeur**
- **Définition** : Responsable d'une sous-direction, sous l'autorité d'un directeur
- **Hiérarchie** : Niveau sous-direction
- **Rôle dans workflow** : Traité comme un directeur (workflow court)
- **Exemples** :
  - Sous-directeur Sous-direction Administration
  - Sous-directeur Sous-direction Communication
  - Sous-directeur Sous-direction Recrutement
  - Sous-directeur Sous-direction Formation
  - Sous-directeur Sous-direction Développement
  - Sous-directeur Sous-direction Support
  - Sous-directeur Sous-direction Comptabilité
- **Workflow** : Directeur RH → Directeur Général (saut du directeur de direction)

---

### 👔 **Niveau Management**

#### **Chef de Projet**
- **Définition** : Responsable de la gestion et coordination de projets
- **Hiérarchie** : Niveau management
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

#### **Responsable RH**
- **Définition** : Responsable des opérations RH au sein d'une direction
- **Hiérarchie** : Niveau management
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

#### **Responsable Communication**
- **Définition** : Responsable de la communication et du marketing
- **Hiérarchie** : Niveau management
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

---

### 💼 **Niveau Opérationnel**

#### **Développeur**
- **Définition** : Développeur de logiciels et applications
- **Hiérarchie** : Niveau opérationnel
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

#### **Analyste**
- **Définition** : Analyste de données et processus
- **Hiérarchie** : Niveau opérationnel
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

#### **Technicien**
- **Définition** : Technicien spécialisé
- **Hiérarchie** : Niveau opérationnel
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

#### **Comptable**
- **Définition** : Comptable responsable de la gestion financière
- **Hiérarchie** : Niveau opérationnel
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

#### **Assistante**
- **Définition** : Assistante administrative
- **Hiérarchie** : Niveau opérationnel
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

#### **Chargée de Mission**
- **Définition** : Chargée de missions spéciales
- **Hiérarchie** : Niveau opérationnel
- **Rôle dans workflow** : Employé normal
- **Workflow** : Directeur de Direction → Directeur RH → Directeur Général

---

## 3️⃣ RÔLES DANS LES WORKFLOWS

### 🔄 **Employé Normal**

**Définition** : Employé qui n'est ni directeur ni sous-directeur.

**Détection** :
```python
# Le système vérifie si la designation contient "directeur" ou "sous-directeur"
is_director_or_subdirector = (
    'directeur' in designation_name.lower() or 
    'sous-directeur' in designation_name.lower()
)
```

**Workflow** :
1. **Directeur de Direction** (directeur de la direction de l'employé)
2. **Directeur RH**
3. **Directeur Général**

**Exemples de designations** :
- Développeur
- Chef de Projet
- Analyste
- Technicien
- Comptable
- Responsable RH
- Assistante
- Chargée de Mission

---

### 🔄 **Directeur/Sous-directeur**

**Définition** : Employé avec une designation contenant "directeur" ou "sous-directeur".

**Détection** :
- Designation contient "directeur" (sauf "sous-directeur" exclu pour trouver le vrai directeur)
- Designation contient "sous-directeur" ou "sous directeur"

**Workflow** :
1. **Directeur RH**
2. **Directeur Général**

**Note** : Le directeur de direction est sauté car c'est lui qui fait la demande.

**Exemples de designations** :
- Directeur Général
- Directeur RH
- Directeur Technique
- Directeur Financier
- Sous-directeur Sous-direction Administration
- Sous-directeur Sous-direction Communication
- Tous les sous-directeurs

---

### ✅ **Approbateur**

**Définition** : Utilisateur désigné pour approuver ou rejeter une demande.

**Caractéristiques** :
- Assigné automatiquement lors de la création d'une demande
- Peut voir les demandes dans "Action requise"
- Peut approuver (`APPROVED`) ou rejeter (`REJECTED`)
- Peut ajouter un commentaire

**Types d'approbateurs** :
1. **Directeur de Direction** : Pour les employés de sa direction
2. **Directeur RH** : Pour toutes les demandes
3. **Directeur Général** : Approbateur final pour toutes les demandes

---

## 4️⃣ GROUPES DJANGO

**État actuel** : Aucun groupe configuré dans le système.

**Définition** : Les groupes Django permettent de regrouper des permissions et de les assigner à plusieurs utilisateurs.

**Utilisation recommandée** :
- **Groupe "Employés"** : Permissions de base (voir ses données, créer des demandes)
- **Groupe "Directeurs"** : Permissions étendues (voir toutes les données de leur direction)
- **Groupe "RH"** : Permissions RH complètes
- **Groupe "Administrateurs"** : Toutes les permissions

---

## 5️⃣ PERMISSIONS PRINCIPALES

### 📦 **Module Leave (Congés)**

- `leave.add_leave` : Créer un congé
- `leave.view_leave` : Voir les congés
- `leave.change_leave` : Modifier un congé
- `leave.delete_leave` : Supprimer un congé
- `leave.add_earlyleave` : Créer un départ anticipé
- `leave.view_earlyleave` : Voir les départs anticipés
- `leave.add_holiday` : Créer un jour férié

### 📦 **Module Mission**

- `mission.add_mission` : Créer une mission
- `mission.view_mission` : Voir les missions
- `mission.change_mission` : Modifier une mission
- `mission.delete_mission` : Supprimer une mission
- `mission.add_report` : Créer un rapport de mission

### 📦 **Module Employee (Employés)**

- `employee.add_employee` : Créer un employé
- `employee.view_employee` : Voir les employés
- `employee.change_employee` : Modifier un employé
- `employee.delete_employee` : Supprimer un employé
- `employee.add_attendance` : Enregistrer une présence
- `employee.view_attendance` : Voir les présences
- `employee.add_agreement` : Créer un type de contrat
- `employee.view_agreement` : Voir les types de contrats

### 📦 **Module Training (Formations)**

- `training.add_training` : Créer une formation
- `training.view_training` : Voir les formations
- `training.change_training` : Modifier une formation
- `training.delete_training` : Supprimer une formation

---

## 6️⃣ MATRICE DES RÔLES

| Rôle | Type User | is_staff | is_superuser | Filtrage Données | Workflow |
|------|-----------|----------|--------------|------------------|----------|
| **Superutilisateur** | Superuser | ✅ | ✅ | ❌ (Tout) | N/A |
| **Directeur** | Staff | ✅ | ❌ | ❌ (Tout) | RH → DG |
| **Sous-directeur** | Staff | ✅ | ❌ | ❌ (Tout) | RH → DG |
| **Employé Normal** | Normal | ❌ | ❌ | ✅ (Ses données) | Dir → RH → DG |

---

## 7️⃣ DÉTECTION AUTOMATIQUE DES RÔLES

### **Code de Détection**

```python
# Dans core/views/base/create.py

# 1. Récupérer l'employé
employee = form.instance.employee

# 2. Vérifier la designation
is_director_or_subdirector = False
if employee and employee.designation:
    designation_name = employee.designation.name.lower()
    is_director_or_subdirector = (
        'directeur' in designation_name or 
        'sous-directeur' in designation_name or
        'sous directeur' in designation_name
    )

# 3. Sélectionner le workflow
if is_director_or_subdirector:
    # Workflow court: Directeur RH → DG
    approvers = [Directeur RH, Directeur Général]
else:
    # Workflow complet: Directeur Direction → Directeur RH → DG
    approvers = [Directeur Direction, Directeur RH, Directeur Général]
```

---

## 8️⃣ RÉSUMÉ DES RÔLES

### **Par Hiérarchie**

1. **Superutilisateur** : Accès total
2. **Directeur Général** : Approbateur final
3. **Directeur RH** : Approbateur pour toutes les demandes
4. **Directeur de Direction** : Approbateur pour sa direction
5. **Sous-directeur** : Traité comme directeur (workflow court)
6. **Chef/Responsable** : Employé normal
7. **Employé Opérationnel** : Employé normal

### **Par Fonction dans Workflow**

1. **Demandeur** : Crée la demande
2. **Approbateur** : Approuve/rejette la demande
3. **Bénéficiaire** : Reçoit la notification de l'approbation

---

## 9️⃣ RECOMMANDATIONS

### **Création de Groupes**

Il est recommandé de créer des groupes Django pour faciliter la gestion des permissions :

1. **Groupe "Employés"** :
   - `leave.add_leave`, `leave.view_leave`
   - `mission.add_mission`, `mission.view_mission`
   - `employee.view_employee` (seulement soi-même)

2. **Groupe "Directeurs"** :
   - Toutes les permissions "Employés"
   - `leave.view_leave` (tous)
   - `mission.view_mission` (tous)
   - `employee.view_employee` (tous de leur direction)

3. **Groupe "RH"** :
   - Toutes les permissions
   - Gestion complète des employés

4. **Groupe "Administrateurs"** :
   - Toutes les permissions
   - Accès à tous les modules

---

*Document créé le 25 février 2026*
