from django.utils.translation import gettext_lazy as _


STEP_META = {
    'employee': {
        'label': _('Informations'),
        'title': _('Informations personnelles'),
        'subtitle': _('Coordonnées, état civil et affectation de l’agent.'),
    },
    'child': {
        'label': _('Enfants'),
        'title': _('Enfants à charge'),
        'subtitle': _('Déclarez les enfants rattachés au dossier de l’agent.'),
        'add_label': _('Ajouter un enfant'),
    },
    'education': {
        'label': _('Éducations'),
        'title': _('Parcours éducatif'),
        'subtitle': _('Veuillez renseigner les diplômes et formations obtenus.'),
        'add_label': _('Ajouter une formation'),
    },
    'experience': {
        'label': _('Expériences'),
        'title': _('Parcours professionnel'),
        'subtitle': _('Historique des expériences et postes occupés.'),
        'add_label': _('Ajouter une expérience'),
    },
    'document': {
        'label': _('Documents'),
        'title': _('Documents du dossier'),
        'subtitle': _('Pièces jointes et justificatifs associés à l’agent.'),
        'add_label': _('Ajouter un document'),
    },
}


def build_employee_form_steps(model_name, formsets):
    steps = []
    employee_meta = STEP_META['employee']
    steps.append({
        'id': model_name,
        'label': employee_meta['label'],
        'title': employee_meta['title'],
        'subtitle': employee_meta['subtitle'],
    })
    for formset in formsets:
        step_id = formset.model._meta.model_name
        meta = STEP_META.get(step_id, {})
        steps.append({
            'id': step_id,
            'label': meta.get('label') or formset.model._meta.verbose_name_plural.title(),
            'title': meta.get('title') or formset.model._meta.verbose_name_plural.title(),
            'subtitle': meta.get('subtitle', ''),
            'add_label': meta.get('add_label', ''),
        })
    return steps
