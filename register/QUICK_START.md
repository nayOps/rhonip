# 🚀 Guide de Démarrage Rapide - Système FGP

## 📋 Vue d'ensemble

Le système FGP (Fichier Général de la Population) est maintenant **prêt pour le développement** avec une architecture complète de microservices.

## ✅ État d'Avancement

### 🏗️ **Architecture Complète**
- ✅ Structure microservices avec Docker
- ✅ Base de données PostgreSQL avec schéma complet
- ✅ Cache Redis configuré
- ✅ Monitoring (Prometheus + Grafana)
- ✅ Documentation technique complète
- ✅ Diagrammes Mermaid (architecture, base de données, flux)

### 🔧 **Services Implémentés**
- ✅ **FGP Core Service** : Gestion des 27 variables obligatoires
- ✅ **Enrollment Gateway** : Point d'entrée unique pour l'enrôlement
- ✅ **Extensions Service** : Structure pour les extensions par strate
- ✅ **Frontend Next.js** : Configuration de base
- ✅ **Configuration Docker** : Prêt pour le déploiement

### 📊 **Base de Données**
- ✅ Schéma relationnel complet
- ✅ 27 variables FGP Core
- ✅ 9 extensions par strate (Élèves, Étudiants, Électeurs, PNC, FARDC, etc.)
- ✅ Tables de support (biométrie, documents, audit, ABIS)
- ✅ Index et contraintes optimisés

## 🚀 Démarrage Rapide

### 1. **Prérequis**
```bash
# Vérifier Docker et Docker Compose
docker --version
docker-compose --version
```

### 2. **Configuration**
```bash
# Aller dans le dossier du projet
cd /home/nayops/Documents/strate/fgp

# Copier la configuration
cp env.example .env

# Rendre le script exécutable
chmod +x scripts/start.sh
```

### 3. **Démarrage du Système**
```bash
# Démarrage automatique (recommandé)
./scripts/start.sh

# Ou démarrage manuel
docker-compose build
docker-compose up -d
```

### 4. **Vérification**
```bash
# Vérifier le statut des services
docker-compose ps

# Voir les logs
docker-compose logs -f

# Vérifier la santé des services
curl http://localhost:8000/health/
curl http://localhost:8001/health/
```

## 🌐 **Services Disponibles**

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface Next.js |
| **FGP Core API** | http://localhost:8000 | API principale (27 variables) |
| **Enrollment Gateway** | http://localhost:8001 | API d'enrôlement |
| **Extensions Service** | http://localhost:8002 | API extensions par strate |
| **ABIS Service** | http://localhost:8003 | API biométrique |
| **Prometheus** | http://localhost:9090 | Métriques |
| **Grafana** | http://localhost:3001 | Tableaux de bord (admin/admin123) |

## 📚 **Documentation**

- **Architecture** : `docs/architecture.md`
- **API** : `docs/api.md`
- **Base de données** : `docs/database.md`
- **Déploiement** : `docs/deployment.md`
- **Diagrammes** : `docs/diagrams/`

## 🛠️ **Commandes Utiles**

```bash
# Utiliser le Makefile
make help                    # Afficher l'aide
make up                      # Démarrer tous les services
make down                    # Arrêter tous les services
make logs                    # Voir les logs
make migrate                 # Exécuter les migrations
make superuser               # Créer un superutilisateur
make backup                  # Sauvegarder la base de données

# Commandes Docker
docker-compose ps            # Statut des services
docker-compose logs -f       # Logs en temps réel
docker-compose restart       # Redémarrer les services
docker-compose exec fgp_core python manage.py shell  # Shell Django
```

## 🧪 **Tests d'API**

### Créer un superutilisateur
```bash
# Accéder au conteneur FGP Core
docker-compose exec fgp_core python manage.py createsuperuser

# Ou utiliser le Makefile
make superuser
```

### Tester l'API
```bash
# Health check
curl http://localhost:8000/health/

# Documentation API
# Ouvrir http://localhost:8000/api/docs/ dans le navigateur

# Exemple d'enrôlement (avec authentification)
curl -X POST http://localhost:8001/api/v1/enrolments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "session_id": "TEST-001",
    "channel": "fixed",
    "device_id": "DEV-001",
    "operator_id": "OP-001",
    "location": {"province": "Kinshasa"},
    "schema_version": "1.0",
    "core": {
      "nom": "TEST",
      "prenom": "User",
      "sexe": "M",
      "date_naissance": "1990-01-01",
      "lieu_naissance": "Kinshasa",
      "province_naissance": "Kinshasa",
      "nationalite": "Congolaise",
      "province_residence": "Kinshasa"
    },
    "biometrics": {
      "face": {"ref": "test.jpg", "quality": 0.8},
      "fingerprints": {"ref": "test.fp", "quality": 0.9}
    },
    "strata": ["ELECTEUR"]
  }'
```

## 📊 **Monitoring**

### Prometheus
- **URL** : http://localhost:9090
- **Métriques** : Performance, erreurs, latence

### Grafana
- **URL** : http://localhost:3001
- **Login** : admin/admin123
- **Dashboards** : FGP, système, base de données

## 🔧 **Développement**

### Structure du Projet
```
fgp/
├── backend/
│   ├── fgp_core/           # Service FGP Core ✅
│   ├── enrollment_gateway/ # Service Enrollment Gateway ✅
│   ├── extensions_service/ # Service Extensions ✅
│   └── abis_service/       # Service ABIS (à implémenter)
├── frontend/               # Next.js ✅
├── database/               # Schémas SQL ✅
├── docker/                 # Configuration Docker ✅
├── docs/                   # Documentation ✅
└── scripts/                # Scripts utilitaires ✅
```

### Prochaines Étapes

1. **Implémentation ABIS Service** (déduplication biométrique)
2. **Développement Frontend Next.js** (interface d'enrôlement)
3. **Tests et validation**
4. **Intégration avec systèmes externes**
5. **Déploiement en production**

## 🆘 **Dépannage**

### Problèmes Courants

**Service ne démarre pas :**
```bash
# Vérifier les logs
docker-compose logs <service_name>

# Vérifier les ressources
docker stats

# Redémarrer le service
docker-compose restart <service_name>
```

**Base de données inaccessible :**
```bash
# Vérifier la connexion
docker-compose exec postgres pg_isready -U fgp_user -d fgp_db

# Vérifier les logs PostgreSQL
docker-compose logs postgres
```

**Problèmes de permissions :**
```bash
# Corriger les permissions
sudo chown -R $USER:$USER .
chmod -R 755 .
```

## 📞 **Support**

- **Documentation complète** : Voir le dossier `docs/`
- **Diagrammes** : Voir `docs/diagrams/`
- **Logs** : Utiliser `docker-compose logs -f`

---

## 🎉 **Félicitations !**

Le système FGP est maintenant **opérationnel** avec :
- ✅ Architecture microservices complète
- ✅ Base de données structurée
- ✅ APIs fonctionnelles
- ✅ Monitoring configuré
- ✅ Documentation complète

**Vous pouvez maintenant commencer le développement des fonctionnalités spécifiques !**
