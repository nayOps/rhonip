# 📋 Proposition : Vue et Widgets pour Employés

## 🎯 Objectif

Créer une interface dédiée aux employés pour qu'ils puissent :
1. **Voir leur profil** via une URL dédiée (pas `/list/employee/employee`)
2. **Avoir des widgets dans le dashboard** avec leurs informations importantes

---

## 📊 Analyse de la Situation Actuelle

### ✅ Ce qui existe déjà :
- ✅ Vue `Employee` dans `employee/views/employee.py` (hérite de `Change`)
- ✅ URL `/employee/change/<pk>` pour modifier un employé
- ✅ Système de widgets avec permissions
- ✅ Filtrage automatique pour les employés normaux

### ❌ Ce qui manque :
- ❌ URL dédiée pour voir son propre profil (ex: `/my-profile/`)
- ❌ Widgets spécifiques pour les employés dans le dashboard
- ❌ Vue personnalisée pour afficher le profil en mode lecture seule

---

## 💡 Proposition de Solution

### 1️⃣ **Créer une vue dédiée "Mon Profil"**

#### **URL** : `/my-profile/` ou `/employee/my-profile/`

#### **Fonctionnalités** :
- Affiche le profil de l'employé connecté en mode lecture seule
- Redirige automatiquement vers le profil de l'utilisateur connecté
- Accessible uniquement aux employés normaux (pas besoin de permission spéciale)
- Bouton "Modifier" si l'utilisateur a la permission `employee.change_employee`

#### **Fichiers à créer/modifier** :
- `employee/views/my_profile.py` : Nouvelle vue
- `employee/urls.py` : Ajouter la route
- `template/employee/my_profile.html` : Template dédié

---

### 2️⃣ **Créer des Widgets pour le Dashboard**

#### **Widget 1 : Mon Profil (Carte d'identité)**
- **Permissions** : `employee.view_employee`
- **Contenu** :
  - Photo de l'employé
  - Nom complet
  - Matricule
  - Position / Designation
  - Direction
  - Lien vers "Mon Profil"

#### **Widget 2 : Mes Congés**
- **Permissions** : `leave.view_leave`
- **Contenu** :
  - Nombre de congés en attente d'approbation
  - Nombre de congés approuvés ce mois
  - Jours de congé restants (si disponible)
  - Lien vers la liste des congés

#### **Widget 3 : Mes Missions**
- **Permissions** : `mission.view_mission`
- **Contenu** :
  - Nombre de missions en cours
  - Nombre de missions à venir
  - Missions en attente d'approbation
  - Lien vers la liste des missions

#### **Widget 4 : Mes Présences (si disponible)**
- **Permissions** : `employee.view_attendance`
- **Contenu** :
  - Présences ce mois
  - Jours travaillés
  - Heures supplémentaires
  - Lien vers les présences

#### **Widget 5 : Actions Requises**
- **Permissions** : Tous les employés
- **Contenu** :
  - Nombre d'approbations en attente
  - Nombre de notifications non lues
  - Lien vers "Action Requise"

---

## 🛠️ Implémentation Proposée

### **Étape 1 : Vue "Mon Profil"**

```python
# employee/views/my_profile.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.http import Http404

class MyProfile(LoginRequiredMixin, View):
    template_name = "employee/my_profile.html"
    
    def get(self, request):
        if not request.user.employee:
            raise Http404("Aucun profil d'employé associé")
        
        employee = request.user.employee
        can_edit = request.user.has_perm('employee.change_employee')
        
        return render(request, self.template_name, {
            'employee': employee,
            'can_edit': can_edit
        })
```

### **Étape 2 : Ajouter l'URL**

```python
# employee/urls.py
urlpatterns = [
    path('my-profile/', MyProfile.as_view(), name='my_profile'),
    # ... autres URLs
]
```

### **Étape 3 : Ajouter au Menu**

```python
# core/context.py - Dans la fonction base()
# Ajouter un menu "Mon Profil" pour les employés normaux
if not request.user.is_superuser and not request.user.is_staff:
    if request.user.employee:
        menu.insert(1, dict({
            'title': _('Mon Profil'),
            'href': reverse_lazy('employee:my_profile'),
            'icon': 'bi-person-fill',
            'forced': True
        }))
```

### **Étape 4 : Créer les Widgets**

Les widgets seront créés via l'interface d'administration Django avec :
- **Nom** : "Mon Profil", "Mes Congés", etc.
- **Permissions** : Les permissions correspondantes
- **Template HTML** : Le code HTML pour afficher les informations
- **View Python** : Le code Python pour récupérer les données

---

## 📝 Exemple de Widget "Mon Profil"

### **Template HTML** :
```html
<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body text-center">
            {% if employee.photo %}
                <img src="{{ employee.photo.url }}" class="rounded-circle mb-3" width="100" height="100">
            {% else %}
                <div class="rounded-circle bg-secondary mb-3 d-inline-flex align-items-center justify-content-center" style="width: 100px; height: 100px;">
                    <i class="bi bi-person-fill text-white" style="font-size: 3rem;"></i>
                </div>
            {% endif %}
            <h5 class="card-title">{{ employee.full_name }}</h5>
            <p class="text-muted mb-1">Matricule: {{ employee.registration_number }}</p>
            {% if employee.designation %}
                <p class="text-muted mb-1">{{ employee.designation.name }}</p>
            {% endif %}
            {% if employee.direction %}
                <p class="text-muted mb-3">{{ employee.direction.name }}</p>
            {% endif %}
            <a href="{% url 'employee:my_profile' %}" class="btn btn-primary">
                <i class="bi bi-eye"></i> Voir mon profil
            </a>
        </div>
    </div>
</div>
```

### **View Python** :
```python
from employee.models import Employee

employee = request.user.employee
```

---

## ✅ Avantages de cette Solution

1. **URL dédiée** : `/my-profile/` est plus claire que `/list/employee/employee`
2. **Interface personnalisée** : Template dédié pour les employés
3. **Widgets informatifs** : Dashboard riche avec toutes les informations importantes
4. **Sécurité** : Accès automatique au profil de l'utilisateur connecté
5. **Extensibilité** : Facile d'ajouter de nouveaux widgets

---

## 🎯 Prochaines Étapes

1. ✅ **Valider cette proposition**
2. 🔨 **Créer la vue "Mon Profil"**
3. 🔨 **Créer le template**
4. 🔨 **Ajouter l'URL et le menu**
5. 🔨 **Créer les widgets via l'interface admin**
6. 🧪 **Tester avec David KALONJI**

---

## ❓ Questions à Valider

1. **URL préférée** : `/my-profile/` ou `/employee/my-profile/` ?
2. **Widgets prioritaires** : Quels widgets créer en premier ?
3. **Template** : Utiliser le template `read.html` existant ou créer un nouveau ?
4. **Menu** : Où placer "Mon Profil" dans le menu ? (après Dashboard ?)

---

*Document créé le : 2025-01-XX*
