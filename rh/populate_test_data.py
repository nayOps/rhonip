#!/usr/bin/env python
"""
Script pour créer des données de test complètes :
- 10 employés avec toutes les informations
- Congés
- Formations
- Missions
- Départs anticipés
- Heures supplémentaires
- Présences
- Demandes d'information
"""

import os
import django
from datetime import date, timedelta, datetime, time
from random import choice, randint

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payday.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.apps import apps
from django.utils import timezone

User = get_user_model()
Employee = apps.get_model('employee', 'Employee')
Designation = apps.get_model('employee', 'Designation')
Agreement = apps.get_model('employee', 'Agreement')
Grade = apps.get_model('employee', 'Grade')
Direction = apps.get_model('employee', 'Direction')
SubDirection = apps.get_model('employee', 'SubDirection')
Service = apps.get_model('employee', 'Service')
Branch = apps.get_model('employee', 'Branch')
Status = apps.get_model('employee', 'Status')
Child = apps.get_model('employee', 'Child')
Education = apps.get_model('employee', 'Education')
Experience = apps.get_model('employee', 'Experience')
Document = apps.get_model('employee', 'Document')
Attendance = apps.get_model('employee', 'Attendance')
Overtime = apps.get_model('employee', 'Overtime')
RequestForInfo = apps.get_model('employee', 'RequestForInfo')
ReplyWithInfo = apps.get_model('employee', 'ReplyWithInfo')

Leave = apps.get_model('leave', 'Leave')
TypeOfLeave = apps.get_model('leave', 'TypeOfLeave')
EarlyLeave = apps.get_model('leave', 'EarlyLeave')
Holiday = apps.get_model('leave', 'Holiday')

Mission = apps.get_model('mission', 'Mission')
Report = apps.get_model('mission', 'Report')

Training = apps.get_model('training', 'Training')

# Données de test
EMPLOYEES_DATA = [
    {
        'registration_number': 'EMP001',
        'first_name': 'Jean',
        'middle_name': 'Pierre',
        'last_name': 'KABONGO',
        'gender': 'male',
        'email': 'jean.kabongo@onip.cd',
        'designation': 'Directeur Général',
        'direction': 'Direction Générale',
        'service': 'Administration',
    },
    {
        'registration_number': 'EMP002',
        'first_name': 'Marie',
        'middle_name': 'Claire',
        'last_name': 'MUKAMBA',
        'gender': 'female',
        'email': 'marie.mukamba@onip.cd',
        'designation': 'Responsable RH',
        'direction': 'Ressources Humaines',
        'service': 'Gestion du Personnel',
    },
    {
        'registration_number': 'EMP003',
        'first_name': 'Paul',
        'middle_name': 'Antoine',
        'last_name': 'KASENGA',
        'gender': 'male',
        'email': 'paul.kasenga@onip.cd',
        'designation': 'Chef de Projet',
        'direction': 'Direction Technique',
        'service': 'Développement',
    },
    {
        'registration_number': 'EMP004',
        'first_name': 'Sophie',
        'middle_name': 'Agnès',
        'last_name': 'LUBAMBA',
        'gender': 'female',
        'email': 'sophie.lubamba@onip.cd',
        'designation': 'Comptable',
        'direction': 'Direction Financière',
        'service': 'Comptabilité',
    },
    {
        'registration_number': 'EMP005',
        'first_name': 'David',
        'middle_name': 'Marcel',
        'last_name': 'KALONJI',
        'gender': 'male',
        'email': 'david.kalonji@onip.cd',
        'designation': 'Développeur',
        'direction': 'Direction Technique',
        'service': 'Développement',
    },
    {
        'registration_number': 'EMP006',
        'first_name': 'Aline',
        'middle_name': 'Grace',
        'last_name': 'NKULU',
        'gender': 'female',
        'email': 'aline.nkulu@onip.cd',
        'designation': 'Assistante',
        'direction': 'Direction Générale',
        'service': 'Secrétariat',
    },
    {
        'registration_number': 'EMP007',
        'first_name': 'Thomas',
        'middle_name': 'Joseph',
        'last_name': 'MULUMBA',
        'gender': 'male',
        'email': 'thomas.mulumba@onip.cd',
        'designation': 'Analyste',
        'direction': 'Direction Technique',
        'service': 'Analyse',
    },
    {
        'registration_number': 'EMP008',
        'first_name': 'Julie',
        'middle_name': 'Béatrice',
        'last_name': 'KAPENGA',
        'gender': 'female',
        'email': 'julie.kapenga@onip.cd',
        'designation': 'Responsable Communication',
        'direction': 'Direction Générale',
        'service': 'Communication',
    },
    {
        'registration_number': 'EMP009',
        'first_name': 'Marc',
        'middle_name': 'André',
        'last_name': 'KATEMBO',
        'gender': 'male',
        'email': 'marc.katembo@onip.cd',
        'designation': 'Technicien',
        'direction': 'Direction Technique',
        'service': 'Support',
    },
    {
        'registration_number': 'EMP010',
        'first_name': 'Céline',
        'middle_name': 'Dorothée',
        'last_name': 'MUTOMBO',
        'gender': 'female',
        'email': 'celine.mutombo@onip.cd',
        'designation': 'Chargée de Mission',
        'direction': 'Direction Générale',
        'service': 'Projets',
    },
]

def get_or_create_model(model_class, **kwargs):
    """Crée ou récupère un objet"""
    obj, created = model_class.objects.get_or_create(**kwargs)
    return obj

def create_base_data():
    """Crée les données de base nécessaires"""
    print("📋 Création des données de base...")
    
    # Designations
    designations = {}
    for name in ['Directeur Général', 'Responsable RH', 'Chef de Projet', 'Comptable', 
                 'Développeur', 'Assistante', 'Analyste', 'Responsable Communication', 
                 'Technicien', 'Chargée de Mission']:
        designations[name] = get_or_create_model(Designation, name=name)
    
    # Agreements
    agreements = {}
    for name in ['CDI', 'CDD', 'Stage']:
        agreements[name] = get_or_create_model(Agreement, name=name)
    
    # Grades
    grades = {}
    for name in ['A', 'B', 'C', 'D', 'E']:
        grades[name] = get_or_create_model(Grade, name=name)
    
    # Directions
    directions = {}
    for name in ['Direction Générale', 'Ressources Humaines', 'Direction Technique', 
                 'Direction Financière']:
        directions[name] = get_or_create_model(Direction, name=name)
    
    # Services
    services = {}
    for name in ['Administration', 'Gestion du Personnel', 'Développement', 'Comptabilité',
                 'Secrétariat', 'Analyse', 'Communication', 'Support', 'Projets']:
        services[name] = get_or_create_model(Service, name=name)
    
    # Branches
    branches = {}
    for name in ['Siège', 'Branche Est', 'Branche Ouest']:
        branches[name] = get_or_create_model(Branch, name=name)
    
    # Status
    statuses = {}
    for name in ['Actif', 'Inactif', 'En congé']:
        statuses[name] = get_or_create_model(Status, name=name)
    
    # Types de congés
    leave_types = {}
    for name, max_days in [('Congé annuel', 30), ('Congé maladie', 15), 
                           ('Congé maternité', 90), ('Congé sans solde', 0)]:
        leave_types[name] = get_or_create_model(TypeOfLeave, name=name, max_days_per_year=max_days)
    
    return {
        'designations': designations,
        'agreements': agreements,
        'grades': grades,
        'directions': directions,
        'services': services,
        'branches': branches,
        'statuses': statuses,
        'leave_types': leave_types,
    }

def create_employees(base_data):
    """Crée les 10 employés"""
    print("\n👥 Création des 10 employés...")
    employees = []
    
    for i, emp_data in enumerate(EMPLOYEES_DATA):
        # Récupérer les objets liés
        designation = base_data['designations'].get(emp_data['designation'])
        direction = base_data['directions'].get(emp_data['direction'])
        service = base_data['services'].get(emp_data['service'])
        branch = base_data['branches'].get('Siège')
        agreement = base_data['agreements'].get('CDI')
        grade = base_data['grades'].get(choice(['A', 'B', 'C']))

        # Date de naissance (entre 25 et 50 ans)
        birth_year = 1974 + randint(0, 25)
        birth_date = date(birth_year, randint(1, 12), randint(1, 28))
        
        # Date d'engagement (il y a 1 à 10 ans)
        join_date = date.today() - timedelta(days=randint(365, 3650))
        
        employee, created = Employee.objects.get_or_create(
            registration_number=emp_data['registration_number'],
            defaults={
                'first_name': emp_data['first_name'],
                'middle_name': emp_data['middle_name'],
                'last_name': emp_data['last_name'],
                'gender': emp_data['gender'],
                'email': emp_data['email'],
                'email_professional': emp_data['email'],
                'designation': designation,
                'direction': direction,
                'service': service,
                'branch': branch,
                'agreement': agreement,
                'grade': grade,
                'agent_situation': 'active',
                'date_of_birth': birth_date,
                'date_of_join': join_date,
                'place_of_birth': 'Kinshasa',
                'citizenship': 'République démocratique du Congo',
                'home_country': 'République démocratique du Congo',
                'home_province': 'Kinshasa',
                'marital_status': choice(['maried', 'single']),
                'telephone_number': f'+243{randint(800000000, 999999999)}',
                'mobile_number': f'+243{randint(800000000, 999999999)}',
                'physical_address': f'Quartier {choice(["Gombe", "Lingwala", "Kasa-Vubu", "Ngaliema"])}, Kinshasa',
                'payment_method': choice(['bank', 'mobile money']),
                'payer_name': 'Banque Commerciale',
                'payment_account': f'{randint(1000000000, 9999999999)}',
                'type_of_identity': 'national_id',
                'identity_number': f'{randint(100000000, 999999999)}',
                'date_of_issue': join_date - timedelta(days=365),
                'date_of_expiry': join_date + timedelta(days=365*5),
            }
        )
        
        # Ne pas créer d'utilisateurs automatiquement pour éviter les conflits
        # Les utilisateurs peuvent être créés manuellement via l'interface
        
        # Ajouter des enfants (pour certains employés)
        if employee.marital_status == 'maried' and randint(1, 3) == 1:
            for j in range(randint(1, 3)):
                Child.objects.get_or_create(
                    employee=employee,
                    full_name=f'Enfant {j+1} {employee.last_name}',
                    date_of_birth=date.today() - timedelta(days=randint(365*2, 365*10)),
                )
        
        # Ajouter une éducation
        from employee.models.education_references import Degree, FieldOfStudy, Institution, StudyLevel
        from employee.utils.education_references import resolve_reference

        institution = resolve_reference(Institution, choice(['Université de Kinshasa', 'Université Pédagogique Nationale', 'ISTA']))
        degree = resolve_reference(Degree, choice(['Licence', 'Master', 'Doctorat']))
        field_of_study = resolve_reference(FieldOfStudy, choice(['Informatique', 'Gestion', 'Droit', 'Communication']))
        Education.objects.get_or_create(
            employee=employee,
            defaults={
                'institution': institution,
                'degree': degree,
                'field_of_study': field_of_study,
                'study_level': resolve_reference(StudyLevel, 'Licence (Bac+5)'),
            }
        )
        
        # Ajouter une expérience
        Experience.objects.get_or_create(
            employee=employee,
            defaults={
                'organization': f'Entreprise {randint(1, 5)}',
                'position': employee.designation.name if employee.designation else 'Poste précédent',
                'start_date': join_date - timedelta(days=randint(365, 1825)),
                'end_date': join_date - timedelta(days=1),
            }
        )
        
        employees.append(employee)
        print(f"  ✓ {employee.full_name()} créé (ID: {employee.id})")
    
    return employees

def create_leaves(employees, base_data):
    """Crée des congés pour les employés"""
    print("\n🏖️ Création des congés...")
    
    leave_type = base_data['leave_types']['Congé annuel']
    
    for i, employee in enumerate(employees[:7]):  # 7 employés avec congés
        start_date = date.today() + timedelta(days=randint(30, 90))
        end_date = start_date + timedelta(days=randint(5, 15))
        
        # Choisir un remplaçant différent
        interim = choice([e for e in employees if e.id != employee.id])
        
        Leave.objects.get_or_create(
            employee=employee,
            start_dt=start_date,
            defaults={
                'type_of_leave': leave_type,
                'end_dt': end_date,
                'interim': interim,
                'reason': f'Congé annuel de {employee.full_name()}',
            }
        )
        print(f"  ✓ Congé créé pour {employee.full_name()} du {start_date} au {end_date}")

def create_early_leaves(employees):
    """Crée des départs anticipés"""
    print("\n⏰ Création des départs anticipés...")
    
    for i, employee in enumerate(employees[:5]):  # 5 employés
        leave_date = date.today() - timedelta(days=randint(1, 30))
        start_time = time(randint(14, 16), randint(0, 59))
        end_time = time(randint(17, 18), randint(0, 59))
        
        EarlyLeave.objects.get_or_create(
            employee=employee,
            date=leave_date,
            start_time=start_time,
            defaults={
                'destination': choice(['Rendez-vous médical', 'Urgence familiale', 'Affaire personnelle']),
                'end_time': end_time,
                'reason': f'Départ anticipé pour {choice(["rendez-vous", "urgence", "affaire personnelle"])}',
            }
        )
        print(f"  ✓ Départ anticipé créé pour {employee.full_name()} le {leave_date}")

def create_trainings(employees):
    """Crée des formations"""
    print("\n📚 Création des formations...")
    
    trainings_data = [
        {
            'name': 'Formation Django Avancé',
            'description': 'Formation approfondie sur Django et les bonnes pratiques',
            'place_of_training': 'Kinshasa',
            'trainer': 'Expert Django',
            'start_date': date.today() - timedelta(days=60),
            'end_date': date.today() - timedelta(days=30),
            'has_certificate': True,
            'is_completed': True,
        },
        {
            'name': 'Gestion de Projet Agile',
            'description': 'Formation sur les méthodologies agiles',
            'place_of_training': 'Kinshasa',
            'trainer': 'Coach Agile',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=35),
            'has_certificate': True,
            'is_completed': False,
        },
        {
            'name': 'Communication Interpersonnelle',
            'description': 'Améliorer les compétences en communication',
            'place_of_training': 'Kinshasa',
            'trainer': 'Coach Communication',
            'start_date': date.today() - timedelta(days=15),
            'end_date': date.today() - timedelta(days=10),
            'has_certificate': False,
            'is_completed': True,
        },
    ]
    
    for training_data in trainings_data:
        training, created = Training.objects.get_or_create(
            name=training_data['name'],
            defaults=training_data
        )
        print(f"  ✓ Formation '{training.name}' créée")

def create_missions(employees):
    """Crée des missions avec rapports"""
    print("\n🚀 Création des missions...")
    
    missions_data = [
        {
            'name': 'Mission à Goma',
            'description': 'Mission d\'évaluation des projets dans la région',
            'destination': 'Goma, Nord-Kivu',
            'start_date': date.today() - timedelta(days=45),
            'end_date': date.today() - timedelta(days=40),
            'employees': employees[2:5],  # 3 employés
        },
        {
            'name': 'Formation à Lubumbashi',
            'description': 'Formation des équipes locales',
            'destination': 'Lubumbashi, Haut-Katanga',
            'start_date': date.today() + timedelta(days=20),
            'end_date': date.today() + timedelta(days=25),
            'employees': employees[0:2],  # 2 employés
        },
        {
            'name': 'Audit à Kisangani',
            'description': 'Audit des systèmes informatiques',
            'destination': 'Kisangani, Tshopo',
            'start_date': date.today() - timedelta(days=20),
            'end_date': date.today() - timedelta(days=15),
            'employees': employees[6:8],  # 2 employés
        },
    ]
    
    for mission_data in missions_data:
        mission, created = Mission.objects.get_or_create(
            name=mission_data['name'],
            defaults={
                'description': mission_data['description'],
                'destination': mission_data['destination'],
                'start_date': mission_data['start_date'],
                'end_date': mission_data['end_date'],
            }
        )
        
        # Ajouter les employés
        mission.employees.set(mission_data['employees'])
        
        # Créer des rapports pour les missions passées
        if mission.end_date < date.today():
            for employee in mission_data['employees']:
                Report.objects.get_or_create(
                    mission=mission,
                    employee=employee,
                    defaults={
                        'document': None,  # Pas de fichier pour le test
                    }
                )
        
        print(f"  ✓ Mission '{mission.name}' créée avec {len(mission_data['employees'])} employés")

def create_attendances(employees):
    """Crée des pointages sur 4 plages (code du travail ONIP)."""
    print("\n⏱️ Création des pointages (4 plages)...")

    for employee in employees:
        for day in range(30):
            attendance_date = date.today() - timedelta(days=day)
            if attendance_date.weekday() >= 5:
                continue

            scenario = randint(1, 100)
            punches = []

            if scenario <= 8:
                continue

            if scenario <= 20:
                punches.append(time(8, randint(5, 40)))
            else:
                punches.append(time(7, randint(50, 59)) if scenario <= 30 else time(8, randint(0, 15)))

            if scenario not in (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22):
                lunch_out = time(12, randint(0, 30))
                break_minutes = randint(55, 65)
                lunch_in_minutes = 12 * 60 + lunch_out.minute + break_minutes
                lunch_in = time(lunch_in_minutes // 60, lunch_in_minutes % 60)
                punches.extend([lunch_out, lunch_in])

            if scenario not in (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20):
                punches.append(time(16, randint(0, 10)))

            for punch_time in sorted(set(punches)):
                Attendance.objects.get_or_create(
                    employee=employee,
                    date=attendance_date,
                    time=punch_time,
                    defaults={'source': 'manual'},
                )

        print(f"  ✓ Pointages créés pour {employee.full_name()} (30 jours)")

def create_overtimes(employees):
    """Crée des heures supplémentaires"""
    print("\n⏰ Création des heures supplémentaires...")
    
    for i, employee in enumerate(employees[:6]):  # 6 employés
        overtime_date = date.today() - timedelta(days=randint(1, 20))
        from_time = time(randint(17, 18), randint(0, 59))
        to_time = time(randint(19, 21), randint(0, 59))
        
        Overtime.objects.get_or_create(
            employee=employee,
            date=overtime_date,
            from_time=from_time,
            defaults={
                'to_time': to_time,
                'reason': f'Heures supplémentaires pour {choice(["projet urgent", "deadline", "support client"])}',
            }
        )
        print(f"  ✓ Heures supplémentaires créées pour {employee.full_name()} le {overtime_date}")

def create_requests_for_info(employees):
    """Crée des demandes d'information"""
    print("\n📋 Création des demandes d'information...")
    
    # Utiliser le superutilisateur existant ou créer une demande sans utilisateurs
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            # Créer une demande simple
            request = RequestForInfo.objects.create(
                name='Demande de documents administratifs',
                description='Besoin des documents administratifs pour le projet X',
                created_by=admin_user,
            )
            # Ajouter quelques utilisateurs si disponibles
            users = list(User.objects.filter(is_active=True)[:4])
            if len(users) > 1:
                request.users.set(users[1:])
            
            print(f"  ✓ Demande d'information créée")
        else:
            print(f"  ⚠ Aucun superutilisateur trouvé, demande d'information non créée")
    except Exception as e:
        print(f"  ⚠ Erreur lors de la création de la demande d'information: {e}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 CRÉATION DES DONNÉES DE TEST")
    print("=" * 60)
    
    try:
        # 1. Créer les données de base
        base_data = create_base_data()
        
        # 2. Créer les employés
        employees = create_employees(base_data)
        
        # 3. Créer les congés
        create_leaves(employees, base_data)
        
        # 4. Créer les départs anticipés
        create_early_leaves(employees)
        
        # 5. Créer les formations
        create_trainings(employees)
        
        # 6. Créer les missions
        create_missions(employees)
        
        # 7. Créer les présences
        create_attendances(employees)
        
        # 8. Créer les heures supplémentaires
        create_overtimes(employees)
        
        # 9. Créer les demandes d'information
        create_requests_for_info(employees)
        
        print("\n" + "=" * 60)
        print("✅ DONNÉES DE TEST CRÉÉES AVEC SUCCÈS!")
        print("=" * 60)
        print(f"\n📊 Résumé:")
        print(f"  - {len(employees)} employés créés")
        print(f"  - {Leave.objects.count()} congés créés")
        print(f"  - {EarlyLeave.objects.count()} départs anticipés créés")
        print(f"  - {Training.objects.count()} formations créées")
        print(f"  - {Mission.objects.count()} missions créées")
        print(f"  - {Report.objects.count()} rapports de mission créés")
        print(f"  - {Attendance.objects.count()} présences créées")
        print(f"  - {Overtime.objects.count()} heures supplémentaires créées")
        print(f"  - {RequestForInfo.objects.count()} demandes d'information créées")
        print("\n🎉 Vous pouvez maintenant tester l'application complètement!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
