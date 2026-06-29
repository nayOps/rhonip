from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _

from core.models.fields import ModelSelect, ModelSelect2Multiple
from core.utils import upload_directory_file
from core.models import Base

from django.urls import reverse_lazy
from django.db import models

class RequestForInfo(Base):
    name = models.CharField(max_length=255, verbose_name=_('nom'))
    description = models.TextField(verbose_name=_('description'))
    users = ModelSelect2Multiple('core.User', verbose_name=_('à'))

    list_display = ('id', 'name', 'updated_at')
    layout = Layout(
        Row(
            Column('name'),
            Column('users'),
        ),
        'description'
    )

    def get_absolute_url(self):
        return reverse_lazy('employee:request_for_info_change', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('demande d\'information')
        verbose_name_plural = _('demandes d\'informations')

class ReplyWithInfo(Base):
    request_for_info = ModelSelect(RequestForInfo, verbose_name=_('demande d\'information'), null=True, on_delete=models.SET_NULL)
    document = models.FileField(verbose_name=_('document'), upload_to=upload_directory_file, null=True, blank=True, default=None)
    user = ModelSelect('core.User', verbose_name=_('de'), null=True, on_delete=models.SET_NULL)
    description = models.TextField(verbose_name=_('description'))

    list_display = ('id', 'request_for_info', 'updated_at')
    inline_form_fields = ('user', 'document', 'description')
    layout = Layout('document', 'description')

    @property
    def name(self):
        return '{} - {}'.format(self.request_for_info.name, self.user)

    class Meta:
        verbose_name = _('réponse à la demande d\'information')
        verbose_name_plural = _('réponses à la demande d\'information')