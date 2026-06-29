# 📚 Documentation API - Système FGP

## Vue d'ensemble

Le système FGP expose plusieurs APIs REST pour la gestion de l'identification nationale. Chaque service a sa propre API avec des endpoints spécialisés.

## Services et URLs

| Service | URL | Description |
|---------|-----|-------------|
| FGP Core | http://localhost:8000 | API principale (27 variables) |
| Enrollment Gateway | http://localhost:8001 | API d'enrôlement |
| Extensions Service | http://localhost:8002 | API extensions par strate |
| ABIS Service | http://localhost:8003 | API biométrique |

## Authentification

### JWT Token
Toutes les APIs utilisent l'authentification JWT :

```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Utiliser le token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/core/persons/
```

### Headers requis
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-ONIP-Channel: fixed|mobile|itinerant|school|pnc|fardc|prison|refugee|ceni
X-Schema-Version: 1.0
```

## FGP Core API

### Endpoints Principaux

#### 1. Liste des personnes
```http
GET /api/v1/core/persons/
```

**Paramètres de requête :**
- `search` : Recherche globale (nom, prénom, NIN, téléphone)
- `province_residence` : Filtre par province
- `sexe` : Filtre par sexe (M/F)
- `page` : Numéro de page
- `page_size` : Taille de page (max 100)

**Exemple :**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/core/persons/?search=KABAMBA&province_residence=Kinshasa"
```

#### 2. Créer une personne
```http
POST /api/v1/core/persons/
```

**Payload :**
```json
{
  "nom": "KABAMBA",
  "postnom": "ILUNGA",
  "prenom": "Marie",
  "sexe": "F",
  "date_naissance": "1990-05-15",
  "lieu_naissance": "Kinshasa",
  "province_naissance": "Kinshasa",
  "nationalite": "Congolaise",
  "statut_matrimonial": "Célibataire",
  "nom_pere": "KABAMBA Joseph",
  "nom_mere": "ILUNGA Marie",
  "province_residence": "Kinshasa",
  "territoire_residence": "Funa",
  "commune_residence": "Lemba",
  "quartier_residence": "Lemba",
  "avenue_residence": "Avenue Kasa-Vubu",
  "numero_residence": "123",
  "telephone": "+243123456789",
  "email": "marie.kabamba@email.com",
  "profession": "Ingénieur",
  "niveau_etude": "Universitaire",
  "type_piece_identite": "Acte de naissance",
  "numero_piece_identite": "ACT-2025-001234",
  "date_emission_piece": "2025-01-15",
  "lieu_emission_piece": "Kinshasa"
}
```

#### 3. Obtenir une personne par NIN
```http
GET /api/v1/core/persons/by-nin/{nin}/
```

**Exemple :**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/core/persons/by-nin/CD-2025-0001-123456789/"
```

#### 4. Recherche avancée
```http
GET /api/v1/core/search/
```

**Paramètres :**
- `q` : Terme de recherche
- `province` : Province de résidence
- `sexe` : Sexe
- `age_min` : Âge minimum
- `age_max` : Âge maximum

### Gestion des Strates

#### 1. Lister les strates d'une personne
```http
GET /api/v1/core/strata/by-nin/{nin}/
```

#### 2. Ajouter une strate
```http
POST /api/v1/core/strata/
```

**Payload :**
```json
{
  "nin": "CD-2025-0001-123456789",
  "strate_code": "ELECTEUR",
  "valid_from": "2025-01-01",
  "valid_to": null,
  "status": "ACTIVE"
}
```

### Gestion des Documents

#### 1. Lister les documents d'une personne
```http
GET /api/v1/core/documents/?nin={nin}
```

#### 2. Ajouter un document
```http
POST /api/v1/core/documents/
```

**Payload :**
```json
{
  "nin": "CD-2025-0001-123456789",
  "document_type": "acte_naissance",
  "document_uri": "s3://fgp-documents/acte_123.pdf",
  "file_size": 1024000,
  "mime_type": "application/pdf"
}
```

## Enrollment Gateway API

### Enrôlement Complet

#### 1. Enrôlement principal
```http
POST /api/v1/enrolments/
```

**Headers :**
```http
X-ONIP-Channel: fixed
X-Schema-Version: 1.0
X-Payload-Signature: <JWS>
```

**Payload :**
```json
{
  "core": {
    "nin": null,
    "version": "1.0",
    "data": {
      "nom": "KABAMBA",
      "postnom": "ILUNGA",
      "prenom": "Marie",
      "sexe": "F",
      "date_naissance": "1990-05-15",
      "lieu_naissance": "Kinshasa",
      "province_naissance": "Kinshasa",
      "nationalite": "Congolaise",
      "statut_matrimonial": "Célibataire",
      "nom_pere": "KABAMBA Joseph",
      "nom_mere": "ILUNGA Marie",
      "province_residence": "Kinshasa",
      "territoire_residence": "Funa",
      "commune_residence": "Lemba",
      "quartier_residence": "Lemba",
      "avenue_residence": "Avenue Kasa-Vubu",
      "numero_residence": "123",
      "telephone": "+243123456789",
      "email": "marie.kabamba@email.com",
      "profession": "Ingénieur",
      "niveau_etude": "Universitaire",
      "type_piece_identite": "Acte de naissance",
      "numero_piece_identite": "ACT-2025-001234",
      "date_emission_piece": "2025-01-15",
      "lieu_emission_piece": "Kinshasa"
    }
  },
  "biometrics": {
    "face": {
      "ref": "s3://fgp-biometric/face_123.jpg",
      "quality": 0.85
    },
    "fingerprints": {
      "ref": "s3://fgp-biometric/fp_123.iso",
      "quality": 0.92
    }
  },
  "strata": ["ELECTEUR", "ETUDIANT"],
  "extensions": {
    "education": {
      "matricule_universitaire": "UNIKIN-2025-12345",
      "universite": "Université de Kinshasa",
      "faculte": "Sciences",
      "departement": "Informatique",
      "niveau": "L3",
      "annee_academique": "2024-2025",
      "statut_academique": "régulier"
    },
    "electoral": {
      "centre_vote": "École Kimbondo",
      "code_centre_vote": "CENI-KIN-01234",
      "circonscription": "Kinshasa-Limete",
      "secteur_vote": "LIMETE",
      "statut_inscription": "inscrit",
      "date_inscription_ceni": "2025-01-15"
    }
  },
  "attachments": [
    {
      "type": "acte_naissance",
      "ref": "s3://fgp-documents/acte_123.pdf",
      "hash": "sha256:abc123..."
    }
  ]
}
```

**Réponse :**
```json
{
  "nin": "CD-2025-0001-123456789",
  "status": "ENROLLED",
  "core_persisted": true,
  "extensions_persisted": ["education", "electoral"],
  "abis": {
    "match": false,
    "score": 0.12
  },
  "events": [
    "fgp.core.created",
    "ext.education.created",
    "ext.electoral.created"
  ],
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### 2. Statut d'enrôlement
```http
GET /api/v1/enrolments/{id}/
```

#### 3. Validation préalable
```http
POST /api/v1/enrolments/validate/
```

## Extensions Service API

### Extensions par Strate

#### 1. Extension Élèves
```http
POST /api/v1/extensions/eleves/
```

**Payload :**
```json
{
  "nin": "CD-2025-0001-123456789",
  "matricule_scolaire": "EDU-2025-00000123",
  "etablissement": "École Primaire Saint-Joseph",
  "code_etablissement": "EP-KIN-00012",
  "niveau": "6e Primaire",
  "cycle": "Primaire",
  "annee_scolaire": "2024-2025",
  "section": "Générale",
  "statut_scolaire": "public",
  "responsable_tuteur": "MULAMBA Joseph",
  "contact_tuteur": "+243987654321",
  "lien_tuteur": "Père"
}
```

#### 2. Extension Étudiants
```http
POST /api/v1/extensions/etudiants/
```

#### 3. Extension Électeurs
```http
POST /api/v1/extensions/electeurs/
```

#### 4. Extension PNC
```http
POST /api/v1/extensions/pnc/
```

#### 5. Extension FARDC
```http
POST /api/v1/extensions/fardc/
```

#### 6. Extension Prisonniers
```http
POST /api/v1/extensions/prison/
```

#### 7. Extension Réfugiés
```http
POST /api/v1/extensions/refugies/
```

#### 8. Extension Enfants
```http
POST /api/v1/extensions/enfants/
```

#### 9. Extension Fonctionnaires
```http
POST /api/v1/extensions/fonctionnaires/
```

## ABIS Service API

### Déduplication Biométrique

#### 1. Enrôlement biométrique
```http
POST /api/v1/abis/enroll/
```

**Payload :**
```json
{
  "nin": "CD-2025-0001-123456789",
  "templates": [
    {
      "type": "face",
      "data": "base64_encoded_template",
      "quality": 0.85
    },
    {
      "type": "fingerprint",
      "data": "base64_encoded_template",
      "quality": 0.92
    }
  ]
}
```

#### 2. Recherche 1:N
```http
POST /api/v1/abis/search/
```

**Payload :**
```json
{
  "template_type": "face",
  "template_data": "base64_encoded_template",
  "threshold": 0.8,
  "max_results": 10
}
```

**Réponse :**
```json
{
  "matches": [
    {
      "nin": "CD-2025-0001-123456789",
      "similarity_score": 0.95,
      "decision": "HIT"
    }
  ],
  "total_searched": 1000000,
  "search_time_ms": 150
}
```

#### 3. Correspondances trouvées
```http
GET /api/v1/abis/matches/
```

**Paramètres :**
- `nin_candidate` : NIN de la personne candidate
- `decision` : Décision (HIT/NO_HIT/REVIEW)
- `reviewed` : Filtrer par statut de révision

## Codes de Statut HTTP

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé avec succès |
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Non autorisé |
| 404 | Ressource non trouvée |
| 409 | Conflit (doublon) |
| 422 | Données non valides |
| 500 | Erreur serveur |

## Codes d'Erreur

### Erreurs de Validation
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Les données fournies ne sont pas valides",
  "details": {
    "nom": ["Ce champ est obligatoire"],
    "telephone": ["Format de téléphone invalide"]
  }
}
```

### Erreurs de Doublon
```json
{
  "error": "DUPLICATE_FOUND",
  "message": "Une personne avec ces données existe déjà",
  "nin_existing": "CD-2025-0001-123456789",
  "similarity_score": 0.95
}
```

### Erreurs d'ABIS
```json
{
  "error": "ABIS_ERROR",
  "message": "Erreur lors de la déduplication biométrique",
  "code": "TEMPLATE_QUALITY_TOO_LOW",
  "details": "La qualité du gabarit est insuffisante (0.65 < 0.7)"
}
```

## Pagination

Toutes les listes supportent la pagination :

```json
{
  "count": 1250,
  "next": "http://localhost:8000/api/v1/core/persons/?page=3",
  "previous": "http://localhost:8000/api/v1/core/persons/?page=1",
  "results": [...]
}
```

## Filtrage et Recherche

### Opérateurs de filtrage
- `exact` : Correspondance exacte
- `icontains` : Contient (insensible à la casse)
- `in` : Dans une liste de valeurs
- `range` : Entre deux valeurs
- `date` : Filtre par date
- `isnull` : Valeur nulle ou non nulle

### Exemples de filtres
```bash
# Recherche par nom
GET /api/v1/core/persons/?nom__icontains=KABAMBA

# Filtre par province et sexe
GET /api/v1/core/persons/?province_residence=Kinshasa&sexe=F

# Filtre par date de naissance
GET /api/v1/core/persons/?date_naissance__year=1990

# Filtre par âge
GET /api/v1/core/persons/?date_naissance__gte=1990-01-01&date_naissance__lte=2000-12-31
```

## Rate Limiting

Les APIs sont protégées par un rate limiting :

- **API générale** : 60 requêtes/minute
- **API d'enrôlement** : 10 requêtes/minute
- **API ABIS** : 5 requêtes/minute
- **API d'authentification** : 5 requêtes/minute

## Webhooks

Le système supporte les webhooks pour notifier les systèmes externes :

```json
{
  "event": "person.created",
  "data": {
    "nin": "CD-2025-0001-123456789",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "webhook_url": "https://external-system.com/webhook"
}
```

## Documentation Interactive

- **Swagger UI** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/
- **Schema OpenAPI** : http://localhost:8000/api/schema/
