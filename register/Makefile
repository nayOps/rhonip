# =====================================================
# Makefile pour le système FGP
# =====================================================

.PHONY: help build up down restart logs shell migrate superuser backup restore clean

# Variables
COMPOSE_FILE = docker-compose.yml
ENV_FILE = .env

# Couleurs pour les messages
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Afficher l'aide
	@echo "$(BLUE)Système FGP - Fichier Général de la Population RDC$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(GREEN)Commandes disponibles:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Services disponibles:$(NC)"
	@echo "  Frontend:        http://localhost:3000"
	@echo "  FGP Core:        http://localhost:8000"
	@echo "  Enrollment:      http://localhost:8001"
	@echo "  Extensions:      http://localhost:8002"
	@echo "  ABIS:           http://localhost:8003"
	@echo "  Prometheus:     http://localhost:9090"
	@echo "  Grafana:        http://localhost:3001"

build: ## Construire toutes les images Docker
	@echo "$(BLUE)Construction des images Docker...$(NC)"
	docker-compose build --parallel

build-no-cache: ## Construire toutes les images Docker sans cache
	@echo "$(BLUE)Construction des images Docker (sans cache)...$(NC)"
	docker-compose build --no-cache --parallel

up: ## Démarrer tous les services
	@echo "$(BLUE)Démarrage des services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services démarrés!$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)API Docs: http://localhost:8000/api/docs/$(NC)"

down: ## Arrêter tous les services
	@echo "$(BLUE)Arrêt des services...$(NC)"
	docker-compose down

restart: ## Redémarrer tous les services
	@echo "$(BLUE)Redémarrage des services...$(NC)"
	docker-compose restart

restart-service: ## Redémarrer un service spécifique (usage: make restart-service SERVICE=fgp_core)
	@echo "$(BLUE)Redémarrage du service $(SERVICE)...$(NC)"
	docker-compose restart $(SERVICE)

logs: ## Afficher les logs de tous les services
	docker-compose logs -f

logs-service: ## Afficher les logs d'un service spécifique (usage: make logs-service SERVICE=fgp_core)
	docker-compose logs -f $(SERVICE)

status: ## Afficher le statut des services
	@echo "$(BLUE)Statut des services:$(NC)"
	docker-compose ps

shell: ## Accéder au shell du service FGP Core
	docker-compose exec fgp_core bash

shell-service: ## Accéder au shell d'un service spécifique (usage: make shell-service SERVICE=fgp_core)
	docker-compose exec $(SERVICE) bash

migrate: ## Exécuter les migrations de base de données
	@echo "$(BLUE)Exécution des migrations...$(NC)"
	docker-compose exec fgp_core python manage.py migrate
	docker-compose exec enrollment_gateway python manage.py migrate
	docker-compose exec extensions_service python manage.py migrate
	docker-compose exec abis_service python manage.py migrate
	@echo "$(GREEN)Migrations terminées!$(NC)"

migrate-service: ## Exécuter les migrations d'un service spécifique (usage: make migrate-service SERVICE=fgp_core)
	@echo "$(BLUE)Exécution des migrations pour $(SERVICE)...$(NC)"
	docker-compose exec $(SERVICE) python manage.py migrate

superuser: ## Créer un superutilisateur Django
	@echo "$(BLUE)Création du superutilisateur...$(NC)"
	docker-compose exec fgp_core python manage.py createsuperuser

collectstatic: ## Collecter les fichiers statiques
	@echo "$(BLUE)Collecte des fichiers statiques...$(NC)"
	docker-compose exec fgp_core python manage.py collectstatic --noinput
	docker-compose exec enrollment_gateway python manage.py collectstatic --noinput
	docker-compose exec extensions_service python manage.py collectstatic --noinput
	docker-compose exec abis_service python manage.py collectstatic --noinput

backup: ## Sauvegarder la base de données
	@echo "$(BLUE)Sauvegarde de la base de données...$(NC)"
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U fgp_user fgp_db > backups/fgp_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Sauvegarde terminée dans le dossier backups/$(NC)"

restore: ## Restaurer la base de données (usage: make restore FILE=backup.sql)
	@echo "$(BLUE)Restauration de la base de données...$(NC)"
	docker-compose exec -T postgres psql -U fgp_user fgp_db < $(FILE)
	@echo "$(GREEN)Restauration terminée!$(NC)"

clean: ## Nettoyer les images et volumes Docker inutilisés
	@echo "$(BLUE)Nettoyage des ressources Docker...$(NC)"
	docker system prune -f
	docker volume prune -f
	docker image prune -f

clean-all: ## Nettoyage complet (ATTENTION: supprime toutes les données)
	@echo "$(RED)ATTENTION: Cette commande supprimera toutes les données!$(NC)"
	@read -p "Êtes-vous sûr? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	docker system prune -af
	docker volume prune -f

dev: ## Mode développement (logs en temps réel)
	@echo "$(BLUE)Mode développement...$(NC)"
	docker-compose up

test: ## Exécuter les tests
	@echo "$(BLUE)Exécution des tests...$(NC)"
	docker-compose exec fgp_core python manage.py test
	docker-compose exec enrollment_gateway python manage.py test
	docker-compose exec extensions_service python manage.py test
	docker-compose exec abis_service python manage.py test

lint: ## Vérifier le code avec les linters
	@echo "$(BLUE)Vérification du code...$(NC)"
	docker-compose exec fgp_core flake8 .
	docker-compose exec fgp_core black --check .
	docker-compose exec fgp_core isort --check-only .

format: ## Formater le code
	@echo "$(BLUE)Formatage du code...$(NC)"
	docker-compose exec fgp_core black .
	docker-compose exec fgp_core isort .

install: ## Installation complète du système
	@echo "$(BLUE)Installation du système FGP...$(NC)"
	@chmod +x scripts/start.sh
	@./scripts/start.sh

update: ## Mettre à jour le système
	@echo "$(BLUE)Mise à jour du système...$(NC)"
	git pull origin main
	make backup
	make build
	make migrate
	make collectstatic
	make restart
	@echo "$(GREEN)Mise à jour terminée!$(NC)"

monitor: ## Ouvrir les interfaces de monitoring
	@echo "$(BLUE)Ouverture des interfaces de monitoring...$(NC)"
	@echo "$(YELLOW)Prometheus: http://localhost:9090$(NC)"
	@echo "$(YELLOW)Grafana: http://localhost:3001 (admin/admin123)$(NC)"

health: ## Vérifier la santé des services
	@echo "$(BLUE)Vérification de la santé des services...$(NC)"
	@curl -s http://localhost:8000/health/ && echo " ✅ FGP Core"
	@curl -s http://localhost:8001/health/ && echo " ✅ Enrollment Gateway"
	@curl -s http://localhost:8002/health/ && echo " ✅ Extensions Service"
	@curl -s http://localhost:8003/health/ && echo " ✅ ABIS Service"
	@curl -s http://localhost:3000 > /dev/null && echo " ✅ Frontend"

# Commandes de développement
dev-logs: ## Logs en temps réel pour le développement
	docker-compose logs -f --tail=100

dev-restart: ## Redémarrage rapide pour le développement
	docker-compose restart
	sleep 5
	make logs

# Commandes de production
prod-build: ## Build pour la production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Démarrage en production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down: ## Arrêt en production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
