from django.db.models.signals import m2m_changed
from mission.models import Mission, Report
from django.dispatch import receiver


@receiver(m2m_changed, sender=Mission.employees.through)
def mission_created(sender, instance, action, reverse, *args, **kwargs):
    if action != 'post_add' or reverse: return    
    report = [Report(**{
        'mission': instance,
        'employee': employee,
        'document': None
    }) for employee in instance.employees.all()]
    Report.objects.bulk_create(report)
