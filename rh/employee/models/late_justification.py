from crispy_forms.layout import Layout, Row, Column
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from core.models import Approbation, Base
from core.models.fields import DateField, ModelSelect, TimeField
from core.utils import upload_directory_file

from employee.models import Employee


class LateJustification(Base):
    employee = ModelSelect(
        Employee,
        verbose_name=_('employé'),
        null=True,
        default=None,
        on_delete=models.CASCADE,
        related_name='late_justifications',
    )
    date = DateField(verbose_name=_('date du retard'))
    delay_minutes = models.PositiveIntegerField(
        verbose_name=_('retard (minutes)'),
        default=0,
    )
    morning_punch_time = TimeField(
        verbose_name=_('heure d\'arrivée'),
        blank=True,
        null=True,
        default=None,
    )
    reason = models.TextField(verbose_name=_('motif'))
    document = models.FileField(
        verbose_name=_('pièce justificative'),
        upload_to=upload_directory_file,
        blank=True,
        null=True,
        default=None,
    )

    list_display = ('id', 'employee', 'date', 'delay_minutes')
    list_filter = ('date',)
    change_list_template = 'list_agent_requests.html'
    agent_list_title = _('Mes justifications')
    search_fields = (
        'employee__registration_number',
        'employee__first_name',
        'employee__last_name',
        'reason',
    )
    layout = Layout(
        'employee',
        Row(Column('date'), Column('delay_minutes')),
        'morning_punch_time',
        'reason',
        'document',
    )

    class Meta:
        verbose_name = _('justification de retard')
        verbose_name_plural = _('justifications de retard')
        constraints = [
            models.UniqueConstraint(
                fields=('employee', 'date'),
                name='employee_late_justification_unique_day',
            ),
        ]
        ordering = ('-date', '-id')

    @property
    def name(self):
        employee_label = self.employee.full_name() if self.employee else '—'
        return _('Justification retard — %(employee)s — %(date)s') % {
            'employee': employee_label,
            'date': self.date.strftime('%d/%m/%Y') if self.date else '—',
        }

    @property
    def request_type_display(self):
        return _('Justification de retard')

    @property
    def period_display(self):
        if self.date:
            label = self.date.strftime('%d/%m/%Y')
            if self.delay_minutes:
                return f'{label} · {self.delay_minutes} min'
            return label
        return '—'

    def approbations(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Approbation.objects.filter(content_type=content_type, object_id=self.pk)

    @property
    def approval_status(self):
        qs = self.approbations()
        if not qs.exists():
            return 'none'
        if qs.filter(action='REJECTED').exists():
            return 'rejected'
        if qs.is_fully_approved():
            return 'approved'
        return 'pending'

    @property
    def approval_status_label(self):
        labels = {
            'none': _('Sans validation'),
            'pending': _('En attente N+1'),
            'approved': _('Validée'),
            'rejected': _('Rejetée'),
        }
        return labels.get(self.approval_status, self.approval_status)

    def clean(self):
        from employee.utils.late_justification import validate_late_day_for_employee

        super().clean()
        if not self.employee_id or not self.date:
            return

        existing = (
            LateJustification.objects.filter(
                employee_id=self.employee_id,
                date=self.date,
            )
            .exclude(pk=self.pk)
            .first()
        )
        if existing and existing.approval_status in ('pending', 'approved'):
            raise ValidationError(
                _('Une justification existe déjà pour cette date.')
            )

        evaluation = validate_late_day_for_employee(self.employee, self.date)
        if evaluation.get('error'):
            raise ValidationError(evaluation['error'])

        self.delay_minutes = evaluation.get('delay_minutes', 0)
        self.morning_punch_time = evaluation.get('morning_punch_time')
