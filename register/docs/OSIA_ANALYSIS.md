# 📊 Analyse OSIA - Open Standard Identity APIs

## 🔍 Vue d'ensemble OSIA

**OSIA (Open Standard Identity APIs)** est une initiative de la Secure Identity Alliance qui fournit:
- Des interfaces standardisées entre les building blocks d'identité
- Un dictionnaire de données commun
- Une architecture modulaire non-préscriptive

Référence: [OSIA Documentation](https://osia.readthedocs.io/en/stable/01%20-%20intro.html)

---

## 🏗️ Building Blocks OSIA (Blocs Fonctionnels)

Selon la spécification OSIA, les principaux building blocks sont:

### 1. **Civil Registry (CR)** - Registre Civil
Gestion des événements vitaux (naissance, décès, mariage, divorce)

### 2. **Population Registry (PR)** - Registre de Population
Registre principal de la population (comme le FGP)

### 3. **Biometric Identification System (BIS/ABIS)** - Système d'Identification Biométrique
Déduplication et authentification biométrique

### 4. **Identity Gateway (IG)** - Passerelle d'Identité
Point d'entrée pour les requêtes d'identité

### 5. **Functional Registries** - Registres Fonctionnels
Registres sectoriels (éducation, santé, électoral, etc.)

### 6. **Credential Management System (CMS)** - Gestion des Credentials
Émission et gestion des cartes d'identité

---

## 📋 ENTITÉS OSIA - Dictionnaire de Données

### 🔵 Building Block: Population Registry (PR)

#### **Entité: Person (Personne)**

**Attributs obligatoires OSIA:**
- `personId` (String) - Identifiant unique de la personne
- `givenName` (String) - Prénom(s)
- `familyName` (String) - Nom de famille
- `dateOfBirth` (Date) - Date de naissance
- `gender` (Enum: MALE, FEMALE, OTHER, UNKNOWN) - Sexe
- `nationality` (String) - Nationalité
- `registrationStatus` (Enum) - Statut d'enregistrement

**Attributs optionnels:**
- `middleName` (String) - Postnom/Nom intermédiaire
- `placeOfBirth` (String) - Lieu de naissance
- `maritalStatus` (Enum) - Statut matrimonial
- `address` (Address Object) - Adresse
- `contactInformation` (Contact Object) - Informations de contact
- `identificationDocuments` (Array[Document]) - Documents d'identité
- `parents` (Array[ParentReference]) - Références aux parents
- `spouse` (PersonReference) - Référence au conjoint
- `biometricData` (BiometricReference) - Référence aux données biométriques

#### **Entité: Address (Adresse)**
- `addressType` (Enum: RESIDENCE, BIRTH, OTHER)
- `country` (String)
- `stateProvince` (String) - Province/État
- `district` (String) - Territoire/District
- `city` (String) - Ville/Commune
- `postalCode` (String)
- `street` (String) - Rue/Avenue
- `streetNumber` (String) - Numéro
- `addressLine1` (String)
- `addressLine2` (String)

#### **Entité: Contact Information (Contact)**
- `telephone` (String)
- `mobilePhone` (String)
- `email` (String)
- `postOfficeBox` (String)

#### **Entité: Identification Document (Document)**
- `documentType` (Enum: BIRTH_CERTIFICATE, NATIONAL_ID, PASSPORT, etc.)
- `documentNumber` (String)
- `issuingAuthority` (String)
- `dateOfIssue` (Date)
- `dateOfExpiry` (Date)
- `placeOfIssue` (String)
- `documentImage` (URI/String) - Référence au document

#### **Entité: Parent Reference (Référence Parent)**
- `parentId` (String) - PersonId du parent
- `relationshipType` (Enum: FATHER, MOTHER, GUARDIAN, OTHER)
- `order` (Integer) - Ordre (pour multiples parents)

#### **Entité: Strata/Functional Registry Membership**
- `strataCode` (String) - Code de la strate
- `validFrom` (Date)
- `validTo` (Date)
- `status` (Enum: ACTIVE, INACTIVE, SUSPENDED)
- `strataSpecificData` (JSON/Object) - Données spécifiques à la strate

---

### 🟢 Building Block: Biometric Identification System (BIS/ABIS)

#### **Entité: Biometric Template (Gabarit Biométrique)**
- `templateId` (UUID)
- `personId` (String) - Référence à la personne
- `biometricType` (Enum: FACE, FINGERPRINT, IRIS, VOICE)
- `templateData` (Binary/Encrypted) - Données du gabarit
- `templateFormat` (String) - Format (ISO, ANSI, etc.)
- `qualityScore` (Decimal 0.0-1.0) - Score de qualité
- `captureDate` (DateTime)
- `captureDevice` (String) - Identifiant du dispositif
- `captureLocation` (String) - Lieu de capture

#### **Entité: Biometric Match Result (Résultat de Correspondance)**
- `matchId` (UUID)
- `candidatePersonId` (String)
- `matchedPersonId` (String)
- `matchType` (Enum: FACE, FINGERPRINT, IRIS, MULTIMODAL)
- `similarityScore` (Decimal 0.0-1.0)
- `threshold` (Decimal) - Seuil utilisé
- `decision` (Enum: HIT, NO_HIT, REVIEW)
- `reviewStatus` (Enum: PENDING, APPROVED, REJECTED)
- `reviewedBy` (String)
- `reviewedAt` (DateTime)
- `reviewNotes` (String)

---

### 🟡 Building Block: Civil Registry (CR)

#### **Entité: Vital Event (Événement Vital)**
- `eventId` (UUID)
- `eventType` (Enum: BIRTH, DEATH, MARRIAGE, DIVORCE, ADOPTION)
- `personId` (String) - Personne concernée
- `eventDate` (Date)
- `eventLocation` (Address)
- `registrationNumber` (String)
- `registrationDate` (Date)
- `registeringAuthority` (String)
- `certificate` (Document Reference)
- `witnesses` (Array[Witness])
- `eventData` (JSON) - Données spécifiques à l'événement

#### **Entité: Birth Event (Naissance)**
- `childPersonId` (String)
- `fatherPersonId` (String) - Optionnel
- `motherPersonId` (String) - Optionnel
- `birthWeight` (Decimal) - Optionnel
- `birthTime` (Time) - Optionnel
- `birthOrder` (Integer) - Optionnel (jumeaux, etc.)

#### **Entité: Death Event (Décès)**
- `deceasedPersonId` (String)
- `causeOfDeath` (String) - Optionnel
- `placeOfDeath` (Address)
- `certifyingPhysician` (String) - Optionnel

#### **Entité: Marriage Event (Mariage)**
- `spouse1PersonId` (String)
- `spouse2PersonId` (String)
- `marriageType` (Enum: CIVIL, RELIGIOUS, CUSTOMARY)
- `divorceDate` (Date) - Optionnel (si divorcé)

---

### 🟠 Building Block: Functional Registries

#### **Entité: Functional Registry Entry**
- `entryId` (UUID)
- `personId` (String)
- `registryType` (Enum: EDUCATION, HEALTH, ELECTORAL, SECURITY, etc.)
- `registryCode` (String) - Code du registre fonctionnel
- `entryData` (JSON) - Données spécifiques au registre
- `validFrom` (Date)
- `validTo` (Date)
- `status` (Enum)
- `registryReference` (String) - Référence dans le registre source

#### **Exemples de registres fonctionnels:**
- **Education Registry**: Élèves, Étudiants
- **Electoral Registry**: Électeurs
- **Security Registry**: PNC, FARDC
- **Justice Registry**: Prisonniers
- **Refugee Registry**: Réfugiés
- **Displacement Registry**: Déplacés

---

### 🟣 Building Block: Identity Gateway (IG)

#### **Entité: Identity Request (Requête d'Identité)**
- `requestId` (UUID)
- `requestType` (Enum: VERIFY, SEARCH, ENROLL, UPDATE, DELETE)
- `requestorId` (String) - Identifiant du demandeur
- `channel` (Enum: FIXED, MOBILE, ITINERANT, ONLINE)
- `requestData` (JSON) - Données de la requête
- `timestamp` (DateTime)
- `status` (Enum: PENDING, PROCESSING, COMPLETED, FAILED)
- `response` (JSON) - Réponse

#### **Entité: Enrollment Session (Session d'Enrôlement)**
- `sessionId` (UUID)
- `personId` (String) - Optionnel (si déjà connu)
- `channel` (String)
- `deviceId` (String)
- `operatorId` (String)
- `location` (GPS Coordinates)
- `payload` (JSON) - Données complètes d'enrôlement
- `payloadHash` (String)
- `payloadSignature` (String) - Signature JWS
- `status` (Enum)
- `progressPercentage` (Integer)
- `validationResults` (Array[ValidationResult])
- `abisResult` (BiometricMatchResult)
- `createdAt` (DateTime)
- `completedAt` (DateTime)

#### **Entité: Validation Result (Résultat de Validation)**
- `validationId` (UUID)
- `sessionId` (UUID)
- `validationType` (Enum: DATA, BIOMETRIC, DOCUMENT, BUSINESS_RULE)
- `status` (Enum: PASSED, FAILED, WARNING)
- `validationRules` (JSON)
- `errors` (Array[ValidationError])
- `warnings` (Array[ValidationWarning])

---

### 🔴 Building Block: Credential Management System (CMS)

#### **Entité: Credential (Credential)**
- `credentialId` (UUID)
- `personId` (String)
- `credentialType` (Enum: NATIONAL_ID, PASSPORT, DRIVERS_LICENSE, etc.)
- `credentialNumber` (String)
- `issueDate` (Date)
- `expiryDate` (Date)
- `issuingAuthority` (String)
- `status` (Enum: ACTIVE, EXPIRED, REVOKED, SUSPENDED)
- `credentialData` (JSON) - Données du credential
- `biometricData` (BiometricReference)
- `securityFeatures` (Array[SecurityFeature])

---

## 📊 TABLEAU RÉCAPITULATIF DES ENTITÉS OSIA

| Building Block | Entité Principale | Attributs Clés | Relations |
|---------------|-------------------|----------------|-----------|
| **Population Registry** | Person | personId, givenName, familyName, dateOfBirth | 1:N Address, Documents, Parents |
| **Population Registry** | Address | addressType, country, stateProvince, city | N:1 Person |
| **Population Registry** | Contact | telephone, email, mobilePhone | 1:1 Person |
| **Population Registry** | IdentificationDocument | documentType, documentNumber, issuingAuthority | N:1 Person |
| **Population Registry** | ParentReference | parentId, relationshipType | N:1 Person |
| **Biometric System** | BiometricTemplate | templateId, personId, biometricType, templateData | N:1 Person |
| **Biometric System** | BiometricMatchResult | matchId, candidatePersonId, matchedPersonId, similarityScore | N:1 Person (candidate) N:1 Person (matched) |
| **Civil Registry** | VitalEvent | eventId, eventType, personId, eventDate | N:1 Person |
| **Civil Registry** | BirthEvent | childPersonId, fatherPersonId, motherPersonId | 1:1 VitalEvent |
| **Functional Registry** | FunctionalRegistryEntry | entryId, personId, registryType, registryCode | N:1 Person |
| **Identity Gateway** | EnrollmentSession | sessionId, personId, channel, payload | 1:1 Person (optionnel) |
| **Identity Gateway** | IdentityRequest | requestId, requestType, requestorId | N:1 Person |
| **Credential Management** | Credential | credentialId, personId, credentialType, credentialNumber | N:1 Person |

---

## 🔗 RELATIONS ENTRE ENTITÉS OSIA

### Cardinalités OSIA Standard:

```
Person (1) ──────── (0..N) Address
Person (1) ──────── (0..1) Contact
Person (1) ──────── (0..N) IdentificationDocument
Person (1) ──────── (0..N) ParentReference
Person (1) ──────── (0..N) BiometricTemplate
Person (1) ──────── (0..N) VitalEvent
Person (1) ──────── (0..N) FunctionalRegistryEntry
Person (1) ──────── (0..N) Credential
Person (1) ──────── (0..N) EnrollmentSession
Person (1) ──────── (0..N) IdentityRequest

BiometricMatchResult (N) ─── (1) Person [candidate]
BiometricMatchResult (N) ─── (1) Person [matched]

ParentReference (N) ─── (1) Person [parent]
ParentReference (N) ─── (1) Person [child]
```

---

## 📝 PROCHAINES ÉTAPES

1. ✅ **Analyse OSIA complétée**
2. ⏳ **Création du MCD (Modèle Conceptuel de Données) Merise basé sur OSIA**
3. ⏳ **Création du MLD (Modèle Logique de Données) avec mapping OSIA → FGP**
4. ⏳ **Création du diagramme de séquences**

---

**Références:**
- [OSIA Specification](https://osia.readthedocs.io/en/stable/)
- Secure Identity Alliance - OSIA Initiative

