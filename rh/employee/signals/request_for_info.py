from employee.models import RequestForInfo, ReplyWithInfo
from django.utils.translation import gettext as _
from django.db.models.signals import m2m_changed
from notifications.signals import notify
from django.dispatch import receiver

@receiver(m2m_changed, sender=RequestForInfo.users.through)
def request_for_employee_to_added(sender, instance, action, reverse, *args, **kwargs):
    if action != 'post_add' or reverse: return 

    qs = [ReplyWithInfo(**{
        'request_for_info': instance,
        'user': obj,
    }) for obj in instance.users.all()]
    qs = ReplyWithInfo.objects.bulk_create(qs)

    # notify user
    [notify.send(**{
        'sender': obj,
        'recipient': obj.user,
        'actor': instance.created_by,
        'verb': _('{} a fait une demande d\'information').format(instance.created_by.name),
        'action_object': obj,
        'target': obj,
        'level': 'info',
        'description': instance.name,
        'public': False,
        'url': obj.get_absolute_url()
    }) for obj in qs]