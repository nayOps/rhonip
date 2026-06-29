# 🎯 MCD (Modèle Conceptuel de Données) - OSIA Compliant

## Vue d'ensemble

Ce MCD représente le modèle conceptuel Merise de la base de données FGP, conforme à la norme **OSIA (Open Standard Identity APIs)**.

---

## 📐 DIAGRAMME MCD - NOTATION MERISE

### LÉGENDE MERISE
- **◯ Entité** : Classe d'objets
- **◇ Association** : Lien entre entités
- **Cardinalités** :
  - `0,1` : zéro ou un
  - `1,1` : un et un seul
  - `0,N` : zéro, un ou plusieurs
  - `1,N` : un ou plusieurs

---

## 🏗️ ENTITÉS PRINCIPALES OSIA

### 1. ENTITÉS CORE (Population Registry)

#### **PERSONNE**
```
◯ PERSONNE
├── personId (Identifiant unique - NIN)
├── givenName (Prénom)
├── familyName (Nom)
├── middleName (Postnom)
├── dateOfBirth (Date de naissance)
├── gender (Sexe: M/F)
├── nationality (Nationalité)
├── placeOfBirth (Lieu de naissance)
├── maritalStatus (Statut matrimonial)
└── registrationStatus (Statut d'enregistrement)
```

#### **ADRESSE**
```
◯ ADRESSE
├── addressId (Identifiant)
├── addressType (Type: RÉSIDENCE | NAISSANCE | AUTRE)
├── country (Pays)
├── stateProvince (Province/État)
├── district (District/Territoire)
├── city (Ville/Commune)
├── postalCode (Code postal)
├── street (Rue/Avenue)
└── streetNumber (Numéro)
```

#### **CONTACT**
```
◯ CONTACT
├── contactId (Identifiant)
├── telephone (Téléphone fixe)
├── mobilePhone (Téléphone mobile)
├── email (Adresse email)
└── postOfficeBox (Boîte postale)
```

#### **DOCUMENT_IDENTITE**
```
◯ DOCUMENT_IDENTITE
├── documentId (Identifiant)
├── documentType (Type: ACTE_NAISSANCE | CARTE_ID | PASSEPORT | ...)
├── documentNumber (Numéro du document)
├── issuingAuthority (Autorité émettrice)
├── dateOfIssue (Date d'émission)
├── dateOfExpiry (Date d'expiration)
├── placeOfIssue (Lieu d'émission)
└── documentImageUri (URI du document)
```

---

### 2. ENTITÉS PARENTALITÉ

#### **PARENT**
```
◯ PARENT
├── parentId (Identifiant)
├── relationshipType (Type: PÈRE | MÈRE | TUTEUR | AUTRE)
└── order (Ordre - pour cas spéciaux)
```

**Note**: En Merise, PARENT est une entité associative entre PERSONNE (parent) et PERSONNE (enfant).

---

### 3. ENTITÉS BIOMÉTRIQUES (BIS/ABIS)

#### **GABARIT_BIOMETRIQUE**
```
◯ GABARIT_BIOMETRIQUE
├── templateId (Identifiant unique)
├── biometricType (Type: FACE | FINGERPRINT | IRIS | VOICE)
├── templateData (Données du gabarit - binaire)
├── templateFormat (Format: ISO | ANSI | ...)
├── qualityScore (Score de qualité 0.0-1.0)
├── captureDate (Date de capture)
├── captureDevice (Identifiant du dispositif)
└── captureLocation (Lieu de capture)
```

#### **CORRESPONDANCE_BIOMETRIQUE**
```
◯ CORRESPONDANCE_BIOMETRIQUE
├── matchId (Identifiant)
├── matchType (Type: FACE | FINGERPRINT | IRIS | MULTIMODAL)
├── similarityScore (Score de similarité 0.0-1.0)
├── threshold (Seuil de décision)
├── decision (Décision: HIT | NO_HIT | REVIEW)
├── reviewStatus (Statut révision: PENDING | APPROVED | REJECTED)
├── reviewedBy (Révisé par)
├── reviewedAt (Date de révision)
└── reviewNotes (Notes de révision)
```

---

### 4. ENTITÉS REGISTRE CIVIL (Civil Registry)

#### **EVENEMENT_VITAL**
```
◯ EVENEMENT_VITAL
├── eventId (Identifiant)
├── eventType (Type: NAISSANCE | DÉCÈS | MARIAGE | DIVORCE | ADOPTION)
├── eventDate (Date de l'événement)
├── eventLocation (Lieu de l'événement)
├── registrationNumber (Numéro d'enregistrement)
├── registrationDate (Date d'enregistrement)
└── registeringAuthority (Autorité enregistrante)
```

#### **EVENEMENT_NAISSANCE** (Spécialisation)
```
◯ EVENEMENT_NAISSANCE
├── birthWeight (Poids de naissance)
├── birthTime (Heure de naissance)
└── birthOrder (Ordre de naissance - jumeaux)
```

#### **EVENEMENT_DECES** (Spécialisation)
```
◯ EVENEMENT_DECES
├── causeOfDeath (Cause du décès)
└── certifyingPhysician (Médecin certifiant)
```

#### **EVENEMENT_MARIAGE** (Spécialisation)
```
◯ EVENEMENT_MARIAGE
├── marriageType (Type: CIVIL | RELIGIEUX | COUTUMIER)
└── divorceDate (Date de divorce - si applicable)
```

---

### 5. ENTITÉS REGISTRES FONCTIONNELS (Functional Registries)

#### **STRATE**
```
◯ STRATE
├── strateCode (Code: ELEVE | ETUDIANT | ELECTEUR | PNC | FARDC | ...)
├── strateName (Nom de la strate)
└── strateDescription (Description)
```

#### **APPARTENANCE_STRATE**
```
◯ APPARTENANCE_STRATE
├── validFrom (Date de début de validité)
├── validTo (Date de fin de validité)
├── status (Statut: ACTIVE | INACTIVE | SUSPENDED)
└── registryReference (Référence dans le registre source)
```

---

### 6. ENTITÉS GATEWAY (Identity Gateway)

#### **SESSION_ENROLEMENT**
```
◯ SESSION_ENROLEMENT
├── sessionId (Identifiant unique)
├── channel (Canal: FIXED | MOBILE | ITINERANT | ONLINE)
├── deviceId (Identifiant du dispositif)
├── operatorId (Identifiant de l'opérateur)
├── location (Coordonnées GPS)
├── payloadHash (Hash du payload)
├── payloadSignature (Signature JWS)
├── status (Statut: PENDING | PROCESSING | COMPLETED | FAILED)
├── progressPercentage (Pourcentage de progression)
├── createdAt (Date de création)
└── completedAt (Date de completion)
```

#### **REQUETE_IDENTITE**
```
◯ REQUETE_IDENTITE
├── requestId (Identifiant)
├── requestType (Type: VERIFY | SEARCH | ENROLL | UPDATE | DELETE)
├── requestorId (Identifiant du demandeur)
├── timestamp (Horodatage)
└── status (Statut)
```

#### **VALIDATION**
```
◯ VALIDATION
├── validationId (Identifiant)
├── validationType (Type: DATA | BIOMETRIC | DOCUMENT | BUSINESS_RULE)
├── status (Statut: PASSED | FAILED | WARNING)
└── validationRules (Règles de validation - JSON)
```

---

### 7. ENTITÉS CREDENTIAL (Credential Management)

#### **CREDENTIAL**
```
◯ CREDENTIAL
├── credentialId (Identifiant)
├── credentialType (Type: CARTE_NATIONALE | PASSEPORT | PERMIS_CONDUITE | ...)
├── credentialNumber (Numéro du credential)
├── issueDate (Date d'émission)
├── expiryDate (Date d'expiration)
├── issuingAuthority (Autorité émettrice)
└── status (Statut: ACTIVE | EXPIRED | REVOKED | SUSPENDED)
```

---

### 8. ENTITÉS MONÉTISATION (Billing & Monetization)

#### **CLIENT**
```
◯ CLIENT
├── clientId (Identifiant unique)
├── clientCode (Code client unique)
├── clientName (Nom du client - banque, institution)
├── clientType (Type: BANQUE | ASSURANCE | TELCO | GOUVERNEMENT | PRIVÉ)
├── billingModel (Modèle: TRANSACTIONNEL | ABONNEMENT | HYBRIDE)
├── creditLimit (Limite de crédit)
├── currentBalance (Solde actuel)
├── status (Statut: ACTIF | SUSPENDU | BLOQUÉ)
├── contractStartDate (Date début contrat)
└── contractEndDate (Date fin contrat)
```

#### **CLE_API**
```
◯ CLE_API
├── keyId (Identifiant)
├── apiKey (Clé API publique)
├── apiSecretHash (Hash de la clé secrète)
├── permissions (Permissions - JSON)
├── rateLimit (Limite de requêtes/heure)
├── ipWhitelist (Liste IP autorisées)
├── status (Statut: ACTIF | EXPIRÉ | RÉVOQUÉ)
└── expiresAt (Date d'expiration)
```

#### **TARIF**
```
◯ TARIF
├── pricingId (Identifiant)
├── transactionType (Type: IDENTITY_VERIFY | BIOMETRIC_VERIFY | IRIS_VERIFY | ...)
├── basePrice (Prix de base)
├── currency (Devise: USD | CDF)
├── clientType (Type de client - optionnel pour tarif personnalisé)
├── volumeDiscountThreshold (Seuil pour remise volume)
├── volumeDiscountPercentage (Pourcentage de remise)
├── validFrom (Date début validité)
└── validTo (Date fin validité)
```

#### **TRANSACTION**
```
◯ TRANSACTION
├── transactionId (Identifiant unique)
├── transactionType (Type de transaction)
├── apiEndpoint (Endpoint appelé)
├── requestTimestamp (Horodatage requête)
├── responseStatus (Statut: SUCCESS | FAILED | ERROR)
├── responseTimeMs (Temps de réponse en ms)
├── amount (Montant facturé)
├── currency (Devise)
├── billingStatus (Statut facturation: PENDING | INVOICED | PAID)
└── personId (NIN - optionnel pour recherche)
```

#### **ABONNEMENT**
```
◯ ABONNEMENT
├── subscriptionId (Identifiant)
├── planType (Type: STARTER | BUSINESS | ENTERPRISE | UNLIMITED)
├── quotaMonthly (Quota mensuel)
├── usedQuota (Quota utilisé)
├── billingCycle (Cycle: MENSUEL | TRIMESTRIEL | ANNUEL)
├── startDate (Date début)
├── endDate (Date fin)
├── autoRenew (Renouvellement automatique: OUI | NON)
└── status (Statut: ACTIF | EXPIRÉ | SUSPENDU)
```

#### **FACTURE**
```
◯ FACTURE
├── invoiceId (Identifiant unique)
├── invoiceNumber (Numéro facture unique)
├── billingPeriodStart (Début période facturation)
├── billingPeriodEnd (Fin période facturation)
├── totalAmount (Montant total)
├── taxAmount (Montant taxes)
├── totalWithTax (Total TTC)
├── currency (Devise)
├── status (Statut: DRAFT | SENT | PAID | OVERDUE)
├── dueDate (Date échéance)
├── paidDate (Date paiement)
└── paymentReference (Référence paiement)
```

---

## 🔗 ASSOCIATIONS MERISE (Relations)

### Relations principales:

```
PERSONNE ────◇─── ADRESSE
(1,1)              (0,N)
"habite à" / "est localisée à"

PERSONNE ────◇─── CONTACT
(1,1)              (0,1)
"a pour contact"

PERSONNE ────◇─── DOCUMENT_IDENTITE
(1,1)              (0,N)
"possède"

PERSONNE ────◇─── GABARIT_BIOMETRIQUE
(1,1)              (0,N)
"a pour gabarit biométrique"

PERSONNE ────◇─── APPARTENANCE_STRATE ────◇─── STRATE
(1,N)              (0,N)                    (1,1)
"appartient à"     "est membre de"

PERSONNE (parent) ────◇─── PARENT ────◇─── PERSONNE (enfant)
(1,N)                    (0,N)              (0,N)
"est parent de"          "a pour parent"

PERSONNE ────◇─── EVENEMENT_VITAL
(1,N)              (0,N)
"a pour événement vital"

PERSONNE ────◇─── SESSION_ENROLEMENT
(1,1)              (0,N)
"enregistrée via"

PERSONNE ────◇─── CREDENTIAL
(1,1)              (0,N)
"possède un credential"

PERSONNE (candidate) ────◇─── CORRESPONDANCE_BIOMETRIQUE ────◇─── PERSONNE (matched)
(1,N)                           (0,N)                              (1,1)
"candidate dans"                "correspond à"

CLIENT ────◇─── CLE_API
(1,1)          (1,N)
"possède"      "définit les clés d'accès"

CLIENT ────◇─── TRANSACTION
(1,N)          (0,N)
"effectue"     "génère des transactions"

CLIENT ────◇─── ABONNEMENT
(1,1)          (0,1)
"a un abonnement"

TRANSACTION ────◇─── TARIF
(0,N)              (1,1)
"utilise le tarif"

TRANSACTION ────◇─── PERSONNE
(0,N)              (1,1)
"concerns"         "concernant la personne"

TRANSACTION ────◇─── REQUETE_IDENTITE
(0,1)              (1,1)
"correspond à"     "génère une transaction"

TRANSACTION ────◇─── FACTURE
(0,N)              (1,1)
"est inclus dans"  "contient des transactions"

CLIENT ────◇─── FACTURE
(1,N)          (0,N)
"reçoit"        "destinée à"
```

---

## 📊 DIAGRAMME MCD COMPLET - NOTATION MERISE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MCD FGP - CONFORME OSIA                          │
└─────────────────────────────────────────────────────────────────────────┘

                     ┌─────────────┐
                     │  PERSONNE   │
                     │  (Core)     │
                     └──────┬──────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
     ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
     │ ADRESSE │       │ CONTACT │      │DOCUMENT │
     │         │       │         │      │IDENTITE │
     └─────────┘       └─────────┘      └─────────┘
                            │
                            │
     ┌──────────────────────┼──────────────────────┐
     │                      │                      │
┌────▼─────────┐    ┌──────▼───────┐    ┌─────────▼────┐
│   PARENT     │    │  GABARIT     │    │  CREDENTIAL  │
│              │    │ BIOMETRIQUE  │    │              │
└──────┬───────┘    └──────────────┘    └──────────────┘
       │
       │
┌──────▼──────────────────────────────────────────┐
│      PERSONNE (parent)                          │
└─────────────────────────────────────────────────┘

                ┌─────────────┐
                │    STRATE    │
                └──────┬───────┘
                       │
                ┌──────▼──────────┐
                │APPARTENANCE_    │
                │STRATE           │
                └──────┬──────────┘
                       │
                ┌──────▼───────┐
                │   PERSONNE   │
                └──────────────┘

                ┌───────────────┐
                │EVENEMENT_VITAL │
                └───────┬────────┘
                        │
                ┌───────▼─────────┐
                │    PERSONNE     │
                └─────────────────┘

    ┌─────────────────────────────┐
    │  CORRESPONDANCE_BIOMETRIQUE  │
    └───┬─────────────────────┬───┘
        │                     │
┌───────▼───┐          ┌──────▼──────┐
│ PERSONNE  │          │  PERSONNE  │
│(candidate)│          │ (matched)  │
└───────────┘          └─────────────┘

                ┌──────────────────┐
                │SESSION_ENROLEMENT│
                └────────┬──────────┘
                         │
                ┌────────▼──────┐
                │   VALIDATION   │
                └────────────────┘

     ┌──────────────────────────────────────────┐
     │          MONÉTISATION                    │
     │                                          │
     │  ┌──────────┐      ┌──────────────┐     │
     │  │  CLIENT  │      │ ABONNEMENT    │     │
     │  └────┬─────┘      └──────────────┘     │
     │       │                                  │
     │  ┌────▼─────┐    ┌──────────────┐       │
     │  │ CLE_API  │    │   FACTURE    │       │
     │  └──────────┘    └──────┬───────┘       │
     │                        │                 │
     │                 ┌──────▼──────────┐      │
     │                 │  TRANSACTION    │      │
     │                 └──────┬──────────┘      │
     │                        │                 │
     │                 ┌──────▼─────┐          │
     │                 │   TARIF     │          │
     │                 └─────────────┘          │
     │                        │                 │
     │                 ┌──────▼──────┐          │
     │                 │  PERSONNE   │          │
     │                 └─────────────┘          │
     └──────────────────────────────────────────┘
```

---

## 📋 RÈGLES DE GESTION (Règles métier OSIA)

### RG1: Identification Unique
- Chaque PERSONNE a un et un seul `personId` (NIN) unique
- Format NIN: `CD-YYYY-NNNN-NNNNNNNNN`

### RG2: Appartenance aux Strates
- Une PERSONNE peut appartenir à plusieurs STRATE simultanément
- L'appartenance a une période de validité (validFrom, validTo)

### RG3: Biométrie
- Une PERSONNE peut avoir plusieurs GABARIT_BIOMETRIQUE (multimodal)
- La déduplication biométrique génère des CORRESPONDANCE_BIOMETRIQUE

### RG4: Documents
- Une PERSONNE peut avoir plusieurs DOCUMENT_IDENTITE
- Chaque document doit avoir un `documentType` et un `documentNumber` uniques par type

### RG5: Parentalité
- Une PERSONNE peut avoir plusieurs PARENT (père, mère, tuteurs)
- La relation est bidirectionnelle (parent ↔ enfant)

### RG6: Événements Vitaux
- Chaque EVENEMENT_VITAL concerne une ou plusieurs PERSONNE
- Les événements spécialisés (NAISSANCE, DÉCÈS, MARIAGE) héritent d'EVENEMENT_VITAL

### RG7: Session d'Enrôlement
- Une SESSION_ENROLEMENT peut créer une nouvelle PERSONNE ou mettre à jour une existante
- Le statut suit un workflow: PENDING → PROCESSING → COMPLETED/FAILED

### RG8: Monétisation - Clients
- Chaque CLIENT a un et un seul modèle de facturation (TRANSACTIONNEL | ABONNEMENT | HYBRIDE)
- Un CLIENT peut avoir plusieurs CLE_API pour différents environnements (dev, prod)
- Chaque CLIENT a un ABONNEMENT optionnel (si modèle SUBSCRIPTION ou HYBRIDE)

### RG9: Monétisation - Transactions
- Chaque TRANSACTION est liée à un CLIENT (via requestor_id)
- Chaque TRANSACTION utilise un TARIF selon son type et le clientType
- Une TRANSACTION peut concerner une PERSONNE (optionnel si recherche 1:N)
- Chaque TRANSACTION a un statut de facturation: PENDING → INVOICED → PAID

### RG10: Monétisation - Facturation
- Une FACTURE regroupe plusieurs TRANSACTION d'un même CLIENT sur une période
- Les FACTURE sont générées mensuellement (1er du mois)
- Le statut de FACTURE suit: DRAFT → SENT → PAID (ou OVERDUE si impayé)
- Si une FACTURE est OVERDUE > 60 jours, le CLIENT est SUSPENDU

### RG11: Monétisation - Tarifs
- Chaque TARIF a une période de validité (validFrom, validTo)
- Les TARIF peuvent être personnalisés par clientType
- Les remises volume s'appliquent si volume_discount_threshold est atteint
- Un TARIF est actif si validFrom ≤ aujourd'hui ≤ validTo

### RG12: Monétisation - Abonnements
- Un ABONNEMENT définit un quota mensuel de transactions incluses
- Les transactions dans le quota sont facturées à 0$ (déjà payées via abonnement)
- Les transactions au-delà du quota utilisent le TARIF normal
- Si autoRenew = TRUE, l'ABONNEMENT se renouvelle automatiquement à endDate

---

## ✅ PROCHAINES ÉTAPES

1. ✅ **MCD OSIA créé** (incluant monétisation)
2. ⏳ **Création du MLD (Modèle Logique de Données)** avec tables détaillées
3. ⏳ **Mapping OSIA → FGP** pour chaque entité
4. ⏳ **Diagramme de séquences** pour les interactions avec la base de données

---

## 📊 RÉCAPITULATIF DES ENTITÉS MCD COMPLET

### Entités OSIA Core: 18 entités
1. PERSONNE
2. ADRESSE
3. CONTACT
4. DOCUMENT_IDENTITE
5. PARENT
6. GABARIT_BIOMETRIQUE
7. CORRESPONDANCE_BIOMETRIQUE
8. EVENEMENT_VITAL
9. EVENEMENT_NAISSANCE
10. EVENEMENT_DECES
11. EVENEMENT_MARIAGE
12. STRATE
13. APPARTENANCE_STRATE
14. SESSION_ENROLEMENT
15. REQUETE_IDENTITE
16. VALIDATION
17. CREDENTIAL

### Entités Monétisation: 6 entités
18. CLIENT
19. CLE_API
20. TARIF
21. TRANSACTION
22. ABONNEMENT
23. FACTURE

**TOTAL: 24 entités dans le MCD complet**

---

**Date de création**: $(date)  
**Dernière mise à jour**: $(date) - Monétisation intégrée  
**Conforme à**: OSIA Specification v1.0  
**Norme**: Open Standard Identity APIs (Secure Identity Alliance)

