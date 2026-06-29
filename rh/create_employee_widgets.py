#!/usr/bin/env python
"""
Script pour créer les widgets pour les employés dans le dashboard.

Usage:
    python create_employee_widgets.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payday.settings')
django.setup()

from django.contrib.auth.models import Permission
from core.models import Widget

def create_widgets():
    """Crée les widgets pour les employés"""
    print("🔧 Création des widgets pour les employés...")
    
    widgets_data = [
        {
            'name': 'Mon Profil',
            'description': 'Affiche les informations principales de votre profil',
            'permission_codename': 'view_employee',
            'permission_app': 'employee',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body text-center">
            {% if employee.photo %}
                <img src="{{ employee.photo.url }}" class="rounded-circle mb-3" width="100" height="100" style="object-fit: cover;">
            {% else %}
                <div class="rounded-circle bg-secondary mb-3 d-inline-flex align-items-center justify-content-center text-white" style="width: 100px; height: 100px;">
                    <i class="bi bi-person-fill" style="font-size: 3rem;"></i>
                </div>
            {% endif %}
            <h5 class="card-title">{{ employee.full_name }}</h5>
            <p class="text-muted mb-1"><strong>Matricule:</strong> {{ employee.registration_number }}</p>
            {% if employee.designation %}
                <p class="text-muted mb-1"><strong>Position:</strong> {{ employee.designation.name }}</p>
            {% endif %}
            {% if employee.direction %}
                <p class="text-muted mb-3"><strong>Direction:</strong> {{ employee.direction.name }}</p>
            {% endif %}
            <a href="{% url 'employee:my_profile' %}" class="btn btn-primary">
                <i class="bi bi-eye"></i> Voir mon profil
            </a>
        </div>
    </div>
</div>''',
            'view': '''from employee.models import Employee

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee'''
        },
        {
            'name': 'Mes Congés',
            'description': 'Statistiques de vos congés',
            'permission_codename': 'view_leave',
            'permission_app': 'leave',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-calendar-check"></i> Mes Congés</h5>
            <div class="row mt-3">
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-primary">{{ pending_leaves }}</h3>
                        <p class="text-muted small">En attente</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-success">{{ approved_leaves }}</h3>
                        <p class="text-muted small">Approuvés</p>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <a href="{% url 'core:list' app='leave' model='leave' %}" class="btn btn-outline-primary btn-sm w-100">
                    <i class="bi bi-list"></i> Voir tous mes congés
                </a>
            </div>
        </div>
    </div>
</div>''',
            'view': '''from leave.models import Leave
from core.models import Approbation

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee

if employee:
    leaves = Leave.objects.filter(employee=employee)
    pending_leaves = 0
    approved_leaves = 0
    
    for leave in leaves:
        approbations = Approbation.objects.for_model(Leave).filter(object_id=leave.id)
        if approbations.exists() and not approbations.is_fully_approved():
            pending_leaves += 1
        elif approbations.is_fully_approved():
            approved_leaves += 1
else:
    pending_leaves = 0
    approved_leaves = 0'''
        },
        {
            'name': 'Mes Missions',
            'description': 'Statistiques de vos missions',
            'permission_codename': 'view_mission',
            'permission_app': 'mission',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-airplane"></i> Mes Missions</h5>
            <div class="row mt-3">
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-info">{{ current_missions }}</h3>
                        <p class="text-muted small">En cours</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-warning">{{ upcoming_missions }}</h3>
                        <p class="text-muted small">À venir</p>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <a href="{% url 'core:list' app='mission' model='mission' %}" class="btn btn-outline-info btn-sm w-100">
                    <i class="bi bi-list"></i> Voir toutes mes missions
                </a>
            </div>
        </div>
    </div>
</div>''',
            'view': '''from mission.models import Mission
from datetime import date

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee
today = date.today()

if employee:
    missions = Mission.objects.filter(employees=employee)
    current_missions = missions.filter(start_date__lte=today, end_date__gte=today).count()
    upcoming_missions = missions.filter(start_date__gt=today).count()
else:
    current_missions = 0
    upcoming_missions = 0'''
        },
        {
            'name': 'Actions Requises',
            'description': 'Vos approbations et notifications en attente',
            'permission_codename': None,
            'permission_app': None,
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-bell"></i> Actions Requises</h5>
            <div class="row mt-3">
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-warning">{{ action_required_count }}</h3>
                        <p class="text-muted small">Approbations</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-primary">{{ unread_notifications }}</h3>
                        <p class="text-muted small">Notifications</p>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <a href="{% url 'core:action-required' %}" class="btn btn-outline-warning btn-sm w-100 mb-2">
                    <i class="bi bi-lightning-fill"></i> Actions requises
                </a>
                <a href="{% url 'core:notifications' %}" class="btn btn-outline-primary btn-sm w-100">
                    <i class="bi bi-bell"></i> Notifications
                </a>
            </div>
        </div>
    </div>
</div>''',
            'view': '''from core.models import Approbation

action_required_count = 0
unread_notifications = 0
if request and hasattr(request, 'user'):
    action_required_count = Approbation.objects.filter(user=request.user, action__isnull=True).count()
    unread_notifications = request.user.notifications.unread().count()'''
        },
        {
            'name': 'Mes Départs Anticipés',
            'description': 'Vos départs anticipés récents et à venir',
            'permission_codename': 'view_earlyleave',
            'permission_app': 'leave',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-clock-history"></i> Mes Départs Anticipés</h5>
            <div class="row mt-3">
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-info">{{ recent_early_leaves }}</h3>
                        <p class="text-muted small">Ce mois</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-secondary">{{ total_early_leaves }}</h3>
                        <p class="text-muted small">Total</p>
                    </div>
                </div>
            </div>
            {% if next_early_leave %}
            <div class="mt-3 p-2 bg-light rounded">
                <small class="text-muted">Prochain départ:</small><br>
                <strong>{{ next_early_leave.date|date:"d/m/Y" }}</strong> à {{ next_early_leave.start_time }}
            </div>
            {% endif %}
            <div class="mt-3">
                <a href="{% url 'core:list' app='leave' model='earlyleave' %}" class="btn btn-outline-info btn-sm w-100">
                    <i class="bi bi-list"></i> Voir tous mes départs
                </a>
            </div>
        </div>
    </div>
</div>''',
            'view': '''from leave.models import EarlyLeave
from datetime import date, timedelta

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee

today = date.today()
first_day_month = today.replace(day=1)
next_month = (first_day_month + timedelta(days=32)).replace(day=1)
last_day_month = next_month - timedelta(days=1)

if employee:
    early_leaves = EarlyLeave.objects.filter(employee=employee)
    recent_early_leaves = early_leaves.filter(date__gte=first_day_month, date__lte=last_day_month).count()
    total_early_leaves = early_leaves.count()
    next_early_leave = early_leaves.filter(date__gte=today).order_by('date', 'start_time').first()
else:
    recent_early_leaves = 0
    total_early_leaves = 0
    next_early_leave = None'''
        },
        {
            'name': 'Mes Heures Supplémentaires',
            'description': 'Statistiques de vos heures supplémentaires',
            'permission_codename': 'view_overtime',
            'permission_app': 'employee',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-hourglass-split"></i> Mes Heures Supplémentaires</h5>
            <div class="row mt-3">
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-success">{{ month_hours }}</h3>
                        <p class="text-muted small">Ce mois</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <h3 class="text-primary">{{ total_hours }}</h3>
                        <p class="text-muted small">Total</p>
                    </div>
                </div>
            </div>
            {% if recent_overtime %}
            <div class="mt-3 p-2 bg-light rounded">
                <small class="text-muted">Dernière:</small><br>
                <strong>{{ recent_overtime.date|date:"d/m/Y" }}</strong><br>
                <small>{{ recent_overtime.from_time }} - {{ recent_overtime.to_time }}</small>
            </div>
            {% endif %}
            <div class="mt-3">
                <a href="{% url 'core:list' app='employee' model='overtime' %}" class="btn btn-outline-success btn-sm w-100">
                    <i class="bi bi-list"></i> Voir toutes mes heures
                </a>
            </div>
        </div>
    </div>
</div>''',
            'view': '''from employee.models import Overtime
from datetime import date, timedelta, datetime

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee

today = date.today()
first_day_month = today.replace(day=1)
next_month = (first_day_month + timedelta(days=32)).replace(day=1)
last_day_month = next_month - timedelta(days=1)

if employee:
    overtimes = Overtime.objects.filter(employee=employee)
    month_overtimes = overtimes.filter(date__gte=first_day_month, date__lte=last_day_month)
    
    month_hours = 0
    for ot in month_overtimes:
        from_time = datetime.strptime(str(ot.from_time), '%H:%M:%S').time()
        to_time = datetime.strptime(str(ot.to_time), '%H:%M:%S').time()
        from_dt = datetime.combine(date.today(), from_time)
        to_dt = datetime.combine(date.today(), to_time)
        if to_dt < from_dt:
            to_dt += timedelta(days=1)
        diff = to_dt - from_dt
        month_hours += diff.total_seconds() / 3600
    
    total_hours = 0
    for ot in overtimes:
        from_time = datetime.strptime(str(ot.from_time), '%H:%M:%S').time()
        to_time = datetime.strptime(str(ot.to_time), '%H:%M:%S').time()
        from_dt = datetime.combine(date.today(), from_time)
        to_dt = datetime.combine(date.today(), to_time)
        if to_dt < from_dt:
            to_dt += timedelta(days=1)
        diff = to_dt - from_dt
        total_hours += diff.total_seconds() / 3600
    
    recent_overtime = overtimes.order_by('-date', '-from_time').first()
else:
    month_hours = 0
    total_hours = 0
    recent_overtime = None'''
        },
        {
            'name': 'Statistiques Annuelle',
            'description': 'Résumé de vos activités de l\'année',
            'permission_codename': 'view_employee',
            'permission_app': 'employee',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-graph-up"></i> Statistiques Annuelle</h5>
            <div class="mt-3">
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Congés pris:</span>
                    <strong>{{ year_leaves_days }} jours</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Missions:</span>
                    <strong>{{ year_missions }}</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-muted">Heures supp.:</span>
                    <strong>{{ year_overtime_hours|floatformat:1 }}h</strong>
                </div>
                <div class="d-flex justify-content-between">
                    <span class="text-muted">Départs anticipés:</span>
                    <strong>{{ year_early_leaves }}</strong>
                </div>
            </div>
            <div class="mt-3 pt-3 border-top">
                <small class="text-muted">Année {{ current_year }}</small>
            </div>
        </div>
    </div>
</div>''',
            'view': '''from leave.models import Leave, EarlyLeave
from mission.models import Mission
from employee.models import Overtime
from core.models import Approbation
from datetime import date, datetime, timedelta

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee

current_year = date.today().year
year_start = date(current_year, 1, 1)
year_end = date(current_year, 12, 31)

if employee:
    year_leaves = Leave.objects.filter(employee=employee, start_dt__gte=year_start, start_dt__lte=year_end)
    year_leaves_days = sum(leave.days for leave in year_leaves if hasattr(leave, 'days'))
    
    year_missions = Mission.objects.filter(employees=employee, start_date__gte=year_start, start_date__lte=year_end).count()
    
    year_overtimes = Overtime.objects.filter(employee=employee, date__gte=year_start, date__lte=year_end)
    year_overtime_hours = 0
    for ot in year_overtimes:
        from_time = datetime.strptime(str(ot.from_time), '%H:%M:%S').time()
        to_time = datetime.strptime(str(ot.to_time), '%H:%M:%S').time()
        from_dt = datetime.combine(date.today(), from_time)
        to_dt = datetime.combine(date.today(), to_time)
        if to_dt < from_dt:
            to_dt += timedelta(days=1)
        diff = to_dt - from_dt
        year_overtime_hours += diff.total_seconds() / 3600
    
    year_early_leaves = EarlyLeave.objects.filter(employee=employee, date__gte=year_start, date__lte=year_end).count()
else:
    year_leaves_days = 0
    year_missions = 0
    year_overtime_hours = 0
    year_early_leaves = 0'''
        },
        {
            'name': 'Prochaines Échéances',
            'description': 'Vos congés et missions à venir',
            'permission_codename': 'view_leave',
            'permission_app': 'leave',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-calendar-event"></i> Prochaines Échéances</h5>
            <div class="mt-3">
                {% if next_leave %}
                <div class="mb-3 p-2 bg-light rounded">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-calendar-check text-primary me-2"></i>
                        <div class="flex-grow-1">
                            <strong>Congé</strong><br>
                            <small>{{ next_leave.start_dt|date:"d/m/Y" }} - {{ next_leave.end_dt|date:"d/m/Y" }}</small>
                        </div>
                    </div>
                </div>
                {% endif %}
                {% if next_mission %}
                <div class="mb-3 p-2 bg-light rounded">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-airplane text-info me-2"></i>
                        <div class="flex-grow-1">
                            <strong>{{ next_mission.name }}</strong><br>
                            <small>{{ next_mission.start_date|date:"d/m/Y" }} - {{ next_mission.end_date|date:"d/m/Y" }}</small>
                        </div>
                    </div>
                </div>
                {% endif %}
                {% if not next_leave and not next_mission %}
                <p class="text-muted text-center">Aucune échéance à venir</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>''',
            'view': '''from leave.models import Leave
from mission.models import Mission
from core.models import Approbation
from datetime import date

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee

today = date.today()

if employee:
    approved_leaves = []
    leaves = Leave.objects.filter(employee=employee, start_dt__gte=today).order_by('start_dt')
    for leave in leaves:
        approbations = Approbation.objects.for_model(Leave).filter(object_id=leave.id)
        if approbations.exists() and approbations.is_fully_approved():
            approved_leaves.append(leave)
    
    next_leave = approved_leaves[0] if approved_leaves else None
    
    missions = Mission.objects.filter(employees=employee, start_date__gte=today).order_by('start_date')
    next_mission = missions.first() if missions.exists() else None
else:
    next_leave = None
    next_mission = None'''
        },
        {
            'name': 'Calendrier Mensuel',
            'description': 'Vos congés approuvés du mois en cours',
            'permission_codename': 'view_leave',
            'permission_app': 'leave',
            'template': '''<div class="col-md-6 col-lg-4">
    <div class="card">
        <div class="card-body">
            <h5 class="card-title"><i class="bi bi-calendar-month"></i> Calendrier Mensuel</h5>
            <div class="mt-3">
                <div class="text-center mb-3">
                    <h4 class="text-primary">{{ current_month_name }} {{ current_year }}</h4>
                    <p class="text-muted small">{{ month_leaves_count }} congé(s) approuvé(s)</p>
                </div>
                {% if month_leaves %}
                <div class="list-group list-group-flush">
                    {% for leave in month_leaves|slice:":5" %}
                    <div class="list-group-item px-0 py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>{{ leave.start_dt|date:"d" }}{% if leave.start_dt != leave.end_dt %} - {{ leave.end_dt|date:"d" }}{% endif %}</strong>
                                <small class="text-muted d-block">{{ leave.type_of_leave.name|default:"Congé" }}</small>
                            </div>
                            <span class="badge bg-success">{{ leave.days }} jour(s)</span>
                        </div>
                    </div>
                    {% endfor %}
                    {% if month_leaves|length > 5 %}
                    <div class="text-center mt-2">
                        <small class="text-muted">+ {{ month_leaves|length|add:"-5" }} autre(s)</small>
                    </div>
                    {% endif %}
                </div>
                {% else %}
                <p class="text-muted text-center">Aucun congé ce mois</p>
                {% endif %}
            </div>
            <div class="mt-3">
                <a href="{% url 'core:list' app='leave' model='leave' %}" class="btn btn-outline-primary btn-sm w-100">
                    <i class="bi bi-calendar"></i> Voir tous mes congés
                </a>
            </div>
        </div>
    </div>
</div>''',
            'view': '''from leave.models import Leave
from core.models import Approbation
from datetime import date, timedelta
from calendar import month_name

employee = None
if request and hasattr(request, 'user') and hasattr(request.user, 'employee') and request.user.employee:
    employee = request.user.employee

today = date.today()
current_year = today.year
current_month = today.month
current_month_name = month_name[current_month]

first_day_month = today.replace(day=1)
next_month = (first_day_month + timedelta(days=32)).replace(day=1)
last_day_month = next_month - timedelta(days=1)

if employee:
    leaves = Leave.objects.filter(
        employee=employee,
        start_dt__gte=first_day_month,
        start_dt__lte=last_day_month
    ).order_by('start_dt')
    
    month_leaves = []
    for leave in leaves:
        approbations = Approbation.objects.for_model(Leave).filter(object_id=leave.id)
        if approbations.exists() and approbations.is_fully_approved():
            month_leaves.append(leave)
    
    month_leaves_count = len(month_leaves)
else:
    month_leaves = []
    month_leaves_count = 0'''
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for widget_data in widgets_data:
        try:
            widget, created = Widget.objects.get_or_create(
                name=widget_data['name'],
                defaults={
                    'description': widget_data['description'],
                    'template': widget_data['template'],
                    'view': widget_data['view']
                }
            )
            
            if not created:
                widget.description = widget_data['description']
                widget.template = widget_data['template']
                widget.view = widget_data['view']
                widget.save()
                updated_count += 1
                print(f"  ✅ Widget '{widget.name}' mis à jour")
            else:
                created_count += 1
                print(f"  ✅ Widget '{widget.name}' créé")
            
            if widget_data['permission_codename']:
                try:
                    permission = Permission.objects.get(
                        content_type__app_label=widget_data['permission_app'],
                        codename=widget_data['permission_codename']
                    )
                    if permission not in widget.permissions.all():
                        widget.permissions.add(permission)
                        print(f"    ✅ Permission '{widget_data['permission_app']}.{widget_data['permission_codename']}' ajoutée")
                except Permission.DoesNotExist:
                    print(f"    ⚠️  Permission '{widget_data['permission_app']}.{widget_data['permission_codename']}' non trouvée")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de la création du widget '{widget_data['name']}': {e}")
    
    print(f"\n📊 Résumé:")
    print(f"  ✅ {created_count} widget(s) créé(s)")
    print(f"  🔄 {updated_count} widget(s) mis à jour")
    print(f"\n✅ Configuration terminée!")

if __name__ == '__main__':
    create_widgets()
