# 🔄 Configuration des Workflows d'Approbation

## ✅ Ce qui a été créé

### 📁 Directions et Sous-directions

#### 1. **Direction Générale**
- Directeur : `directeur.general@onip.cd`
- Sous-directions :
  - Sous-direction Administration
  - Sous-direction Communication
- Sous-directeurs : 2 créés

#### 2. **Direction des Ressources Humaines**
- Directeur : `directeur.rh@onip.cd`
- Sous-directions :
  - Sous-direction Recrutement
  - Sous-direction Formation
- Sous-directeurs : 2 créés

#### 3. **Direction Technique**
- Directeur : `directeur.technique@onip.cd`
- Sous-directions :
  - Sous-direction Développement
  - Sous-direction Support
- Sous-directeurs : 2 créés

#### 4. **Direction Financière**
- Directeur : `directeur.financier@onip.cd`
- Sous-directions :
  - Sous-direction Comptabilité
- Sous-directeurs : 1 créé

### 🔄 Workflows d'Approbation

#### Workflow pour Congé (Leave)

**Pour Employé Normal :**
1. **Directeur de Direction** (directeur de la direction de l'employé)
2. **Directeur RH** (`directeur.rh@onip.cd`)
3. **Directeur Général** (`directeur.general@onip.cd`)

**Pour Directeur/Sous-directeur :**
1. **Directeur RH** (`directeur.rh@onip.cd`)
2. **Directeur Général** (`directeur.general@onip.cd`)

#### Workflow pour Mission

**Pour Employé Normal :**
1. **Directeur de Direction** (directeur de la direction de l'employé)
2. **Directeur RH** (`directeur.rh@onip.cd`)
3. **Directeur Général** (`directeur.general@onip.cd`)

**Pour Directeur/Sous-directeur :**
1. **Directeur RH** (`directeur.rh@onip.cd`)
2. **Directeur Général** (`directeur.general@onip.cd`)

## 🔧 Fonctionnement

### Logique de Sélection du Workflow

Le système détermine automatiquement le workflow à utiliser lors de la création d'un congé ou d'une mission :

1. **Détection du rôle** : Le système vérifie si l'employé est un directeur ou sous-directeur en analysant sa designation
2. **Sélection des approbateurs** :
   - **Employé normal** : Le système trouve automatiquement le directeur de la direction de l'employé, puis ajoute Directeur RH et DG
   - **Directeur/Sous-directeur** : Le système saute l'étape du directeur de direction et passe directement à Directeur RH puis DG

### Code Modifié

Le fichier `core/views/base/create.py` a été modifié pour implémenter cette logique intelligente.

## 👥 Identifiants des Directeurs

Tous les directeurs ont le mot de passe : **`onip2024`**

- **Directeur Général** : `directeur.general@onip.cd`
- **Directeur RH** : `directeur.rh@onip.cd`
- **Directeur Technique** : `directeur.technique@onip.cd`
- **Directeur Financier** : `directeur.financier@onip.cd`

## 📝 Notes Importantes

1. **Contrainte du système** : Le modèle Flow a une contrainte unique sur `content_type`, donc un seul Flow peut être associé à un modèle (Leave ou Mission). La logique de sélection du workflow est donc gérée dans le code Python.

2. **Détection automatique** : Le système détecte automatiquement si un employé est directeur/sous-directeur en vérifiant si le mot "directeur" ou "sous-directeur" est présent dans le nom de sa designation.

3. **Workflow dynamique** : Pour les employés normaux, le système trouve automatiquement le directeur de leur direction et l'ajoute comme premier approbateur.

4. **Ordre d'approbation** : Les approbations sont créées dans l'ordre hiérarchique défini par les FlowStep (via le champ `parent`).

## 🧪 Test du Système

Pour tester les workflows :

1. **Créer un congé pour un employé normal** :
   - Connectez-vous avec un employé normal
   - Créez un congé
   - Vérifiez que les approbations sont créées : Directeur de sa direction → Directeur RH → DG

2. **Créer un congé pour un directeur** :
   - Connectez-vous avec un directeur (ex: `directeur.technique@onip.cd`)
   - Créez un congé
   - Vérifiez que les approbations sont créées : Directeur RH → DG (sans directeur de direction)

3. **Approuver** :
   - Connectez-vous avec un approbateur
   - Allez sur `/action/required` pour voir les actions en attente
   - Approuvez ou rejetez la demande

## 🔍 Vérification

Pour vérifier que tout est configuré :

```bash
# Dans le conteneur
docker exec onip-rh-server-1 sh -c "cd /app/backend && python manage.py shell"
```

Puis dans le shell :
```python
from core.models import Flow, FlowStep
from leave.models import Leave
from mission.models import Mission
from django.contrib.contenttypes.models import ContentType

# Vérifier les flows
leave_ct = ContentType.objects.get_for_model(Leave)
mission_ct = ContentType.objects.get_for_model(Mission)

print("Flows pour Leave:", Flow.objects.filter(content_type=leave_ct).count())
print("Flows pour Mission:", Flow.objects.filter(content_type=mission_ct).count())

# Vérifier les étapes
for flow in Flow.objects.all():
    print(f"\nFlow: {flow.name}")
    for step in flow.steps.all():
        print(f"  - {step.name}: {step.user.email}")
```

---

*Configuration créée le 25 février 2026*
