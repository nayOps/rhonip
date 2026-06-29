# 🔐 Permissions d'un Employé

## 📋 État Actuel

**Situation** : Les employés normaux n'ont actuellement **aucune permission assignée** dans le système.

**Impact** :
- ❌ Ne peuvent pas voir les menus configurés
- ❌ Ne peuvent pas créer de congés
- ❌ Ne peuvent pas créer de missions
- ❌ Ne peuvent pas voir leurs propres données
- ✅ Peuvent se connecter
- ✅ Peuvent voir le tableau de bord (vide)
- ✅ Peuvent voir les notifications
- ✅ Peuvent voir "Action requise"

---

## ✅ Permissions Recommandées pour un Employé

### **1. Module Leave (Congés)**

#### **Permissions Essentielles**
- ✅ `leave.add_leave` : **Créer un congé**
  - **Nécessaire pour** : Permettre à l'employé de créer des demandes de congé
  - **URL** : `/leave/leave/create/`
  - **Action** : Création de demandes de congé

- ✅ `leave.view_leave` : **Voir les congés**
  - **Nécessaire pour** : Permettre à l'employé de voir ses propres congés
  - **URL** : `/leave/leave/`
  - **Action** : Liste et détails de ses congés
  - **Filtrage** : Automatique (seulement ses propres congés)

- ✅ `leave.change_leave` : **Modifier un congé**
  - **Nécessaire pour** : Permettre à l'employé de modifier ses congés (si pas encore approuvés)
  - **URL** : `/leave/leave/change/<id>/`
  - **Action** : Modification de ses congés

- ⚠️ `leave.delete_leave` : **Supprimer un congé** (Optionnel)
  - **Nécessaire pour** : Permettre à l'employé de supprimer ses congés (si pas encore approuvés)
  - **URL** : `/leave/leave/delete/<id>/`
  - **Action** : Suppression de ses congés
  - **Note** : Généralement, on ne permet pas la suppression après création

#### **Permissions Optionnelles**
- `leave.view_earlyleave` : Voir les départs anticipés
- `leave.add_earlyleave` : Créer un départ anticipé

---

### **2. Module Mission**

#### **Permissions Essentielles**
- ✅ `mission.add_mission` : **Créer une mission**
  - **Nécessaire pour** : Permettre à l'employé de créer des demandes de mission
  - **URL** : `/mission/mission/create/`
  - **Action** : Création de demandes de mission

- ✅ `mission.view_mission` : **Voir les missions**
  - **Nécessaire pour** : Permettre à l'employé de voir ses propres missions
  - **URL** : `/mission/mission/`
  - **Action** : Liste et détails de ses missions
  - **Filtrage** : Automatique (seulement ses propres missions)

- ✅ `mission.change_mission` : **Modifier une mission**
  - **Nécessaire pour** : Permettre à l'employé de modifier ses missions (si pas encore approuvées)
  - **URL** : `/mission/mission/change/<id>/`
  - **Action** : Modification de ses missions

- ⚠️ `mission.delete_mission` : **Supprimer une mission** (Optionnel)
  - **Nécessaire pour** : Permettre à l'employé de supprimer ses missions (si pas encore approuvées)
  - **URL** : `/mission/mission/delete/<id>/`
  - **Action** : Suppression de ses missions

#### **Permissions Optionnelles**
- `mission.add_report` : Créer un rapport de mission
- `mission.view_report` : Voir les rapports de mission

---

### **3. Module Employee (Employés)**

#### **Permissions Essentielles**
- ✅ `employee.view_employee` : **Voir les employés**
  - **Nécessaire pour** : Permettre à l'employé de voir son propre profil
  - **URL** : `/employee/employee/`
  - **Action** : Voir son profil d'employé
  - **Filtrage** : Automatique (seulement lui-même)

- ⚠️ `employee.change_employee` : **Modifier un employé** (Optionnel)
  - **Nécessaire pour** : Permettre à l'employé de modifier certaines informations de son profil
  - **URL** : `/employee/employee/change/<id>/`
  - **Action** : Modification de son profil
  - **Note** : Généralement limité à certaines informations (téléphone, adresse, etc.)

#### **Permissions Optionnelles**
- `employee.view_attendance` : Voir ses présences
- `employee.add_attendance` : Enregistrer sa présence (si système de pointage)
- `employee.view_overtime` : Voir ses heures supplémentaires

---

### **4. Module Training (Formations)**

#### **Permissions Optionnelles**
- `training.view_training` : Voir les formations
  - **Utile pour** : Permettre à l'employé de voir les formations disponibles et ses formations
  - **URL** : `/training/training/`
  - **Filtrage** : Automatique (seulement ses formations)

---

## 📊 Liste Complète des Permissions Recommandées

### **Permissions Essentielles (Minimum)**

```
leave.add_leave          # Créer un congé
leave.view_leave         # Voir les congés
leave.change_leave       # Modifier un congé

mission.add_mission      # Créer une mission
mission.view_mission     # Voir les missions
mission.change_mission   # Modifier une mission

employee.view_employee   # Voir son profil
```

### **Permissions Recommandées (Complet)**

```
leave.add_leave          # Créer un congé
leave.view_leave         # Voir les congés
leave.change_leave       # Modifier un congé

mission.add_mission      # Créer une mission
mission.view_mission     # Voir les missions
mission.change_mission   # Modifier une mission

employee.view_employee   # Voir son profil
employee.change_employee # Modifier son profil (limité)

training.view_training   # Voir les formations
```

---

## 🔧 Comment Assigner les Permissions

### **Méthode 1 : Via l'Interface Admin Django**

1. Se connecter en tant qu'admin
2. Aller sur `/buple/core/user/`
3. Sélectionner l'employé
4. Dans "Permissions utilisateur", assigner les permissions
5. Sauvegarder

### **Méthode 2 : Via un Groupe Django (Recommandé)**

1. Créer un groupe "Employés" dans `/buple/auth/group/`
2. Assigner toutes les permissions recommandées au groupe
3. Ajouter l'employé au groupe

**Avantages** :
- Plus facile à gérer
- Cohérence entre tous les employés
- Modification en un seul endroit

### **Méthode 3 : Via le Code Python**

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()

# Récupérer l'employé
employee = User.objects.get(email='david.kalonji@onip.cd')

# Permissions essentielles
permissions = [
    'leave.add_leave',
    'leave.view_leave',
    'leave.change_leave',
    'mission.add_mission',
    'mission.view_mission',
    'mission.change_mission',
    'employee.view_employee',
]

# Assigner les permissions
for perm_string in permissions:
    app_label, codename = perm_string.split('.')
    perm = Permission.objects.get(
        content_type__app_label=app_label,
        codename=codename
    )
    employee.user_permissions.add(perm)
```

---

## 🎯 Script de Configuration Automatique

### **Créer un Groupe "Employés" avec Permissions**

```python
from django.contrib.auth.models import Group, Permission

# Créer le groupe
group, created = Group.objects.get_or_create(name='Employés')

# Permissions essentielles
permissions = [
    'leave.add_leave',
    'leave.view_leave',
    'leave.change_leave',
    'mission.add_mission',
    'mission.view_mission',
    'mission.change_mission',
    'employee.view_employee',
]

# Assigner les permissions au groupe
for perm_string in permissions:
    app_label, codename = perm_string.split('.')
    try:
        perm = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename
        )
        group.permissions.add(perm)
    except Permission.DoesNotExist:
        print(f"Permission {perm_string} non trouvée")

print(f"Groupe '{group.name}' créé avec {group.permissions.count()} permissions")
```

### **Assigner le Groupe aux Employés**

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
group = Group.objects.get(name='Employés')

# Assigner à tous les employés normaux
employees = User.objects.filter(is_staff=False, is_superuser=False)
for employee in employees:
    employee.groups.add(group)
    print(f"Groupe assigné à {employee.email}")

print(f"{employees.count()} employés assignés au groupe")
```

---

## 📋 Matrice des Permissions

| Permission | Créer | Voir | Modifier | Supprimer | Employé Normal |
|-----------|-------|------|----------|------------|----------------|
| **Congé** | `leave.add_leave` | `leave.view_leave` | `leave.change_leave` | `leave.delete_leave` | ✅ Essentiel |
| **Mission** | `mission.add_mission` | `mission.view_mission` | `mission.change_mission` | `mission.delete_mission` | ✅ Essentiel |
| **Employé** | ❌ | `employee.view_employee` | `employee.change_employee` | ❌ | ✅ Essentiel |
| **Formation** | ❌ | `training.view_training` | ❌ | ❌ | ⚠️ Optionnel |

---

## 🔍 Filtrage Automatique

### **Comportement pour Employés Normaux**

Les employés normaux (`is_staff=False`, `is_superuser=False`) bénéficient d'un **filtrage automatique** :

```python
# Dans core/models/managers/base.py
# Les employés normaux voient seulement :
# - Les objets qui leur appartiennent (user=request.user)
# - Les objets liés à leur employé (employee=request.user.employee)
```

**Exemples** :
- ✅ `leave.view_leave` : Voit seulement ses propres congés
- ✅ `mission.view_mission` : Voit seulement ses propres missions
- ✅ `employee.view_employee` : Voit seulement son propre profil

**Même avec `view_*` permissions**, un employé normal ne verra **jamais** les données des autres employés.

---

## ⚠️ Permissions Spéciales

### **Approbateur**

Un employé peut être **approbateur** même sans permissions spéciales. Il suffit qu'il soit assigné comme approbateur dans une demande.

**Permissions nécessaires** :
- Aucune permission spéciale requise
- Le système vérifie automatiquement si l'utilisateur est dans la liste des approbateurs

**Fonctionnalités** :
- Voir les demandes dans "Action requise"
- Approuver/rejeter les demandes
- Ajouter des commentaires

---

## 🎯 Résumé

### **Permissions Minimum pour un Employé**

Pour qu'un employé puisse utiliser le système de base :

1. ✅ `leave.add_leave` - Créer des congés
2. ✅ `leave.view_leave` - Voir ses congés
3. ✅ `mission.add_mission` - Créer des missions
4. ✅ `mission.view_mission` - Voir ses missions
5. ✅ `employee.view_employee` - Voir son profil

### **Permissions Recommandées**

Ajouter également :

6. ✅ `leave.change_leave` - Modifier ses congés
7. ✅ `mission.change_mission` - Modifier ses missions
8. ⚠️ `employee.change_employee` - Modifier son profil (limité)
9. ⚠️ `training.view_training` - Voir les formations

---

## 🚀 Action Immédiate

**Pour activer les fonctionnalités pour les employés**, il faut :

1. **Créer un groupe "Employés"** avec les permissions essentielles
2. **Assigner tous les employés normaux** à ce groupe
3. **Vérifier** que les employés peuvent maintenant créer des congés et missions

**Script disponible** : Voir section "Script de Configuration Automatique" ci-dessus.

---

*Document créé le 25 février 2026*
