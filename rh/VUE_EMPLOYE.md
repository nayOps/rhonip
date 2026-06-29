# 👤 Ce qu'un Employé Voit en Se Connectant

## 🎯 Vue d'Ensemble

Quand un employé se connecte à l'application, il accède à une interface personnalisée selon ses **permissions** et son **rôle**. Voici ce qu'il voit :

---

## 🏠 **1. Page d'Accueil (Tableau de Bord)**

**URL** : `/` ou `/home/`

### **Contenu** :
- **Widgets personnalisés** : Des widgets configurés selon les permissions de l'utilisateur
- Si aucun widget n'est configuré ou si l'utilisateur n'a pas les permissions : Message "Aucun widget trouver"

### **Comment ça fonctionne** :
```python
# Le système filtre les widgets selon les permissions
permissions = request.user.get_all_permissions()
widgets = Widget.objects.filter(permissions__codename__in=permissions)
```

---

## 📋 **2. Menu de Navigation (Sidebar)**

Le menu est toujours visible sur le côté gauche de l'écran. Il contient :

### **A. Menus Forcés (Toujours Visibles)**

#### **1. Tableau de bord** 🏠
- **Icône** : `bi-grid-fill`
- **URL** : `/`
- **Description** : Page d'accueil avec les widgets
- **Toujours visible** : ✅ Oui

#### **2. Notification** 🔔
- **Icône** : `bi-bell-fill`
- **URL** : `/notifications`
- **Badge** : Nombre de notifications non lues
- **Description** : Liste de toutes les notifications reçues
- **Toujours visible** : ✅ Oui

#### **3. Action requise** ⚡
- **Icône** : `bi-lightning-fill`
- **URL** : `/action/required`
- **Badge** : Nombre d'approbations en attente
- **Description** : Liste des demandes nécessitant une approbation
- **Toujours visible** : ✅ Oui
- **Contenu** : 
  - Liste des approbations en attente (`action=None`)
  - Pour chaque approbation :
    - Type de demande (Congé, Mission, etc.)
    - Demandeur
    - Date de création
    - Lien pour voir les détails

#### **4. Paramètres** ⚙️
- **Icône** : `bi-gear-fill`
- **Sous-menus** (selon permissions) :
  - Menus
  - Modèle de document
  - Importateur
  - Widget
  - Préférences
  - Équipe
  - Autorisations des groupes
  - Organisation
  - Flux de travail
  - Job

#### **5. Profil** 👤
- **Icône** : `bi-person-lines-fill`
- **Sous-menus** :
  - Modifier le mot de passe
  - Se déconnecter

### **B. Menus Configurés (Selon Permissions)**

Les menus sont créés dynamiquement selon les **permissions** de l'utilisateur :

```python
# Le système vérifie les permissions pour chaque élément de menu
menu = [{
    'title': module.name,
    'children': [{
        'title': child.name,
        'href': reverse_lazy('core:list', kwargs={'app': child.app_label, 'model': child.model}),
        'permission': f'{child.app_label}.view_{child.model}'
    } for child in module.children.all() 
        if request.user.has_perm(f'{child.app_label}.view_{child.model}')]
} for module in modules]
```

**Exemples de menus configurés** :
- **Employé** : Liste des modules liés aux employés (si permissions)
  - Site
  - Position
  - Direction
  - Employé
  - Sous-direction
  - Service
  - Demande d'information
  - Réponse à la demande d'information
  - Heures supplémentaires
  - Présence

- **Mission** : Liste des modules liés aux missions (si permissions)
  - Mission
  - Rapport

---

## 🔐 **3. Permissions et Accès**

### **Système de Permissions**

L'application utilise le système de permissions Django standard :

- **Format** : `<app_label>.<action>_<model>`
- **Exemples** :
  - `leave.view_leave` : Voir les congés
  - `leave.add_leave` : Créer un congé
  - `leave.change_leave` : Modifier un congé
  - `mission.view_mission` : Voir les missions

### **Filtrage Automatique des Données**

Pour les **employés normaux** (non-staff, non-superuser), le système filtre automatiquement les données :

```python
# Dans core/models/managers/base.py
# Les employés normaux voient seulement :
# - Les objets qui leur appartiennent (user=request.user)
# - Les objets liés à leur employé (employee=request.user.employee)
```

**Exemples** :
- Un employé voit **seulement ses propres congés**
- Un employé voit **seulement ses propres missions**
- Un employé voit **seulement ses propres données**

---

## 📝 **4. Fonctionnalités Accessibles**

### **A. Créer une Demande**

#### **Créer un Congé**
- **URL** : `/leave/leave/create/`
- **Permission requise** : `leave.add_leave`
- **Champs** :
  - Type de congé
  - Dates (du/au)
  - Motif
  - Remplaçant (optionnel)
- **Comportement** :
  - Le champ "employé" est automatiquement rempli avec l'employé connecté
  - Le champ "employé" est désactivé (non modifiable)
  - Après création, les approbations sont créées automatiquement

#### **Créer une Mission**
- **URL** : `/mission/mission/create/`
- **Permission requise** : `mission.add_mission`
- **Champs** :
  - Nom
  - Description
  - Destination
  - Employés (peut inclure plusieurs employés)
  - Dates (début/fin)
- **Comportement** :
  - L'employé peut s'ajouter lui-même ou d'autres employés
  - Après création, les approbations sont créées automatiquement

### **B. Voir ses Demandes**

#### **Liste des Congés**
- **URL** : `/leave/leave/`
- **Permission requise** : `leave.view_leave`
- **Contenu** : Liste filtrée de ses propres congés

#### **Liste des Missions**
- **URL** : `/mission/mission/`
- **Permission requise** : `mission.view_mission`
- **Contenu** : Liste filtrée de ses propres missions

### **C. Voir les Détails**

#### **Détail d'un Congé**
- **URL** : `/leave/leave/read/<id>/`
- **Contenu** :
  - Informations complètes du congé
  - État des approbations
  - Historique des approbations
  - Boutons d'action (si approbateur)

#### **Détail d'une Mission**
- **URL** : `/mission/mission/read/<id>/`
- **Contenu** : Informations complètes de la mission

### **D. Approuver/Rejeter (Si Approbateur)**

Si l'employé est un **approbateur** pour une demande :

- **Bouton "Approve"** : Approuver la demande
- **Bouton "Désapprouver"** : Rejeter la demande
- **Champ commentaire** : Ajouter un commentaire

**URLs** :
- Approuver : `/approbation/approved/<app>/<model>/<pk>`
- Rejeter : `/approbation/rejected/<app>/<model>/<pk>`

---

## 🔔 **5. Notifications**

### **Page des Notifications**
- **URL** : `/notifications`
- **Contenu** :
  - Liste de toutes les notifications reçues
  - Notifications lues/non lues
  - Détails de chaque notification

### **Types de Notifications**
- **Demande d'approbation** : Quand une demande nécessite votre approbation
- **Approbation effectuée** : Quand une de vos demandes est approuvée/rejetée
- **Autres notifications système**

---

## ⚡ **6. Action Requise**

### **Page Action Requise**
- **URL** : `/action/required`
- **Contenu** :
  - Tableau listant toutes les approbations en attente
  - Colonnes :
    - # (numéro)
    - Modèle (type de demande)
    - Demandeur
    - Description
    - Créé à (date)
    - Action (lien "Voir")
  - Si aucune approbation : Message "Oupps... Nous n'avons rien trouvé"

### **Fonctionnement**
```python
# Affiche seulement les approbations en attente pour l'utilisateur
Approbation.objects.filter(user=request.user, action__isnull=True)
```

---

## 🎨 **7. Interface Utilisateur**

### **En-tête (Header)**
- **Logo** de l'organisation
- **Nom de l'utilisateur** connecté
- **Menu utilisateur** (déconnexion, etc.)

### **Sidebar (Menu Latéral)**
- **Logo** de l'organisation
- **Toggle dark/light mode** (thème clair/sombre)
- **Menu de navigation** avec tous les modules accessibles

### **Zone de Contenu**
- **Messages** (succès, erreur, avertissement)
- **Breadcrumb** (fil d'Ariane)
- **Contenu principal** selon la page

---

## 📊 **8. Exemple Concret : Employé Normal**

### **Scénario : David KALONJI (Développeur)**

1. **Se connecte** avec `david.kalonji@onip.cd` / `onip2024`

2. **Voit dans le menu** :
   - ✅ Tableau de bord
   - ✅ Notification (badge: 0)
   - ✅ Action requise (badge: 0)
   - ✅ Paramètres (sous-menus selon permissions)
   - ✅ Profil
   - ❌ Menus configurés (si pas de permissions)

3. **Page d'accueil** :
   - Widgets (si configurés et permissions)
   - Sinon : "Aucun widget trouver"

4. **Peut créer** :
   - Un congé (si permission `leave.add_leave`)
   - Une mission (si permission `mission.add_mission`)

5. **Voit seulement** :
   - Ses propres congés
   - Ses propres missions
   - Ses propres données

6. **Si approbateur** :
   - Voit les demandes dans "Action requise"
   - Peut approuver/rejeter

---

## 🔑 **9. Différences : Employé vs Directeur**

| Fonctionnalité | Employé Normal | Directeur |
|---------------|----------------|-----------|
| **Voir tous les congés** | ❌ Seulement les siens | ✅ Tous (si permissions) |
| **Voir toutes les missions** | ❌ Seulement les siennes | ✅ Toutes (si permissions) |
| **Créer un congé** | ✅ Oui (pour lui) | ✅ Oui (pour lui) |
| **Approuver des demandes** | ✅ Si approbateur | ✅ Si approbateur |
| **Voir les employés** | ❌ Seulement lui | ✅ Tous (si permissions) |
| **Accès admin** | ❌ Non | ✅ Si `is_staff=True` |

---

## ⚠️ **10. Notes Importantes**

1. **Permissions** : Si un employé n'a pas de permissions, il ne verra que les menus forcés (Tableau de bord, Notifications, Action requise, Paramètres, Profil)

2. **Filtrage automatique** : Les employés normaux voient automatiquement seulement leurs propres données

3. **Workflow automatique** : Lors de la création d'un congé/mission, les approbations sont créées automatiquement

4. **Notifications** : Les notifications sont envoyées automatiquement aux approbateurs

5. **Action requise** : Cette page est cruciale pour les approbateurs, elle liste toutes les demandes en attente

---

## 🎯 **11. Résumé**

Quand un employé se connecte, il voit :

✅ **Toujours** :
- Tableau de bord
- Notifications
- Action requise
- Paramètres
- Profil

✅ **Selon permissions** :
- Menus configurés (Employé, Mission, etc.)
- Widgets sur la page d'accueil
- Accès aux listes et formulaires

✅ **Fonctionnalités** :
- Créer des congés/missions
- Voir ses propres données
- Approuver/rejeter (si approbateur)
- Recevoir des notifications

---

*Document créé le 25 février 2026*
