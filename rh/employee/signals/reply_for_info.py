from django.utils.translation import gettext as _
from django.db.models.signals import post_save
from employee.models import ReplyWithInfo
from notifications.signals import notify
from django.dispatch import receiver

@receiver(post_save, sender=ReplyWithInfo)
def request_for_employee_to_added(sender, instance, created, *args, **kwargs):
    if not created or not instance.description: return
    notify.send(**{
        'sender': instance,
        'actor': instance.user,
        'recipient': instance.request_for_info.created_by,
        
        'verb': _('Réponse sur {}').format(instance.request_for_info.name),
        'description': _('Demande d\'information mis a jour'),
        'public': False,
        
        'action_object': instance,
        'target': instance,
        'level': 'info'
    })