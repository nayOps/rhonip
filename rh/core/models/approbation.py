from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.core.serializers import serialize
from core.models.fields import ModelSelect

from django.conf import settings
from django.apps import apps

from core.models.managers import *
from core.models import Base
from django.db import models

class ApprobationChoice(models.TextChoices):
    APPROVED = "APPROVED", _("approuvé")
    REJECTED = "REJECTED", _("rejetée")

class Approbation(Base):
    content_type = ModelSelect(ContentType, verbose_name=_('type de contenu'), on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField(verbose_name=_('id de l\'objet'), null=True)

    content_object = GenericForeignKey('content_type', 'object_id')
    user = ModelSelect(settings.AUTH_USER_MODEL, verbose_name=_('utilisateur'), on_delete=models.CASCADE)

    comment = models.TextField(verbose_name=_('commentaire'), blank=True, null=True, default=None)
    action = models.CharField(verbose_name=_('action'), max_length=10, choices=ApprobationChoice.choices, null=True, default=None)

    objects = ApprobationQueryset.as_manager()

    class Meta:
        verbose_name = _('approbation')
        verbose_name_plural = _('approbations')
        ordering = ('content_type__app_label', 'content_type__model', 'object_id')

    def __str__(self):
        return '{} approval obj id:{}'.format(str(self.content_type).title(), self.object_id)

    def natural_key(self):
        return (self.object_id,) + self.content_type.natural_key()
    
    natural_key.dependencies = ['contenttypes.contenttype']

    def get_model(self):
        return apps.get_model(self.content_object.app_name, self.content_object.model)