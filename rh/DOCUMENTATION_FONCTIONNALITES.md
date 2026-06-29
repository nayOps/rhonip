# 📚 Documentation Complète des Fonctionnalités - Payday ONIP

## 🎯 Vue d'ensemble

**Payday ONIP** est un système de gestion des ressources humaines (SGRH) complet développé en Django. Il permet de gérer les employés, les congés, les missions, les formations, et bien plus encore.

---

## 🏗️ Architecture du Système

### Applications Django

1. **`core`** - Module central avec fonctionnalités génériques
2. **`employee`** - Gestion des employés
3. **`leave`** - Gestion des congés
4. **`mission`** - Gestion des missions
5. **`training`** - Gestion des formations
6. **`api`** - API REST pour intégrations

---

## 📦 MODULE CORE - Fonctionnalités Génériques

### 1. **Système d'Authentification et Utilisateurs**

#### Modèle User (`core/models/user.py`)
- **Identifiant** : Email (pas de username)
- **Liaison** : Chaque utilisateur peut être lié à un employé
- **Permissions** : Système de permissions Django standard
- **Fonctionnalités** :
  - Connexion par email
  - Gestion des permissions
  - Association avec un employé

### 2. **Système d'Approbation (Approbation)**

#### Modèle Approbation (`core/models/approbation.py`)
- **Fonction** : Système générique d'approbation pour n'importe quel modèle
- **Utilisation** : Utilise GenericForeignKey pour lier à n'importe quel objet
- **Actions** :
  - `APPROVED` - Approuvé
  - `REJECTED` - Rejeté
- **Fonctionnalités** :
  - Commentaires d'approbation
  - Traçabilité (qui a approuvé/rejeté)
  - URL : `/approbation/<action>/<app>/<model>/<pk>`

### 3. **Système de Flux de Travail (Flow)**

#### Modèles Flow et FlowStep (`core/models/flow.py`)
- **Flow** : Définit un flux d'approbation pour un type de contenu
- **FlowStep** : Étapes du flux avec hiérarchie (parent/enfant)
- **Fonctionnalités** :
  - Flux personnalisables par type de contenu
  - Étapes hiérarchiques
  - Attribution d'utilisateurs par étape
  - URL : `/flow/<pk>`

### 4. **Système de Templates de Documents**

#### Modèle Template (`core/models/template.py`)
- **Fonction** : Création de modèles de documents réutilisables
- **Fonctionnalités** :
  - Contenu HTML riche (TinyMCE)
  - Association à un type de contenu
  - Génération de documents PDF/Word
  - URL : `/template/<pk>`

### 5. **Système de Widgets Personnalisables**

#### Modèle Widget (`core/models/widget.py`)
- **Fonction** : Widgets dynamiques pour le tableau de bord
- **Fonctionnalités** :
  - Template HTML personnalisable
  - Code Python pour la logique (exécuté dynamiquement)
  - Filtrage par permissions
  - Affichage sur la page d'accueil selon les permissions

### 6. **Système d'Import de Données**

#### Modèle Importer (`core/models/importer.py`)
- **Fonction** : Import en masse depuis fichiers Excel
- **Statuts** :
  - `PENDING` - En attente
  - `PROCESSING` - En cours
  - `SUCCESS` - Succès
  - `ERROR` - Erreur
- **Fonctionnalités** :
  - Import asynchrone via Celery
  - Notifications automatiques
  - Support de modèles Excel
  - Traitement en arrière-plan

### 7. **Système de Jobs Planifiés**

#### Modèle Job (`core/models/job.py`)
- **Fonction** : Exécution de tâches Python planifiées
- **Fréquences** : Quotidienne (DAILY)
- **Fonctionnalités** :
  - Code Python exécuté via Celery
  - Exécution quotidienne automatique
  - Gestion des erreurs

### 8. **Vues Génériques CRUD**

#### Vues disponibles (`core/views/`)
- **List** : Liste générique de tous les modèles
  - URL : `/list/<app>/<model>`
- **Create** : Création générique
  - URL : `/create/<app>/<model>`
- **Read** : Lecture/affichage
  - URL : `/read/<app>/<model>/<pk>`
- **Change** : Modification
  - URL : `/change/<app>/<model>/<pk>`
- **Delete** : Suppression
  - URL : `/delete/<app>/<model>/<pk>`

#### Vues Modales
- Versions modales de toutes les vues CRUD
- URL : `/modal/list|create|change|delete/<app>/<model>/<pk>`

### 9. **Système de Notifications**

- Intégration avec `django-notifications-hq`
- Notifications en temps réel
- URL : `/notifications` et `/notification/<pk>`

### 10. **Système d'Impression**

- Génération de documents imprimables
- URL : `/print/<app>/<model>/<pk>`

### 11. **Actions Requises**

- Vue centralisée des actions en attente
- URL : `/action/required`

---

## 👥 MODULE EMPLOYEE - Gestion des Employés

### 1. **Modèle Employee Principal**

#### Informations de Base
- **Matricule** : Numéro d'enregistrement unique
- **Numéro de sécurité sociale**
- **Photo** : Photo de profil
- **Type de contrat** : Liaison avec Agreement
- **Date d'engagement**

#### Structure Organisationnelle
- **Direction** : Direction de l'employé
- **Sous-direction** : Sous-direction
- **Service** : Service
- **Site/Branche** : Localisation
- **Position/Designation** : Poste occupé
- **Grade** : Niveau hiérarchique

#### Informations Personnelles
- **Nom complet** : Prénom, Post-nom, Nom
- **Genre** : Masculin/Féminin
- **Date et lieu de naissance**
- **Nationalité et origine** : Pays, province, territoire, secteur, village
- **Pièce d'identité** : Type, numéro, dates de délivrance/expiration
- **État civil** : Marié/Célibataire
- **Conjoint** : Nom du conjoint

#### Informations de Contact
- **Téléphone professionnel**
- **Téléphone mobile**
- **Email professionnel**
- **Email personnel**
- **Adresse physique**
- **Contact d'urgence** : Nom, téléphone, relation
- **Médecin référent** : Nom, téléphone, email

#### Informations de Paiement
- **Mode de paiement** : Cash, Banque, Mobile Money
- **Numéro de compte**
- **Nom du payeur**

#### Informations Professionnelles
- **Lettre de nomination** : Fichier PDF
- **Numéro d'acte de nomination**
- **Statut** : Liaison avec Status
- **Commentaires**

#### Fonctionnalités Spéciales
- **Création automatique d'utilisateur** : `create_user()` si email existe
- **Calcul de présence** : `attendances(period)`
- **Inlines** : Enfants, Éducation, Expérience, Documents

### 2. **Modèles Associés**

#### Child (Enfants)
- Nom complet
- Date de naissance
- Métadonnées

#### Education (Formation)
- Institution
- Diplôme/Degré
- Liaison avec employé

#### Experience (Expérience Professionnelle)
- Historique des emplois précédents

#### Document (Documents)
- Documents liés à l'employé
- Upload de fichiers

#### Attendance (Présence)
- **Direction** : IN (entrée) / OUT (sortie)
- **Date et heure** : Enregistrement précis
- **Unique** : Un employé ne peut avoir qu'une entrée et une sortie par jour
- **Fonctionnalités** :
  - Suivi des présences
  - Calcul automatique des heures
  - Export JSON

#### Overtime (Heures Supplémentaires)
- **Employé**
- **Date**
- **Heures** : De/À
- **Motif**
- **Approbateurs** : Système d'approbation

#### RequestForInfo (Demande d'Information)
- **Nom et description**
- **Destinataires** : Liste d'utilisateurs
- **Réponses** : Via ReplyWithInfo
- **Fonctionnalités** :
  - Demande d'informations à plusieurs utilisateurs
  - Système de réponses avec documents

### 3. **Modèles de Configuration**

#### Designation (Position)
- Nom du poste

#### Agreement (Type de Contrat)
- Types de contrats (CDI, CDD, etc.)

#### Grade (Grade)
- Niveaux hiérarchiques

#### Status (Statut)
- Statuts des employés (Actif, Inactif, etc.)

#### Branch (Site/Branche)
- Sites de l'organisation

#### Direction, SubDirection, Service
- Structure organisationnelle hiérarchique

---

## 🏖️ MODULE LEAVE - Gestion des Congés

### 1. **Modèle Leave (Congé)**

#### Informations Principales
- **Type de congé** : Liaison avec TypeOfLeave
- **Employé** : Qui demande le congé
- **Remplaçant (Interim)** : Qui remplace pendant le congé
- **Dates** : Du/Au
- **Motif** : Raison du congé

#### Fonctionnalités Automatiques
- **Calcul des jours** : `days` property
- **Jours pris** : `taken` property (total pour l'employé)
- **Jours disponibles** : `available_days` property
- **Validation** : Vérifie que les jours demandés ne dépassent pas les jours disponibles

#### Types de Congés
- Configurables via TypeOfLeave
- Chaque type a un nombre maximum de jours par an

### 2. **Modèle EarlyLeave (Départ Anticipé)**

#### Informations
- **Employé**
- **Destination**
- **Date**
- **Heures** : De/À
- **Motif**
- **Observation**

#### Validation
- Vérifie l'heure de début minimale (configurable via Preference)

### 3. **Modèle Holiday (Jours Fériés)**

- Gestion des jours fériés
- Dates fixes ou récurrentes

### 4. **Modèle TypeOfLeave (Type de Congé)**

- **Nom** : Type de congé (Annuel, Maladie, Maternité, etc.)
- **Jours maximum par an** : Limite annuelle

---

## 🚀 MODULE MISSION - Gestion des Missions

### 1. **Modèle Mission**

#### Informations Principales
- **Nom** : Titre de la mission
- **Description** : Détails
- **Destination** : Lieu de la mission
- **Employés** : Liste des employés en mission (plusieurs)
- **Dates** : Date de début et de fin

#### Validations
- Date de début < Date de fin
- Vérifie que les employés n'ont pas de rapports non remplis

### 2. **Modèle Report (Rapport de Mission)**

#### Informations
- **Mission** : Liaison avec Mission
- **Employé** : Qui fait le rapport
- **Document** : Fichier du rapport (PDF, Word, etc.)

#### Fonctionnalités
- Un rapport par employé par mission
- Upload de documents
- Validation avant création de nouvelle mission

---

## 📚 MODULE TRAINING - Gestion des Formations

### 1. **Modèle Training**

#### Informations
- **Nom** : Titre de la formation
- **Description** : Contenu
- **Lieu** : Où se déroule la formation
- **Formateur** : Nom du formateur
- **Dates** : Date de début et de fin
- **Certificat** : Booléen (certificat délivré ?)
- **Terminé** : Booléen (formation achevée ?)

---

## 🔌 MODULE API - API REST

### Endpoints Disponibles

#### 1. **Liste** - `GET /api/list/<app>/<model>`
- Retourne la liste de tous les objets d'un modèle
- Format JSON

#### 2. **Création** - `POST /api/create/<app>/<model>`
- Crée un nouvel objet
- Retourne l'objet créé

#### 3. **Détail** - `GET /api/detail/<app>/<model>/<pk>`
- Retourne les détails d'un objet
- **PUT** : Modification
- **DELETE** : Suppression

#### 4. **Autocomplete** - `GET /api/autocomplete/<app>/<model>/<to_field>`
- Recherche autocomplete pour les champs de sélection
- Utilisé par les formulaires

### Sérialisation
- Sérialisation automatique de tous les modèles
- Support des relations (depth configurable)
- Format JSON standardisé

---

## 🔧 Fonctionnalités Techniques Avancées

### 1. **Système de Permissions Granulaires**

- Filtrage automatique des données selon les permissions
- QuerySet personnalisé dans `core/models/managers/base.py`
- Les utilisateurs ne voient que leurs données (sauf superuser/staff)

### 2. **Traçabilité Complète**

- **created_by** : Qui a créé
- **updated_by** : Qui a modifié
- **created_at** : Date de création
- **updated_at** : Date de modification
- **metadata** : Champs JSON pour données supplémentaires

### 3. **Système de Champs Personnalisés**

- **ModelSelect** : Sélection de modèles avec autocomplete
- **DateField** : Champ date personnalisé
- **TimeField** : Champ heure
- **JSONField** : Stockage JSON
- **AceField** : Éditeur de code (Python, HTML)

### 4. **Tâches Asynchrones (Celery)**

- **Import de données** : Traitement en arrière-plan
- **Jobs quotidiens** : Exécution automatique
- **Notifications** : Envoi asynchrone

### 5. **Système de Notifications**

- Notifications en temps réel
- Notifications par email (si configuré)
- Notifications dans l'interface

### 6. **Génération de Documents**

- Templates HTML → PDF/Word
- Utilisation de TinyMCE pour l'édition
- Variables dynamiques dans les templates

---

## 📊 Workflows et Processus Métier

### 1. **Workflow de Congé**

1. Employé crée une demande de congé
2. Système vérifie les jours disponibles
3. Demande soumise pour approbation
4. Approbation via Flow (si configuré)
5. Notification à l'employé
6. Remplaçant assigné (optionnel)

### 2. **Workflow de Mission**

1. Création de mission avec employés
2. Vérification des rapports non remplis
3. Assignation des employés
4. Création de rapports par employé
5. Upload des documents de rapport

### 3. **Workflow d'Import**

1. Upload d'un fichier Excel
2. Sélection du modèle cible
3. Tâche Celery créée
4. Traitement en arrière-plan
5. Notification de succès/erreur

### 4. **Workflow d'Approbation**

1. Objet créé (congé, heures sup, etc.)
2. Flow associé au type de contenu
3. Étapes d'approbation séquentielles
4. Notifications aux approbateurs
5. Action finale (approuvé/rejeté)

---

## 🎨 Interface Utilisateur

### 1. **Page d'Accueil**

- Widgets personnalisables selon permissions
- Dashboard dynamique
- Actions rapides

### 2. **Listes**

- Filtres configurables
- Recherche
- Tri
- Pagination

### 3. **Formulaires**

- Layouts personnalisables (Crispy Forms)
- Champs avec autocomplete
- Validation en temps réel
- Modales pour actions rapides

### 4. **Responsive Design**

- Bootstrap 5
- Interface mobile-friendly

---

## 🔐 Sécurité

### 1. **Authentification**

- Email comme identifiant
- Mots de passe hashés (Django)
- Support LDAP (optionnel)

### 2. **Autorisations**

- Permissions Django standard
- Filtrage automatique des données
- Protection CSRF

### 3. **Production**

- HTTPS forcé
- Headers de sécurité
- CORS configurable
- Sentry pour monitoring

---

## 📈 Intégrations

### 1. **Celery + Redis**

- Tâches asynchrones
- Jobs planifiés
- Queue de traitement

### 2. **PostgreSQL**

- Base de données principale
- Support SQLite en développement

### 3. **Storage**

- Support fichiers locaux
- Support AWS S3 (optionnel)

### 4. **Email**

- Console backend en développement
- SMTP en production

### 5. **Keycloak** (Optionnel)

- SSO
- Authentification centralisée

---

## 🚀 Déploiement

### Docker Compose

- **Services** :
  - PostgreSQL (base de données)
  - Redis (cache/broker)
  - Server (Django + Gunicorn)
  - Worker (Celery)

### Variables d'Environnement

- Configuration via `.env`
- Support multi-environnements

---

## 📝 Notes Importantes

1. **Tous les modèles héritent de `Base`** : Traçabilité automatique
2. **Système générique** : CRUD automatique pour tous les modèles
3. **Extensibilité** : Facile d'ajouter de nouveaux modèles
4. **Internationalisation** : Support multilingue (français par défaut)
5. **API REST** : Intégration facile avec autres systèmes

---

## 🎯 Cas d'Usage Principaux

1. **Gestion du personnel** : Fiches employés complètes
2. **Gestion des absences** : Congés, départs anticipés
3. **Gestion des missions** : Missions et rapports
4. **Formation** : Suivi des formations
5. **Présence** : Pointage entrée/sortie
6. **Heures supplémentaires** : Suivi et approbation
7. **Documents** : Génération et stockage
8. **Approbations** : Workflows personnalisables

---

*Documentation générée le 25 février 2026*
