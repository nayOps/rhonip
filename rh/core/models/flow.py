from core.models.fields import ModelSelect, ModelSelect2Single
from django.contrib.contenttypes.models import ContentType
from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.conf import settings

from core.models import Base
from django.db import models

class Flow(Base):
    name = models.CharField(verbose_name=_('nom'), max_length=255)
    content_type = ModelSelect2Single(ContentType, verbose_name=_('type de contenu'), on_delete=models.CASCADE, null=True, default=None)

    list_display = ('id', 'name', 'content_type')
    layout = Layout(
        Row(
            Column('name', css_class='col-md-6'),
            Column('content_type', css_class='col-md-6'),
        )
    )
    
    def get_absolute_url(self):
        return reverse_lazy('core:flow', kwargs={'pk': self.pk})
    
    class Meta:
        verbose_name = _('flux')
        verbose_name_plural = _('flux')


class FlowStep(Base):
    parent = ModelSelect('self', verbose_name=_('parent'), on_delete=models.CASCADE, blank=True, null=True, default=None, related_name='child')
    flow = ModelSelect(Flow, verbose_name=_('flux'), on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(verbose_name=_('nom'), max_length=255)
    user = ModelSelect(settings.AUTH_USER_MODEL, verbose_name=_('utilisateur'), on_delete=models.CASCADE)

    list_display = ('id', 'flow', 'parent', 'user')
    layout = Layout('flow', 'name', 'parent', 'user')

    def get_absolute_url(self):
        return reverse_lazy('core:flow', kwargs={'pk': self.flow.pk})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('étape du flux')
        verbose_name_plural = _('étapes du flux')