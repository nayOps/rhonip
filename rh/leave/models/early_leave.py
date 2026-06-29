from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _
from django.db import models

from core.models.fields import ModelSelect, TimeField, DateField
from django.forms import ValidationError
from core.models import Base, Preference
from core.approval_status import approval_status_code, approval_status_label

from employee.models import Employee
from datetime import datetime


class DepartureType(models.TextChoices):
    PERSONAL = 'personal', _('Personnel')
    MEDICAL = 'medical', _('Médical')
    ADMINISTRATIVE = 'administrative', _('Administratif')
    OFFICIAL = 'official', _('Mission / officiel')
    OTHER = 'other', _('Autre')


class EarlyLeave(Base):
    employee = ModelSelect(Employee, verbose_name=_('employé'), null=True, default=None, on_delete=models.SET_NULL)
    departure_type = models.CharField(
        verbose_name=_('type de départ'),
        max_length=20,
        choices=DepartureType.choices,
        default=DepartureType.PERSONAL,
    )
    destination = models.CharField(verbose_name=_('destination'), max_length=250, blank=True, null=True, default=None)
    date = DateField(verbose_name=_('date'), default=datetime.today)

    start_time = TimeField(verbose_name=_('de'))
    end_time = TimeField(verbose_name=_('à'))

    observation = models.TextField(verbose_name=_('observation'), blank=True, null=True, default=None)
    reason = models.TextField(verbose_name=_('motif'))

    list_filter = ('departure_type', 'date')
    list_display = ('id', 'employee', 'start_time', 'end_time')
    change_list_template = 'list_early_leave.html'
    agent_list_title = _('Départs anticipés')
    layout = Layout(
        'employee',
        Row(Column('departure_type'), Column('destination')),
        'date',
        Row(Column('start_time'), Column('end_time')),
        'reason',
        'observation',
    )
    search_fields = (
        'employee__registration_number',
        'employee__first_name',
        'employee__middle_name',
        'employee__last_name',
    )

    @property
    def name(self):
        return '{employee} — {type} ({start} → {end})'.format(**{
            'employee': self.employee.full_name() if self.employee else '—',
            'type': self.get_departure_type_display(),
            'start': self.start_time,
            'end': self.end_time,
        })

    @property
    def request_type_display(self):
        return self.get_departure_type_display()

    @property
    def approval_status(self):
        return approval_status_code(self)

    @property
    def approval_status_label(self):
        return approval_status_label(self)

    @property
    def period_display(self):
        if self.date:
            return f'{self.date.strftime("%d/%m/%Y")} · {self.start_time or "—"} → {self.end_time or "—"}'
        return '—'

    def clean(self):
        preference = Preference.get('EARLY_LEAVE_START_TIME_HOUR')
        if not preference:
            return super().clean()
        if int(preference.value) > int(self.start_time.split(':')[0]):
            raise ValidationError(
                _('Vous ne pouvez pas faire de demande avant %s heures du matin') % (preference.value)
            )
        return super().clean()

    class Meta:
        verbose_name = _('départ anticipé')
        verbose_name_plural = _('départs anticipés')
