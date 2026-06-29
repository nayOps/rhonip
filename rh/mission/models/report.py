from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _


from core.utils import upload_directory_file
from core.models.fields import ModelSelect
from core.models import Base

from django.db import models

class Report(Base):
    mission = ModelSelect('mission.Mission', verbose_name=_('mission'), null=True, default=None, on_delete=models.SET_NULL)
    employee = ModelSelect('employee.Employee', verbose_name=_('employé'), null=True, default=None, on_delete=models.SET_NULL)
    document = models.FileField(verbose_name=_('document'), upload_to=upload_directory_file, null=True, default=None)

    search_fields = ('mission__name', 'employee__registration_number', 'employee__first_name', 'employee__middle_name', 'employee__last_name')
    inline_form_fields = ('employee', 'document')
    list_display = ('id', 'mission', 'employee')
    layout = Layout(
        Row(Column('mission'), Column('employee')),
        'document',
    )

    @property
    def name(self):
        return "Rapport de mission n°{}".format(self.id)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('rapport')
        verbose_name_plural = _('rapports')
        ordering = ('-id',)

