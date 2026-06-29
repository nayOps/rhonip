# 📊 Diagrammes des Workflows

## 🔄 Workflow pour Congé - Employé Normal

```
┌─────────────────────────────────────────────────────────────┐
│  EMPLOYÉ CRÉE UNE DEMANDE DE CONGÉ                          │
│  Exemple: Jean Dupont (Direction Technique)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  SYSTÈME DÉTECTE:                                           │
│  ✓ Employé normal (pas directeur)                          │
│  ✓ Direction: Direction Technique                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  SYSTÈME TROUVE LES APPROBATEURS:                           │
│  1. Directeur Technique (directeur.technique@onip.cd)       │
│  2. Directeur RH (directeur.rh@onip.cd)                    │
│  3. Directeur Général (directeur.general@onip.cd)          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  CRÉATION DES 3 APPROBATIONS:                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Approbation #1                                      │   │
│  │ User: directeur.technique@onip.cd                  │   │
│  │ Action: None (en attente)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Approbation #2                                      │   │
│  │ User: directeur.rh@onip.cd                          │   │
│  │ Action: None (en attente)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Approbation #3                                      │   │
│  │ User: directeur.general@onip.cd                     │   │
│  │ Action: None (en attente)                           │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  NOTIFICATIONS ENVOYÉES                                     │
│  → Directeur Technique reçoit une notification             │
│  → Directeur RH reçoit une notification                    │
│  → Directeur Général reçoit une notification               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1: DIRECTEUR TECHNIQUE                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Va sur /action-required/                             │   │
│  │ Voit la demande de congé de Jean Dupont              │   │
│  │ Clique sur "Approve"                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  → Approbation #1: action = 'APPROVED'                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2: DIRECTEUR RH                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Va sur /action-required/                             │   │
│  │ Voit la demande de congé de Jean Dupont              │   │
│  │ Clique sur "Approve"                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  → Approbation #2: action = 'APPROVED'                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 3: DIRECTEUR GÉNÉRAL                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Va sur /action-required/                             │   │
│  │ Voit la demande de congé de Jean Dupont              │   │
│  │ Clique sur "Approve"                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  → Approbation #3: action = 'APPROVED'                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ TOUTES LES APPROBATIONS SONT COMPLÈTES                  │
│  La demande de congé est approuvée                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow pour Congé - Directeur/Sous-directeur

```
┌─────────────────────────────────────────────────────────────┐
│  DIRECTEUR CRÉE UNE DEMANDE DE CONGÉ                       │
│  Exemple: Directeur Technique                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  SYSTÈME DÉTECTE:                                           │
│  ✓ Designation contient "Directeur"                        │
│  ✓ C'est un directeur/sous-directeur                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  SYSTÈME TROUVE LES APPROBATEURS:                           │
│  1. Directeur RH (directeur.rh@onip.cd)                    │
│  2. Directeur Général (directeur.general@onip.cd)          │
│                                                             │
│  ⚠ Note: Le directeur de direction est sauté               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  CRÉATION DES 2 APPROBATIONS:                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Approbation #1                                      │   │
│  │ User: directeur.rh@onip.cd                          │   │
│  │ Action: None (en attente)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Approbation #2                                      │   │
│  │ User: directeur.general@onip.cd                     │   │
│  │ Action: None (en attente)                           │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  NOTIFICATIONS ENVOYÉES                                     │
│  → Directeur RH reçoit une notification                    │
│  → Directeur Général reçoit une notification               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 1: DIRECTEUR RH                                     │
│  → Approbation #1: action = 'APPROVED'                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  ÉTAPE 2: DIRECTEUR GÉNÉRAL                                │
│  → Approbation #2: action = 'APPROVED'                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ TOUTES LES APPROBATIONS SONT COMPLÈTES                  │
│  La demande de congé est approuvée                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow pour Mission - Employé Normal

```
┌─────────────────────────────────────────────────────────────┐
│  EMPLOYÉ CRÉE UNE DEMANDE DE MISSION                        │
│  Exemple: Mission à Kinshasa avec 3 employés               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  SYSTÈME DÉTECTE:                                           │
│  ✓ Prend le premier employé de la liste                   │
│  ✓ Vérifie si c'est un directeur                           │
│  ✓ Si non, utilise le workflow employé normal              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  MÊME PROCESSUS QUE POUR LE CONGÉ                          │
│  1. Directeur de Direction                                 │
│  2. Directeur RH                                           │
│  3. Directeur Général                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Structure des Modèles

### Flow
```
Flow
├── name: "Workflow Approbation Congé - Employé"
├── content_type: ContentType(Leave)
└── steps: FlowStep[]
```

### FlowStep
```
FlowStep
├── flow: Flow
├── name: "Approbation Directeur de Direction"
├── user: User (directeur.technique@onip.cd)
└── parent: FlowStep (null pour la première étape)
```

### Approbation
```
Approbation
├── content_type: ContentType(Leave)
├── object_id: 123 (ID du congé)
├── user: User (directeur.technique@onip.cd)
├── action: None | "APPROVED" | "REJECTED"
└── comment: "Approuvé, bon congé !"
```

---

## 🔍 Détection du Rôle - Code

```python
# Dans core/views/base/create.py

# 1. Récupérer l'employé
employee = form.instance.employee  # ou form.instance.employees.first()

# 2. Vérifier la designation
is_director_or_subdirector = False
if employee and employee.designation:
    designation_name = employee.designation.name.lower()
    is_director_or_subdirector = (
        'directeur' in designation_name or 
        'sous-directeur' in designation_name or
        'sous directeur' in designation_name
    )

# 3. Sélectionner les approbateurs
if is_director_or_subdirector:
    # Workflow court: RH → DG
    approvers = [Directeur RH, Directeur Général]
else:
    # Workflow complet: Directeur Direction → RH → DG
    # Trouver le directeur de la direction de l'employé
    direction_director = User.objects.filter(
        employee__direction=employee.direction,
        employee__designation__name__icontains='Directeur'
    ).exclude(
        employee__designation__name__icontains='Sous-directeur'
    ).first()
    
    approvers = [direction_director, Directeur RH, Directeur Général]
```

---

## 🎯 Points Clés

1. **Automatique** : Les approbateurs sont assignés automatiquement
2. **Intelligent** : Le système détecte le rôle et adapte le workflow
3. **Hiérarchique** : Respect de la hiérarchie organisationnelle
4. **Sécurisé** : Seuls les approbateurs désignés peuvent approuver
5. **Traçable** : Toutes les actions sont enregistrées
6. **Notifié** : Les approbateurs reçoivent des notifications

---

*Diagrammes créés le 25 février 2026*
