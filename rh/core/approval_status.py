from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from core.models import Approbation


def get_approval_status(obj):
    ct = ContentType.objects.get_for_model(obj.__class__)
    qs = Approbation.objects.filter(content_type=ct, object_id=obj.pk)
    if not qs.exists():
        return 'pending', _('En attente de validation')
    if qs.filter(action='REJECTED').exists():
        return 'rejected', _('Rejetée')
    if qs.is_fully_approved():
        return 'approved', _('Validée')
    return 'pending', _('En attente de validation')


def approval_status_label(obj):
    return get_approval_status(obj)[1]


def approval_status_code(obj):
    return get_approval_status(obj)[0]
