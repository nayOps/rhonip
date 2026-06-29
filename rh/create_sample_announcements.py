#!/usr/bin/env python
"""
Script pour créer des annonces de test pour le dashboard employé
À exécuter dans le conteneur Docker: docker exec -it payday-backend-1 python create_sample_announcements.py
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payday.settings')
django.setup()

from core.models import Announcement
from core.models.announcement import AnnouncementType

def create_sample_announcements():
    print("=" * 60)
    print("Création d'annonces de test")
    print("=" * 60)
    
    announcements_data = [
        {
            'title': "Mise à jour du protocole de sécurité informatique",
            'content': "Veuillez mettre à jour vos mots de passe avant vendredi. Des informations détaillées ont été envoyées par email.",
            'type': AnnouncementType.SERVICE_NOTE,
            'is_active': True,
        },
        {
            'title': "Nouveaux avantages d'assurance santé",
            'content': "Le livret d'accueil mis à jour est disponible au téléchargement sur le portail RH. Contactez le service RH pour plus d'informations.",
            'type': AnnouncementType.HR_UPDATE,
            'is_active': True,
        },
        {
            'title': "Fermeture exceptionnelle des bureaux",
            'content': "Les bureaux seront fermés le 15 mars pour maintenance annuelle. Le télétravail est encouragé.",
            'type': AnnouncementType.GENERAL,
            'is_active': True,
        },
        {
            'title': "Formation obligatoire sur la sécurité",
            'content': "Une formation obligatoire sur la sécurité au travail est prévue le mois prochain. Les inscriptions sont ouvertes.",
            'type': AnnouncementType.SERVICE_NOTE,
            'is_active': True,
        },
        {
            'title': "Annonce archivée (ne devrait pas apparaître)",
            'content': "Ceci est une ancienne annonce qui ne devrait plus apparaître car elle est inactive.",
            'type': AnnouncementType.GENERAL,
            'is_active': False,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for data in announcements_data:
        announcement, created = Announcement.objects.update_or_create(
            title=data['title'],
            defaults={
                'content': data['content'],
                'type': data['type'],
                'is_active': data['is_active'],
            }
        )
        if created:
            print(f"  ✅ Annonce '{announcement.title}' créée.")
            created_count += 1
        else:
            print(f"  🔄 Annonce '{announcement.title}' mise à jour.")
            updated_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ {created_count} annonce(s) créée(s), {updated_count} annonce(s) mise(s) à jour")
    print("=" * 60)

if __name__ == '__main__':
    try:
        create_sample_announcements()
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des annonces: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
