from django.db.models.signals import post_save
from django.dispatch import receiver

from core.tasks import importer
from core.models import Importer


@receiver(post_save, sender=Importer)
def user_created(sender, instance, created, **kwargs):
    if not created: return
    importer.delay(instance.pk)