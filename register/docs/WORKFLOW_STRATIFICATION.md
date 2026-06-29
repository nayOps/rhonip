# 🔄 Workflow du Système FGP - Stratification Fonctionnelle

## 📋 Vue d'ensemble

Ce document technique décrit le workflow complet du système FGP (Fichier Général de la Population), en mettant un accent particulier sur le mécanisme de **stratification fonctionnelle** qui permet d'adapter le système selon le secteur d'appartenance de chaque personne.

---

## 1. ARCHITECTURE GÉNÉRALE DU SYSTÈME

### 1.1 Composants Principaux

Le système FGP est organisé en microservices selon l'architecture OSIA :

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                        │
│         Interface d'Enrôlement Dynamique par Strate        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              ENROLLMENT GATEWAY (Port 8001)                  │
│         Point d'entrée unique - Orchestration               │
└───────────┬───────────────────────────────┬─────────────────┘
            │                               │
            ▼                               ▼
┌───────────────────────┐    ┌──────────────────────────────┐
│  FGP CORE (8000)       │    │  EXTENSIONS SERVICE (8002)    │
│  27 variables de base  │    │  Extensions par strate       │
└───────────┬───────────┘    └───────────┬──────────────────┘
            │                             │
            └──────────────┬──────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  ABIS SERVICE (8003)   │
              │  Déduplication Bio.    │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  PostgreSQL Database   │
              │  Tables Core + Ext.    │
              └────────────────────────┘
```

### 1.2 Principe de Stratification

**La stratification** est le mécanisme qui permet à une personne d'appartenir à un ou plusieurs secteurs fonctionnels (éducation, sécurité, électoral, etc.). Chaque strate définit :
- Les données supplémentaires à collecter (extensions)
- Les règles de validation spécifiques
- Les formulaires d'enrôlement adaptés
- Les intégrations avec les systèmes externes sectoriels

---

## 2. WORKFLOW D'ENRÔLEMENT AVEC STRATIFICATION

### 2.1 Phase 1 : Initialisation de la Session

```
1. Opérateur lance l'application d'enrôlement
   ↓
2. Système affiche le formulaire de base (27 variables FGP)
   ↓
3. Opérateur sélectionne le CANAL d'enrôlement :
   - FIXED (Poste fixe)
   - MOBILE (Kit mobile)
   - ITINERANT (Campagne itinérante)
   - ONLINE (En ligne)
   ↓
4. Création de la session dans enrollment_sessions
   - sessionId généré (UUID)
   - channel enregistré
   - deviceId identifié
   - operatorId authentifié
   - status = "PENDING"
```

**Point clé** : Le canal peut influencer les strates disponibles (ex: canal "school" pour élèves).

---

### 2.2 Phase 2 : Collecte des Données de Base (Noyau FGP)

```
1. Formulaire base s'affiche avec les 27 variables obligatoires :
   - Identité : nom, prénom, postnom, sexe
   - Naissance : date, lieu, province, nationalité
   - Résidence : province, territoire, commune, quartier, avenue, numéro
   - Contact : téléphone, email
   - Parents : nom père, nom mère
   - Profession/Éducation : profession, niveau d'étude
   - Pièce d'identité : type, numéro, date émission, lieu émission
   ↓
2. Validation en temps réel des champs obligatoires
   ↓
3. Sauvegarde temporaire dans le payload de la session
   (Pas encore de création en base de données)
```

**Important** : Ces données sont communes à TOUTES les strates.

---

### 2.3 Phase 3 : SÉLECTION DES STRATES ⭐ CŒUR DU SYSTÈME

Cette phase est **fondamentale** car elle détermine tout le reste du processus.

#### **3.1 Présentation des Strates Disponibles**

```
Après la collecte des données de base, le système présente les strates disponibles :

┌─────────────────────────────────────────────────┐
│         SÉLECTION DES STRATES                  │
│                                                 │
│  ☐ ÉLÈVES (Primaire/Secondaire)                 │
│  ☐ ÉTUDIANTS (Supérieur)                        │
│  ☐ ÉLECTEURS (Corps électoral)                  │
│  ☐ PNC (Police Nationale Congolaise)           │
│  ☐ FARDC (Forces Armées)                        │
│  ☐ PRISONNIERS (Système pénitentiaire)          │
│  ☐ RÉFUGIÉS (Statut HCR)                        │
│  ☐ ENFANTS (Mineurs non scolarisés)             │
│  ☐ FONCTIONNAIRES (Agents de l'État)            │
└─────────────────────────────────────────────────┘
```

#### **3.2 Logique de Sélection Multi-Strate**

**Principe** : Une personne peut appartenir à **plusieurs strates simultanément**.

**Exemples concrets** :
- Un **étudiant** peut être aussi **électeur** (si ≥ 18 ans)
- Un **militaire FARDC** peut être **électeur**
- Un **élève** peut aussi être dans la strate **ENFANTS**

**Règles de validation automatique** :
```
SI age < 18 ans :
    → ÉLECTEURS non disponible (message d'erreur)
    → ÉLÈVES disponible
    → ENFANTS disponible

SI age >= 18 ans :
    → ÉLECTEURS disponible
    → ÉLÈVES non disponible (sauf cas exceptionnel)
    → ENFANTS non disponible

SI strate ÉLÈVES sélectionnée :
    → Vérification : établissement scolaire existe ?
    → Vérification : niveau scolaire valide ?

SI strate PNC/FARDC sélectionnée :
    → Vérification : matricule unique ?
    → Vérification : grade valide ?
```

#### **3.3 Enregistrement de la Sélection**

```
L'utilisateur sélectionne une ou plusieurs strates → Clic "Continuer"
   ↓
Système enregistre dans enrollment_sessions.payload :
{
  "core": { /* 27 variables */ },
  "strata": ["ELEVES", "ELECTEURS"],  // Liste des strates sélectionnées
  "extensions": {}  // Vide pour le moment
}
   ↓
Session mise à jour : status = "PROCESSING"
```

---

### 2.4 Phase 4 : COLLECTE DES DONNÉES PAR STRATE (Extensions)

C'est ici que le système devient **dynamique** selon les strates sélectionnées.

#### **4.1 Affichage Dynamique des Formulaires**

Le frontend **charge dynamiquement** les formulaires d'extension selon les strates sélectionnées :

```
POUR CHAQUE strate dans strata :
    SI strate == "ELEVES" :
        Afficher formulaire ext_eleves :
        - Matricule scolaire
        - Établissement
        - Code établissement
        - Niveau
        - Cycle
        - Année scolaire
        - Section
        - Statut scolaire
        - Responsable/Tuteur
        - Contact tuteur
        - Lien tuteur
    
    SI strate == "ETUDIANTS" :
        Afficher formulaire ext_etudiants :
        - Matricule universitaire
        - Université
        - Code université
        - Faculté
        - Département/Filière
        - Niveau (L1, L2, L3, M1, M2, D1, D2, D3)
        - Année académique
        - Statut académique
        - Résidence universitaire
    
    SI strate == "ELECTEURS" :
        Afficher formulaire ext_electeurs :
        - Centre de vote
        - Code centre de vote
        - Circonscription
        - Secteur de vote
        - Statut inscription CENI
        - Date inscription
        - Bureau de vote
    
    SI strate == "PNC" :
        Afficher formulaire ext_pnc :
        - Matricule PNC
        - Grade
        - Unité
        - Fonction
        - Date intégration
        - Statut service
        - Zone affectation
        - Type arme
    
    SI strate == "FARDC" :
        Afficher formulaire ext_fardc :
        - Matricule FARDC
        - Grade
        - Unité affectation
        - Zone opération
        - Fonction
        - Date intégration
        - Statut militaire
        - Type mission
    
    SI strate == "PRISONNIERS" :
        Afficher formulaire ext_prison :
        - Numéro dossier judiciaire
        - Centre détention
        - Statut détention
        - Date incarcération
        - Date libération prévue
        - Infraction
        - Autorité judiciaire
    
    SI strate == "REFUGIES" :
        Afficher formulaire ext_refugies :
        - Numéro HCR
        - Pays origine
        - Statut juridique
        - Document séjour
        - Date entrée territoire
        - Camp réfugié
        - Organisme encadrement
    
    SI strate == "ENFANTS" :
        Afficher formulaire ext_enfants :
        - Tuteur nom
        - Tuteur NIN (si enregistré)
        - Lien tuteur
        - Adresse tuteur
        - Document parentalité
        - Autorisation parentale
        - Structure accueil
    
    SI strate == "FONCTIONNAIRES" :
        Afficher formulaire ext_fonctionnaires :
        - Matricule fonctionnaire
        - Ministère affectation
        - Service affectation
        - Poste/Fonction
        - Date recrutement
        - Statut service
        - Salaire brut
```

#### **4.2 Validation par Strate**

Chaque formulaire d'extension a ses **propres règles de validation** :

```
POUR CHAQUE extension collectée :

    SI strate == "ELEVES" :
        Vérifier :
        - Matricule scolaire unique dans l'établissement
        - Code établissement existe dans répertoire MENPS
        - Niveau correspond à l'âge
        - Tuteur obligatoire si mineur
    
    SI strate == "ETUDIANTS" :
        Vérifier :
        - Matricule universitaire unique
        - Code université existe
        - Niveau académique cohérent avec l'âge
    
    SI strate == "ELECTEURS" :
        Vérifier :
        - Âge >= 18 ans (OBLIGATOIRE)
        - Centre de vote existe dans répertoire CENI
        - Pas déjà inscrit ailleurs
    
    SI strate == "PNC" :
        Vérifier :
        - Matricule PNC unique dans le système
        - Grade valide selon hiérarchie PNC
        - Unité existe
    
    SI strate == "FARDC" :
        Vérifier :
        - Matricule FARDC unique
        - Grade valide selon hiérarchie militaire
        - Unité affectation existe
    
    SI strate == "PRISONNIERS" :
        Vérifier :
        - Numéro dossier judiciaire unique
        - Centre détention existe
        - Statut détention valide
```

#### **4.3 Sauvegarde des Extensions**

```
POUR CHAQUE extension validée :
    Ajouter dans enrollment_sessions.payload.extensions :
    {
      "ELEVES": {
        "matricule_scolaire": "...",
        "etablissement": "...",
        ...
      },
      "ELECTEURS": {
        "centre_vote": "...",
        ...
      }
    }
```

---

### 2.5 Phase 5 : Collecte Biométrique

Indépendamment des strates, la collecte biométrique suit un processus standard :

```
1. Photo faciale
   - Capture via caméra
   - Vérification qualité (>= 0.7)
   - Stockage temporaire
   
2. Empreintes digitales (10 doigts)
   - Capture via scanner
   - Vérification qualité (>= 0.7)
   - Génération du template
   - Stockage temporaire
   
3. Iris (optionnel selon équipement)
   - Capture via lecteur iris
   - Vérification qualité (>= 0.8)
   - Génération du template
   - Stockage temporaire
   
4. Signature
   - Capture via tablette
   - Stockage image
   
Données biométriques ajoutées au payload :
{
  "biometric": {
    "photo": {...},
    "fingerprints": {...},
    "iris": {...},
    "signature": {...}
  }
}
```

---

### 2.6 Phase 6 : Documents et Pièces Justificatives

```
1. Scanner les documents présentés :
   - Acte de naissance
   - Carte d'identité (si existe)
   - Autres documents selon strate
   
2. OCR (Reconnaissance optique) :
   - Extraction des données
   - Vérification cohérence avec données saisies
   
3. Stockage :
   - Upload vers stockage sécurisé (S3/MinIO)
   - Hash SHA-256 calculé
   - URI stockée dans payload
   
Documents ajoutés au payload :
{
  "documents": [
    {
      "type": "acte_naissance",
      "uri": "s3://...",
      "hash": "...",
      ...
    }
  ]
}
```

---

### 2.7 Phase 7 : Validation Complète et Déduplication ABIS

#### **7.1 Validation des Données**

```
1. Validation du Noyau FGP (27 variables) :
   ✓ Format NIN si déjà attribué
   ✓ Cohérence dates (naissance < aujourd'hui)
   ✓ Âge minimum/maximum
   ✓ Champs obligatoires présents
   
2. Validation des Extensions par Strate :
   
   POUR CHAQUE strate dans strata :
       Appeler Extensions Service :
       POST /api/v1/extensions/validate/{strate_code}
       {
         "core_data": {...},
         "extension_data": {...}
       }
       
       Réponse :
       {
         "valid": true/false,
         "errors": [...],
         "warnings": [...]
       }
   
3. Validation Biométrique :
   ✓ Qualité minimale atteinte
   ✓ Tous les types requis capturés
   
4. Validation Documents :
   ✓ Documents requis présents selon strate
   ✓ Hash vérifié
```

#### **7.2 Déduplication Biométrique (ABIS)**

```
1. Extraction des gabarits biométriques du payload
   ↓
2. Appel ABIS Service :
   POST /api/v1/abis/search
   {
     "fingerprints": {...},
     "face": {...},
     "iris": {...}
   }
   ↓
3. ABIS effectue recherche 1:N dans la base :
   - Compare avec tous les gabarits existants
   - Calcule scores de similarité
   - Applique seuils de décision
   ↓
4. Résultats possibles :
   
   CAS A : NO_HIT (score < seuil)
      → Aucune correspondance trouvée
      → Enrôlement peut continuer
      → Nouvelle personne confirmée
   
   CAS B : HIT (score >= seuil)
      → Correspondance trouvée avec personne existante
      → Enrôlement BLOQUÉ
      → Workflow de révision déclenché
      → Opérateur doit vérifier manuellement
      → Décision : REJET ou APPROBATION (doublon légitime)
   
   CAS C : REVIEW (score proche du seuil)
      → Correspondance incertaine
      → Enrôlement EN ATTENTE
      → Révision manuelle obligatoire
      → Expert biométrique doit décider
   ↓
5. Enregistrement dans abis_matches :
   - candidatePersonId (sera le NIN si approuvé)
   - matchedPersonId (si correspondance)
   - similarityScore
   - decision
   - reviewStatus
```

**Critique** : La déduplication se fait **AVANT** la création en base pour éviter les doublons.

---

### 2.8 Phase 8 : Génération du NIN et Création en Base

#### **8.1 Génération du NIN (Numéro d'Identification Nationale)**

**Format** : `CD-YYYY-NNNN-NNNNNNNNN`

```
SI déduplication = NO_HIT :
    1. Récupérer le compteur pour l'année en cours
    2. Générer NIN :
       - CD = Code pays (RDC)
       - YYYY = Année en cours (2025)
       - NNNN = Série (selon province/zone)
       - NNNNNNNNN = Numéro séquentiel unique
    3. Vérifier unicité dans la base
    4. Si collision, réessayer avec numéro suivant
    
    Exemple : CD-2025-0001-000000123
```

#### **8.2 Création en Base de Données**

**Transaction atomique** - Tout ou rien :

```
BEGIN TRANSACTION;

1. Créer fgp_person_core :
   INSERT INTO fgp_person_core (
     nin, nom, prenom, date_naissance, ...
   ) VALUES (...)
   
2. Créer fgp_biometric :
   INSERT INTO fgp_biometric (
     nin, photo_uri, fingerprints_uri, ...
   ) VALUES (...)
   
3. Créer fgp_strata_membership pour CHAQUE strate :
   
   POUR CHAQUE strate dans strata :
       INSERT INTO fgp_strata_membership (
         nin, strate_code, valid_from, status
       ) VALUES (
         nin, 'ELEVES', CURRENT_DATE, 'ACTIVE'
       )
   
4. Créer les extensions selon les strates :
   
   SI strate == "ELEVES" :
       INSERT INTO ext_eleves (
         nin, matricule_scolaire, etablissement, ...
       ) VALUES (...)
   
   SI strate == "ELECTEURS" :
       INSERT INTO ext_electeurs (
         nin, centre_vote, code_centre_vote, ...
       ) VALUES (...)
   
   SI strate == "PNC" :
       INSERT INTO ext_pnc (
         nin, matricule_pnc, grade, ...
       ) VALUES (...)
   
   [... pour chaque strate sélectionnée ...]
   
5. Créer fgp_documents :
   
   POUR CHAQUE document :
       INSERT INTO fgp_documents (
         nin, document_type, document_uri, ...
       ) VALUES (...)
   
6. Enregistrer audit trail :
   INSERT INTO fgp_audit_trail (
     nin, action, table_name, new_values, ...
   ) VALUES ('CREATE', 'fgp_person_core', ...)

COMMIT;  // Si toutes les opérations réussissent
ROLLBACK; // Si une seule opération échoue
```

**Important** : Si une seule opération échoue, toute la transaction est annulée pour garantir la cohérence.

---

### 2.9 Phase 9 : Intégrations Externes par Strate

Après la création en base, le système peut notifier les systèmes externes selon les strates :

```
POUR CHAQUE strate dans strata :
    
    SI strate == "ELEVES" :
        Appeler API MENPS (Ministère Éducation) :
        POST /api/v1/menps/enroll
        {
          "nin": "...",
          "matricule_scolaire": "...",
          ...
        }
        → Synchronisation avec registre éducatif
        
    SI strate == "ELECTEURS" :
        Appeler API CENI (Commission Électorale) :
        POST /api/v1/ceni/enroll
        {
          "nin": "...",
          "centre_vote": "...",
          ...
        }
        → Inscription sur liste électorale
        
    SI strate == "PNC" :
        Appeler API PNC :
        POST /api/v1/pnc/enroll
        {
          "nin": "...",
          "matricule_pnc": "...",
          ...
        }
        → Synchronisation registre police
        
    SI strate == "FARDC" :
        Appeler API FARDC :
        POST /api/v1/fardc/enroll
        {
          "nin": "...",
          "matricule_fardc": "...",
          ...
        }
        → Synchronisation registre militaire
        
    SI strate == "REFUGIES" :
        Appeler API HCR :
        POST /api/v1/hcr/enroll
        {
          "nin": "...",
          "numero_hcr": "...",
          ...
        }
        → Synchronisation registre HCR
```

**Note** : Ces intégrations peuvent être asynchrones (queue de messages) pour ne pas bloquer l'enrôlement.

---

### 2.10 Phase 10 : Génération du Récépissé et Finalisation

```
1. Génération du récépissé d'enrôlement :
   - Format PDF
   - Contient : NIN, nom, photo, date enrôlement
   - QR Code avec données chiffrées
   - Signature numérique ONIP
   
2. Mise à jour de la session :
   UPDATE enrollment_sessions
   SET status = 'COMPLETED',
       nin = 'CD-2025-0001-000000123',
       completed_at = NOW(),
       progress_percentage = 100
   WHERE session_id = ...
   
3. Enregistrement du récépissé :
   INSERT INTO enrollment_receipts (
     session_id, nin, receipt_pdf_url, qr_code_data
   ) VALUES (...)
   
4. Notification :
   - SMS envoyé au téléphone (si fourni)
   - Email envoyé (si fourni)
   - Récépissé disponible en téléchargement
   
5. Log événement :
   INSERT INTO enrollment_events (
     session_id, event_type, message
   ) VALUES (
     '...', 'ENROLLMENT_COMPLETED', 'Enrôlement réussi'
   )
```

---

## 3. MÉCANISMES AVANCÉS DE STRATIFICATION

### 3.1 Appartenance Multiple aux Strates

**Exemple concret** : Une personne est à la fois ÉLÈVE et ÉLECTEUR.

```
1. Lors de l'enrôlement initial :
   - Strates sélectionnées : ["ELEVES", "ELECTEURS"]
   - Création de 2 entrées dans fgp_strata_membership :
     
     INSERT INTO fgp_strata_membership (nin, strate_code, ...)
     VALUES 
       ('CD-2025-0001-000000123', 'ELEVES', ...),
       ('CD-2025-0001-000000123', 'ELECTEURS', ...)
   
   - Création de 2 extensions :
     - ext_eleves (avec données scolaires)
     - ext_electeurs (avec données électorales)

2. Plus tard, la personne devient ÉTUDIANT :
   - Mise à jour via nouvelle session d'enrôlement
   - Ajout d'une nouvelle strate :
     INSERT INTO fgp_strata_membership (nin, strate_code, ...)
     VALUES ('CD-2025-0001-000000123', 'ETUDIANTS', ...)
   
   - La personne garde ses strates précédentes :
     - Toujours ÉLECTEUR (valid_from ancienne date)
     - Plus ÉLÈVE (valid_to = date d'inscription université)
     - Nouvellement ÉTUDIANT (valid_from = date inscription)
```

### 3.2 Gestion Temporelle des Strates

**Validité dans le temps** :

```
fgp_strata_membership :
- valid_from : Date de début de validité
- valid_to : Date de fin de validité (NULL = toujours valide)
- status : ACTIVE, INACTIVE, SUSPENDED

Exemple :
- Un ÉLÈVE finit ses études secondaires → valid_to = date de fin
- Un MILITAIRE prend sa retraite → valid_to = date retraite
- Un PRISONNIER est libéré → valid_to = date libération
```

### 3.3 Règles de Validation Inter-Strates

Certaines strates ont des règles de cohérence entre elles :

```
RÈGLE 1 : ÉLÈVES vs ÉTUDIANT
    → Une personne ne peut pas être ÉLÈVE et ÉTUDIANT simultanément
    → Vérification automatique lors de l'enrôlement
    
RÈGLE 2 : ENFANTS vs ÉLÈVES
    → Un ENFANT peut être aussi ÉLÈVE (scolarisé)
    → Un ENFANT peut être non-ÉLÈVE (non scolarisé)
    
RÈGLE 3 : ÉLECTEURS
    → Minimum 18 ans OBLIGATOIRE
    → Vérification automatique : date_naissance + 18 <= aujourd'hui
    
RÈGLE 4 : PNC vs FARDC
    → Une personne ne peut pas être PNC et FARDC simultanément
    → Règle métier : appartenance exclusive
```

---

## 4. ARCHITECTURE TECHNIQUE DE LA STRATIFICATION

### 4.1 Frontend Dynamique (Next.js)

Le frontend charge dynamiquement les formulaires selon les strates :

```typescript
// Frontend : Dynamic Form Loading
const StratifiedEnrollmentForm = () => {
  const [selectedStrata, setSelectedStrata] = useState<string[]>([]);
  const [extensionForms, setExtensionForms] = useState<Record<string, any>>({});
  
  // Quand les strates changent, charger les formulaires correspondants
  useEffect(() => {
    selectedStrata.forEach(strate => {
      // Charger dynamiquement le composant du formulaire
      import(`./extensions/${strate.toLowerCase()}_form.tsx`)
        .then(module => {
          setExtensionForms(prev => ({
            ...prev,
            [strate]: module.default
          }));
        });
    });
  }, [selectedStrata]);
  
  return (
    <>
      <BaseForm /> {/* 27 variables */}
      <StrataSelector onChange={setSelectedStrata} />
      {selectedStrata.map(strate => {
        const FormComponent = extensionForms[strate];
        return FormComponent ? <FormComponent key={strate} /> : null;
      })}
    </>
  );
};
```

### 4.2 Backend : Extensions Service

Le service Extensions gère la validation et la sauvegarde par strate :

```python
# Backend : Extensions Service
class ExtensionsService:
    def validate_extension(self, strate_code: str, core_data: dict, extension_data: dict):
        """Valide les données d'extension selon la strate"""
        
        if strate_code == 'ELEVES':
            validator = ElevesValidator()
            return validator.validate(core_data, extension_data)
            
        elif strate_code == 'ELECTEURS':
            validator = ElecteursValidator()
            return validator.validate(core_data, extension_data)
            
        # ... autres strates
        
    def save_extension(self, nin: str, strate_code: str, extension_data: dict):
        """Sauvegarde l'extension dans la table correspondante"""
        
        if strate_code == 'ELEVES':
            return ElevesExtension.objects.create(
                nin=nin,
                **extension_data
            )
        elif strate_code == 'ELECTEURS':
            return ElecteursExtension.objects.create(
                nin=nin,
                **extension_data
            )
        # ... autres strates
```

### 4.3 Base de Données : Tables d'Extension

Chaque strate a sa propre table d'extension :

```sql
-- Structure type d'une table d'extension
CREATE TABLE ext_{strate_code} (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin),
    -- Champs spécifiques à la strate
    ...
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Avantage** : Isolation des données par secteur, performance optimale, contraintes spécifiques par strate.

---

## 5. WORKFLOW DE MISE À JOUR DES STRATES

### 5.1 Ajout d'une Nouvelle Strate

```
1. Personne déjà enregistrée (NIN existant)
   ↓
2. Nouvelle session d'enrôlement lancée
   ↓
3. Recherche de la personne existante (par NIN ou biométrie)
   ↓
4. Sélection d'une NOUVELLE strate
   ↓
5. Collecte des données d'extension pour cette strate
   ↓
6. Validation et création :
   - INSERT INTO fgp_strata_membership (nouvelle entrée)
   - INSERT INTO ext_{nouvelle_strate}
   - Intégration avec système externe correspondant
```

### 5.2 Modification d'une Strate Existante

```
1. Personne existante avec strate ACTIVE
   ↓
2. Modification des données d'extension
   ↓
3. Mise à jour :
   - UPDATE ext_{strate_code} SET ...
   - UPDATE fgp_strata_membership SET updated_at = NOW()
   ↓
4. Synchronisation avec système externe
```

### 5.3 Désactivation d'une Strate

```
1. Personne sort d'une strate (fin d'études, retraite, etc.)
   ↓
2. Mise à jour :
   UPDATE fgp_strata_membership
   SET valid_to = CURRENT_DATE,
       status = 'INACTIVE'
   WHERE nin = ... AND strate_code = ...
   ↓
3. Les données d'extension restent en base (historique)
4. Notification au système externe (désinscription)
```

---

## 6. PERFORMANCE ET OPTIMISATION

### 6.1 Index sur les Strates

```sql
-- Index pour recherche rapide par strate
CREATE INDEX idx_strata_membership_strate 
ON fgp_strata_membership(strate_code, status)
WHERE status = 'ACTIVE';

-- Index pour recherche personne par strate
CREATE INDEX idx_strata_membership_nin_strate
ON fgp_strata_membership(nin, strate_code);
```

### 6.2 Vues Matérialisées

```sql
-- Vue pour statistiques par strate
CREATE MATERIALIZED VIEW mv_strata_statistics AS
SELECT 
    strate_code,
    COUNT(*) as total_members,
    COUNT(*) FILTER (WHERE status = 'ACTIVE') as active_members,
    COUNT(*) FILTER (WHERE status = 'INACTIVE') as inactive_members
FROM fgp_strata_membership
GROUP BY strate_code;
```

---

## 7. CONCLUSION

La **stratification fonctionnelle** est le mécanisme central qui permet au FGP de :

1. **S'adapter** aux besoins spécifiques de chaque secteur
2. **Évoluer** en ajoutant de nouvelles strates sans refonte
3. **Intégrer** avec les systèmes externes sectoriels
4. **Gérer** les appartenances multiples et temporelles
5. **Garantir** la cohérence des données par secteur

Le système est conçu pour être **extensible** : l'ajout d'une nouvelle strate nécessite uniquement :
- Création d'une table d'extension
- Ajout d'un validateur spécifique
- Ajout d'un formulaire frontend
- Configuration de l'intégration externe

Cette architecture garantit la **pérennité** et l'**évolutivité** du système FGP.

---

**Date de création** : $(date)  
**Version** : 1.0  
**Système** : FGP - Fichier Général de la Population - RDC  
**Conforme à** : OSIA Specification

s