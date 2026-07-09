from django.utils.translation import gettext_lazy as _


REPORT_CATALOG = (
    {
        'code': 'enregistrement',
        'title': _('Enregistrement biométrique'),
        'description': _(
            'Liste des agents avec photo, statut et empreintes digitales (10 doigts). '
            'Filtres par période, statut agent et niveau d’enrôlement.'
        ),
        'icon': 'bi-fingerprint',
        'badge': _('Global'),
        'filename_hint': 'rapport-rh-onip-enregistrement-[date].pdf',
        'preview_name': 'employee:biometric_enrollment_report',
        'schedule_name': 'employee:biometric_enrollment_report_schedule',
        'export_name': 'employee:biometric_enrollment_report_export',
        'default_query': '',
    },
    {
        'code': 'enregistrement-journalier',
        'title': _('Enregistrement journalier 10/10'),
        'description': _(
            'Agents ACTIF avec enrôlement complet (10/10 empreintes tablette), '
            'regroupés par journée d’activité.'
        ),
        'icon': 'bi-calendar-day',
        'badge': _('Journalier'),
        'filename_hint': 'rapport-rh-onip-enregistrement-journalier-[date].pdf',
        'preview_name': 'employee:enrollment_day_report',
        'schedule_name': 'employee:enrollment_day_report_schedule',
        'export_name': 'employee:enrollment_day_report_export',
        'default_query': '',
    },
)
