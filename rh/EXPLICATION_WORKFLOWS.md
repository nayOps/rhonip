# 🔄 Explication Complète des Workflows d'Approbation

## 📋 Vue d'Ensemble

Le système de workflow d'approbation permet de gérer les demandes de **congés** et de **missions** avec un processus d'approbation hiérarchique automatique. Le système détermine automatiquement les approbateurs selon le rôle de l'employé qui fait la demande.

---

## 🏗️ Architecture du Système

### 1. **Modèles de Base**

#### **Flow** (`core/models/flow.py`)
- **Rôle** : Définit un workflow d'approbation pour un type de contenu (ex: Leave, Mission)
- **Champs** :
  - `name` : Nom du workflow
  - `content_type` : Type de contenu associé (Leave, Mission, etc.)
- **Relation** : Un Flow peut avoir plusieurs `FlowStep`

#### **FlowStep** (`core/models/flow.py`)
- **Rôle** : Définit une étape dans le workflow
- **Champs** :
  - `flow` : Le workflow parent
  - `name` : Nom de l'étape
  - `user` : L'utilisateur responsable de cette étape
  - `parent` : L'étape précédente (pour créer une hiérarchie)
- **Hiérarchie** : Les étapes sont liées par `parent` pour créer un ordre séquentiel

#### **Approbation** (`core/models/approbation.py`)
- **Rôle** : Enregistre l'approbation ou le rejet d'une demande
- **Champs** :
  - `content_type` + `object_id` : L'objet à approuver (via GenericForeignKey)
  - `user` : L'utilisateur qui approuve/rejette
  - `action` : `APPROVED` ou `REJECTED`
  - `comment` : Commentaire optionnel
- **États** :
  - `action=None` : En attente d'approbation
  - `action='APPROVED'` : Approuvé
  - `action='REJECTED'` : Rejeté

---

## 🔄 Processus Complet d'un Workflow

### **Étape 1 : Création d'une Demande (Congé ou Mission)**

Lorsqu'un employé crée une demande de congé ou de mission, le système :

1. **Enregistre la demande** dans la base de données
2. **Détermine automatiquement les approbateurs** selon le rôle de l'employé
3. **Crée les enregistrements d'approbation** pour chaque approbateur

#### **Code dans `core/views/base/create.py`** :

```python
# Après la sauvegarde du formulaire
form.save()

# 1. Récupérer le Flow correspondant au type de modèle
flow = Flow.objects.filter(content_type__model=model._meta.model_name).first()

# 2. Déterminer si l'employé est un directeur/sous-directeur
is_director_or_subdirector = False
if employee and employee.designation:
    designation_name = employee.designation.name.lower()
    is_director_or_subdirector = (
        'directeur' in designation_name or 
        'sous-directeur' in designation_name
    )

# 3. Sélectionner les approbateurs selon le rôle
if is_director_or_subdirector:
    # Workflow pour directeur: Directeur RH → DG
    approvers = [Directeur RH, Directeur Général]
else:
    # Workflow pour employé: Directeur de Direction → Directeur RH → DG
    approvers = [Directeur de Direction, Directeur RH, Directeur Général]

# 4. Créer les enregistrements d'approbation
Approbation.objects.bulk_create(approvers)
```

---

### **Étape 2 : Notification des Approbateurs**

Lors de la création, le système envoie des notifications aux approbateurs via le système de notifications Django.

#### **Code dans `core/views/base/base.py`** :

```python
# Notification automatique
notify.send(
    sender=request.user,
    recipient=approver,
    verb='Demande d\'approbation',
    description='Demande d\'approbation pour le/la {model} #{pk}'
)
```

---

### **Étape 3 : Approbation/Rejet**

Chaque approbateur peut :

1. **Voir les demandes en attente** via la page "Action Required" (`/action-required/`)
2. **Approuver ou rejeter** via les boutons sur la page de détail de la demande
3. **Ajouter un commentaire** optionnel

#### **URLs d'approbation** :
- **Approuver** : `/approbation/approved/<app>/<model>/<pk>`
- **Rejeter** : `/approbation/rejected/<app>/<model>/<pk>`

#### **Code dans `core/views/approbation.py`** :

```python
def post(self, request, action, app, model, pk):
    # Vérifier que l'utilisateur est bien un approbateur
    if request.user.id not in approbations.users():
        messages.warning(request, 'Vous n\'êtes pas désigné comme approbateur')
        return redirect(obj.get_absolute_url())
    
    # Enregistrer l'approbation/rejet
    approbations.filter(
        user=request.user, 
        action=None
    ).update(
        action=action.upper(),  # 'APPROVED' ou 'REJECTED'
        comment=comment
    )
```

---

## 🎯 Workflows par Type de Demande

### **1. Workflow pour Congé (Leave)**

#### **Pour un Employé Normal** :

```
1. Directeur de Direction (directeur de la direction de l'employé)
   ↓
2. Directeur RH (directeur.rh@onip.cd)
   ↓
3. Directeur Général (directeur.general@onip.cd)
```

**Logique** :
- Le système trouve automatiquement le directeur de la direction de l'employé
- Puis ajoute le Directeur RH et le Directeur Général

#### **Pour un Directeur/Sous-directeur** :

```
1. Directeur RH (directeur.rh@onip.cd)
   ↓
2. Directeur Général (directeur.general@onip.cd)
```

**Logique** :
- Le système détecte que l'employé est un directeur/sous-directeur
- Il saute l'étape du directeur de direction
- Passe directement au Directeur RH puis au DG

---

### **2. Workflow pour Mission**

#### **Pour un Employé Normal** :

```
1. Directeur de Direction (directeur de la direction de l'employé)
   ↓
2. Directeur RH (directeur.rh@onip.cd)
   ↓
3. Directeur Général (directeur.general@onip.cd)
```

**Note** : Pour une mission, si plusieurs employés sont impliqués, le système prend le premier employé pour déterminer le workflow.

#### **Pour un Directeur/Sous-directeur** :

```
1. Directeur RH (directeur.rh@onip.cd)
   ↓
2. Directeur Général (directeur.general@onip.cd)
```

---

## 🔍 Détection Automatique du Rôle

Le système détermine automatiquement si un employé est un directeur/sous-directeur en analysant sa **designation** :

```python
if employee and employee.designation:
    designation_name = employee.designation.name.lower()
    is_director_or_subdirector = (
        'directeur' in designation_name or 
        'sous-directeur' in designation_name or
        'sous directeur' in designation_name
    )
```

**Exemples de designations détectées** :
- ✅ "Directeur Technique"
- ✅ "Sous-directeur RH"
- ✅ "Sous directeur Financier"
- ❌ "Chef de Service" (non détecté comme directeur)

---

## 📊 États d'une Demande

### **États des Approbations**

Une demande peut avoir plusieurs approbations, chacune avec son propre état :

1. **En attente** (`action=None`) : L'approbateur n'a pas encore pris de décision
2. **Approuvé** (`action='APPROVED'`) : L'approbateur a approuvé
3. **Rejeté** (`action='REJECTED'`) : L'approbateur a rejeté

### **Méthodes Utiles** (`core/models/managers/approbation.py`)

```python
# Approbations en attente
Approbation.objects.pending()

# Approbations approuvées
Approbation.objects.approved()

# Approbations rejetées
Approbation.objects.rejected()

# Liste des utilisateurs approbateurs
Approbation.objects.users()

# Vérifier si toutes les approbations sont faites
Approbation.objects.is_fully_approved()
```

---

## 🎨 Interface Utilisateur

### **1. Page "Action Required"**

**URL** : `/action-required/`

Affiche toutes les demandes en attente d'approbation pour l'utilisateur connecté :

```python
Approbation.objects.filter(user=request.user, action__isnull=True)
```

### **2. Page de Détail d'une Demande**

Sur la page de détail d'un congé ou d'une mission, les approbateurs voient :

- **Bouton "Approve"** : Pour approuver la demande
- **Bouton "Désapprouver"** : Pour rejeter la demande
- **Champ commentaire** : Pour ajouter un commentaire

**Code dans `template/read.html` et `template/change.html`** :

```html
<a href="{% url 'core:approbation' 'approved' app model obj.pk %}">
    Approve
</a>
<a href="{% url 'core:approbation' 'rejected' app model obj.pk %}">
    Désapprouver
</a>
```

---

## 🔐 Sécurité et Permissions

### **Vérifications de Sécurité**

1. **Vérification de l'approbateur** :
   ```python
   if request.user.id not in approbations.users():
       messages.warning(request, 'Vous n\'êtes pas désigné comme approbateur')
       return redirect(obj.get_absolute_url())
   ```

2. **Vérification de l'action** :
   ```python
   if action.upper() not in ['APPROVED', 'REJECTED']:
       raise Http404
   ```

3. **Vérification de l'état** :
   - Seules les approbations avec `action=None` peuvent être modifiées
   - Une fois approuvée/rejetée, l'approbation ne peut plus être modifiée

---

## 📝 Exemple Concret : Demande de Congé

### **Scénario 1 : Employé Normal**

1. **Jean Dupont** (employé de la Direction Technique) crée une demande de congé
2. **Le système détecte** :
   - Jean n'est pas directeur/sous-directeur
   - Sa direction est "Direction Technique"
3. **Le système trouve** :
   - Directeur de Direction Technique : `directeur.technique@onip.cd`
   - Directeur RH : `directeur.rh@onip.cd`
   - Directeur Général : `directeur.general@onip.cd`
4. **Le système crée 3 approbations** :
   - Approbation 1 : `directeur.technique@onip.cd` (en attente)
   - Approbation 2 : `directeur.rh@onip.cd` (en attente)
   - Approbation 3 : `directeur.general@onip.cd` (en attente)
5. **Notifications envoyées** aux 3 approbateurs
6. **Le Directeur Technique approuve** → Approbation 1 devient `APPROVED`
7. **Le Directeur RH approuve** → Approbation 2 devient `APPROVED`
8. **Le Directeur Général approuve** → Approbation 3 devient `APPROVED`
9. **✅ Toutes les approbations sont complètes**

### **Scénario 2 : Directeur**

1. **Directeur Technique** crée une demande de congé
2. **Le système détecte** :
   - C'est un directeur (designation contient "Directeur")
3. **Le système crée 2 approbations** :
   - Approbation 1 : `directeur.rh@onip.cd` (en attente)
   - Approbation 2 : `directeur.general@onip.cd` (en attente)
4. **Le Directeur RH approuve** → Approbation 1 devient `APPROVED`
5. **Le Directeur Général approuve** → Approbation 2 devient `APPROVED`
6. **✅ Toutes les approbations sont complètes**

---

## 🛠️ Configuration des Workflows

Les workflows sont configurés via le script `setup_workflows.py` qui :

1. **Crée les Directions et Sous-directions**
2. **Crée les utilisateurs** pour les directeurs et sous-directeurs
3. **Crée les Flow** pour Leave et Mission
4. **Crée les FlowStep** avec la hiérarchie appropriée

**Note importante** : Le modèle `Flow` ne permet qu'un seul Flow par `ContentType`. C'est pourquoi la logique de distinction entre employé normal et directeur est gérée dans la vue `Create` plutôt que par des Flow séparés.

---

## 🔄 Flux de Données Complet

```
┌─────────────────┐
│  Employé crée   │
│  une demande    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Système détecte│
│  le rôle        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sélection des  │
│  approbateurs   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Création des   │
│  Approbations   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Notifications  │
│  envoyées       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Approbateurs   │
│  voient la      │
│  demande        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Approbation/   │
│  Rejet          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Mise à jour    │
│  de l'état      │
└─────────────────┘
```

---

## ✅ Résumé

1. **Création automatique** : Les approbateurs sont assignés automatiquement lors de la création
2. **Détection intelligente** : Le système détecte le rôle de l'employé pour choisir le bon workflow
3. **Hiérarchie respectée** : Les approbations suivent l'ordre hiérarchique (Directeur → RH → DG)
4. **Notifications** : Les approbateurs sont notifiés automatiquement
5. **Sécurité** : Seuls les approbateurs désignés peuvent approuver/rejeter
6. **Traçabilité** : Toutes les approbations sont enregistrées avec commentaires et dates

---

*Documentation créée le 25 février 2026*
