from crispy_forms.layout import Layout, Row, Column
from django.urls import reverse_lazy
from django.db import models
from django.utils.translation import gettext as _
from core.models.fields import ModelSelect
from core.models import Base

from .employee import Employee


class PayrollPeriod(Base):
    code = models.CharField(_('code période'), max_length=32, unique=True)
    label = models.CharField(_('libellé'), max_length=100)
    bank = models.CharField(_('banque'), max_length=100, blank=True, null=True, default=None)
    institution = models.CharField(_('institution'), max_length=255, blank=True, null=True, default=None)
    effectifs = models.PositiveIntegerField(_('effectifs'), default=0)

    list_display = ('code', 'label', 'effectifs', 'bank')
    search_fields = ('code', 'label', 'bank', 'institution')
    layout = Layout(
        Row(Column('code'), Column('label')),
        Row(Column('bank'), Column('institution')),
        'effectifs',
    )

    @property
    def list_url(self):
        return reverse_lazy('employee:payroll_list')

    class Meta:
        verbose_name = _('période de paie')
        verbose_name_plural = _('périodes de paie')

    @property
    def name(self):
        return self.label


class PayrollLine(Base):
    period = ModelSelect(
        PayrollPeriod,
        verbose_name=_('période'),
        on_delete=models.CASCADE,
        related_name='lines',
    )
    employee = ModelSelect(
        Employee,
        verbose_name=_('employé'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        related_name='payroll_lines',
    )
    line_number = models.PositiveIntegerField(_('n° ligne'), default=0)
    registration_number = models.CharField(_('matricule / NIU'), max_length=50, db_index=True)
    full_name = models.CharField(_('nom complet'), max_length=255)
    fonction = models.CharField(_('fonction'), max_length=150, blank=True, null=True, default=None)
    base = models.BigIntegerField(_('base'), default=0)
    prime = models.BigIntegerField(_('prime'), default=0)
    logement = models.BigIntegerField(_('logement'), default=0)
    ipr = models.BigIntegerField(_('IPR'), default=0)
    cpa = models.BigIntegerField(_('CPA'), default=0)
    montant_net = models.BigIntegerField(_('montant net'), default=0)
    ftc = models.BigIntegerField(_('FTC'), default=0)
    net_a_payer = models.BigIntegerField(_('net à payer'), default=0)

    list_display = (
        'line_number',
        'registration_number',
        'full_name',
        'fonction',
        'net_a_payer',
    )
    list_filter = ('period',)
    search_fields = ('registration_number', 'full_name', 'fonction')
    layout = Layout(
        Row(Column('period'), Column('employee')),
        Row(Column('line_number'), Column('registration_number')),
        'full_name',
        Row(Column('fonction'), Column('base')),
        Row(Column('prime'), Column('logement')),
        Row(Column('ipr'), Column('cpa')),
        Row(Column('montant_net'), Column('ftc')),
        'net_a_payer',
    )

    @property
    def list_url(self):
        return reverse_lazy('employee:payroll_list')

    class Meta:
        verbose_name = _('ligne de paie')
        verbose_name_plural = _('lignes de paie')
        constraints = [
            models.UniqueConstraint(
                fields=('period', 'registration_number'),
                name='uniq_payroll_line_period_matricule',
            ),
        ]

    @property
    def name(self):
        return f'{self.registration_number} — {self.full_name}'
