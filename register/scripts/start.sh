#!/bin/bash

# =====================================================
# Script de démarrage du système FGP
# =====================================================

set -e

echo "🚀 Démarrage du système FGP - Fichier Général de la Population RDC"
echo "=================================================================="

# Vérification des prérequis
echo "📋 Vérification des prérequis..."

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

echo "✅ Docker et Docker Compose sont installés"

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/media
mkdir -p data/static

# Vérifier les variables d'environnement
echo "🔧 Configuration des variables d'environnement..."

if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cat > .env << EOF
# Configuration FGP
DEBUG=0
SECRET_KEY=fgp_secret_key_2025_very_secure_change_in_production
DATABASE_URL=postgresql://fgp_user:fgp_password_2025@postgres:5432/fgp_db
REDIS_URL=redis://:fgp_redis_2025@redis:6379/0

# URLs des services
FGP_CORE_URL=http://fgp_core:8000
ENROLLMENT_GATEWAY_URL=http://enrollment_gateway:8000
EXTENSIONS_SERVICE_URL=http://extensions_service:8000
ABIS_SERVICE_URL=http://abis_service:8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_FGP_CORE_URL=http://localhost:8000
NEXT_PUBLIC_EXTENSIONS_URL=http://localhost:8002
NEXT_PUBLIC_ABIS_URL=http://localhost:8003

# Sécurité
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Monitoring
PROMETHEUS_RETENTION_TIME=200h
GRAFANA_ADMIN_PASSWORD=admin123
EOF
    echo "✅ Fichier .env créé"
else
    echo "✅ Fichier .env existe déjà"
fi

# Construire les images Docker
echo "🔨 Construction des images Docker..."
docker-compose build --parallel

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."

# Attendre PostgreSQL
echo "📊 Attente de PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U fgp_user -d fgp_db; do
    echo "⏳ PostgreSQL n'est pas encore prêt..."
    sleep 2
done
echo "✅ PostgreSQL est prêt"

# Attendre Redis
echo "🔄 Attente de Redis..."
until docker-compose exec -T redis redis-cli ping; do
    echo "⏳ Redis n'est pas encore prêt..."
    sleep 2
done
echo "✅ Redis est prêt"

# Exécuter les migrations
echo "🗄️ Exécution des migrations de base de données..."
docker-compose exec -T fgp_core python manage.py migrate
docker-compose exec -T enrollment_gateway python manage.py migrate
docker-compose exec -T extensions_service python manage.py migrate
docker-compose exec -T abis_service python manage.py migrate

# Créer un superutilisateur
echo "👤 Création du superutilisateur..."
docker-compose exec -T fgp_core python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fgp.rdc', 'admin123')
    print('Superutilisateur créé: admin/admin123')
else:
    print('Superutilisateur existe déjà')
EOF

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
docker-compose exec -T fgp_core python manage.py collectstatic --noinput
docker-compose exec -T enrollment_gateway python manage.py collectstatic --noinput
docker-compose exec -T extensions_service python manage.py collectstatic --noinput
docker-compose exec -T abis_service python manage.py collectstatic --noinput

# Vérifier le statut des services
echo "🔍 Vérification du statut des services..."
docker-compose ps

echo ""
echo "🎉 Système FGP démarré avec succès!"
echo "=================================="
echo ""
echo "📱 Frontend (Next.js):     http://localhost:3000"
echo "🔧 FGP Core API:           http://localhost:8000"
echo "🚪 Enrollment Gateway:     http://localhost:8001"
echo "📋 Extensions Service:     http://localhost:8002"
echo "🔍 ABIS Service:           http://localhost:8003"
echo "📊 Prometheus:             http://localhost:9090"
echo "📈 Grafana:                http://localhost:3001 (admin/admin123)"
echo "🗄️ PostgreSQL:             localhost:5432"
echo "🔄 Redis:                  localhost:6379"
echo ""
echo "👤 Admin Django:           http://localhost:8000/admin (admin/admin123)"
echo "📚 API Documentation:      http://localhost:8000/api/docs/"
echo ""
echo "📋 Commandes utiles:"
echo "  - Arrêter:               docker-compose down"
echo "  - Logs:                  docker-compose logs -f [service]"
echo "  - Redémarrer:            docker-compose restart [service]"
echo "  - Shell Django:          docker-compose exec fgp_core python manage.py shell"
echo ""
echo "🔧 Pour le développement:"
echo "  - Logs en temps réel:    docker-compose logs -f"
echo "  - Rebuild:               docker-compose build --no-cache"
echo "  - Reset complet:         docker-compose down -v && docker-compose up -d"
echo ""
