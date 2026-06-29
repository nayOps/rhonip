from django.utils.translation import gettext_lazy as _


REPORT_CATALOG = (
    {
        'code': 'biometric_enrollment',
        'title': _('Enregistrement biométrique'),
        'description': _(
            'Liste des agents avec photo et statut des empreintes digitales (10 doigts).'
        ),
        'icon': 'bi-fingerprint',
        'preview_name': 'employee:biometric_enrollment_report',
        'schedule_name': 'employee:biometric_enrollment_report_schedule',
        'export_name': 'employee:biometric_enrollment_report_export',
    },
)
