# 📊 INVENTAIRE COMPLET DES TABLES OSIA

## Vue d'ensemble

Ce document liste toutes les tables/entités identifiées dans la norme **OSIA (Open Standard Identity APIs)** pour la modélisation de la base de données FGP.

---

## 🗂️ TABLES PAR BUILDING BLOCK OSIA

### 1️⃣ **POPULATION REGISTRY (PR)** - Registre de Population

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **1.1** | `osia_person` | Personne principale | personId (PK), givenName, familyName, dateOfBirth, gender |
| **1.2** | `osia_address` | Adresses | addressId (PK), personId (FK), addressType, country, stateProvince |
| **1.3** | `osia_contact` | Informations de contact | contactId (PK), personId (FK), telephone, email, mobilePhone |
| **1.4** | `osia_identification_document` | Documents d'identité | documentId (PK), personId (FK), documentType, documentNumber |
| **1.5** | `osia_parent_reference` | Références aux parents | parentRefId (PK), childPersonId (FK), parentPersonId (FK), relationshipType |
| **1.6** | `osia_strata_membership` | Appartenance aux strates | membershipId (PK), personId (FK), strateCode, validFrom, validTo |

**Total: 6 tables**

---

### 2️⃣ **BIOMETRIC IDENTIFICATION SYSTEM (BIS/ABIS)** - Système Biométrique

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **2.1** | `osia_biometric_template` | Gabarits biométriques | templateId (PK), personId (FK), biometricType, templateData, qualityScore |
| **2.2** | `osia_biometric_match` | Correspondances biométriques | matchId (PK), candidatePersonId (FK), matchedPersonId (FK), similarityScore, decision |

**Total: 2 tables**

---

### 3️⃣ **CIVIL REGISTRY (CR)** - Registre Civil

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **3.1** | `osia_vital_event` | Événements vitaux | eventId (PK), personId (FK), eventType, eventDate, registrationNumber |
| **3.2** | `osia_birth_event` | Événements de naissance | birthEventId (PK), eventId (FK), childPersonId (FK), fatherPersonId (FK), motherPersonId (FK) |
| **3.3** | `osia_death_event` | Événements de décès | deathEventId (PK), eventId (FK), deceasedPersonId (FK), causeOfDeath |
| **3.4** | `osia_marriage_event` | Événements de mariage | marriageEventId (PK), eventId (FK), spouse1PersonId (FK), spouse2PersonId (FK) |

**Total: 4 tables**

---

### 4️⃣ **FUNCTIONAL REGISTRIES** - Registres Fonctionnels

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **4.1** | `osia_functional_registry_entry` | Entrée registre fonctionnel | entryId (PK), personId (FK), registryType, registryCode, entryData (JSON) |
| **4.2** | `osia_strata_catalog` | Catalogue des strates | strateCode (PK), strateName, strateDescription |

**Total: 2 tables**

---

### 5️⃣ **IDENTITY GATEWAY (IG)** - Passerelle d'Identité

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **5.1** | `osia_enrollment_session` | Session d'enrôlement | sessionId (PK), personId (FK), channel, deviceId, payload (JSON), status |
| **5.2** | `osia_identity_request` | Requête d'identité | requestId (PK), personId (FK), requestType, requestorId, requestData (JSON) |
| **5.3** | `osia_validation_result` | Résultat de validation | validationId (PK), sessionId (FK), validationType, status, errors (JSON) |
| **5.4** | `osia_enrollment_event` | Événements d'enrôlement | eventId (PK), sessionId (FK), eventType, eventData (JSON), timestamp |

**Total: 4 tables**

---

### 6️⃣ **CREDENTIAL MANAGEMENT SYSTEM (CMS)** - Gestion des Credentials

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **6.1** | `osia_credential` | Credentials émis | credentialId (PK), personId (FK), credentialType, credentialNumber, issueDate, expiryDate |

**Total: 1 table**

---

### 7️⃣ **AUDIT & SECURITY** - Audit et Sécurité

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **7.1** | `osia_audit_trail` | Piste d'audit | auditId (PK), personId (FK), action, tableName, oldValues (JSON), newValues (JSON), userId |
| **7.2** | `osia_security_event` | Événements de sécurité | securityEventId (PK), eventType, severity, userId, ipAddress, timestamp |

**Total: 2 tables**

---

### 8️⃣ **MONÉTISATION (BILLING & MONETIZATION)** - Billing & Monetization

| # | Table/Entité | Description | Attributs Clés |
|---|-------------|-------------|----------------|
| **8.1** | `onip_client` | Clients (banques, institutions) | clientId (PK), clientCode (UK), clientName, clientType, billingModel, status |
| **8.2** | `onip_api_key` | Clés API d'accès | keyId (PK), clientId (FK), apiKey (UK), apiSecretHash, rateLimit, status |
| **8.3** | `onip_pricing` | Tarification par type | pricingId (PK), transactionType (UK), basePrice, currency, validFrom, validTo |
| **8.4** | `onip_transaction` | Transactions facturables | transactionId (PK), requestorId (FK), transactionType, amount, billingStatus |
| **8.5** | `onip_subscription` | Abonnements clients | subscriptionId (PK), clientId (FK), planType, quotaMonthly, usedQuota, status |
| **8.6** | `onip_invoice` | Factures mensuelles | invoiceId (PK), clientId (FK), invoiceNumber (UK), totalAmount, status, dueDate |

**Total: 6 tables**

---

## 📊 RÉCAPITULATIF GLOBAL

| Building Block | Nombre de Tables | Tables |
|---------------|------------------|--------|
| **Population Registry (PR)** | 6 | osia_person, osia_address, osia_contact, osia_identification_document, osia_parent_reference, osia_strata_membership |
| **Biometric System (BIS/ABIS)** | 2 | osia_biometric_template, osia_biometric_match |
| **Civil Registry (CR)** | 4 | osia_vital_event, osia_birth_event, osia_death_event, osia_marriage_event |
| **Functional Registries** | 2 | osia_functional_registry_entry, osia_strata_catalog |
| **Identity Gateway (IG)** | 4 | osia_enrollment_session, osia_identity_request, osia_validation_result, osia_enrollment_event |
| **Credential Management (CMS)** | 1 | osia_credential |
| **Audit & Security** | 2 | osia_audit_trail, osia_security_event |
| **Monétisation (Billing)** | 6 | onip_client, onip_api_key, onip_pricing, onip_transaction, onip_subscription, onip_invoice |
| **TOTAL** | **27 tables** | |

---

## 🔗 RELATIONS CLÉS (Foreign Keys)

### Table centrale: `osia_person`
- Toutes les autres tables référencent `osia_person.personId` (sauf exceptions)

### Relations principales:
```
osia_person.personId
  ├── osia_address.personId (FK)
  ├── osia_contact.personId (FK)
  ├── osia_identification_document.personId (FK)
  ├── osia_parent_reference.childPersonId (FK)
  ├── osia_parent_reference.parentPersonId (FK)
  ├── osia_strata_membership.personId (FK)
  ├── osia_biometric_template.personId (FK)
  ├── osia_biometric_match.candidatePersonId (FK)
  ├── osia_biometric_match.matchedPersonId (FK)
  ├── osia_vital_event.personId (FK)
  ├── osia_birth_event.childPersonId (FK)
  ├── osia_birth_event.fatherPersonId (FK)
  ├── osia_birth_event.motherPersonId (FK)
  ├── osia_death_event.deceasedPersonId (FK)
  ├── osia_marriage_event.spouse1PersonId (FK)
  ├── osia_marriage_event.spouse2PersonId (FK)
  ├── osia_functional_registry_entry.personId (FK)
  ├── osia_enrollment_session.personId (FK)
  ├── osia_identity_request.personId (FK)
  ├── osia_credential.personId (FK)
  └── osia_audit_trail.personId (FK)
```

### Relations Monétisation:
```
onip_client.clientId
  ├── onip_api_key.clientId (FK)
  ├── onip_transaction.requestorId (FK)
  ├── onip_subscription.clientId (FK)
  └── onip_invoice.clientId (FK)

onip_transaction
  ├── onip_pricing.transactionType (FK - logique)
  └── onip_invoice.invoiceId (FK)

onip_transaction.personId (FK optionnel)
  └── osia_person.personId
```

---

## 📋 ATTRIBUTS STANDARDS OSIA

### Attributs communs à toutes les tables:
- `created_at` (TIMESTAMPTZ) - Date de création
- `updated_at` (TIMESTAMPTZ) - Date de mise à jour
- `created_by` (VARCHAR) - Créé par
- `updated_by` (VARCHAR) - Mis à jour par
- `version` (INTEGER) - Version pour l'optimistic locking

### Types de données OSIA:
- **personId**: String (format: CD-YYYY-NNNN-NNNNNNNNN)
- **UUID**: UUID v4 pour identifiants secondaires
- **Date**: DATE (ISO 8601)
- **DateTime**: TIMESTAMPTZ (ISO 8601 avec timezone)
- **JSON**: JSONB pour données flexibles
- **Binary**: BYTEA pour données biométriques

---

## 🔄 MAPPING OSIA → FGP (Existant)

| Table OSIA | Table FGP Existante | Statut Mapping |
|------------|---------------------|----------------|
| `osia_person` | `fgp_person_core` | ⚠️ Partiel - manque certains attributs OSIA |
| `osia_address` | `fgp_person_core` (champs adresse) | ⚠️ À séparer en table dédiée |
| `osia_contact` | `fgp_person_core` (telephone, email) | ⚠️ À séparer en table dédiée |
| `osia_identification_document` | `fgp_documents` | ✅ Existe |
| `osia_biometric_template` | `fgp_biometric` | ⚠️ Structure différente |
| `osia_biometric_match` | `abis_matches` | ✅ Existe |
| `osia_strata_membership` | `fgp_strata_membership` | ✅ Existe |
| `osia_enrollment_session` | `enrollment_sessions` | ✅ Existe |
| `osia_validation_result` | `enrollment_validations` | ✅ Existe |
| `osia_audit_trail` | `fgp_audit_trail` | ✅ Existe |

---

## ✅ PROCHAINES ÉTAPES

1. ✅ **Inventaire OSIA complété** - 27 tables identifiées (21 OSIA + 6 monétisation)
2. ⏳ **Création du MLD** avec structure détaillée de chaque table
3. ⏳ **Mapping complet OSIA → FGP**
4. ⏳ **Migration plan** pour adapter le FGP existant à OSIA

---

**Date de création**: $(date)  
**Conforme à**: OSIA Specification  
**Référence**: [OSIA Documentation](https://osia.readthedocs.io/en/stable/)

