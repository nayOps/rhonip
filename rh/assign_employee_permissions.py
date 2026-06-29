#!/usr/bin/env python
"""
Script pour assigner les permissions essentielles aux employés normaux.

Usage:
    python assign_employee_permissions.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payday.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

def create_employee_group():
    """Crée le groupe 'Employés' avec les permissions essentielles"""
    print("🔧 Création du groupe 'Employés'...")
    
    group, created = Group.objects.get_or_create(name='Employés')
    
    if created:
        print(f"  ✅ Groupe '{group.name}' créé")
    else:
        print(f"  ℹ️  Groupe '{group.name}' existe déjà")
    
    # Permissions essentielles
    permissions = [
        'leave.add_leave',
        'leave.view_leave',
        'leave.change_leave',
        'mission.add_mission',
        'mission.view_mission',
        'mission.change_mission',
        'employee.view_employee',
    ]
    
    # Permissions optionnelles
    permissions.extend([
        'leave.delete_leave',
        'mission.delete_mission',
        'employee.change_employee',
        'training.view_training',
    ])
    
    assigned_count = 0
    for perm_string in permissions:
        app_label, codename = perm_string.split('.')
        try:
            perm = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename
            )
            if perm not in group.permissions.all():
                group.permissions.add(perm)
                assigned_count += 1
                print(f"  ✅ Permission ajoutée: {perm_string}")
            else:
                print(f"  ℹ️  Permission déjà assignée: {perm_string}")
        except Permission.DoesNotExist:
            print(f"  ⚠️  Permission non trouvée: {perm_string}")
    
    print(f"\n📊 Groupe '{group.name}' configuré avec {group.permissions.count()} permissions")
    return group

def assign_group_to_employees(group):
    """Assigner le groupe à tous les employés normaux"""
    print("\n👥 Assignment du groupe aux employés...")
    
    employees = User.objects.filter(is_staff=False, is_superuser=False, is_active=True)
    
    if not employees.exists():
        print("  ⚠️  Aucun employé normal trouvé")
        return
    
    assigned_count = 0
    for employee in employees:
        if group not in employee.groups.all():
            employee.groups.add(group)
            assigned_count += 1
            print(f"  ✅ Groupe assigné à: {employee.email}")
        else:
            print(f"  ℹ️  Groupe déjà assigné à: {employee.email}")
    
    print(f"\n📊 {assigned_count} employé(s) ont reçu le groupe")
    print(f"📊 Total employés avec le groupe: {employees.filter(groups=group).count()}")

def verify_permissions():
    """Vérifier les permissions des employés"""
    print("\n🔍 Vérification des permissions...")
    
    employees = User.objects.filter(is_staff=False, is_superuser=False, is_active=True)
    group = Group.objects.filter(name='Employés').first()
    
    if not group:
        print("  ⚠️  Groupe 'Employés' non trouvé")
        return
    
    for employee in employees[:5]:  # Limiter à 5 pour l'affichage
        all_perms = employee.get_all_permissions()
        print(f"\n  👤 {employee.email}:")
        print(f"     - Permissions totales: {len(all_perms)}")
        if all_perms:
            print(f"     - Exemples: {', '.join(list(all_perms)[:3])}")

def main():
    print("=" * 70)
    print("🔐 ASSIGNATION DES PERMISSIONS AUX EMPLOYÉS")
    print("=" * 70)
    
    # 1. Créer le groupe avec permissions
    group = create_employee_group()
    
    # 2. Assigner le groupe aux employés
    assign_group_to_employees(group)
    
    # 3. Vérifier
    verify_permissions()
    
    print("\n" + "=" * 70)
    print("✅ Configuration terminée!")
    print("=" * 70)
    print("\n📋 Permissions assignées:")
    print("   - leave.add_leave, leave.view_leave, leave.change_leave")
    print("   - mission.add_mission, mission.view_mission, mission.change_mission")
    print("   - employee.view_employee")
    print("\n💡 Les employés peuvent maintenant:")
    print("   - Créer et voir leurs congés")
    print("   - Créer et voir leurs missions")
    print("   - Voir leur profil")

if __name__ == '__main__':
    main()
