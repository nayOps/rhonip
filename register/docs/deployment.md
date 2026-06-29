# 🚀 Guide de Déploiement - Système FGP

## Prérequis

### Système
- **OS** : Linux (Ubuntu 20.04+), macOS, ou Windows avec WSL2
- **RAM** : Minimum 8GB, recommandé 16GB
- **CPU** : Minimum 4 cœurs, recommandé 8 cœurs
- **Stockage** : Minimum 50GB d'espace libre

### Logiciels
- **Docker** : Version 20.10+
- **Docker Compose** : Version 2.0+
- **Git** : Pour cloner le repository
- **Make** (optionnel) : Pour les commandes simplifiées

## Installation

### 1. Cloner le Repository
```bash
git clone <repository-url>
cd fgp
```

### 2. Configuration des Variables d'Environnement
```bash
cp .env.example .env
# Éditer le fichier .env selon votre environnement
```

### 3. Démarrage Automatique
```bash
# Rendre le script exécutable
chmod +x scripts/start.sh

# Démarrer le système
./scripts/start.sh
```

### 4. Démarrage Manuel
```bash
# Construire les images
docker-compose build

# Démarrer les services
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

## Configuration

### Variables d'Environnement Principales

#### Base de Données
```env
DATABASE_URL=postgresql://fgp_user:fgp_password_2025@postgres:5432/fgp_db
```

#### Cache Redis
```env
REDIS_URL=redis://:fgp_redis_2025@redis:6379/0
```

#### Sécurité
```env
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

#### URLs des Services
```env
FGP_CORE_URL=http://fgp_core:8000
ENROLLMENT_GATEWAY_URL=http://enrollment_gateway:8000
EXTENSIONS_SERVICE_URL=http://extensions_service:8000
ABIS_SERVICE_URL=http://abis_service:8000
```

## Services et Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Interface Next.js |
| FGP Core | 8000 | API FGP Core |
| Enrollment Gateway | 8001 | API d'enrôlement |
| Extensions Service | 8002 | API extensions |
| ABIS Service | 8003 | API biométrique |
| PostgreSQL | 5432 | Base de données |
| Redis | 6379 | Cache et sessions |
| Nginx | 80/443 | Reverse proxy |
| Prometheus | 9090 | Métriques |
| Grafana | 3001 | Tableaux de bord |

## Commandes Utiles

### Gestion des Services
```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Redémarrer un service spécifique
docker-compose restart fgp_core

# Voir les logs d'un service
docker-compose logs -f fgp_core

# Voir les logs de tous les services
docker-compose logs -f
```

### Base de Données
```bash
# Exécuter les migrations
docker-compose exec fgp_core python manage.py migrate

# Créer un superutilisateur
docker-compose exec fgp_core python manage.py createsuperuser

# Accéder au shell Django
docker-compose exec fgp_core python manage.py shell

# Sauvegarder la base de données
docker-compose exec postgres pg_dump -U fgp_user fgp_db > backup.sql

# Restaurer la base de données
docker-compose exec -T postgres psql -U fgp_user fgp_db < backup.sql
```

### Développement
```bash
# Reconstruire une image
docker-compose build --no-cache fgp_core

# Reconstruire toutes les images
docker-compose build --no-cache

# Accéder au conteneur
docker-compose exec fgp_core bash

# Voir l'utilisation des ressources
docker stats
```

## Monitoring

### Prometheus
- **URL** : http://localhost:9090
- **Métriques** : Performance, erreurs, latence
- **Alertes** : Configurées dans `docker/prometheus/`

### Grafana
- **URL** : http://localhost:3001
- **Login** : admin/admin123
- **Dashboards** : FGP, système, base de données

### Logs
```bash
# Logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f fgp_core

# Logs avec timestamps
docker-compose logs -f -t
```

## Sauvegarde

### Script de Sauvegarde
```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
docker-compose exec -T postgres pg_dump -U fgp_user fgp_db > $BACKUP_DIR/fgp_db_$DATE.sql

# Sauvegarder les fichiers media
docker-compose exec -T fgp_core tar -czf - /app/media > $BACKUP_DIR/media_$DATE.tar.gz

# Sauvegarder les fichiers de configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env docker-compose.yml

echo "Sauvegarde terminée: $BACKUP_DIR/"
```

### Restauration
```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql>"
    exit 1
fi

# Arrêter les services
docker-compose down

# Restaurer la base de données
docker-compose up -d postgres
sleep 10
docker-compose exec -T postgres psql -U fgp_user fgp_db < $BACKUP_FILE

# Redémarrer tous les services
docker-compose up -d

echo "Restauration terminée"
```

## Sécurité

### Configuration HTTPS
```nginx
# docker/nginx/conf.d/ssl.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

## Dépannage

### Problèmes Courants

#### Service ne démarre pas
```bash
# Vérifier les logs
docker-compose logs service_name

# Vérifier les ressources
docker stats

# Redémarrer le service
docker-compose restart service_name
```

#### Base de données inaccessible
```bash
# Vérifier la connexion
docker-compose exec postgres pg_isready -U fgp_user -d fgp_db

# Vérifier les logs PostgreSQL
docker-compose logs postgres

# Redémarrer PostgreSQL
docker-compose restart postgres
```

#### Problèmes de permissions
```bash
# Corriger les permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# Permissions Docker
sudo usermod -aG docker $USER
```

### Logs de Debug
```bash
# Activer le debug
export DEBUG=1

# Logs détaillés
docker-compose logs -f --tail=100
```

## Production

### Configuration Production
```env
# .env.production
DEBUG=0
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com

# Base de données production
DATABASE_URL=postgresql://user:password@prod-db:5432/fgp_db

# Monitoring production
SENTRY_DSN=your-sentry-dsn
```

### Optimisations
```yaml
# docker-compose.prod.yml
services:
  postgres:
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
```

### Load Balancing
```nginx
# docker/nginx/nginx.conf
upstream fgp_core {
    server fgp_core_1:8000;
    server fgp_core_2:8000;
    server fgp_core_3:8000;
}

server {
    location /api/v1/core/ {
        proxy_pass http://fgp_core;
    }
}
```

## Maintenance

### Mise à Jour
```bash
# Sauvegarder avant mise à jour
./scripts/backup.sh

# Mettre à jour le code
git pull origin main

# Reconstruire et redémarrer
docker-compose build
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

### Nettoyage
```bash
# Nettoyer les images inutilisées
docker image prune -f

# Nettoyer les volumes inutilisés
docker volume prune -f

# Nettoyer le système
docker system prune -f
```

### Surveillance
```bash
# Vérifier l'espace disque
df -h

# Vérifier l'utilisation mémoire
free -h

# Vérifier les processus Docker
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
