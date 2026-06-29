# 📋 RAPPORT DE VÉRIFICATION - SCHÉMA FGP

## ✅ CE QUI EXISTE ACTUELLEMENT

### **Tables Django créées automatiquement (17 tables)**
1. ✅ `fgp_person_core` - Table principale FGP Core (27 variables)
2. ✅ `fgp_biometric` - Données biométriques
3. ✅ `enrollment_sessions` - Sessions d'enrôlement
4. ✅ `enrollment_validations` - Validations
5. ✅ `enrollment_events` - Événements
6. ✅ `enrollment_receipts` - Récépissés
7. ✅ `enrollment_statistics` - Statistiques
8. ✅ Tables Django par défaut (auth, admin, etc.)

---

## ❌ CE QUI MANQUE

### **Tables du schéma SQL non créées**

#### **1. Tables d'appartenance aux strates**
- ❌ `fgp_strata_membership` - Appartenance aux différentes strates

#### **2. Tables d'extensions par strate (9 tables)**
- ❌ `ext_eleves` - Extension Élèves
- ❌ `ext_etudiants` - Extension Étudiants
- ❌ `ext_electeurs` - Extension Électeurs
- ❌ `ext_pnc` - Extension Police (PNC)
- ❌ `ext_fardc` - Extension Armée (FARDC)
- ❌ `ext_prison` - Extension Prisonniers
- ❌ `ext_refugies` - Extension Réfugiés
- ❌ `ext_enfants` - Extension Enfants
- ❌ `ext_fonctionnaires` - Extension Fonctionnaires

#### **3. Tables système**
- ❌ `fgp_documents` - Documents et pièces jointes
- ❌ `fgp_audit_trail` - Traçabilité complète
- ❌ `abis_matches` - Résultats de déduplication biométrique

#### **4. Vues**
- ❌ `v_person_complete` - Vue complète d'une personne

---

## 🔍 ANALYSE DES CHAMPS

### **Frontend → Backend → Base de données**

#### **A. FORMULAIRE DE BASE (BaseEnrollmentData)**

| # | Champ Frontend | Modèle Django (PersonCore) | Table SQL (fgp_person_core) | Statut |
|---|---|---|---|---|
| 1 | `nom` | ✅ `nom` | ✅ `nom` | ✅ OK |
| 2 | `prenom` | ✅ `prenom` | ✅ `prenom` | ✅ OK |
| 3 | `postnom` | ✅ `postnom` | ✅ `postnom` | ✅ OK |
| 4 | `autres_noms` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 5 | `sexe` | ✅ `sexe` | ✅ `sexe` | ✅ OK |
| 6 | `date_naissance` | ✅ `date_naissance` | ✅ `date_naissance` | ✅ OK |
| 7 | `lieu_naissance` | ✅ `lieu_naissance` | ✅ `lieu_naissance` | ✅ OK |
| 8 | `nationalite` | ✅ `nationalite` | ✅ `nationalite` | ✅ OK |
| 9 | `taille` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 10 | `couleur_yeux` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 11 | `groupe_sanguin` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 12 | `telephone` | ✅ `telephone` | ✅ `telephone` | ✅ OK |
| 13 | `email` | ✅ `email` | ✅ `email` | ✅ OK |
| 14 | `boite_postale` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

#### **B. ORIGINE (Frontend)**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 15 | `origine_pays` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 16 | `origine_province` | ✅ `province_naissance` | ✅ `province_naissance` | ⚠️ MAPPING |
| 17 | `origine_ville` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 18 | `origine_commune` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 19 | `origine_quartier` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

#### **C. RÉSIDENCE (Frontend)**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 20 | `residence_pays` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 21 | `residence_province` | ✅ `province_residence` | ✅ `province_residence` | ✅ OK |
| 22 | `residence_ville` | ❌ **MANQUANT** (territoire) | ❌ **MANQUANT** | ⚠️ MAPPING |
| 23 | `residence_commune` | ✅ `commune_residence` | ✅ `commune_residence` | ✅ OK |
| 24 | `residence_quartier` | ✅ `quartier_residence` | ✅ `quartier_residence` | ✅ OK |
| 25 | `residence_rue` | ✅ `avenue_residence` | ✅ `avenue_residence` | ⚠️ MAPPING |
| 26 | `residence_numero` | ✅ `numero_residence` | ✅ `numero_residence` | ✅ OK |

#### **D. SITUATION FAMILIALE**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 27 | `etat_matrimonial` | ✅ `statut_matrimonial` | ✅ `statut_matrimonial` | ⚠️ MAPPING |
| 28 | `nombre_enfants` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 29 | `conjoint_nom` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 30 | `conjoint_prenom` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 31 | `conjoint_nationalite` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 32 | `conjoint_lieu_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 33 | `conjoint_date_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 34 | `conjoint_telephone` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

#### **E. FILIATION (Parents)**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 35 | `pere_statut` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 36 | `pere_nom` | ✅ `nom_pere` | ✅ `nom_pere` | ⚠️ PARTIEL |
| 37 | `pere_prenom` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 38 | `pere_nationalite` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 39 | `pere_nin` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 40 | `pere_lieu_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 41 | `pere_date_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 42 | `pere_adresse` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 43 | `mere_statut` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 44 | `mere_nom` | ✅ `nom_mere` | ✅ `nom_mere` | ⚠️ PARTIEL |
| 45 | `mere_prenom` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 46 | `mere_nationalite` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 47 | `mere_nin` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 48 | `mere_lieu_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 49 | `mere_date_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 50 | `mere_adresse` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

#### **F. TUTEUR (pour mineurs)**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 51 | `tuteur_nom` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 52 | `tuteur_prenom` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 53 | `tuteur_nationalite` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 54 | `tuteur_lien` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 55 | `tuteur_lieu_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 56 | `tuteur_date_naissance` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 57 | `tuteur_sexe` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 58 | `tuteur_adresse` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

#### **G. ÉTUDES**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 59 | `niveau_etude` | ✅ `niveau_etude` | ✅ `niveau_etude` | ✅ OK |
| 60 | `certificat_diplome` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 61 | `pays_obtention` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 62 | `etablissement` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 63 | `ville_etablissement` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 64 | `annee_debut` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 65 | `annee_obtention` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 66 | `domaine` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 67 | `specialisation` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 68 | `mention` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 69 | `numero_document` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

#### **H. PROFESSION**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 70 | `profession` | ✅ `profession` | ✅ `profession` | ✅ OK |
| 71 | `employeur` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 72 | `fonction` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

#### **I. PIÈCES D'IDENTITÉ**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 73 | `piece_presentee` | ✅ `type_piece_identite` | ✅ `type_piece_identite` | ⚠️ MAPPING |
| 74 | `numero_piece` | ✅ `numero_piece_identite` | ✅ `numero_piece_identite` | ⚠️ MAPPING |
| 75 | `date_piece` | ✅ `date_emission_piece` | ✅ `date_emission_piece` | ⚠️ MAPPING |

#### **J. DIVERS**

| # | Champ Frontend | Modèle Django | Table SQL | Statut |
|---|---|---|---|---|
| 76 | `handicaps` (array) | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 77 | `strata` (array) | ❌ **MANQUANT** (table séparée) | ❌ **MANQUANT** | ⚠️ PROBLÈME |
| 78 | `type_requete` | ❌ **MANQUANT** | ❌ **MANQUANT** | ⚠️ PROBLÈME |

---

## 📊 STATISTIQUES

### **Champs du formulaire de base**
- **Total champs frontend**: 78 champs
- **Champs existants dans Django**: ~27 champs (35%)
- **Champs manquants**: ~51 champs (65%)

### **Tables**
- **Tables existantes**: 17
- **Tables manquantes**: ~15
- **Taux de complétion**: 53%

---

## 🚨 PROBLÈMES CRITIQUES IDENTIFIÉS

### **1. Modèle PersonCore incomplet**
Le modèle Django `PersonCore` ne contient que les **27 variables obligatoires du décret**, mais le formulaire frontend collecte **78+ champs** détaillés.

**Champs manquants critiques**:
- Informations détaillées des parents (prénom, nationalité, NIN, etc.)
- Informations du conjoint (complet)
- Informations du tuteur (complet)
- Détails des études (établissement, dates, domaine, etc.)
- Caractéristiques physiques (taille, couleur yeux, groupe sanguin)
- Origine géographique détaillée
- Handicaps
- Type de requête

### **2. Tables d'extensions non créées**
Les 9 tables d'extensions par strate n'existent pas dans la base de données. Le schéma SQL n'a été que partiellement exécuté.

### **3. Table `fgp_strata_membership` manquante**
Impossible d'enregistrer l'appartenance aux strates sans cette table.

### **4. Tables système manquantes**
- `fgp_documents` - Stockage des documents
- `fgp_audit_trail` - Traçabilité
- `abis_matches` - Déduplication

---

## 💡 SOLUTIONS PROPOSÉES

### **Option 1: Exécuter le schéma SQL complet** ⭐ RECOMMANDÉ
Exécuter manuellement le fichier `database/schema.sql` pour créer toutes les tables manquantes.

```bash
docker exec -i fgp_postgres psql -U fgp_user -d fgp_db < database/schema.sql
```

### **Option 2: Étendre le modèle PersonCore**
Ajouter les 51 champs manquants au modèle Django `PersonCore` et faire des migrations.

### **Option 3: Utiliser des modèles séparés**
Créer des modèles Django séparés pour:
- `PersonParents` (informations parents)
- `PersonSpouse` (informations conjoint)
- `PersonGuardian` (informations tuteur)
- `PersonEducation` (informations études)
- `PersonPhysical` (caractéristiques physiques)

### **Option 4: Stocker dans JSON**
Utiliser un champ `JSONField` dans `EnrollmentSession.payload` pour les champs supplémentaires (solution temporaire).

---

## 🎯 RECOMMANDATIONS

1. **URGENT**: Exécuter le schéma SQL complet pour créer toutes les tables
2. **CRITIQUE**: Étendre le modèle `PersonCore` avec tous les champs du formulaire
3. **IMPORTANT**: Créer les migrations Django pour les modèles d'extensions
4. **ESSENTIEL**: Vérifier que les API acceptent tous les champs du frontend

---

## 📝 PROCHAINES ÉTAPES

### **Étape 1: Créer les tables manquantes**
```bash
# Exécuter le schéma SQL
docker exec -i fgp_postgres psql -U fgp_user -d fgp_db < /home/nayops/Documents/strate/fgp/database/schema.sql
```

### **Étape 2: Étendre le modèle PersonCore**
Modifier `/home/nayops/Documents/strate/fgp/backend/fgp_core/apps/core/models.py`

### **Étape 3: Créer les migrations**
```bash
docker exec fgp_core python manage.py makemigrations
docker exec fgp_core python manage.py migrate
```

### **Étape 4: Vérifier les serializers**
Mettre à jour les serializers pour accepter tous les nouveaux champs

### **Étape 5: Tester l'enrôlement complet**
Envoyer un payload complet depuis le frontend et vérifier que tout est sauvegardé

---

**Date**: 13 octobre 2025  
**Version**: 1.0  
**Statut**: 🔴 **CRITIQUE - NÉCESSITE ACTION IMMÉDIATE**

