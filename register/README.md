# 🏛️ FGP - Fichier Général de la Population
## Système National d'Identification - RDC

### 📋 Vue d'ensemble
Système d'identification unifié pour la République Démocratique du Congo, conforme au décret portant création du Fichier Général de la Population (FGP).

### 🎯 Objectifs
- **Identification unique** : 27 variables de base (noyau FGP)
- **Stratification fonctionnelle** : Extensions par secteur (éducation, sécurité, justice, etc.)
- **Logiciel d'enrôlement** : Modulable selon la strate sélectionnée
- **Interopérabilité sécurisée** : APIs, PKI, gouvernance centralisée

### 🏗️ Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   Next.js       │◄──►│   Django        │◄──►│   PostgreSQL    │
│   (Enrollment)  │    │   (Microservices)│    │   (FGP Core)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docker        │    │   ABIS Service  │    │   Extensions    │
│   Container     │    │   (Biometric)   │    │   (By Strate)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 📁 Structure du Projet
```
fgp/
├── backend/                 # Services Django
│   ├── fgp_core/           # Service FGP Core (27 variables)
│   ├── enrollment_gateway/ # API d'ingestion
│   ├── extensions/         # Services par strate
│   ├── abis_service/       # Service biométrique
│   └── shared/             # Utilitaires communs
├── frontend/               # Application Next.js
├── database/               # Schémas et migrations
├── docker/                 # Configuration Docker
├── docs/                   # Documentation
└── scripts/                # Scripts d'initialisation
```

### 🚀 Démarrage Rapide
```bash
# Cloner et configurer
git clone <repository>
cd fgp

# Démarrer avec Docker
docker-compose up -d

# Accéder à l'application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Admin Django: http://localhost:8000/admin
```

### 📊 Strates Supportées
- **ÉLÈVES** : Enfants scolarisés (primaire/secondaire)
- **ÉTUDIANTS** : Apprenants du supérieur
- **ÉLECTEURS** : Citoyens en âge de voter
- **PNC** : Police Nationale Congolaise
- **FARDC** : Forces Armées
- **PRISONNIERS** : Personnes incarcérées
- **RÉFUGIÉS** : Personnes reconnues par HCR
- **ENFANTS** : Mineurs non scolarisés
- **FONCTIONNAIRES** : Agents de l'État

### 🔐 Sécurité
- **PKI ONIP** : Signatures JWS
- **Chiffrement** : AES-256 au repos, TLS 1.3 en transit
- **RBAC/ABAC** : Contrôle d'accès par rôle
- **Audit Trail** : Journalisation inviolable

### 📚 Documentation
- [Architecture Technique](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Schéma Base de Données](docs/database.md)
- [Guide de Déploiement](docs/deployment.md)
