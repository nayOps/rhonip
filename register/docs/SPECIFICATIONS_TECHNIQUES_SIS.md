# Spécifications Techniques - SIS

## 1) Objet du document

Ce document définit les spécifications techniques consolidées du **SIS (Système d'Identification par Stratification)** du programme FGP/ONIP.

Objectifs:
- formaliser l'architecture cible;
- préciser les contrats de données et d'API;
- standardiser le workflow d'enrôlement stratifié;
- encadrer la sécurité, l'exploitation et la qualité;
- servir de base de réalisation (build), tests, déploiement et audit.

## 2) Périmètre

Le SIS couvre:
- l'identification de base des personnes (noyau FGP);
- la gestion d'appartenance multi-strates (education, electoral, securite, justice, refuge, etc.);
- la deduplication biométrique ABIS;
- la gestion documentaire et la traçabilité;
- l'exposition d'API internes et externes;
- l'observabilité, la sécurité et l'operabilité.

Hors périmètre direct:
- UX détaillée des écrans frontend;
- implémentation fournisseur ABIS propriétaire;
- politiques réglementaires non techniques.

## 3) Référentiel et principes

- Référence d'architecture: microservices + API REST.
- Référence de modélisation: alignement OSIA (Open Standard Identity APIs).
- Principe de conception: **core commun + extensions par strate**.
- Principe d'intégrité: transaction atomique de création d'identité.
- Principe de conformité: auditabilité complète, sécurité by design.

## 4) Architecture logique

## 4.1 Composants

- **Frontend** (`Next.js`, port 3000): formulaires dynamiques par strate.
- **API Gateway / Reverse Proxy** (`Nginx`, ports 80/443): routage, TLS, contrôle d'accès réseau.
- **Enrollment Gateway** (port 8001): orchestration d'enrôlement.
- **FGP Core Service** (port 8000): noyau d'identité, NIN, strates, documents.
- **Extensions Service** (port 8002): validation/persistance de données sectorielles.
- **ABIS Service** (port 8003): deduplication biométrique 1:N.
- **PostgreSQL** (port 5432): persistance relationnelle.
- **Redis** (port 6379): cache/session/queues temporaires.
- **Prometheus + Grafana** (9090/3001): monitoring et dashboards.

## 4.2 Style d'échange inter-services

- REST/JSON synchrone pour opérations critiques.
- Exécution asynchrone recommandée pour intégrations tierces sectorielles (MENPS, CENI, HCR, etc.).
- Propagation d'identifiants de corrélation inter-services.

## 4.3 Disponibilité et scalabilité

- Scalabilité horizontale des services stateless.
- Répartition de charge par Nginx.
- Optimisation DB via index, partitionnement ciblé (audit, gros volumes).
- Caching Redis pour requêtes fréquentes.

## 5) Modèle de données

## 5.1 Entités coeur (minimum)

- `fgp_person_core`: identité de base (27 variables obligatoires).
- `fgp_biometric`: métadonnées biométriques capturées.
- `fgp_strata_membership`: appartenance multi-strates temporelle.
- `fgp_documents`: pièces justificatives, hash et vérification.
- `fgp_audit_trail`: journal de traçabilité des actions.
- `fgp_biometric_templates`: templates biométriques pour ABIS.
- `abis_matches`: résultats de comparaison et révision.

## 5.2 Extensions par strate (tables dédiées)

- `ext_eleves`
- `ext_etudiants`
- `ext_electeurs`
- `ext_pnc`
- `ext_fardc`
- `ext_prison`
- `ext_refugies`
- `ext_enfants`
- `ext_fonctionnaires`

## 5.3 Règles cardinalité/validité

- Une personne peut appartenir à **N strates** simultanément.
- Une appartenance est historisée: `valid_from`, `valid_to`, `status`.
- Les données d'extension sont 1:1 par strate active et personne.
- Les historiques (audit, ABIS, événements) sont non destructifs.

## 5.4 Contraintes de validation minimales

- NIN: format `CD-YYYY-NNNN-NNNNNNNNN`.
- Téléphone: format national défini (ex. `+243XXXXXXXXX`).
- Email: format RFC simplifié.
- Qualité biométrique: bornes [0..1], seuil minimum par modalité.
- Statuts de strate: `ACTIVE | INACTIVE | SUSPENDED`.

## 6) Contrat fonctionnel de stratification

## 6.1 Catalogue de strates initial

- ELEVES
- ETUDIANTS
- ELECTEURS
- PNC
- FARDC
- PRISON
- REFUGIES
- ENFANTS
- FONCTIONNAIRES

## 6.2 Règles inter-strates (minimum)

- `ELECTEURS` exige age >= 18 ans.
- `ELEVES` et `ETUDIANTS` non simultanés (règle métier configurable).
- `PNC` et `FARDC` non simultanés (règle métier configurable).
- `ENFANTS` applicable prioritairement aux mineurs.

## 6.3 Extensibilité

L'ajout d'une nouvelle strate implique:
- création table d'extension;
- validateur métier dédié;
- endpoint extension;
- formulaire frontend dynamique;
- mapping d'intégration externe éventuel.

## 7) API - spécifications techniques

## 7.1 Sécurité d'accès API

- Authentification JWT obligatoire.
- Headers applicatifs requis:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
  - `X-ONIP-Channel`
  - `X-Schema-Version`

## 7.2 Endpoints noyau

- `GET /api/v1/core/persons/`
- `POST /api/v1/core/persons/`
- `GET /api/v1/core/persons/by-nin/{nin}/`
- `GET /api/v1/core/search/`
- `GET /api/v1/core/strata/by-nin/{nin}/`
- `POST /api/v1/core/strata/`
- `GET /api/v1/core/documents/?nin={nin}`
- `POST /api/v1/core/documents/`

## 7.3 Endpoints enrôlement

- `POST /api/v1/enrolments/` (orchestration complète)
- `GET /api/v1/enrolments/{id}/` (statut)
- `POST /api/v1/enrolments/validate/` (pré-validation)

## 7.4 Endpoints extensions

- `POST /api/v1/extensions/{strate}/` pour chaque strate supportée.

## 7.5 Endpoints ABIS

- `POST /api/v1/abis/enroll/`
- `POST /api/v1/abis/search/`
- `GET /api/v1/abis/matches/`

## 7.6 Exigences API transverses

- Pagination standard (`count`, `next`, `previous`, `results`).
- Filtres normalisés (`exact`, `icontains`, `range`, etc.).
- Codes HTTP standardisés (200, 201, 400, 401, 403, 404, 409, 422, 500).
- Format d'erreur unifié avec code, message, détails champ.
- Rate limit par catégorie d'API (general/enrolment/abis/auth).

## 8) Workflow d'enrôlement stratifié (normatif)

## 8.1 Étapes

1. **Initialisation session** (canal, opérateur, device, statut `PENDING`).
2. **Collecte core** (27 variables).
3. **Sélection strates** (multi-select + règles de cohérence).
4. **Collecte extensions** (formulaires dynamiques par strate).
5. **Collecte biométrie** (face/empreintes/iris/signature selon équipement).
6. **Collecte documents** (scan, hash, stockage sécurisé).
7. **Validation complète** (core + extensions + biométrie + documents).
8. **Dedup ABIS 1:N** (décision `NO_HIT | HIT | REVIEW`).
9. **Génération NIN + persistance atomique**.
10. **Émission récépissé + notifications + événements**.

## 8.2 Règles transactionnelles

- La création finale doit s'exécuter dans une **transaction DB atomique**.
- Si une opération critique échoue, rollback complet.
- Les intégrations tierces sont idéalement découplées du commit principal.

## 8.3 Gestion des doublons ABIS

- `NO_HIT`: poursuite enrôlement.
- `HIT`: blocage et traitement de revue.
- `REVIEW`: mise en attente avec décision experte obligatoire.

## 9) Sécurité technique

## 9.1 Contrôles obligatoires

- TLS 1.2+ (cible 1.3) en transit.
- Chiffrement au repos des données sensibles.
- Protection des templates biométriques (clés sécurisées/HSM recommandé).
- RBAC/ABAC pour les droits applicatifs.
- Signature/payload integrity sur canaux critiques (JWS).

## 9.2 Journalisation et conformité

- Journal d'audit applicatif immuable logique (WORM recommandé).
- Trace de toutes opérations CRUD sensibles.
- Traçage des accès, modifications, décisions ABIS, actions opérateur.
- Politique de rétention et minimisation de données par domaine.

## 10) Déploiement et exploitation

## 10.1 Environnement d'exécution

- Docker Compose pour environnements de référence.
- Variables d'environnement minimales:
  - `DATABASE_URL`
  - `REDIS_URL`
  - `SECRET_KEY`
  - `ALLOWED_HOSTS`
  - `CORS_ALLOWED_ORIGINS`

## 10.2 Topologie de production (cible)

- Reverse proxy HTTPS en frontal.
- Réplication PostgreSQL et sauvegardes planifiées.
- Observabilité active (metrics, logs, alerting).
- Procédure rollback et reprise après incident documentée.

## 10.3 Sauvegarde/restauration

- Sauvegarde DB quotidienne + incrémentale selon RPO.
- Sauvegarde médias/documents.
- Test de restauration périodique obligatoire (au moins mensuel).

## 11) Observabilité et SRE

## 11.1 Métriques minimales

- Disponibilité par service.
- Latence p50/p95/p99 par endpoint.
- Taux d'erreur par code HTTP.
- Débit requêtes.
- Durée moyenne du workflow d'enrôlement.
- Taux de `HIT/REVIEW` ABIS.

## 11.2 Logging

- Logs structurés JSON.
- Correlation ID de bout en bout.
- Rotation/archivage automatique.

## 11.3 Alertes

- Service down.
- Saturation CPU/RAM/DB connections.
- Hausse anormale d'erreurs 5xx.
- Dégradation ABIS (latence, erreurs, ratio review).

## 12) Exigences non fonctionnelles

## 12.1 Performance (cible initiale)

- API core en lecture: p95 < 500 ms.
- API enrôlement synchrone: p95 < 2 s hors ABIS.
- Réponse ABIS search: p95 < 2 s (à ajuster selon volumétrie).

## 12.2 Disponibilité

- Cible de disponibilité plateforme: >= 99.5%.

## 12.3 Intégrité et qualité des données

- 100% des mutations critiques auditées.
- 0 tolérance sur création doublon confirmé ABIS sans revue.

## 13) Stratégie de tests

- Tests unitaires sur validateurs core/extensions.
- Tests d'intégration inter-services (enrolment -> core/ext/abis).
- Tests de contrat API (schéma OpenAPI).
- Tests de charge sur endpoints critiques.
- Tests sécurité (authz, injections, brute force, replay).
- Tests de résilience (timeouts, retry, idempotence).

## 14) Gouvernance des versions

- Versionnement d'API (`/api/v1` puis `v2` sans rupture brutale).
- Versionnement de schéma via migrations contrôlées.
- Compatibilité ascendante des payloads pendant période de transition.

## 15) Plan d'alignement OSIA

Pour converger vers un alignement OSIA complet:
- isoler adresses/contacts du core si nécessaire;
- renforcer modèle d'événements vitaux;
- standardiser dictionnaire attributaire OSIA;
- formaliser mapping table par table (OSIA <-> FGP);
- maintenir un catalogue de strates et règles inter-strates versionnées.

## 16) Risques techniques et mitigations

- **Risque doublon biométrique** -> revue experte + seuils calibrés + audit ABIS.
- **Risque incohérence inter-strates** -> moteur de règles centralisé.
- **Risque latence forte** -> cache, index, partitionnement, traitements async.
- **Risque sécurité API** -> rotation clés/JWT, IP whitelisting, rate limits.
- **Risque opérationnel** -> backup/restauration testés + runbooks d'incident.

## 17) Livrables techniques attendus

- Schéma SQL validé + scripts migration.
- Contrats OpenAPI publiés.
- Catalogue de strates et règles métier versionné.
- Playbooks d'exploitation (backup, restore, incident, release).
- Dashboards monitoring + SLO/SLA opérationnels.

## 18) Critères d'acceptation techniques

Le SIS est considéré conforme si:
- les flux d'enrôlement et mise à jour strate passent les tests E2E;
- les contrôles ABIS empêchent les doublons non revus;
- la traçabilité complète est disponible pour chaque identité;
- les endpoints documentés répondent aux contrats;
- le déploiement reproductible et la restauration sont validés;
- les exigences sécurité/monitoring sont actives en pré-production.

---

Version: 1.0 (consolidée)  
Statut: Spécification technique de référence  
Périmètre: SIS - Identification par stratification (FGP/ONIP)
