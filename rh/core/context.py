from functools import reduce

from django.utils.translation import gettext as _
from core.models import Menu, Approbation
from core.models import Organization
from django.urls import reverse_lazy
from django.apps import apps

from django.urls import reverse_lazy
from django.conf import settings


def _href_path(href):
    if not href or href == '#':
        return ''
    return str(href).split('?')[0]


def _mark_menu_active(menu, path):
    for item in menu:
        item['active'] = False
        href_path = _href_path(item.get('href'))
        if href_path and path == href_path:
            item['active'] = True
        for child in item.get('children') or []:
            child['active'] = False
            child_path = _href_path(child.get('href'))
            if child_path and (path == child_path or path.startswith(child_path.rstrip('/') + '/')):
                child['active'] = True
                item['active'] = True
    return menu


EMPLOYEE_SIDEBAR_MODELS = {
    'leave.leave',
    'leave.earlyleave',
    'mission.mission',
}


def _is_agent_user(request):
    return (
        request.user.is_authenticated
        and not request.user.is_superuser
        and not request.user.is_staff
        and getattr(request.user, 'employee', None)
    )


def _employee_agent_menus(request):
    menus = [
        {
            'title': _('Présences'),
            'href': reverse_lazy('employee:my_attendance'),
            'icon': 'bi-calendar-check',
            'forced': True,
        },
    ]
    if request.user.has_perm('leave.view_leave'):
        menus.append({
            'title': _('Congés'),
            'href': reverse_lazy('core:list', kwargs={'app': 'leave', 'model': 'leave'}),
            'icon': 'bi-calendar-event-fill',
            'forced': True,
        })

    if request.user.has_perm('leave.view_earlyleave'):
        menus.append({
            'title': _('Départs anticipés'),
            'href': reverse_lazy('core:list', kwargs={'app': 'leave', 'model': 'earlyleave'}),
            'icon': 'bi-box-arrow-right',
            'forced': True,
        })

    if request.user.has_perm('mission.view_mission'):
        menus.append({
            'title': _('Missions'),
            'href': reverse_lazy('core:list', kwargs={'app': 'mission', 'model': 'mission'}),
            'icon': 'bi-briefcase-fill',
            'forced': True,
        })

    return menus


def base(request):
    PASSWORD_RESET_REDIRECT_URL = getattr(settings, 'PASSWORD_RESET_REDIRECT_URL', reverse_lazy('password_reset'))
    if not request.user.is_authenticated: return {
        'organization':Organization.objects.first(),
        'PASSWORD_RESET_REDIRECT_URL': PASSWORD_RESET_REDIRECT_URL
    }
    modules = Menu.objects.all().order_by('created_at')
    is_agent = _is_agent_user(request)

    menu = []
    for module in modules:
        children = []
        for child in module.children.all():
            label = f'{child.app_label}.{child.model}'
            if is_agent and label in EMPLOYEE_SIDEBAR_MODELS:
                continue
            perm = f'{child.app_label}.view_{child.model}'
            if request.user.has_perm(perm):
                children.append({
                    'title': child.name,
                    'href': reverse_lazy('core:list', kwargs={'app': child.app_label, 'model': child.model}),
                    'permission': perm,
                })
        if children:
            menu.append({
                'title': module.name,
                'href': '#',
                'icon': f'bi-{module.icon}',
                'children': children,
            })
    
    menu.insert(0, dict({
        'title': _('Tableau de bord'),
        'href': reverse_lazy('core:home'),
        'icon': 'bi-grid-fill',
        'forced': True
    }))
    
    menu.insert(1, dict({
        'title': _('Notification'),
        'href': reverse_lazy('core:notifications'),
        'icon': 'bi-bell-fill',
        'forced': True,
        'badge': request.user.notifications.unread().count()
    }))

    menu.insert(2, dict({
        'title': _('Action requise'),
        'href': reverse_lazy('core:action-required'),
        'icon': 'bi-check-circle-fill',
        'forced': True,
        'badge': action_required(request).get('action_required_count', 0)
    }))

    next_forced_index = 3
    if request.user.is_staff or request.user.is_superuser:
        menu.insert(next_forced_index, dict({
            'title': _('Présences générale'),
            'href': reverse_lazy('employee:company_attendance'),
            'icon': 'bi-calendar2-check-fill',
            'forced': True,
        }))
        next_forced_index += 1
        menu.insert(next_forced_index, dict({
            'title': _('Rapports'),
            'href': reverse_lazy('employee:biometric_enrollment_report'),
            'icon': 'bi-file-earmark-bar-graph-fill',
            'forced': True,
        }))
        next_forced_index += 1
    
    if is_agent:
        agent_menus = _employee_agent_menus(request)
        menu.insert(next_forced_index, dict({
            'title': _('Mon Profil'),
            'href': reverse_lazy('employee:my_profile'),
            'icon': 'bi-person-fill',
            'forced': True,
        }))
        next_forced_index += 1
        for idx, agent_menu in enumerate(agent_menus):
            menu.insert(next_forced_index + idx, agent_menu)
    
    menu.insert(len(menu), dict({
        'title': _('Paramètres'),
        'href': '#',
        'icon': 'bi-gear-fill',
        'children': [item for item in [{
            'title': _('Menus'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'menu'}),
            'permission': 'core.view_menu'
        }, {
            'title': _('Modèle de document'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'template'}),
            'permission': 'core.view_template'
        }, {
            'title': _('Importateur'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'importer'}),
            'permission': 'core.view_importer'
        }, {
            'title': _('Widget'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'widget'}),
            'permission': 'core.view_widget'
        }, {
            'title': _('Préférences'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'preference'}),
            'permission': 'core.view_preference'
        }, {
            'title': _('Équipe'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'user'}),
            'permission': 'core.view_user'
        }, {
            'title': _('Autorisations des groupes'),
            'href': reverse_lazy('core:list', kwargs={'app': 'auth', 'model': 'group'}),
            'permission': 'auth.view_group'
        }, {
            'title': _('Plages de présence'),
            'href': reverse_lazy('employee:attendance_schedule_settings'),
            'permission': 'employee.view_employee',
        }, {
            'title': _('Organisation'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'organization'}),
            'permission': 'core.view_organization'
        }, {
            'title': _('Flux de travail'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'flow'}),
            'permission': 'core.view_flow'
        }, {
            'title': _('Job'),
            'href': reverse_lazy('core:list', kwargs={'app': 'core', 'model': 'job'}),
            'permission': 'core.view_job'
        }] if request.user.has_perm(item.get('permission'))]
    }))
    menu = _mark_menu_active(menu, request.path)
    return {'menus': menu, 'organization': Organization.objects.first(), 'PASSWORD_RESET_REDIRECT_URL': PASSWORD_RESET_REDIRECT_URL}

def action_required(request):
    if not request.user.is_authenticated: return {}
    return {'action_required_count': Approbation.objects.filter(user=request.user, action__isnull=True).count()}