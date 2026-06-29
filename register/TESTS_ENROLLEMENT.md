# 🧪 GUIDE DE TESTS D'ENRÔLEMENT - FGP

**Date**: 13 octobre 2025  
**Objectif**: Tester la communication Frontend ↔ Backend pour l'enrôlement

---

## 📋 TABLE DES MATIÈRES

1. [Tests Terminal (Backend Direct)](#1-tests-terminal-backend-direct)
2. [Tests Navigateur (Frontend → Backend)](#2-tests-navigateur-frontend--backend)
3. [Scénarios de Test par Strate](#3-scénarios-de-test-par-strate)
4. [Vérification dans pgAdmin](#4-vérification-dans-pgadmin)

---

## 1. TESTS TERMINAL (Backend Direct)

### ✅ **Test 1.1 : Health Check Backend**

```bash
# Test de santé de l'API
curl -X GET http://localhost:8001/api/v1/enrolments/health/

# Résultat attendu:
# {"status": "healthy", "timestamp": "..."}
```

### ✅ **Test 1.2 : Dashboard Stats**

```bash
# Récupérer les statistiques
curl -X GET http://localhost:8001/api/v1/enrolments/stats/

# Résultat attendu:
# {"total_sessions": 0, "completed": 0, "pending": 0, ...}
```

### ✅ **Test 1.3 : Création Enrôlement ÉLECTEUR (Minimal)**

```bash
curl -X POST http://localhost:8001/api/v1/enrolments/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TEST-001",
    "channel": "fixed",
    "device_id": "DEV-001",
    "operator_id": "OP-001",
    "location": {
      "province": "Kinshasa",
      "territoire": "Ngaliema",
      "commune": "Ngaliema"
    },
    "schema_version": "1.0",
    "core": {
      "nom": "KABILA",
      "prenom": "Joseph",
      "sexe": "M",
      "date_naissance": "1990-01-01",
      "lieu_naissance": "Kinshasa",
      "province_naissance": "Kinshasa",
      "nationalite": "Congolaise",
      "province_residence": "Kinshasa"
    },
    "biometrics": {
      "face": {
        "quality": 0.95,
        "icaoCompliant": true,
        "image": "data:image/jpeg;base64,/9j/4AAQ..."
      }
    },
    "strata": ["ELECTEUR"],
    "extensions": {}
  }'
```

**Résultat attendu** :
```json
{
  "id": "uuid...",
  "session_id": "TEST-001",
  "status": "PENDING",
  "nin": null,
  "created_at": "2025-10-13T..."
}
```

### ✅ **Test 1.4 : Création Enrôlement ÉTRANGER (Nouveau)**

```bash
curl -X POST http://localhost:8001/api/v1/enrolments/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TEST-ETRANGER-001",
    "channel": "fixed",
    "device_id": "DEV-001",
    "operator_id": "OP-001",
    "location": {
      "province": "Kinshasa",
      "territoire": "Gombe",
      "commune": "Gombe"
    },
    "schema_version": "1.0",
    "core": {
      "nom": "SMITH",
      "prenom": "John",
      "sexe": "M",
      "date_naissance": "1985-05-15",
      "lieu_naissance": "New York",
      "province_naissance": "New York",
      "nationalite": "Américaine",
      "province_residence": "Kinshasa"
    },
    "biometrics": {
      "face": {
        "quality": 0.92,
        "icaoCompliant": true,
        "image": "data:image/jpeg;base64,/9j/4AAQ..."
      }
    },
    "strata": ["ETRANGER"],
    "extensions": {
      "etranger": {
        "pays_origine": "États-Unis",
        "numero_passeport": "US123456789",
        "ville_delivrance": "Washington DC",
        "date_delivrance": "2020-01-01",
        "date_expiration": "2030-01-01",
        "numero_visa_permis": "VISA-RDC-2024-001",
        "date_visa": "2024-01-15",
        "type_sejour": "Temporaire",
        "adresse_residence_rdc": "Avenue des Aviateurs, Gombe",
        "profession_rdc": "Consultant",
        "employeur_organisation": "USAID"
      }
    }
  }'
```

### ✅ **Test 1.5 : Création Enrôlement DÉPLACÉ (Nouveau)**

```bash
curl -X POST http://localhost:8001/api/v1/enrolments/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TEST-DEPLACE-001",
    "channel": "itinerant",
    "device_id": "DEV-MOBILE-001",
    "operator_id": "OP-002",
    "location": {
      "province": "Nord-Kivu",
      "territoire": "Rutshuru",
      "commune": "Kiwanja"
    },
    "schema_version": "1.0",
    "core": {
      "nom": "MUKENDI",
      "prenom": "Marie",
      "sexe": "F",
      "date_naissance": "1992-08-20",
      "lieu_naissance": "Goma",
      "province_naissance": "Nord-Kivu",
      "nationalite": "Congolaise",
      "province_residence": "Nord-Kivu"
    },
    "biometrics": {
      "face": {
        "quality": 0.88,
        "icaoCompliant": true,
        "image": "data:image/jpeg;base64,/9j/4AAQ..."
      }
    },
    "strata": ["DEPLACE"],
    "extensions": {
      "deplace": {
        "lieu_origine": "Masisi",
        "province_origine": "Nord-Kivu",
        "territoire_origine": "Masisi",
        "raison_deplacement": "Conflit armé",
        "date_deplacement": "2023-11-15",
        "site_camp_deplaces": "Camp de Kanyaruchinya",
        "organisme_assistance": "HCR",
        "type_hebergement": "Tente familiale",
        "besoins_prioritaires": "Nourriture, abri, soins médicaux"
      }
    }
  }'
```

### ✅ **Test 1.6 : Création Enrôlement DIASPORA (Nouveau)**

```bash
curl -X POST http://localhost:8001/api/v1/enrolments/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TEST-DIASPORA-001",
    "channel": "fixed",
    "device_id": "DEV-CONSULAT-001",
    "operator_id": "OP-DIASPORA-001",
    "location": {
      "province": "Kinshasa",
      "territoire": "Ambassade",
      "commune": "Paris"
    },
    "schema_version": "1.0",
    "core": {
      "nom": "TSHISEKEDI",
      "prenom": "Patrick",
      "sexe": "M",
      "date_naissance": "1988-03-10",
      "lieu_naissance": "Kinshasa",
      "province_naissance": "Kinshasa",
      "nationalite": "Congolaise",
      "province_residence": "Étranger"
    },
    "biometrics": {
      "face": {
        "quality": 0.94,
        "icaoCompliant": true,
        "image": "data:image/jpeg;base64,/9j/4AAQ..."
      }
    },
    "strata": ["DIASPORA"],
    "extensions": {
      "diaspora": {
        "pays_residence_actuelle": "France",
        "ville_residence": "Paris",
        "date_depart_rdc": "2015-06-01",
        "type_residence": "Permanent",
        "document_etranger": "Carte de résident français",
        "numero_document_etranger": "FR-RES-123456",
        "profession_etranger": "Ingénieur informatique",
        "employeur_etranger": "TotalEnergies",
        "souhait_retour": true,
        "date_retour_prevue": "2026-12-31",
        "representation_consulaire": "Ambassade RDC à Paris",
        "ville_consulat": "Paris",
        "statut_legal_etranger": "Résident permanent",
        "double_nationalite": false
      }
    }
  }'
```

### ✅ **Test 1.7 : Récupérer un Enrôlement**

```bash
# Remplacer SESSION-ID par l'ID retourné
curl -X GET http://localhost:8001/api/v1/enrolments/sessions/SESSION-ID/
```

### ✅ **Test 1.8 : Lister Tous les Enrôlements**

```bash
curl -X GET http://localhost:8001/api/v1/enrolments/sessions/
```

---

## 2. TESTS NAVIGATEUR (Frontend → Backend)

### ✅ **Test 2.1 : Accéder au Dashboard**

1. **Ouvrir** : http://localhost:3000
2. **Vérifier** :
   - ✅ Redirection automatique vers `/enrollment`
   - ✅ Sidebar visible avec "Enrôlement" et "Tableau de bord"
   - ✅ Design flat avec couleurs RDC (rouge, bleu, jaune)

### ✅ **Test 2.2 : Accéder au Tableau de Bord**

1. **Cliquer** sur "Tableau de bord" dans la sidebar
2. **Vérifier** :
   - ✅ URL : http://localhost:3000/dashboard
   - ✅ Statistiques affichées
   - ✅ Graphiques visibles
   - ✅ **Ouvrir la console du navigateur** (F12)
   - ✅ Vérifier qu'il n'y a pas d'erreurs

### ✅ **Test 2.3 : Formulaire d'Enrôlement - Sélection Strate**

1. **Naviguer** vers : http://localhost:3000/enrollment
2. **Vérifier** les 10 strates affichées :
   - ☐ Enfant
   - ☐ Élève
   - ☐ Électeur/Majeur
   - ☐ Militaire
   - ☐ Policier
   - ☐ Prisonnier
   - ☐ Réfugié
   - ☐ Déplacé interne
   - ☐ Étranger
   - ☐ Diaspora

### ✅ **Test 2.4 : Enrôlement ÉLECTEUR Complet**

**Étape 1 : Données de Base**
1. Sélectionner : ☑️ **Électeur/Majeur**
2. Remplir les champs obligatoires :
   - Nom : MBALA
   - Prénom : Jean
   - Sexe : M
   - Date de naissance : 15/08/1995
   - Lieu de naissance : Lubumbashi
   - Nationalité : Congolaise
   - Province de résidence : Haut-Katanga
3. Cliquer sur **"Suivant"**

**Étape 2 : Extensions Électeur**
1. Remplir :
   - Centre de vote : Centre Lubumbashi 1
   - Code centre : LUB-001
   - Circonscription : Lubumbashi
   - Secteur : Secteur 1
   - Date inscription CENI : 01/01/2024
   - Bureau de vote : Bureau 001
2. Cliquer sur **"Suivant"**

**Étape 3 : Photo**
1. Cliquer sur **"Capturer Photo"**
2. Vérifier le score ICAO
3. Cliquer sur **"Valider"**

**Étape 4 : Empreintes Digitales**
1. Simuler la capture des 10 doigts
2. Vérifier la qualité
3. Cliquer sur **"Suivant"**

**Étape 5 : Iris**
1. Vérifier le bandeau lecteur (bridge `8765`, mode mock ou device sur port 50218)
2. **Capturer les 2 yeux** (ou œil par œil + handicap si besoin)
3. **Valider et continuer** — vérifier en console : `PATCH .../modality/iris/{session_id}/`

**Étape 6 : Documents**
1. Uploader la fiche d'identification
2. Uploader les pièces
3. Cliquer sur **"Suivant"**

**Étape 7 : Vérification**
1. Cliquer sur **"Lancer le Matching"**
2. Vérifier les résultats
3. Cliquer sur **"Valider et Générer le Récépissé"**

**Étape 8 : Récépissé**
1. Vérifier l'affichage du récépissé
2. Vérifier le QR code
3. **Ouvrir la console (F12) et vérifier** :
   - ✅ Requête POST envoyée à `/api/v1/enrolments/sessions/`
   - ✅ Réponse 200 ou 201
   - ✅ Pas d'erreur de réseau

### ✅ **Test 2.5 : Enrôlement ÉTRANGER**

**Étape 1 : Données de Base**
1. Sélectionner : ☑️ **Étranger**
2. Remplir :
   - Nom : NGUYEN
   - Prénom : Van
   - Sexe : M
   - Date de naissance : 10/12/1987
   - Lieu de naissance : Hanoi
   - Nationalité : Vietnamienne
   - Province de résidence : Kinshasa
3. Cliquer sur **"Suivant"**

**Étape 2 : Extensions Étranger**
1. Remplir les champs obligatoires :
   - **Pays d'origine** : Vietnam
   - **Numéro de passeport** : VN987654321
2. Remplir les champs optionnels :
   - Ville de délivrance : Hanoi
   - Date de délivrance : 01/01/2020
   - Date d'expiration : 01/01/2030
   - Numéro visa/permis : VISA-RDC-2024-VN-001
   - Date du visa : 15/01/2024
   - Type de séjour : Temporaire
   - Adresse en RDC : Avenue du Port, Kinshasa
   - Profession en RDC : Commerçant
   - Employeur : Import-Export Vietnam-RDC
3. Cliquer sur **"Suivant"**

**Continuer** les étapes 3-8 comme pour ÉLECTEUR

**Vérifier dans la console** :
```javascript
// Payload envoyé doit contenir:
{
  strata: ["ETRANGER"],
  extensions: {
    etranger: {
      pays_origine: "Vietnam",
      numero_passeport: "VN987654321",
      // ... autres champs
    }
  }
}
```

### ✅ **Test 2.6 : Enrôlement DÉPLACÉ**

**Étape 1 : Données de Base**
1. Sélectionner : ☑️ **Déplacé interne**
2. Remplir les champs de base
3. Cliquer sur **"Suivant"**

**Étape 2 : Extensions Déplacé** (Tous optionnels)
1. Remplir si disponible :
   - Lieu d'origine : Bunia
   - Province d'origine : Ituri
   - Raison du déplacement : Conflit
   - Date du déplacement : 01/06/2023
   - Site/camp : Camp de Goma
   - Organisme d'assistance : UNHCR
2. Cliquer sur **"Suivant"** (même si vide)

**Continuer** les étapes 3-8

### ✅ **Test 2.7 : Enrôlement DIASPORA**

**Étape 1 : Données de Base**
1. Sélectionner : ☑️ **Diaspora**
2. Remplir les champs de base
3. Cliquer sur **"Suivant"**

**Étape 2 : Extensions Diaspora** (Tous optionnels)
1. Remplir si disponible :
   - Pays de résidence actuelle : Belgique
   - Ville : Bruxelles
   - Date de départ RDC : 01/09/2010
   - Type de résidence : Permanent
   - Document étranger : Carte de résident belge
   - Profession à l'étranger : Médecin
   - Souhait de retour : Oui
   - Représentation consulaire : Ambassade RDC Bruxelles
2. Cliquer sur **"Suivant"**

**Continuer** les étapes 3-8

---

## 3. SCÉNARIOS DE TEST PAR STRATE

### 📝 **Checklist de Test**

| Strate | Test Terminal | Test Navigateur | Extensions OK | Biométrie OK | Récépissé OK |
|---|---|---|---|---|---|
| ENFANT | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| ELEVE | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| ELECTEUR | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| PNC | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| FARDC | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| PRISONNIER | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| REFUGIE | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **DEPLACE** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **ETRANGER** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **DIASPORA** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

---

## 4. VÉRIFICATION DANS pgAdmin

### ✅ **Vérifier les Données Créées**

1. **Ouvrir pgAdmin** : http://localhost:5050
2. **Se connecter** : admin@fgp.cd / admin2025
3. **Connexion PostgreSQL** : postgres / fgp_db

### **Requêtes de Vérification**

```sql
-- 1. Vérifier les sessions d'enrôlement créées
SELECT session_id, status, channel, created_at 
FROM enrollment_sessions 
ORDER BY created_at DESC 
LIMIT 10;

-- 2. Vérifier les strates enregistrées
SELECT strate_code, COUNT(*) as total
FROM fgp_strata_membership
GROUP BY strate_code;

-- 3. Vérifier les extensions ÉTRANGER
SELECT * FROM ext_etrangers 
ORDER BY created_at DESC;

-- 4. Vérifier les extensions DÉPLACÉ
SELECT * FROM ext_deplaces 
ORDER BY created_at DESC;

-- 5. Vérifier les extensions DIASPORA
SELECT * FROM ext_diaspora 
ORDER BY created_at DESC;

-- 6. Vérifier tous les enrôlements avec leurs strates
SELECT 
    pc.nin,
    pc.nom,
    pc.prenom,
    string_agg(sm.strate_code, ', ') as strates,
    pc.created_at
FROM fgp_person_core pc
LEFT JOIN fgp_strata_membership sm ON pc.nin = sm.nin
GROUP BY pc.nin, pc.nom, pc.prenom, pc.created_at
ORDER BY pc.created_at DESC;

-- 7. Statistiques par strate
SELECT 
    strate_code,
    COUNT(*) as total_personnes,
    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as actifs
FROM fgp_strata_membership
GROUP BY strate_code
ORDER BY total_personnes DESC;
```

---

## 🐛 DÉBOGAGE

### **Problèmes Courants**

#### **Erreur 1 : Backend inaccessible**
```bash
# Vérifier que le backend est démarré
docker ps | grep fgp

# Redémarrer si nécessaire
cd /home/nayops/Documents/strate/fgp
docker compose restart enrollment_gateway
```

#### **Erreur 2 : Frontend ne charge pas**
```bash
# Vérifier les logs
docker compose logs frontend --tail=50

# Rebuild si nécessaire
docker compose build frontend
docker compose restart frontend
```

#### **Erreur 3 : 404 Not Found sur API**
```bash
# Vérifier les routes disponibles
curl http://localhost:8001/api/v1/enrolments/

# Vérifier les logs backend
docker compose logs enrollment_gateway --tail=50
```

#### **Erreur 4 : Données non sauvegardées**
```sql
-- Vérifier dans PostgreSQL
SELECT COUNT(*) FROM enrollment_sessions;
SELECT COUNT(*) FROM fgp_person_core;

-- Si vide, vérifier les permissions
SELECT * FROM enrollment_events 
WHERE event_type LIKE '%error%' 
ORDER BY created_at DESC LIMIT 10;
```

---

## ✅ **CHECKLIST FINALE**

Avant de considérer les tests comme réussis, vérifier :

- [ ] ✅ Backend accessible sur `localhost:8001`
- [ ] ✅ Frontend accessible sur `localhost:3000`
- [ ] ✅ pgAdmin accessible sur `localhost:5050`
- [ ] ✅ Au moins 1 enrôlement ÉLECTEUR réussi (terminal)
- [ ] ✅ Au moins 1 enrôlement ÉTRANGER réussi (terminal)
- [ ] ✅ Au moins 1 enrôlement DÉPLACÉ réussi (terminal)
- [ ] ✅ Au moins 1 enrôlement DIASPORA réussi (terminal)
- [ ] ✅ Au moins 1 enrôlement complet depuis le navigateur
- [ ] ✅ Données visibles dans pgAdmin
- [ ] ✅ Aucune erreur dans la console navigateur
- [ ] ✅ Aucune erreur dans les logs Docker

---

**Prêt à commencer les tests ?** 🚀

Dites-moi par quelle strate vous souhaitez commencer !



