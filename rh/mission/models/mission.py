from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from core.models.fields import ModelSelect2Multiple, DateField
from core.models import Base

from django.forms import ValidationError
from django.db import models
from django.apps import apps

class Mission(Base):
    name = models.CharField(verbose_name=_('nom'), max_length=255)
    description = models.TextField(verbose_name=_('description'), null=True)

    destination = models.CharField(verbose_name=_('destination'), max_length=255, null=True)
    employees = ModelSelect2Multiple('employee.Employee', verbose_name=_('employés'))

    start_date = DateField(verbose_name=_('date de début'), null=True)
    end_date = DateField(verbose_name=_('date de fin'), null=True)

    list_display = ('id', 'name', 'destination', 'start_date', 'end_date')
    layout = Layout(
        'name',
        'description',
        Row(Column('start_date'), Column('end_date')),
        Row(Column('destination'), Column('employees')),
    )

    def get_absolute_url(self):
        return reverse_lazy('mission:mission', kwargs={'pk': self.pk})

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError(_('La date de début doit être inférieur à la date de fin'))
        return super().clean()
    
    def form_clean(self):
        model = apps.get_model('mission', model_name='report')
        unreported = model.objects.filter(models.Q(document__isnull=True) | models.Q(document=''))
        unreported = unreported.filter(employee__in=self.cleaned_data['employees'])
        unreported = unreported.values_list('employee__last_name', flat=True)
        unreported = unreported.order_by('employee__last_name').distinct()
        if unreported.exists():
            raise ValidationError(_('Les employés sélectionnés ont des rapports de mission non remplis: [%s]' % ', '.join([str(report) for report in unreported])))
        return self.cleaned_data

    class Meta:
        verbose_name = _('mission')
        verbose_name_plural = _('missions')