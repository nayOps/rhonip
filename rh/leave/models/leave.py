from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _
from django.forms import ValidationError
from django.db import models

from core.models.fields import ModelSelect, DateField
from core.models import Base
from core.approval_status import approval_status_code, approval_status_label

from .type_of_leave import TypeOfLeave
from employee.models import Employee

# replace the obj model with the string format in foreign field
class Leave(Base):
    interim = ModelSelect(Employee, verbose_name=_('remplaçant'), null=True, default=None, on_delete=models.SET_NULL, related_name='interim')
    type_of_leave = ModelSelect(TypeOfLeave, verbose_name=_('type de congé'), null=True, default=None, on_delete=models.SET_NULL)
    employee = ModelSelect(Employee, verbose_name=_('employé'), null=True, default=None, on_delete=models.SET_NULL)
    
    start_dt = DateField(verbose_name=_('du'))
    end_dt = DateField(verbose_name=_('au'))

    reason = models.TextField(verbose_name=_('motif'), null=True, default=None)

    list_filter = ('start_dt', 'end_dt')
    list_display = ('id', 'employee', 'interim', 'start_dt', 'end_dt')
    change_list_template = 'list_agent_requests.html'
    agent_list_title = _('Mes congés')
    layout = Layout('type_of_leave', Row(Column('employee'), Column('interim')), Row(Column('start_dt'), Column('end_dt')), 'reason')
    search_fields = ('employee__registration_number', 'employee__first_name', 'employee__middle_name', 'employee__last_name') 

    @property
    def name(self):
        return f"{self.type_of_leave} de {self.employee}"
    
    @property
    def days(self):
        return (self.end_dt - self.start_dt).days
    
    @property
    def taken(self):
        return sum([leave.days for leave in Leave.objects.filter(employee=self.employee)])

    @property
    def available_days(self):
        return self.type_of_leave.max_days_per_year - self.taken

    @property
    def request_type_display(self):
        return self.type_of_leave or _('Congé')

    @property
    def approval_status(self):
        return approval_status_code(self)

    @property
    def approval_status_label(self):
        return approval_status_label(self)

    @property
    def period_display(self):
        if self.start_dt and self.end_dt:
            return f'{self.start_dt.strftime("%d/%m/%Y")} → {self.end_dt.strftime("%d/%m/%Y")}'
        return '—'
    
    def clean(self):
        available_days = self.available_days
        if self.days > available_days:
            raise ValidationError(_('Vous ne pouvez pas demander plus de jours que ceux disponibles (Il vous reste %d jour(s))') 
                                  % (available_days))
        return super().clean()

    class Meta:
        verbose_name = _('congé')
        verbose_name_plural = _('congés')