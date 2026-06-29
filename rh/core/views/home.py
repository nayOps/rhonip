from types import SimpleNamespace

from django.utils.translation import gettext as _
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.apps import apps
from datetime import date, timedelta
from calendar import month_name

from core.models import Approbation, Announcement, Organization
from leave.models import Leave, EarlyLeave
from mission.models import Mission
from employee.models import Overtime, Attendance


class Home(LoginRequiredMixin, View):
    today = date.today()

    def get(self, request):
        # Détecter le type d'utilisateur
        is_normal_employee = (
            not request.user.is_superuser and 
            not request.user.is_staff and 
            hasattr(request.user, 'employee') and 
            request.user.employee
        )
        
        if is_normal_employee:
            # Dashboard pour employé normal
            return self._employee_dashboard(request)
        else:
            # Dashboard pour admin/staff
            return self._admin_dashboard(request)
    
    def _employee_dashboard(self, request):
        """Dashboard personnel pour les employés normaux"""
        from django.utils import timezone
        from employee.models import Document

        employee = request.user.employee
        hour = timezone.localtime().hour
        if hour < 12:
            greeting = _('Bonjour')
        elif hour < 18:
            greeting = _('Bon après-midi')
        else:
            greeting = _('Bonsoir')

        remaining_leave = self._get_remaining_leave(employee)
        training_hours = self._get_training_hours(employee)
        workflow_tasks = self._get_workflow_tasks(request.user)
        announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
        featured_announcement = announcements.first()
        if not featured_announcement:
            featured_announcement = SimpleNamespace(
                title=_('Mise à jour de la réglementation du travail — T3 2026'),
                content=_(
                    'Chers agents, une nouvelle note de service relative aux procédures '
                    'internes et aux directives de conformité est disponible. '
                    'Merci de prendre connaissance des lignes directrices pour assurer '
                    'la continuité des opérations sur le terrain.'
                ),
                is_default=True,
            )

        recent_documents = []
        for doc in Document.objects.filter(employee=employee).exclude(document='').order_by('-updated_at')[:4]:
            filename = doc.name or (doc.document.name.split('/')[-1] if doc.document else _('Document'))
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            recent_documents.append({
                'title': filename,
                'url': doc.document.url if doc.document else '#',
                'type': 'pdf' if ext == 'pdf' else 'doc',
                'updated_at': doc.updated_at,
            })

        dashboard_notifications = self._get_dashboard_notifications(request.user)
        stats = self._get_employee_dashboard_stats(request.user, employee, workflow_tasks)

        context = {
            'employee': employee,
            'greeting': greeting,
            'remaining_leave': remaining_leave,
            'training_hours': training_hours,
            'training_courses': self._get_training_courses(employee),
            'workflow_tasks': workflow_tasks,
            'recent_documents': recent_documents,
            'announcements': announcements[:5],
            'featured_announcement': featured_announcement,
            'dashboard_notifications': dashboard_notifications,
            'stats': stats,
            'unread_notifications_count': request.user.notifications.unread().count(),
            'organization': Organization.objects.first(),
            'request': request,
        }

        return render(request, 'home_employee.html', context)

    def _get_employee_dashboard_stats(self, user, employee, workflow_tasks):
        from django.contrib.contenttypes.models import ContentType

        presence_rate = self._get_employee_presence_rate(employee)

        Mission = apps.get_model('mission', 'Mission')
        missions_count = Mission.objects.filter(employees=employee).count()

        Leave = apps.get_model('leave', 'Leave')
        leave_ct = ContentType.objects.get_for_model(Leave)
        open_requests = 0
        for leave in Leave.objects.filter(employee=employee).order_by('-created_at')[:20]:
            approbations = Approbation.objects.filter(content_type=leave_ct, object_id=leave.id)
            if not approbations.exists() or not approbations.is_fully_approved():
                open_requests += 1

        mission_ct = ContentType.objects.get_for_model(Mission)
        for mission in Mission.objects.filter(employees=employee).order_by('-created_at')[:20]:
            approbations = Approbation.objects.filter(content_type=mission_ct, object_id=mission.id)
            if not approbations.exists() or not approbations.is_fully_approved():
                open_requests += 1

        return {
            'missions_count': missions_count,
            'presence_rate': presence_rate,
            'remaining_leave_days': self._get_remaining_leave(employee)['days'],
            'open_requests': open_requests,
        }

    def _get_employee_presence_rate(self, employee):
        from calendar import monthrange

        if not employee:
            return 0

        year, month = self.today.year, self.today.month
        last_day = monthrange(year, month)[1]
        month_start = date(year, month, 1)
        month_end = date(year, month, last_day)

        attendances = Attendance.objects.filter(
            employee=employee,
            date__gte=month_start,
            date__lte=min(month_end, self.today),
            direction='IN',
        ).values('date').distinct().count()

        working_days = sum(
            1 for d in range((min(month_end, self.today) - month_start).days + 1)
            if (month_start + timedelta(days=d)).weekday() < 5
        )
        if working_days <= 0:
            return 0
        return round(min(100, (attendances / working_days) * 100), 1)

    def _get_training_courses(self, employee):
        from training.models import Training

        courses = []
        for training in Training.objects.filter(is_completed=False).order_by('-start_date')[:2]:
            progress = 85 if training.name else 50
            courses.append({
                'name': training.name,
                'progress': progress,
                'tone': 'blue' if progress >= 50 else 'alt',
            })
        if not courses:
            courses = [
                {'name': _('Protocole de sécurité V2'), 'progress': 85, 'tone': 'blue'},
                {'name': _('Conformité RGPD'), 'progress': 42, 'tone': 'alt'},
            ]
        return courses

    def _get_dashboard_notifications(self, user):
        from django.utils.timesince import timesince

        level_map = {
            'error': ('urgent', 'bi-exclamation-triangle', _('Urgent')),
            'warning': ('hr', 'bi-person-badge', _('RH')),
            'success': ('update', 'bi-check-circle', _('Mise à jour')),
            'info': ('system', 'bi-gear', _('Système')),
        }
        items = []
        for notif in user.notifications.all().order_by('-timestamp')[:5]:
            tone, icon, label = level_map.get(notif.level, level_map['info'])
            items.append({
                'tone': tone,
                'icon': icon,
                'label': label,
                'title': notif.verb or _('Notification'),
                'description': notif.description or '',
                'time': timesince(notif.timestamp),
                'url': notif.get_absolute_url() if hasattr(notif, 'get_absolute_url') else None,
                'unread': notif.unread,
            })
        return items
    
    def _admin_dashboard(self, request):
        """Dashboard admin pour les administrateurs et staff"""
        # Statistiques organisationnelles
        Employee = apps.get_model('employee', 'Employee')
        from employee.utils.roster import roster_employees_queryset
        total_employees = roster_employees_queryset().count()
        
        # Congés en cours aujourd'hui
        on_leave_today = Leave.objects.filter(
            start_dt__lte=self.today,
            end_dt__gte=self.today
        ).count()
        
        # Évaluations en attente (à adapter selon votre modèle)
        pending_evaluations = self._get_pending_evaluations()
        
        # Contrats actifs (à adapter selon votre modèle)
        active_contracts = self._get_active_contracts()
        
        # Présences aujourd'hui
        attendance_today = self._get_attendance_today()
        
        # Congés en attente de validation
        pending_leaves = self._get_pending_leaves_for_approval()
        
        # Alertes et activités
        alerts = self._get_alerts()
        activities = self._get_recent_activities()
        
        # Anniversaires du mois
        birthdays = self._get_month_birthdays()
        
        context = {
            'total_employees': total_employees,
            'on_leave_today': on_leave_today,
            'pending_evaluations': pending_evaluations,
            'active_contracts': active_contracts,
            'pending_leaves': pending_leaves,
            'alerts': alerts,
            'activities': activities,
            'birthdays': birthdays,
            'attendance_today': attendance_today,
            'organization': Organization.objects.first(),
            'request': request,
        }
        
        return render(request, "home_admin.html", context)
    
    def _get_remaining_leave(self, employee):
        """Calcule le solde de congés restants"""
        if not employee:
            return {'days': 0, 'status': 'N/A'}
        
        # Récupérer les congés approuvés de l'année
        current_year = self.today.year
        year_start = date(current_year, 1, 1)
        year_end = date(current_year, 12, 31)
        
        approved_leaves = Leave.objects.filter(
            employee=employee,
            start_dt__gte=year_start,
            start_dt__lte=year_end
        )
        
        # Vérifier si les congés sont approuvés
        from django.contrib.contenttypes.models import ContentType
        
        total_days_taken = 0
        leave_content_type = ContentType.objects.get_for_model(Leave)
        
        for leave in approved_leaves:
            approbations = Approbation.objects.filter(
                content_type=leave_content_type,
                object_id=leave.id
            )
            if approbations.exists() and approbations.is_fully_approved():
                total_days_taken += leave.days
        
        # Supposons 30 jours par défaut (à adapter selon votre logique)
        max_days = 30
        remaining = max_days - total_days_taken
        
        return {
            'days': max(0, remaining),
            'status': 'Accrued' if remaining > 0 else 'Exhausted'
        }
    
    def _get_training_hours(self, employee):
        """Calcule les heures de formation en cours"""
        # À implémenter selon votre modèle Training
        return {'hours': 8.0, 'status': 'In Progress'}
    
    def _get_workflow_tasks(self, user):
        """Récupère les tâches du workflow personnel (approubations en attente)"""
        pending_approbations = Approbation.objects.filter(
            user=user,
            action__isnull=True
        ).select_related('content_type')[:10]
        
        tasks = []
        for approbation in pending_approbations:
            try:
                model = apps.get_model(
                    approbation.content_type.app_label,
                    approbation.content_type.model
                )
                obj = model.objects.get(pk=approbation.object_id)
                
                # Déterminer le type de tâche
                task_type = 'Approval'
                if approbation.content_type.model == 'leave':
                    task_type = 'Leave'
                elif approbation.content_type.model == 'mission':
                    task_type = 'Mission'
                elif approbation.content_type.model == 'latejustification':
                    task_type = 'LateJustification'
                
                # Créer la tâche
                task = {
                    'id': approbation.id,
                    'type': task_type,
                    'title': str(obj),
                    'description': f"{model._meta.verbose_name} - En attente d'approbation",
                    'url': obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else '#',
                    'due_date': None,  # À adapter selon votre logique
                    'urgent': False,  # À adapter selon votre logique
                }
                tasks.append(task)
            except Exception:
                continue
        
        return tasks
    
    def _get_pending_leaves_for_approval(self):
        """Récupère les congés en attente d'approbation pour les admins"""
        from django.contrib.contenttypes.models import ContentType
        
        leaves = Leave.objects.filter(
            start_dt__gte=self.today
        ).select_related('employee', 'type_of_leave')[:10]
        
        pending = []
        leave_content_type = ContentType.objects.get_for_model(Leave)
        
        for leave in leaves:
            # Récupérer les approbations pour ce leave spécifique
            approbations = Approbation.objects.filter(
                content_type=leave_content_type,
                object_id=leave.id
            )
            
            # Vérifier s'il y a des approbations en attente (non complètement approuvées)
            if approbations.exists():
                # Si toutes les approbations sont approuvées, le leave n'est plus en attente
                if not approbations.is_fully_approved():
                    pending.append(leave)
            else:
                # Si aucune approbation n'existe, le leave est en attente
                pending.append(leave)
        
        return pending
    
    def _get_alerts(self):
        """Récupère les alertes pour les admins"""
        # À implémenter selon vos besoins
        return []
    
    def _get_recent_activities(self):
        """Récupère les activités récentes pour les admins"""
        # À implémenter selon vos besoins
        return []
    
    def _get_month_birthdays(self):
        """Récupère les anniversaires du mois"""
        Employee = apps.get_model('employee', 'Employee')
        current_month = self.today.month
        
        # Filtrer uniquement les employés avec une date de naissance valide
        employees_with_birthday = Employee.objects.filter(
            date_of_birth__isnull=False
        )
        
        birthdays = []
        for employee in employees_with_birthday:
            # Vérifier que la date de naissance existe et est du mois en cours
            if employee.date_of_birth and employee.date_of_birth.month == current_month:
                try:
                    # Créer une date pour cette année avec le même jour et mois
                    birthday_date = date(self.today.year, employee.date_of_birth.month, employee.date_of_birth.day)
                    birthdays.append({
                        'employee': employee,
                        'date': birthday_date,
                        'day': employee.date_of_birth.day,
                    })
                except (ValueError, AttributeError):
                    # Ignorer les dates invalides (ex: 29 février pour une année non bissextile)
                    continue
        
        # Trier par jour du mois
        birthdays.sort(key=lambda x: x['day'])
        return birthdays[:10]  # Limiter à 10
    
    def _get_pending_evaluations(self):
        """Récupère le nombre d'évaluations en attente"""
        # Placeholder - à implémenter si vous avez un modèle Evaluation
        # Pour l'instant, on peut utiliser un calcul basé sur les dates d'engagement
        Employee = apps.get_model('employee', 'Employee')
        # Exemple : employés engagés il y a plus de 6 mois sans évaluation récente
        six_months_ago = self.today - timedelta(days=180)
        employees_to_evaluate = Employee.objects.filter(
            date_of_join__lte=six_months_ago,
            date_of_join__isnull=False
        ).count()
        # Pour l'instant, retourner 0 ou un nombre calculé
        return min(employees_to_evaluate, 10)  # Limiter à 10 pour l'affichage
    
    def _get_active_contracts(self):
        """Récupère le nombre de contrats actifs"""
        Employee = apps.get_model('employee', 'Employee')
        # Compter les employés avec un statut actif et un contrat
        active_employees = Employee.objects.filter(
            agent_situation='active',
            agreement__isnull=False,
        ).count()
        return active_employees
    
    def _get_attendance_today(self):
        """Récupère les présences d'aujourd'hui"""
        today_attendances = Attendance.objects.filter(date=self.today).select_related('employee')
        
        # Séparer les entrées et sorties
        entries = today_attendances.filter(direction='IN').order_by('time')
        exits = today_attendances.filter(direction='OUT').order_by('time')
        
        # Créer une liste des employés présents aujourd'hui
        present_employees = []
        employees_with_entry = set(entries.values_list('employee_id', flat=True))
        
        for entry in entries[:10]:  # Limiter à 10 pour l'affichage
            employee = entry.employee
            exit_record = exits.filter(employee=employee).first()
            
            present_employees.append({
                'employee': employee,
                'entry_time': entry.time,
                'exit_time': exit_record.time if exit_record else None,
                'is_present': exit_record is None,  # Encore présent si pas de sortie
            })
        
        return {
            'total_present': len(employees_with_entry),
            'total_entries': entries.count(),
            'total_exits': exits.count(),
            'employees': present_employees,
        }