#!/usr/bin/env python
"""
Script pour créer et appliquer les migrations pour le modèle Announcement
À exécuter dans le conteneur Docker: docker exec -it payday-backend-1 python create_migration_announcement.py
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payday.settings')
django.setup()

from django.core.management import call_command

def create_and_apply_migrations():
    print("=" * 60)
    print("Création et application des migrations pour Announcement")
    print("=" * 60)
    
    try:
        # Créer les migrations
        print("\n1. Création des migrations...")
        call_command('makemigrations', 'core', verbosity=2)
        print("✅ Migrations créées avec succès")
        
        # Appliquer les migrations
        print("\n2. Application des migrations...")
        call_command('migrate', verbosity=2)
        print("✅ Migrations appliquées avec succès")
        
        print("\n" + "=" * 60)
        print("✅ Processus terminé avec succès!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la création/application des migrations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    create_and_apply_migrations()
