# 🎯 Plan d'Intégration : Dashboard Personnel Moderne pour Employés

## 📋 Objectif

Intégrer **exactement le même design** que le dashboard personnel ARE (`personnal/`) dans le système ONIP RH, avec :
- ✅ Le même design visuel (Tailwind CSS)
- ✅ La même structure et organisation
- ✅ Les mêmes fonctionnalités
- ✅ Les ajouts proposés (Workflow, Documents, Announcements)

---

## 🏗️ Architecture Proposée

### **1. Détection Automatique du Type d'Utilisateur**

Le système détectera automatiquement si l'utilisateur est un **employé normal** et affichera le dashboard personnel moderne, sinon le dashboard classique.

**Logique** :
- Si `not user.is_superuser and not user.is_staff and user.employee` → Dashboard Personnel Moderne
- Sinon → Dashboard Classique (Bootstrap)

---

## 📁 Fichiers à Créer/Modifier

### **A. Templates**

#### **1. `template/home_employee.html`** ⭐ NOUVEAU
**Description** : Template principal du dashboard personnel avec design Tailwind CSS

**Contenu** :
- Structure identique au dashboard ARE (`personnal/code.html`)
- Intégration des widgets Django existants
- Support du mode sombre
- Responsive design

**Sections** :
- Sidebar personnalisée
- Header avec recherche et notifications
- Section de bienvenue personnalisée
- Cartes "My Balance" (Congés, Formations)
- Section "My Workflow" (Tâches, Approbations)
- Section "Recent Documents"
- Sidebar droite (Quick Links, Announcements, Tip of the Day)

---

#### **2. `template/components/balance_card.html`** ⭐ NOUVEAU
**Description** : Composant réutilisable pour les cartes de solde (Congés, Formations)

**Usage** : `{% include 'components/balance_card.html' with title="Remaining Leave" value="14.5" unit="Days" status="Accrued" icon="flight_takeoff" color="blue" %}`

---

#### **3. `template/components/workflow_item.html`** ⭐ NOUVEAU
**Description** : Composant réutilisable pour les items de workflow

**Usage** : `{% include 'components/workflow_item.html' with task=task %}`

---

#### **4. `template/components/document_item.html`** ⭐ NOUVEAU
**Description** : Composant réutilisable pour les documents récents

**Usage** : `{% include 'components/document_item.html' with document=document %}`

---

#### **5. `template/components/quick_link.html`** ⭐ NOUVEAU
**Description** : Composant réutilisable pour les liens rapides

**Usage** : `{% include 'components/quick_link.html' with title="Request Leave" icon="calendar_add_on" url="leave:create" %}`

---

#### **6. `template/components/announcement_card.html`** ⭐ NOUVEAU
**Description** : Composant réutilisable pour les annonces internes

**Usage** : `{% include 'components/announcement_card.html' with announcement=announcement %}`

---

### **B. Vues Django**

#### **7. `core/views/home.py`** 🔄 MODIFIER
**Modifications** :
- Détecter si l'utilisateur est un employé normal
- Utiliser `home_employee.html` pour les employés normaux
- Utiliser `home.html` pour les admins/staff

**Code à ajouter** :
```python
def get(self, request):
    permissions = request.user.get_all_permissions()
    permissions = [permission.split('.')[-1] for permission in permissions]
    widgets = Widget.objects.filter(permissions__codename__in=permissions).distinct().order_by('id')
    
    # Détecter si c'est un employé normal
    is_normal_employee = (
        not request.user.is_superuser and 
        not request.user.is_staff and 
        hasattr(request.user, 'employee') and 
        request.user.employee
    )
    
    template_name = "home_employee.html" if is_normal_employee else "home.html"
    
    return render(request, template_name, {
        'widgets': widgets, 
        'request': request,
        'is_normal_employee': is_normal_employee
    })
```

---

#### **8. `employee/views/my_workflow.py`** ⭐ NOUVEAU
**Description** : Vue pour afficher le workflow personnel (tâches, approbations en attente)

**Fonctionnalités** :
- Liste des approbations en attente
- Liste des tâches assignées
- Filtrage par type (Mail, Project, Meeting, Approval)

---

#### **9. `employee/views/recent_documents.py`** ⭐ NOUVEAU
**Description** : Vue pour afficher les documents récents de l'employé

**Fonctionnalités** :
- Liste des fichiers uploadés récemment
- Filtrage par type de fichier
- Liens de téléchargement

---

#### **10. `employee/views/announcements.py`** ⭐ NOUVEAU
**Description** : Vue pour afficher les annonces internes

**Fonctionnalités** :
- Liste des annonces actives
- Filtrage par type (Service Note, HR Update)
- Affichage des dernières annonces

---

### **C. Modèles Django**

#### **11. `core/models/announcement.py`** ⭐ NOUVEAU
**Description** : Modèle pour les annonces internes

**Champs** :
- `title` : CharField
- `content` : TextField
- `type` : CharField (choices: Service Note, HR Update, General)
- `is_active` : BooleanField
- `created_at` : DateTimeField
- `updated_at` : DateTimeField

---

#### **12. `core/models/document.py`** ⭐ NOUVEAU (Optionnel)
**Description** : Modèle pour les documents liés aux employés

**Champs** :
- `employee` : ForeignKey(Employee)
- `file` : FileField
- `title` : CharField
- `description` : TextField
- `category` : CharField
- `uploaded_at` : DateTimeField

---

### **D. URLs**

#### **13. `employee/urls.py`** 🔄 MODIFIER
**Ajouts** :
```python
path('my-workflow/', MyWorkflowView.as_view(), name='my_workflow'),
path('recent-documents/', RecentDocumentsView.as_view(), name='recent_documents'),
path('announcements/', AnnouncementsView.as_view(), name='announcements'),
```

---

#### **14. `core/urls.py`** 🔄 MODIFIER (si nécessaire)
**Vérifier** : Que les URLs pour les annonces sont bien configurées

---

### **E. Scripts de Migration**

#### **15. `create_announcements_model.py`** ⭐ NOUVEAU
**Description** : Script pour créer le modèle Announcement et les données initiales

---

#### **16. `create_employee_dashboard_widgets_tailwind.py`** ⭐ NOUVEAU
**Description** : Script pour créer/mettre à jour les widgets avec le design Tailwind CSS

**Widgets à créer/modifier** :
1. **Remaining Leave** (Carte de solde)
2. **Training Hours** (Carte de solde)
3. **My Workflow** (Section workflow)
4. **Recent Documents** (Section documents)
5. **Quick Links** (Sidebar droite)
6. **Announcements** (Sidebar droite)
7. **Tip of the Day** (Sidebar droite)

---

### **F. Configuration**

#### **17. `template/base_employee.html`** ⭐ NOUVEAU (Optionnel)
**Description** : Template de base pour les employés avec Tailwind CSS

**Contenu** :
- Inclusion de Tailwind CSS (CDN)
- Configuration Tailwind personnalisée
- Support du mode sombre
- Material Symbols pour les icônes

---

#### **18. `static/css/employee-dashboard.css`** ⭐ NOUVEAU (Optionnel)
**Description** : Styles CSS personnalisés pour le dashboard employé

---

## 🎨 Design System à Implémenter

### **1. Tailwind CSS**

**Méthode** : Via CDN (comme dans le dashboard ARE)

**Configuration** :
```javascript
tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#1258e2",  // À adapter selon ONIP
                "background-light": "#f6f6f8",
                "background-dark": "#101622",
            },
            fontFamily: {
                "display": ["Inter", "sans-serif"]
            },
        },
    },
}
```

---

### **2. Icônes**

**Bibliothèque** : Material Symbols Outlined (Google Fonts)

**Alternative** : Bootstrap Icons (si préféré)

---

### **3. Polices**

**Police principale** : Inter (Google Fonts)

---

## 📊 Structure du Dashboard Personnel

### **Layout**

```
┌─────────────────────────────────────────────────────────┐
│ Sidebar (256px) │ Header (sticky)                        │
│                 ├─────────────────────────────────────────┤
│                 │ Section Bienvenue                       │
│                 │ ┌──────────────────┬─────────────────┐ │
│                 │ │ Colonne Gauche   │ Sidebar Droite   │ │
│                 │ │ (2/3)            │ (1/3)            │ │
│                 │ │                   │                  │ │
│                 │ │ - Cartes Balance │ - Quick Links    │ │
│                 │ │ - My Workflow    │ - Announcements   │ │
│                 │ │ - Recent Docs    │ - Tip of Day     │ │
│                 │ └──────────────────┴─────────────────┘ │
│                 │ Footer                                  │
└─────────────────────────────────────────────────────────┘
```

---

### **Sections Détaillées**

#### **1. Sidebar**
- Logo ONIP
- Menu navigation (Dashboard, Mon Profil, etc.)
- Profil utilisateur en bas

#### **2. Header**
- Titre : "Tableau de Bord Personnel"
- Barre de recherche
- Notifications avec badge

#### **3. Section Bienvenue**
- Message personnalisé : "Bonjour, [Nom Employé]"
- Description : Message ONIP
- Bouton "Nouvelle Demande"

#### **4. Cartes "My Balance"**
- **Remaining Leave** : Solde de congés restants
- **Training Hours** : Heures de formation en cours

#### **5. Section "My Workflow"**
- Liste des approbations en attente
- Liste des tâches assignées
- Types : Mail, Project, Meeting, Approval

#### **6. Section "Recent Documents"**
- Liste des fichiers récemment uploadés
- Types : PDF, DOCX, etc.

#### **7. Sidebar Droite**
- **Quick Links** :
  - Request Leave
  - Submit Report
  - Book Meeting Room
- **Announcements** :
  - Service Notes
  - HR Updates
- **Tip of the Day** :
  - Citation ou conseil du jour

---

## 🔧 Étapes d'Implémentation

### **Phase 1 : Setup Initial** (30 min)

1. ✅ Créer le modèle `Announcement`
2. ✅ Créer les migrations
3. ✅ Ajouter Tailwind CSS au projet
4. ✅ Créer le template `base_employee.html` (optionnel)

---

### **Phase 2 : Templates** (2h)

1. ✅ Créer `template/home_employee.html`
2. ✅ Créer les composants réutilisables :
   - `components/balance_card.html`
   - `components/workflow_item.html`
   - `components/document_item.html`
   - `components/quick_link.html`
   - `components/announcement_card.html`

---

### **Phase 3 : Vues Django** (1h)

1. ✅ Modifier `core/views/home.py` pour détecter les employés
2. ✅ Créer `employee/views/my_workflow.py`
3. ✅ Créer `employee/views/recent_documents.py`
4. ✅ Créer `employee/views/announcements.py`

---

### **Phase 4 : URLs et Navigation** (30 min)

1. ✅ Modifier `employee/urls.py`
2. ✅ Vérifier `core/urls.py`
3. ✅ Mettre à jour `core/context.py` si nécessaire

---

### **Phase 5 : Widgets Tailwind** (2h)

1. ✅ Créer le script `create_employee_dashboard_widgets_tailwind.py`
2. ✅ Adapter les widgets existants au design Tailwind
3. ✅ Créer les nouveaux widgets (Workflow, Documents, Announcements)

---

### **Phase 6 : Données et Tests** (1h)

1. ✅ Créer des données de test (annonces, documents)
2. ✅ Tester le dashboard avec un employé normal
3. ✅ Vérifier le mode sombre
4. ✅ Vérifier la responsivité

---

## 📝 Checklist Complète

### **Templates**
- [ ] `template/home_employee.html`
- [ ] `template/components/balance_card.html`
- [ ] `template/components/workflow_item.html`
- [ ] `template/components/document_item.html`
- [ ] `template/components/quick_link.html`
- [ ] `template/components/announcement_card.html`
- [ ] `template/base_employee.html` (optionnel)

### **Vues**
- [ ] Modifier `core/views/home.py`
- [ ] Créer `employee/views/my_workflow.py`
- [ ] Créer `employee/views/recent_documents.py`
- [ ] Créer `employee/views/announcements.py`

### **Modèles**
- [ ] Créer `core/models/announcement.py`
- [ ] Créer migrations
- [ ] Créer `core/models/document.py` (optionnel)

### **URLs**
- [ ] Modifier `employee/urls.py`
- [ ] Vérifier `core/urls.py`

### **Scripts**
- [ ] Créer `create_announcements_model.py`
- [ ] Créer `create_employee_dashboard_widgets_tailwind.py`

### **Configuration**
- [ ] Ajouter Tailwind CSS (CDN)
- [ ] Ajouter Material Symbols (Google Fonts)
- [ ] Ajouter Inter font (Google Fonts)
- [ ] Configurer le mode sombre

### **Tests**
- [ ] Tester avec un employé normal
- [ ] Tester avec un admin/staff
- [ ] Tester le mode sombre
- [ ] Tester la responsivité
- [ ] Tester les widgets
- [ ] Tester les nouvelles fonctionnalités

---

## 🎯 Résultat Attendu

### **Pour les Employés Normaux**

Un dashboard moderne avec :
- ✅ Design identique au dashboard ARE personnel
- ✅ Sidebar personnalisée
- ✅ Cartes de solde (Congés, Formations)
- ✅ Workflow personnel (Approbations en attente)
- ✅ Documents récents
- ✅ Quick Links
- ✅ Annonces internes
- ✅ Tip of the Day
- ✅ Mode sombre
- ✅ Responsive design

### **Pour les Admins/Staff**

Le dashboard classique actuel (Bootstrap) reste inchangé.

---

## 🚀 Prochaines Étapes

1. **Valider ce plan** avec vous
2. **Commencer l'implémentation** phase par phase
3. **Tester** à chaque étape
4. **Ajuster** selon vos retours

---

## ❓ Questions à Valider

1. **Couleurs** : Utiliser les couleurs ONIP ou garder celles du dashboard ARE ?
2. **Logo** : Logo ONIP dans la sidebar ?
3. **Icônes** : Material Symbols ou Bootstrap Icons ?
4. **Mode sombre** : Activer par défaut ou laisser le choix à l'utilisateur ?
5. **Documents** : Utiliser un modèle Django ou les fichiers uploadés existants ?
6. **Annonces** : Qui peut créer les annonces ? (Admin uniquement ?)

---

## 📎 Fichiers de Référence

- `personnal/code.html` - Template de référence
- `ANALYSE_PERSONNAL_DASHBOARD.md` - Analyse détaillée
- `SYNTHESE_COMPARATIVE_DASHBOARDS.md` - Comparaison complète
- `create_employee_widgets.py` - Script de widgets existant

---

**Prêt à commencer l'implémentation ?** 🚀
