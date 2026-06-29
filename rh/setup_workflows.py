#!/usr/bin/env python
"""
Script pour créer :
- Directions et sous-directions
- Utilisateurs pour directeurs et sous-directeurs
- Workflows d'approbation pour congés et missions
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payday.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

User = get_user_model()
Employee = apps.get_model('employee', 'Employee')
Direction = apps.get_model('employee', 'Direction')
SubDirection = apps.get_model('employee', 'SubDirection')
Designation = apps.get_model('employee', 'Designation')
Flow = apps.get_model('core', 'Flow')
FlowStep = apps.get_model('core', 'FlowStep')
Leave = apps.get_model('leave', 'Leave')
Mission = apps.get_model('mission', 'Mission')

def get_or_create_model(model_class, **kwargs):
    """Crée ou récupère un objet"""
    obj, created = model_class.objects.get_or_create(**kwargs)
    return obj

def create_directions_and_subdirections():
    """Crée les directions et sous-directions avec leurs directeurs"""
    print("📁 Création des directions et sous-directions...")
    
    directions_data = [
        {
            'name': 'Direction Générale',
            'subdirections': [
                {'name': 'Sous-direction Administration'},
                {'name': 'Sous-direction Communication'},
            ],
            'director_email': 'directeur.general@onip.cd',
            'director_name': 'Directeur Général',
        },
        {
            'name': 'Direction des Ressources Humaines',
            'subdirections': [
                {'name': 'Sous-direction Recrutement'},
                {'name': 'Sous-direction Formation'},
            ],
            'director_email': 'directeur.rh@onip.cd',
            'director_name': 'Directeur RH',
        },
        {
            'name': 'Direction Technique',
            'subdirections': [
                {'name': 'Sous-direction Développement'},
                {'name': 'Sous-direction Support'},
            ],
            'director_email': 'directeur.technique@onip.cd',
            'director_name': 'Directeur Technique',
        },
        {
            'name': 'Direction Financière',
            'subdirections': [
                {'name': 'Sous-direction Comptabilité'},
            ],
            'director_email': 'directeur.financier@onip.cd',
            'director_name': 'Directeur Financier',
        },
    ]
    
    directions_created = {}
    users_created = {}
    
    for dir_data in directions_data:
        # Créer la direction
        direction = get_or_create_model(Direction, name=dir_data['name'])
        directions_created[dir_data['name']] = direction
        print(f"  ✓ Direction '{direction.name}' créée")
        
        # Créer les sous-directions
        for subdir_data in dir_data['subdirections']:
            subdirection = get_or_create_model(
                SubDirection,
                name=subdir_data['name'],
                direction=direction
            )
            print(f"    ✓ Sous-direction '{subdirection.name}' créée")
        
        # Créer le directeur
        designation = get_or_create_model(Designation, name=dir_data['director_name'])
        
        # Créer l'employé directeur
        director_employee, _ = Employee.objects.get_or_create(
            registration_number=f'DIR-{direction.id}',
            defaults={
                'first_name': dir_data['director_name'].split()[0],
                'last_name': dir_data['director_name'].split()[-1],
                'middle_name': '',
                'email': dir_data['director_email'],
                'email_professional': dir_data['director_email'],
                'gender': 'male',
                'designation': designation,
                'direction': direction,
                'marital_status': 'maried',
                'payment_method': 'bank',
                'type_of_identity': 'national_id',
            }
        )
        
        # Créer l'utilisateur directeur
        try:
            director_user = User.objects.get(email=dir_data['director_email'])
            director_user.employee = director_employee
            director_user.is_staff = True
            if not director_user.username:
                director_user.username = dir_data['director_email']
            director_user.save()
        except User.DoesNotExist:
            # Créer directement avec username = email
            director_user = User(
                email=dir_data['director_email'],
                username=dir_data['director_email'],
                employee=director_employee,
                is_staff=True,
                is_active=True,
            )
            director_user.set_password('onip2024')
            director_user.save()
        
        users_created[dir_data['name']] = director_user
        print(f"    ✓ Directeur '{dir_data['director_name']}' créé ({dir_data['director_email']})")
        
        # Créer les sous-directeurs
        for i, subdir_data in enumerate(dir_data['subdirections'][:2]):  # Max 2 sous-directeurs
            subdir = SubDirection.objects.get(name=subdir_data['name'], direction=direction)
            subdir_designation = get_or_create_model(
                Designation,
                name=f'Sous-directeur {subdir.name}'
            )
            
            subdir_email = f'sousdirecteur.{direction.name.lower().replace(" ", ".")}.{i+1}@onip.cd'
            
            subdir_employee, _ = Employee.objects.get_or_create(
                registration_number=f'SUBDIR-{subdir.id}',
                defaults={
                    'first_name': 'Sous-directeur',
                    'last_name': subdir.name.split()[-1],
                    'middle_name': '',
                    'email': subdir_email,
                    'email_professional': subdir_email,
                    'gender': 'male',
                    'designation': subdir_designation,
                    'direction': direction,
                    'marital_status': 'maried',
                    'payment_method': 'bank',
                    'type_of_identity': 'national_id',
                }
            )
            
            try:
                subdir_user = User.objects.get(email=subdir_email)
                subdir_user.employee = subdir_employee
                subdir_user.is_staff = True
                if not subdir_user.username:
                    subdir_user.username = subdir_email
                subdir_user.save()
            except User.DoesNotExist:
                subdir_user = User(
                    email=subdir_email,
                    username=subdir_email,
                    employee=subdir_employee,
                    is_staff=True,
                    is_active=True,
                )
                subdir_user.set_password('onip2024')
                subdir_user.save()
            
            print(f"      ✓ Sous-directeur créé ({subdir_email})")
    
    return directions_created, users_created

def create_workflow_for_employee_leave(directors):
    """Crée le workflow d'approbation pour congé d'un employé normal"""
    print("\n🔄 Création du workflow d'approbation pour congé (employé)...")
    
    # Récupérer le ContentType pour Leave
    leave_content_type = ContentType.objects.get_for_model(Leave)
    
    # Supprimer tous les flows existants pour Leave
    existing_flows = Flow.objects.filter(content_type=leave_content_type)
    for f in existing_flows:
        FlowStep.objects.filter(flow=f).delete()
        f.delete()
    
    # Créer le Flow principal (pour employés normaux)
    flow = Flow.objects.create(
        name='Workflow Approbation Congé - Employé',
        content_type=leave_content_type
    )
    print(f"  ✓ Flow créé: {flow.name}")
    
    # Récupérer les utilisateurs nécessaires
    directeur_rh = directors.get('Direction des Ressources Humaines')
    dg = directors.get('Direction Générale')
    
    if not directeur_rh or not dg:
        print("  ⚠ Directeur RH ou DG non trouvé, workflow non créé")
        return None
    
    # Étape 1: Directeur de direction (sera déterminé dynamiquement selon l'employé)
    # On crée une étape générique avec le Directeur Technique comme exemple
    directeur_tech = directors.get('Direction Technique')
    if directeur_tech:
        step1 = FlowStep.objects.create(
            flow=flow,
            name='Approbation Directeur de Direction',
            user=directeur_tech
        )
        print(f"    ✓ Étape 1: {step1.name} - {step1.user.email}")
        
        # Étape 2: Directeur RH (parent = step1)
        step2 = FlowStep.objects.create(
            flow=flow,
            name='Approbation Directeur RH',
            parent=step1,
            user=directeur_rh
        )
        print(f"    ✓ Étape 2: {step2.name} - {step2.user.email}")
        
        # Étape 3: Directeur Général (parent = step2)
        step3 = FlowStep.objects.create(
            flow=flow,
            name='Approbation Directeur Général',
            parent=step2,
            user=dg
        )
        print(f"    ✓ Étape 3: {step3.name} - {step3.user.email}")
    
    return flow

def create_workflow_for_director_leave(directors):
    """Crée le workflow d'approbation pour congé d'un directeur/sous-directeur"""
    print("\n🔄 Création du workflow d'approbation pour congé (directeur/sous-directeur)...")
    print("  ⚠ Note: Le système actuel ne supporte qu'un seul Flow par ContentType.")
    print("     Le workflow pour directeurs sera géré via la logique métier.")
    print("     Pour les directeurs, le workflow sera: Directeur RH → DG")
    
    # Le workflow pour directeurs sera géré dans le code
    # On ne crée pas de Flow séparé car il y a une contrainte unique sur content_type
    return None

def create_workflow_for_employee_mission(directors):
    """Crée le workflow d'approbation pour mission d'un employé normal"""
    print("\n🔄 Création du workflow d'approbation pour mission (employé)...")
    
    mission_content_type = ContentType.objects.get_for_model(Mission)
    
    # Supprimer tous les flows existants pour Mission
    existing_flows = Flow.objects.filter(content_type=mission_content_type)
    for f in existing_flows:
        FlowStep.objects.filter(flow=f).delete()
        f.delete()
    
    # Créer le Flow
    flow = Flow.objects.create(
        name='Workflow Approbation Mission - Employé',
        content_type=mission_content_type
    )
    print(f"  ✓ Flow créé: {flow.name}")
    
    directeur_rh = directors.get('Direction des Ressources Humaines')
    dg = directors.get('Direction Générale')
    directeur_tech = directors.get('Direction Technique')
    
    if not directeur_rh or not dg:
        print("  ⚠ Directeur RH ou DG non trouvé, workflow non créé")
        return None
    
    if directeur_tech:
        step1 = FlowStep.objects.create(
            flow=flow,
            name='Approbation Directeur de Direction',
            user=directeur_tech
        )
        print(f"    ✓ Étape 1: {step1.name} - {step1.user.email}")
        
        step2 = FlowStep.objects.create(
            flow=flow,
            name='Approbation Directeur RH',
            parent=step1,
            user=directeur_rh
        )
        print(f"    ✓ Étape 2: {step2.name} - {step2.user.email}")
        
        step3 = FlowStep.objects.create(
            flow=flow,
            name='Approbation Directeur Général',
            parent=step2,
            user=dg
        )
        print(f"    ✓ Étape 3: {step3.name} - {step3.user.email}")
    
    return flow

def create_workflow_for_director_mission(directors):
    """Crée le workflow d'approbation pour mission d'un directeur/sous-directeur"""
    print("\n🔄 Création du workflow d'approbation pour mission (directeur/sous-directeur)...")
    print("  ⚠ Note: Le système actuel ne supporte qu'un seul Flow par ContentType.")
    print("     Le workflow pour directeurs sera géré via la logique métier.")
    print("     Pour les directeurs, le workflow sera: Directeur RH → DG")
    
    # Le workflow pour directeurs sera géré dans le code
    return None

def main():
    """Fonction principale"""
    print("=" * 70)
    print("🚀 CONFIGURATION DES WORKFLOWS D'APPROBATION")
    print("=" * 70)
    
    try:
        # 1. Créer les directions et sous-directions avec directeurs
        directions, directors = create_directions_and_subdirections()
        
        # 2. Créer les workflows pour les congés
        create_workflow_for_employee_leave(directors)
        create_workflow_for_director_leave(directors)
        
        # 3. Créer les workflows pour les missions
        create_workflow_for_employee_mission(directors)
        create_workflow_for_director_mission(directors)
        
        print("\n" + "=" * 70)
        print("✅ CONFIGURATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 70)
        print(f"\n📊 Résumé:")
        print(f"  - {Direction.objects.count()} directions créées")
        print(f"  - {SubDirection.objects.count()} sous-directions créées")
        print(f"  - {Flow.objects.count()} workflows créés")
        print(f"  - {FlowStep.objects.count()} étapes de workflow créées")
        print(f"\n👥 Utilisateurs créés:")
        for dir_name, user in directors.items():
            print(f"  - {dir_name}: {user.email} (mot de passe: onip2024)")
        print("\n💡 Note: Les workflows sont associés aux modèles Leave et Mission.")
        print("   Lors de la création d'un congé ou d'une mission, les approbations")
        print("   seront automatiquement créées selon le workflow correspondant.")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
