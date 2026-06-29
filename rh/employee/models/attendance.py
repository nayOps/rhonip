from core.models.fields import ModelSelect
from django.db import models
from core.models import Base

from django.utils.translation import gettext_lazy as _
from api.serializers import model_serializer_factory
from crispy_forms.layout import Layout, Row, Column
from core.models.fields import DateField, TimeField


class Attendance(Base):
    LEGACY_DIRECTIONS = (
        ('IN', _('entrée')),
        ('OUT', _('sortie')),
    )
    SOURCES = (
        ('manual', _('Saisie manuelle')),
        ('fingerprint', _('Empreinte')),
        ('import', _('Import')),
    )

    employee = ModelSelect('employee.Employee', verbose_name=_('employé'), on_delete=models.CASCADE)
    date = DateField(verbose_name=_('date'))
    time = TimeField(verbose_name=_('heure'))
    direction = models.CharField(
        _('direction'),
        max_length=10,
        choices=LEGACY_DIRECTIONS,
        blank=True,
        null=True,
    )
    source = models.CharField(
        _('source'),
        max_length=20,
        choices=SOURCES,
        default='manual',
    )

    list_display = ('id', 'employee', 'date', 'time', 'source', 'direction')
    list_filter = ('date', 'time', 'source', 'direction')

    layout = Layout(
        Row(
            Column('employee', css_class='form-group col-md-6 mb-0'),
            Column('source', css_class='form-group col-md-6 mb-0'),
            css_class='form-row',
        ),
        Row(
            Column('date', css_class='form-group col-md-6 mb-0'),
            Column('time', css_class='form-group col-md-6 mb-0'),
            css_class='form-row',
        ),
        Row(
            Column('direction', css_class='form-group col-md-6 mb-0'),
            css_class='form-row',
        ),
    )

    @property
    def name(self):
        return '{} · {} {}'.format(self.employee, self.date, self.time)

    def json(self):
        serializer = model_serializer_factory(self._meta.model, depth=1)
        return serializer(self).data

    class Meta:
        verbose_name = _('pointage')
        verbose_name_plural = _('pointages')
        constraints = [
            models.UniqueConstraint(
                fields=('employee', 'date', 'time'),
                name='employee_attendance_unique_punch',
            ),
        ]
