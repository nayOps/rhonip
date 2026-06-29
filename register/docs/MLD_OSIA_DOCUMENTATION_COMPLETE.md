# 📚 Documentation Complète - MLD OSIA pour le Système FGP

## 1. IMPORTANCE DU MODÈLE OSIA DANS LE FGP

### 1.1 Contexte et Enjeux

Le **Fichier Général de la Population (FGP)** de la République Démocratique du Congo est un système critique d'identification nationale qui doit gérer des millions de citoyens, garantir l'intégrité des données, et assurer l'interopérabilité avec les systèmes tiers (banques, institutions gouvernementales, services publics).

### 1.2 Pourquoi OSIA ?

**OSIA (Open Standard Identity APIs)** est une initiative de la Secure Identity Alliance qui répond directement aux défis auxquels fait face le FGP :

#### **1.2.1 Interopérabilité et Neutralité Technologique**

Le modèle OSIA permet au FGP de :
- **Éviter le vendor lock-in** : Le système peut intégrer des composants de différents fournisseurs sans dépendance exclusive
- **Assurer la compatibilité future** : Les standards OSIA garantissent que le système reste compatible avec les nouvelles technologies et fournisseurs
- **Faciliter l'intégration** : Les interfaces standardisées simplifient l'intégration avec les systèmes tiers (banques, assurances, télécoms)

#### **1.2.2 Architecture Modulaire**

OSIA définit clairement les **building blocks** (blocs fonctionnels) :
- **Population Registry** : Registre central de la population
- **Biometric Identification System** : Système de déduplication biométrique
- **Civil Registry** : Registre des événements vitaux
- **Identity Gateway** : Point d'entrée unique pour les requêtes
- **Functional Registries** : Registres sectoriels par strate

Cette modularité permet au FGP de :
- Évoluer progressivement sans refonte complète
- Ajouter de nouvelles fonctionnalités de manière indépendante
- Maintenir des services critiques même si un module est en maintenance

#### **1.2.3 Standardisation des Données**

OSIA fournit un **dictionnaire de données standardisé** qui :
- Garantit la cohérence des données à travers tous les systèmes
- Facilite les échanges de données entre institutions
- Assure la traçabilité et l'audit complet
- Permet la migration future vers d'autres systèmes conformes OSIA

#### **1.2.4 Sécurité et Confidentialité**

Le modèle OSIA intègre des exigences de sécurité :
- Authentification forte via API keys
- Chiffrement des données sensibles
- Audit trail complet de toutes les opérations
- Contrôle d'accès granulaire par client/institution

#### **1.2.5 Monétisation et Durabilité**

OSIA permet au FGP/ONIP de :
- Facturer les services rendus aux tiers (banques, institutions)
- Gérer des abonnements et quotas
- Suivre toutes les transactions pour la facturation
- Générer des revenus récurrents pour la pérennité du système

### 1.3 Avantages Concrets pour le FGP

1. **Réduction des coûts** : Pas de dépendance à un seul fournisseur, possibilité de choisir le meilleur composant pour chaque fonction
2. **Innovation continue** : Les nouveaux fournisseurs peuvent proposer des améliorations sans casser l'existant
3. **Conformité internationale** : OSIA est reconnu comme standard ouvert, facilitant les partenariats internationaux
4. **Évolutivité** : Le système peut grandir avec les besoins sans limitation technologique

---

## 2. DESCRIPTION DÉTAILLÉE DES TABLES

### 2.1 POPULATION REGISTRY (Registre de Population)

Le Population Registry est le cœur du système FGP. Il contient les informations essentielles de chaque personne enregistrée dans le système.

#### **2.1.1 Table : `osia_person` (PERSONNE)**

**Description** : Table centrale contenant les informations de base de chaque personne identifiée dans le système FGP. Chaque personne possède un identifiant unique (NIN - Numéro d'Identification Nationale).

**Attributs principaux** :
- `personId` (VARCHAR(20), PK) : Numéro d'Identification Nationale au format `CD-YYYY-NNNN-NNNNNNNNN`
  - CD = Code pays (RDC)
  - YYYY = Année d'enrôlement
  - NNNN = Série
  - NNNNNNNNN = Numéro séquentiel
- `givenName` (TEXT, NOT NULL) : Prénom(s) de la personne
- `familyName` (TEXT, NOT NULL) : Nom de famille
- `middleName` (TEXT) : Postnom ou nom intermédiaire
- `dateOfBirth` (DATE, NOT NULL) : Date de naissance
- `gender` (CHAR(1), NOT NULL) : Sexe ('M' pour Masculin, 'F' pour Féminin)
- `nationality` (TEXT, NOT NULL) : Nationalité (par défaut 'Congolaise')
- `placeOfBirth` (TEXT, NOT NULL) : Lieu de naissance
- `maritalStatus` (VARCHAR(20)) : Statut matrimonial (Célibataire, Marié(e), Divorcé(e), Veuf(ve), Union libre)
- `registrationStatus` (VARCHAR(20)) : Statut d'enregistrement dans le système

**Rôle** : Cette table est la table centrale du système. Toutes les autres tables (adresses, contacts, documents, biométrie, etc.) référencent cette table via le `personId`.

---

#### **2.1.2 Table : `osia_address` (ADRESSE)**

**Description** : Stocke les adresses associées à une personne. Une personne peut avoir plusieurs adresses (résidence, lieu de naissance, etc.).

**Attributs principaux** :
- `addressId` (UUID, PK) : Identifiant unique de l'adresse
- `personId` (VARCHAR(20), FK) : Référence vers la personne propriétaire de l'adresse
- `addressType` (VARCHAR(20), NOT NULL) : Type d'adresse ('RÉSIDENCE', 'NAISSANCE', 'AUTRE')
- `country` (TEXT) : Pays
- `stateProvince` (TEXT, NOT NULL) : Province/État
- `district` (TEXT) : District/Territoire
- `city` (TEXT) : Ville/Commune
- `postalCode` (VARCHAR(10)) : Code postal
- `street` (TEXT) : Rue/Avenue
- `streetNumber` (VARCHAR(20)) : Numéro de rue

**Rôle** : Permet de gérer plusieurs adresses par personne et de différencier le type d'adresse. Cette séparation améliore la normalisation des données et facilite les recherches géographiques.

---

#### **2.1.3 Table : `osia_contact` (CONTACT)**

**Description** : Contient les informations de contact d'une personne (téléphone, email, boîte postale).

**Attributs principaux** :
- `contactId` (UUID, PK) : Identifiant unique du contact
- `personId` (VARCHAR(20), FK, UNIQUE) : Référence vers la personne (une seule entrée par personne)
- `telephone` (VARCHAR(20)) : Numéro de téléphone fixe
- `mobilePhone` (VARCHAR(20)) : Numéro de téléphone mobile
- `email` (VARCHAR(255)) : Adresse email
- `postOfficeBox` (VARCHAR(50)) : Numéro de boîte postale

**Rôle** : Centralise toutes les informations de contact. La contrainte UNIQUE sur `personId` garantit qu'une personne n'a qu'une seule entrée de contact, simplifiant les mises à jour.

---

#### **2.1.4 Table : `osia_identification_document` (DOCUMENT_IDENTITE)**

**Description** : Stocke les documents d'identité présentés lors de l'enrôlement ou émis par le système (acte de naissance, carte d'identité, passeport).

**Attributs principaux** :
- `documentId` (UUID, PK) : Identifiant unique du document
- `personId` (VARCHAR(20), FK) : Référence vers la personne propriétaire
- `documentType` (VARCHAR(50), NOT NULL) : Type de document ('ACTE_NAISSANCE', 'CARTE_ID', 'PASSEPORT', etc.)
- `documentNumber` (VARCHAR(50), NOT NULL) : Numéro du document
- `issuingAuthority` (TEXT) : Autorité qui a émis le document
- `dateOfIssue` (DATE) : Date d'émission
- `dateOfExpiry` (DATE) : Date d'expiration (si applicable)
- `placeOfIssue` (TEXT) : Lieu d'émission
- `documentImageUri` (TEXT) : URI/chemin vers l'image numérisée du document

**Rôle** : Gère tous les documents d'identité d'une personne. Une personne peut avoir plusieurs documents (acte de naissance + carte d'identité + passeport).

---

#### **2.1.5 Table : `osia_parent_reference` (PARENT)**

**Description** : Gère les relations de parentalité entre personnes. Permet de lier une personne (enfant) à ses parents (père, mère, tuteurs).

**Attributs principaux** :
- `parentRefId` (UUID, PK) : Identifiant unique de la relation parentale
- `childPersonId` (VARCHAR(20), FK) : Référence vers la personne enfant
- `parentPersonId` (VARCHAR(20), FK) : Référence vers la personne parent
- `relationshipType` (VARCHAR(20), NOT NULL) : Type de relation ('PÈRE', 'MÈRE', 'TUTEUR', 'AUTRE')
- `order` (INTEGER) : Ordre dans le cas de multiples parents/tuteurs

**Rôle** : Permet de construire l'arbre généalogique et de gérer les relations familiales. Une personne peut avoir plusieurs parents (père, mère, tuteurs), et une personne peut être parent de plusieurs enfants.

---

#### **2.1.6 Table : `osia_strata_membership` (APPARTENANCE_STRATE)**

**Description** : Gère l'appartenance d'une personne à une ou plusieurs strates fonctionnelles (élèves, électeurs, PNC, FARDC, etc.).

**Attributs principaux** :
- `membershipId` (UUID, PK) : Identifiant unique de l'appartenance
- `personId` (VARCHAR(20), FK) : Référence vers la personne
- `strateCode` (VARCHAR(20), FK) : Code de la strate (référence vers `osia_strata_catalog`)
- `validFrom` (DATE, NOT NULL) : Date de début de validité de l'appartenance
- `validTo` (DATE) : Date de fin de validité (NULL si toujours valide)
- `status` (VARCHAR(20), NOT NULL) : Statut ('ACTIVE', 'INACTIVE', 'SUSPENDED')
- `registryReference` (VARCHAR(100)) : Référence dans le registre source externe (ex: matricule scolaire)

**Rôle** : Permet à une personne d'appartenir à plusieurs strates simultanément avec gestion temporelle. Par exemple, une personne peut être à la fois électeur ET élève.

---

### 2.2 BIOMETRIC IDENTIFICATION SYSTEM (Système Biométrique)

#### **2.2.1 Table : `osia_biometric_template` (GABARIT_BIOMETRIQUE)**

**Description** : Stocke les gabarits biométriques (templates) utilisés pour la déduplication et l'authentification.

**Attributs principaux** :
- `templateId` (UUID, PK) : Identifiant unique du gabarit
- `personId` (VARCHAR(20), FK) : Référence vers la personne
- `biometricType` (VARCHAR(20), NOT NULL) : Type biométrique ('FACE', 'FINGERPRINT', 'IRIS', 'VOICE')
- `templateData` (BYTEA) : Données binaires du gabarit (chiffrées)
- `templateFormat` (VARCHAR(50)) : Format du gabarit ('ISO', 'ANSI', 'Propriétaire')
- `qualityScore` (DECIMAL(3,2)) : Score de qualité (0.0 à 1.0)
- `captureDate` (TIMESTAMPTZ, NOT NULL) : Date et heure de capture
- `captureDevice` (VARCHAR(100)) : Identifiant du dispositif de capture
- `captureLocation` (TEXT) : Lieu de capture

**Rôle** : Centralise tous les gabarits biométriques d'une personne. Permet le multimodal (plusieurs types biométriques par personne).

---

#### **2.2.2 Table : `osia_biometric_match` (CORRESPONDANCE_BIOMETRIQUE)**

**Description** : Enregistre les résultats des recherches biométriques (déduplication) et les correspondances trouvées.

**Attributs principaux** :
- `matchId` (UUID, PK) : Identifiant unique de la correspondance
- `candidatePersonId` (VARCHAR(20), FK) : Personne candidate (nouvellement enrôlée)
- `matchedPersonId` (VARCHAR(20), FK) : Personne existante avec correspondance
- `matchType` (VARCHAR(20), NOT NULL) : Type de correspondance ('FACE', 'FINGERPRINT', 'IRIS', 'MULTIMODAL')
- `similarityScore` (DECIMAL(5,4), NOT NULL) : Score de similarité (0.0 à 1.0)
- `threshold` (DECIMAL(5,4), NOT NULL) : Seuil de décision utilisé
- `decision` (VARCHAR(20), NOT NULL) : Décision automatique ('HIT', 'NO_HIT', 'REVIEW')
- `reviewStatus` (VARCHAR(20)) : Statut de révision ('PENDING', 'APPROVED', 'REJECTED')
- `reviewedBy` (VARCHAR(100)) : Utilisateur ayant effectué la révision
- `reviewedAt` (TIMESTAMPTZ) : Date de révision
- `reviewNotes` (TEXT) : Notes de révision manuelle

**Rôle** : Trace toutes les correspondances biométriques pour l'audit et le suivi des décisions de déduplication.

---

### 2.3 CIVIL REGISTRY (Registre Civil)

#### **2.3.1 Table : `osia_vital_event` (EVENEMENT_VITAL)**

**Description** : Enregistre tous les événements vitaux (naissance, décès, mariage, divorce, adoption).

**Attributs principaux** :
- `eventId` (UUID, PK) : Identifiant unique de l'événement
- `personId` (VARCHAR(20), FK) : Référence vers la personne concernée
- `eventType` (VARCHAR(20), NOT NULL) : Type d'événement ('NAISSANCE', 'DÉCÈS', 'MARIAGE', 'DIVORCE', 'ADOPTION')
- `eventDate` (DATE, NOT NULL) : Date de l'événement
- `eventLocation` (TEXT) : Lieu de l'événement
- `registrationNumber` (VARCHAR(50)) : Numéro d'enregistrement officiel
- `registrationDate` (DATE) : Date d'enregistrement
- `registeringAuthority` (TEXT) : Autorité enregistrante

**Rôle** : Centralise tous les événements vitaux. Les tables spécialisées (`osia_birth_event`, `osia_death_event`, `osia_marriage_event`) enrichissent les informations selon le type.

---

#### **2.3.2 Table : `osia_birth_event` (EVENEMENT_NAISSANCE)**

**Description** : Détails spécifiques aux événements de naissance.

**Attributs principaux** :
- `birthEventId` (UUID, PK) : Identifiant unique
- `eventId` (UUID, FK, UNIQUE) : Référence vers l'événement vital parent
- `childPersonId` (VARCHAR(20), FK) : Référence vers l'enfant né
- `fatherPersonId` (VARCHAR(20), FK) : Référence vers le père (optionnel)
- `motherPersonId` (VARCHAR(20), FK) : Référence vers la mère (optionnel)
- `birthWeight` (DECIMAL(5,2)) : Poids de naissance en kg
- `birthTime` (TIME) : Heure de naissance
- `birthOrder` (INTEGER) : Ordre de naissance (pour jumeaux, etc.)

**Rôle** : Enrichit les événements de naissance avec des détails spécifiques et permet de lier automatiquement l'enfant à ses parents.

---

#### **2.3.3 Table : `osia_death_event` (EVENEMENT_DECES)**

**Description** : Détails spécifiques aux événements de décès.

**Attributs principaux** :
- `deathEventId` (UUID, PK) : Identifiant unique
- `eventId` (UUID, FK, UNIQUE) : Référence vers l'événement vital parent
- `deceasedPersonId` (VARCHAR(20), FK) : Référence vers la personne décédée
- `causeOfDeath` (TEXT) : Cause du décès
- `certifyingPhysician` (VARCHAR(200)) : Nom du médecin certifiant

**Rôle** : Documente les décès avec les informations médicales et légales nécessaires.

---

#### **2.3.4 Table : `osia_marriage_event` (EVENEMENT_MARIAGE)**

**Description** : Détails spécifiques aux événements de mariage.

**Attributs principaux** :
- `marriageEventId` (UUID, PK) : Identifiant unique
- `eventId` (UUID, FK, UNIQUE) : Référence vers l'événement vital parent
- `spouse1PersonId` (VARCHAR(20), FK) : Référence vers le premier époux
- `spouse2PersonId` (VARCHAR(20), FK) : Référence vers le second époux
- `marriageType` (VARCHAR(20)) : Type de mariage ('CIVIL', 'RELIGIEUX', 'COUTUMIER')
- `divorceDate` (DATE) : Date de divorce si applicable

**Rôle** : Gère les mariages et permet de mettre à jour automatiquement le statut matrimonial des époux.

---

### 2.4 FUNCTIONAL REGISTRIES (Registres Fonctionnels)

#### **2.4.1 Table : `osia_strata_catalog` (STRATE)**

**Description** : Catalogue des strates disponibles dans le système (élèves, électeurs, PNC, etc.).

**Attributs principaux** :
- `strateCode` (VARCHAR(20), PK) : Code unique de la strate ('ELEVE', 'ETUDIANT', 'ELECTEUR', 'PNC', 'FARDC', etc.)
- `strateName` (TEXT, NOT NULL) : Nom complet de la strate
- `strateDescription` (TEXT) : Description de la strate

**Rôle** : Référence maître pour toutes les strates. Permet d'ajouter facilement de nouvelles strates sans modifier le schéma.

---

#### **2.4.2 Table : `osia_functional_registry_entry` (Entrées Registres Fonctionnels)**

**Description** : Entrées dans les registres fonctionnels sectoriels avec données spécifiques en JSON.

**Attributs principaux** :
- `entryId` (UUID, PK) : Identifiant unique de l'entrée
- `personId` (VARCHAR(20), FK) : Référence vers la personne
- `registryType` (VARCHAR(50), NOT NULL) : Type de registre ('EDUCATION', 'HEALTH', 'ELECTORAL', 'SECURITY')
- `registryCode` (VARCHAR(50)) : Code dans le registre source
- `entryData` (JSONB) : Données spécifiques au registre (structure flexible)
- `validFrom` (DATE, NOT NULL) : Date de début de validité
- `validTo` (DATE) : Date de fin de validité
- `status` (VARCHAR(20)) : Statut de l'entrée

**Rôle** : Permet de stocker des données spécifiques à chaque secteur de manière flexible via JSON, sans créer une table par secteur.

---

### 2.5 IDENTITY GATEWAY (Passerelle d'Identité)

#### **2.5.1 Table : `osia_enrollment_session` (SESSION_ENROLEMENT)**

**Description** : Sessions d'enrôlement des nouvelles personnes dans le système.

**Attributs principaux** :
- `sessionId` (UUID, PK) : Identifiant unique de la session
- `personId` (VARCHAR(20), FK) : Référence vers la personne (NULL si enrôlement en cours)
- `channel` (VARCHAR(20), NOT NULL) : Canal d'enrôlement ('FIXED', 'MOBILE', 'ITINERANT', 'ONLINE')
- `deviceId` (VARCHAR(100)) : Identifiant du dispositif utilisé
- `operatorId` (VARCHAR(100)) : Identifiant de l'opérateur
- `location` (TEXT) : Coordonnées GPS ou adresse
- `payloadHash` (VARCHAR(64)) : Hash SHA-256 du payload complet
- `payloadSignature` (TEXT) : Signature JWS du payload
- `status` (VARCHAR(20), NOT NULL) : Statut ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')
- `progressPercentage` (INTEGER) : Pourcentage de progression (0-100)
- `createdAt` (TIMESTAMPTZ, NOT NULL) : Date de création
- `completedAt` (TIMESTAMPTZ) : Date de complétion

**Rôle** : Trace complète de chaque processus d'enrôlement pour l'audit et le suivi.

---

#### **2.5.2 Table : `osia_identity_request` (REQUETE_IDENTITE)**

**Description** : Requêtes d'identité effectuées par les clients (banques, institutions) via l'API.

**Attributs principaux** :
- `requestId` (UUID, PK) : Identifiant unique de la requête
- `personId` (VARCHAR(20), FK) : Référence vers la personne concernée (optionnel pour recherche)
- `requestType` (VARCHAR(20), NOT NULL) : Type de requête ('VERIFY', 'SEARCH', 'ENROLL', 'UPDATE', 'DELETE')
- `requestorId` (VARCHAR(100), NOT NULL) : Identifiant du client effectuant la requête
- `requestData` (JSONB) : Données de la requête (structure flexible)
- `timestamp` (TIMESTAMPTZ, NOT NULL) : Horodatage de la requête
- `status` (VARCHAR(20)) : Statut de traitement

**Rôle** : Journalise toutes les requêtes d'identité pour l'audit, la facturation et le suivi.

---

#### **2.5.3 Table : `osia_validation_result` (VALIDATION)**

**Description** : Résultats des validations effectuées pendant l'enrôlement.

**Attributs principaux** :
- `validationId` (UUID, PK) : Identifiant unique
- `sessionId` (UUID, FK) : Référence vers la session d'enrôlement
- `validationType` (VARCHAR(50), NOT NULL) : Type de validation ('DATA', 'BIOMETRIC', 'DOCUMENT', 'BUSINESS_RULE')
- `status` (VARCHAR(20), NOT NULL) : Statut ('PASSED', 'FAILED', 'WARNING')
- `validationRules` (JSONB) : Règles de validation appliquées
- `errors` (JSONB) : Détails des erreurs si échec
- `warnings` (JSONB) : Avertissements éventuels
- `createdAt` (TIMESTAMPTZ, NOT NULL) : Date de validation

**Rôle** : Enregistre toutes les validations pour garantir la qualité des données et l'audit.

---

#### **2.5.4 Table : `osia_enrollment_event` (Événements d'Enrôlement)**

**Description** : Événements survenus pendant une session d'enrôlement.

**Attributs principaux** :
- `eventId` (UUID, PK) : Identifiant unique
- `sessionId` (UUID, FK) : Référence vers la session
- `eventType` (VARCHAR(50), NOT NULL) : Type d'événement
- `eventData` (JSONB) : Données de l'événement
- `message` (TEXT) : Message descriptif
- `timestamp` (TIMESTAMPTZ, NOT NULL) : Horodatage
- `createdBy` (VARCHAR(100)) : Utilisateur/système créateur

**Rôle** : Historique détaillé de tous les événements d'une session d'enrôlement.

---

### 2.6 CREDENTIAL MANAGEMENT SYSTEM

#### **2.6.1 Table : `osia_credential` (CREDENTIAL)**

**Description** : Credentials émis (cartes d'identité, passeports, etc.).

**Attributs principaux** :
- `credentialId` (UUID, PK) : Identifiant unique
- `personId` (VARCHAR(20), FK) : Référence vers la personne
- `credentialType` (VARCHAR(50), NOT NULL) : Type ('CARTE_NATIONALE', 'PASSEPORT', 'PERMIS_CONDUITE')
- `credentialNumber` (VARCHAR(50), NOT NULL) : Numéro unique du credential
- `issueDate` (DATE, NOT NULL) : Date d'émission
- `expiryDate` (DATE) : Date d'expiration
- `issuingAuthority` (TEXT) : Autorité émettrice
- `status` (VARCHAR(20), NOT NULL) : Statut ('ACTIVE', 'EXPIRED', 'REVOKED', 'SUSPENDED')

**Rôle** : Gère tous les credentials physiques ou numériques émis pour une personne.

---

### 2.7 AUDIT & SECURITY

#### **2.7.1 Table : `osia_audit_trail` (Piste d'Audit)**

**Description** : Piste d'audit complète de toutes les opérations sur les données.

**Attributs principaux** :
- `auditId` (UUID, PK) : Identifiant unique
- `personId` (VARCHAR(20), FK) : Référence vers la personne concernée
- `action` (VARCHAR(50), NOT NULL) : Action effectuée ('CREATE', 'UPDATE', 'DELETE', 'VIEW')
- `tableName` (VARCHAR(50), NOT NULL) : Table concernée
- `oldValues` (JSONB) : Valeurs avant modification (pour UPDATE/DELETE)
- `newValues` (JSONB) : Valeurs après modification (pour CREATE/UPDATE)
- `userId` (VARCHAR(100), NOT NULL) : Utilisateur ayant effectué l'action
- `userIp` (INET) : Adresse IP de l'utilisateur
- `userAgent` (TEXT) : User agent du client
- `timestamp` (TIMESTAMPTZ, NOT NULL) : Horodatage de l'action

**Rôle** : Traçabilité complète et inviolable de toutes les modifications pour conformité et sécurité.

---

#### **2.7.2 Table : `osia_security_event` (Événements de Sécurité)**

**Description** : Événements de sécurité (tentatives d'intrusion, accès non autorisés, etc.).

**Attributs principaux** :
- `securityEventId` (UUID, PK) : Identifiant unique
- `eventType` (VARCHAR(50), NOT NULL) : Type d'événement ('INTRUSION', 'UNAUTHORIZED_ACCESS', etc.)
- `severity` (VARCHAR(20), NOT NULL) : Gravité ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
- `userId` (VARCHAR(100)) : Utilisateur concerné
- `ipAddress` (INET) : Adresse IP source
- `timestamp` (TIMESTAMPTZ, NOT NULL) : Horodatage
- `description` (TEXT) : Description de l'événement
- `resolved` (BOOLEAN) : Événement résolu ou non

**Rôle** : Monitoring de la sécurité et détection d'incidents.

---

### 2.8 MONÉTISATION (BILLING & MONETIZATION)

#### **2.8.1 Table : `onip_client` (CLIENT)**

**Description** : Clients du système ONIP (banques, institutions, entreprises) qui utilisent l'API.

**Attributs principaux** :
- `clientId` (UUID, PK) : Identifiant unique
- `clientCode` (VARCHAR(50), UNIQUE, NOT NULL) : Code client unique
- `clientName` (VARCHAR(200), NOT NULL) : Nom du client
- `clientType` (VARCHAR(50)) : Type ('BANQUE', 'ASSURANCE', 'TELCO', 'GOUVERNEMENT', 'PRIVÉ')
- `billingModel` (VARCHAR(20), NOT NULL) : Modèle de facturation ('TRANSACTIONNEL', 'ABONNEMENT', 'HYBRIDE')
- `creditLimit` (DECIMAL(12,2)) : Limite de crédit
- `currentBalance` (DECIMAL(12,2), DEFAULT 0) : Solde actuel
- `status` (VARCHAR(20), NOT NULL, DEFAULT 'ACTIF') : Statut ('ACTIF', 'SUSPENDU', 'BLOQUÉ')
- `contractStartDate` (DATE) : Date de début du contrat
- `contractEndDate` (DATE) : Date de fin du contrat

**Rôle** : Gestion des clients et de leur modèle de facturation.

---

#### **2.8.2 Table : `onip_api_key` (CLE_API)**

**Description** : Clés API permettant aux clients d'accéder au système.

**Attributs principaux** :
- `keyId` (UUID, PK) : Identifiant unique
- `clientId` (UUID, FK, NOT NULL) : Référence vers le client
- `apiKey` (VARCHAR(255), UNIQUE, NOT NULL) : Clé API publique
- `apiSecretHash` (VARCHAR(255), NOT NULL) : Hash de la clé secrète
- `permissions` (JSONB) : Permissions accordées (liste des endpoints autorisés)
- `rateLimit` (INTEGER, DEFAULT 1000) : Limite de requêtes par heure
- `ipWhitelist` (TEXT[]) : Liste des adresses IP autorisées
- `status` (VARCHAR(20), NOT NULL, DEFAULT 'ACTIF') : Statut ('ACTIF', 'EXPIRÉ', 'RÉVOQUÉ')
- `expiresAt` (TIMESTAMPTZ) : Date d'expiration
- `lastUsedAt` (TIMESTAMPTZ) : Dernière utilisation

**Rôle** : Authentification et autorisation des clients via API keys.

---

#### **2.8.3 Table : `onip_pricing` (TARIF)**

**Description** : Tarification des différents types de transactions.

**Attributs principaux** :
- `pricingId` (UUID, PK) : Identifiant unique
- `transactionType` (VARCHAR(50), UNIQUE, NOT NULL) : Type de transaction ('IDENTITY_VERIFY', 'BIOMETRIC_VERIFY', etc.)
- `basePrice` (DECIMAL(10,2), NOT NULL) : Prix de base
- `currency` (VARCHAR(3), DEFAULT 'USD') : Devise ('USD', 'CDF')
- `clientType` (VARCHAR(50)) : Type de client pour tarif personnalisé (NULL = tarif général)
- `volumeDiscountThreshold` (INTEGER) : Seuil de transactions/mois pour remise volume
- `volumeDiscountPercentage` (DECIMAL(5,2)) : Pourcentage de remise
- `validFrom` (DATE, NOT NULL) : Date de début de validité
- `validTo` (DATE) : Date de fin de validité

**Rôle** : Définit les tarifs pour chaque type de transaction avec possibilité de personnalisation par type de client.

---

#### **2.8.4 Table : `onip_transaction` (TRANSACTION)**

**Description** : Transactions facturables effectuées par les clients.

**Attributs principaux** :
- `transactionId` (UUID, PK) : Identifiant unique
- `requestorId` (VARCHAR(100), NOT NULL) : Identifiant du client (FK logique vers onip_client)
- `transactionType` (VARCHAR(50), NOT NULL) : Type de transaction
- `personId` (VARCHAR(20), FK) : Référence vers la personne (optionnel pour recherche 1:N)
- `apiEndpoint` (VARCHAR(255)) : Endpoint API appelé
- `requestTimestamp` (TIMESTAMPTZ, NOT NULL) : Horodatage de la requête
- `responseStatus` (VARCHAR(20)) : Statut de la réponse ('SUCCESS', 'FAILED', 'ERROR')
- `responseTimeMs` (INTEGER) : Temps de réponse en millisecondes
- `amount` (DECIMAL(10,2), NOT NULL) : Montant facturé
- `currency` (VARCHAR(3), DEFAULT 'USD') : Devise
- `billingStatus` (VARCHAR(20), DEFAULT 'PENDING') : Statut de facturation ('PENDING', 'INVOICED', 'PAID')
- `invoiceId` (UUID, FK) : Référence vers la facture (si facturé)

**Rôle** : Enregistre chaque transaction facturable pour la facturation mensuelle.

---

#### **2.8.5 Table : `onip_subscription` (ABONNEMENT)**

**Description** : Abonnements des clients (plans avec quota).

**Attributs principaux** :
- `subscriptionId` (UUID, PK) : Identifiant unique
- `clientId` (UUID, FK, NOT NULL) : Référence vers le client
- `planType` (VARCHAR(50), NOT NULL) : Type de plan ('STARTER', 'BUSINESS', 'ENTERPRISE', 'UNLIMITED')
- `quotaMonthly` (INTEGER, NOT NULL) : Quota mensuel de transactions incluses
- `usedQuota` (INTEGER, DEFAULT 0) : Quota utilisé dans le mois en cours
- `billingCycle` (VARCHAR(20), DEFAULT 'MONTHLY') : Cycle de facturation ('MONTHLY', 'QUARTERLY', 'YEARLY')
- `startDate` (DATE, NOT NULL) : Date de début
- `endDate` (DATE) : Date de fin
- `autoRenew` (BOOLEAN, DEFAULT TRUE) : Renouvellement automatique
- `status` (VARCHAR(20), DEFAULT 'ACTIF') : Statut ('ACTIF', 'EXPIRÉ', 'SUSPENDU')

**Rôle** : Gère les abonnements et les quotas mensuels pour les clients.

---

#### **2.8.6 Table : `onip_invoice` (FACTURE)**

**Description** : Factures générées pour les clients.

**Attributs principaux** :
- `invoiceId` (UUID, PK) : Identifiant unique
- `clientId` (UUID, FK, NOT NULL) : Référence vers le client
- `invoiceNumber` (VARCHAR(50), UNIQUE, NOT NULL) : Numéro de facture unique
- `billingPeriodStart` (DATE, NOT NULL) : Début de la période de facturation
- `billingPeriodEnd` (DATE, NOT NULL) : Fin de la période
- `totalAmount` (DECIMAL(12,2), NOT NULL) : Montant total HT
- `taxAmount` (DECIMAL(12,2), DEFAULT 0) : Montant des taxes
- `totalWithTax` (DECIMAL(12,2), NOT NULL) : Montant total TTC
- `currency` (VARCHAR(3), DEFAULT 'USD') : Devise
- `status` (VARCHAR(20), DEFAULT 'DRAFT') : Statut ('DRAFT', 'SENT', 'PAID', 'OVERDUE')
- `dueDate` (DATE) : Date d'échéance
- `paidDate` (DATE) : Date de paiement
- `paymentReference` (VARCHAR(100)) : Référence de paiement

**Rôle** : Génère et suit les factures mensuelles pour chaque client.

---

## 3. RELATIONS ENTRE LES TABLES

### 3.1 Relations de Base (Population Registry)

#### **PERSONNE ↔ ADRESSE**
- **Relation** : Une PERSONNE peut avoir plusieurs ADRESSE (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Une personne a une et une seule entrée principale dans PERSONNE, mais peut avoir plusieurs adresses (résidence actuelle, lieu de naissance, adresse secondaire). Chaque adresse appartient à une seule personne.
- **Utilisation** : Permet de gérer l'historique des adresses et différents types d'adresses.

#### **PERSONNE ↔ CONTACT**
- **Relation** : Une PERSONNE a un et un seul CONTACT (1:1)
- **Cardinalité** : (1,1) ↔ (0,1)
- **Explication** : Une personne a une seule entrée de contact (même si elle contient plusieurs moyens : téléphone, email, mobile). La contrainte UNIQUE sur `personId` garantit l'unicité.
- **Utilisation** : Centralise toutes les informations de contact en un seul endroit.

#### **PERSONNE ↔ DOCUMENT_IDENTITE**
- **Relation** : Une PERSONNE peut avoir plusieurs DOCUMENT_IDENTITE (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Une personne peut posséder plusieurs documents (acte de naissance, carte d'identité, passeport, etc.). Chaque document appartient à une seule personne.
- **Utilisation** : Gère tous les documents présentés lors de l'enrôlement et ceux émis par le système.

#### **PERSONNE ↔ PARENT (relation récursive)**
- **Relation** : Relation récursive sur PERSONNE via PARENT
- **Cardinalité** : 
  - Personne (enfant) ↔ PARENT : (1,1) ↔ (0,N)
  - Personne (parent) ↔ PARENT : (1,1) ↔ (0,N)
- **Explication** : Une personne peut avoir plusieurs parents (père, mère, tuteurs). Une personne peut être parent de plusieurs enfants. La table PARENT fait le lien entre deux personnes.
- **Utilisation** : Construit l'arbre généalogique et gère les relations familiales.

#### **PERSONNE ↔ GABARIT_BIOMETRIQUE**
- **Relation** : Une PERSONNE peut avoir plusieurs GABARIT_BIOMETRIQUE (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Une personne peut avoir plusieurs gabarits biométriques de types différents (visage, empreintes, iris) pour le multimodal. Chaque gabarit appartient à une seule personne.
- **Utilisation** : Permet l'authentification multimodale et la déduplication.

#### **PERSONNE ↔ APPARTENANCE_STRATE ↔ STRATE**
- **Relation** : Relation ternaire via APPARTENANCE_STRATE
- **Cardinalité** :
  - PERSONNE ↔ APPARTENANCE_STRATE : (1,N) ↔ (0,N)
  - STRATE ↔ APPARTENANCE_STRATE : (1,1) ↔ (0,N)
- **Explication** : Une personne peut appartenir à plusieurs strates (élève ET électeur par exemple). Chaque appartenance est unique avec une période de validité. Une strate peut avoir plusieurs membres.
- **Utilisation** : Gère l'appartenance multiple aux strates avec gestion temporelle.

### 3.2 Relations Biométriques

#### **PERSONNE ↔ CORRESPONDANCE_BIOMETRIQUE (relation double)**
- **Relation** : Relation double - une correspondance lie deux personnes
- **Cardinalité** :
  - PERSONNE (candidate) ↔ CORRESPONDANCE_BIOMETRIQUE : (1,N) ↔ (0,N)
  - PERSONNE (matched) ↔ CORRESPONDANCE_BIOMETRIQUE : (1,1) ↔ (0,N)
- **Explication** : Lors d'une recherche de déduplication, une personne candidate (nouvellement enrôlée) peut correspondre à une personne existante (matched). Une personne peut être candidate dans plusieurs recherches, mais chaque correspondance identifie une personne matched unique.
- **Utilisation** : Enregistre les résultats de déduplication biométrique pour audit et révision.

### 3.3 Relations Registre Civil

#### **PERSONNE ↔ EVENEMENT_VITAL**
- **Relation** : Une PERSONNE peut avoir plusieurs EVENEMENT_VITAL (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Une personne peut avoir plusieurs événements vitaux (naissance, mariage, décès, etc.). Chaque événement concerne une ou plusieurs personnes selon le type.
- **Utilisation** : Historique complet des événements vitaux d'une personne.

#### **EVENEMENT_VITAL ↔ EVENEMENT_NAISSANCE/DECES/MARIAGE**
- **Relation** : Spécialisation (héritage)
- **Cardinalité** : (1,1) ↔ (0,1)
- **Explication** : Un événement vital de type NAISSANCE peut avoir une entrée dans EVENEMENT_NAISSANCE qui enrichit l'information. Relation 1:0..1 car tous les événements ne sont pas spécialisés.
- **Utilisation** : Enrichit les événements avec des détails spécifiques selon le type.

#### **PERSONNE ↔ EVENEMENT_NAISSANCE**
- **Relation** : Trois relations distinctes
- **Cardinalité** :
  - PERSONNE (enfant) ↔ EVENEMENT_NAISSANCE : (1,1) ↔ (0,1) - Un enfant n'a qu'un événement de naissance
  - PERSONNE (père) ↔ EVENEMENT_NAISSANCE : (1,1) ↔ (0,N) - Un père peut avoir plusieurs enfants
  - PERSONNE (mère) ↔ EVENEMENT_NAISSANCE : (1,1) ↔ (0,N) - Une mère peut avoir plusieurs enfants
- **Explication** : Un événement de naissance lie un enfant à ses parents optionnels.
- **Utilisation** : Construit automatiquement les relations parentales lors de l'enregistrement des naissances.

#### **PERSONNE ↔ EVENEMENT_MARIAGE**
- **Relation** : Deux personnes pour un mariage
- **Cardinalité** :
  - PERSONNE (époux 1) ↔ EVENEMENT_MARIAGE : (1,1) ↔ (0,N) - Une personne peut se marier plusieurs fois
  - PERSONNE (époux 2) ↔ EVENEMENT_MARIAGE : (1,1) ↔ (0,N)
- **Explication** : Un mariage lie deux époux. Une personne peut avoir plusieurs mariages (divorces/remariages).
- **Utilisation** : Gère les mariages et met à jour le statut matrimonial.

### 3.4 Relations Identity Gateway

#### **PERSONNE ↔ SESSION_ENROLEMENT**
- **Relation** : Une PERSONNE peut être enregistrée via plusieurs SESSION_ENROLEMENT (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Une personne peut être enrôlée une fois (ou mise à jour via une nouvelle session). Une session peut créer une nouvelle personne ou mettre à jour une existante.
- **Utilisation** : Trace complète du processus d'enrôlement.

#### **SESSION_ENROLEMENT ↔ VALIDATION**
- **Relation** : Une SESSION_ENROLEMENT peut avoir plusieurs VALIDATION (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Pendant une session d'enrôlement, plusieurs validations sont effectuées (validation des données, biométrie, documents, règles métier). Chaque validation appartient à une seule session.
- **Utilisation** : Suivi détaillé des validations pendant l'enrôlement.

#### **REQUETE_IDENTITE ↔ TRANSACTION**
- **Relation** : Une REQUETE_IDENTITE peut générer une TRANSACTION (1:0..1)
- **Cardinalité** : (1,1) ↔ (0,1)
- **Explication** : Toutes les requêtes ne génèrent pas forcément une transaction facturable (ex: requêtes internes). Une transaction correspond toujours à une requête.
- **Utilisation** : Lie les requêtes aux transactions pour la facturation.

### 3.5 Relations Monétisation

#### **CLIENT ↔ CLE_API**
- **Relation** : Un CLIENT peut avoir plusieurs CLE_API (1:N)
- **Cardinalité** : (1,1) ↔ (1,N)
- **Explication** : Un client peut avoir plusieurs clés API (une pour le développement, une pour la production, etc.). Chaque clé appartient à un seul client. Minimum une clé par client.
- **Utilisation** : Gestion des accès API par client avec possibilité de multiples environnements.

#### **CLIENT ↔ TRANSACTION**
- **Relation** : Un CLIENT effectue plusieurs TRANSACTION (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Un client peut effectuer de nombreuses transactions. Chaque transaction est liée à un client via `requestorId`. Un client peut avoir zéro transaction (nouveau client).
- **Utilisation** : Enregistrement de toutes les transactions pour facturation.

#### **CLIENT ↔ ABONNEMENT**
- **Relation** : Un CLIENT peut avoir un ABONNEMENT optionnel (1:0..1)
- **Cardinalité** : (1,1) ↔ (0,1)
- **Explication** : Si le client a un modèle de facturation 'ABONNEMENT' ou 'HYBRIDE', il a un abonnement. Un client avec modèle 'TRANSACTIONNEL' n'a pas d'abonnement.
- **Utilisation** : Gère les quotas mensuels pour les clients avec abonnement.

#### **CLIENT ↔ FACTURE**
- **Relation** : Un CLIENT reçoit plusieurs FACTURE (1:N)
- **Cardinalité** : (1,1) ↔ (0,N)
- **Explication** : Un client reçoit une facture mensuelle (ou plus selon le cycle). Chaque facture est destinée à un seul client.
- **Utilisation** : Génération et suivi des factures mensuelles.

#### **TRANSACTION ↔ TARIF**
- **Relation** : Plusieurs TRANSACTION utilisent un TARIF (N:1)
- **Cardinalité** : (0,N) ↔ (1,1)
- **Explication** : Chaque transaction utilise un tarif selon son type. Un tarif peut être utilisé par plusieurs transactions. Relation logique via `transactionType`.
- **Utilisation** : Détermine le montant facturé pour chaque transaction.

#### **TRANSACTION ↔ PERSONNE**
- **Relation** : Une TRANSACTION peut concerner une PERSONNE optionnelle (N:0..1)
- **Cardinalité** : (0,N) ↔ (1,1)
- **Explication** : La plupart des transactions concernent une personne spécifique (vérification d'identité). Cependant, les recherches 1:N ne concernent pas une personne unique. Une personne peut avoir plusieurs transactions la concernant.
- **Utilisation** : Lie les transactions aux personnes pour audit et suivi.

#### **TRANSACTION ↔ FACTURE**
- **Relation** : Plusieurs TRANSACTION sont incluses dans une FACTURE (N:1)
- **Cardinalité** : (0,N) ↔ (1,1)
- **Explication** : Une facture regroupe plusieurs transactions d'un client sur une période. Une transaction peut être en 'PENDING' (non encore facturée) ou 'INVOICED' (incluse dans une facture). Une transaction appartient au maximum à une facture.
- **Utilisation** : Agrégation des transactions pour facturation mensuelle.

---

## 4. EXPLICATION DES CARDINALITÉS

### 4.1 Cardinalité (1,1) - Un et un seul

**Signification** : L'entité A a exactement une relation avec l'entité B, obligatoire.

**Exemples** :
- **PERSONNE ↔ CONTACT** : Une personne a exactement un contact (même s'il peut être vide). Obligatoire.
- **EVENEMENT_NAISSANCE ↔ EVENEMENT_VITAL** : Un événement de naissance est exactement lié à un événement vital parent. Obligatoire.

**Contrainte** : Foreign Key avec NOT NULL. Chaque ligne de A doit avoir une ligne correspondante dans B.

---

### 4.2 Cardinalité (0,1) - Zéro ou un seul

**Signification** : L'entité A peut avoir zéro ou une relation avec l'entité B.

**Exemples** :
- **PERSONNE ↔ SESSION_ENROLEMENT** : Une personne peut avoir été enrôlée via zéro ou une session (si mise à jour après enrôlement initial).
- **CLIENT ↔ ABONNEMENT** : Un client peut avoir zéro ou un abonnement (selon son modèle de facturation).

**Contrainte** : Foreign Key nullable. Une ligne de A peut ou non avoir une ligne correspondante dans B.

---

### 4.3 Cardinalité (0,N) - Zéro, un ou plusieurs

**Signification** : L'entité A peut avoir zéro, un ou plusieurs relations avec l'entité B.

**Exemples** :
- **PERSONNE ↔ ADRESSE** : Une personne peut avoir zéro, une ou plusieurs adresses.
- **PERSONNE ↔ DOCUMENT_IDENTITE** : Une personne peut avoir zéro, un ou plusieurs documents.
- **CLIENT ↔ FACTURE** : Un client peut avoir zéro ou plusieurs factures.

**Contrainte** : Foreign Key standard. Une ligne de A peut avoir zéro ou plusieurs lignes correspondantes dans B.

---

### 4.4 Cardinalité (1,N) - Un ou plusieurs

**Signification** : L'entité A a au minimum une relation avec l'entité B, peut en avoir plusieurs.

**Exemples** :
- **PERSONNE ↔ PARENT** : Une personne a au moins un parent (même si inconnu). Peut en avoir plusieurs (père, mère, tuteurs).
- **CLIENT ↔ CLE_API** : Un client a au minimum une clé API. Peut en avoir plusieurs (environnements).

**Contrainte** : Foreign Key avec NOT NULL. Chaque ligne de A doit avoir au minimum une ligne correspondante dans B.

---

## 5. CONCLUSION

Ce modèle MLD OSIA pour le FGP garantit :

1. **Interopérabilité** : Standards ouverts permettant l'intégration avec n'importe quel système conforme OSIA
2. **Scalabilité** : Architecture modulaire pouvant évoluer avec les besoins
3. **Sécurité** : Audit trail complet et contrôle d'accès granulaire
4. **Monétisation** : Système de facturation intégré pour la pérennité
5. **Flexibilité** : Données JSON pour les extensions futures sans modification de schéma
6. **Traçabilité** : Historique complet de toutes les opérations

Le modèle est conçu pour supporter des millions de personnes, des milliers de transactions par jour, et une croissance continue du système.

---

**Date de création** : $(date)  
**Version** : 1.0  
**Conforme à** : OSIA Specification v1.0  
**Auteur** : Système FGP - ONIP RDC

