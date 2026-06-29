from collections import defaultdict
from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext as _

from core.models import Approbation
from employee.models import Attendance, LateJustification
from employee.utils.attendance_slots import evaluate_day_slots
from employee.utils.hierarchy import resolve_n_plus_one


def _punches_for_day(employee, day):
    records = Attendance.objects.filter(employee=employee, date=day).order_by('time')
    return [record.time for record in records]


def _day_has_justifiable_anomaly(detail, day):
    """Retard, présence partielle ou absence passée."""
    today = timezone.localdate()
    if detail['status'] == 'late' or detail.get('delay_minutes', 0) > 0:
        return True
    if detail['status'] == 'partial' and detail.get('validated_slots', 0) > 0:
        return True
    if detail['status'] == 'absent' and day < today:
        return True
    return False


def validate_late_day_for_employee(employee, day):
    if day.weekday() >= 5:
        return {'error': _('La justification ne concerne pas le week-end.')}
    detail = evaluate_day_slots(day, _punches_for_day(employee, day))
    if not _day_has_justifiable_anomaly(detail, day):
        return {'error': _('Aucune anomalie de présence à justifier pour cette date.')}
    morning = detail.get('slots', {}).get('MORNING_IN', {})
    return {
        'error': None,
        'delay_minutes': detail.get('delay_minutes', 0),
        'morning_punch_time': morning.get('punch_time'),
        'status': detail['status'],
        'validated_slots': detail.get('validated_slots', 0),
    }


def justifications_by_date(employee, start, end):
    rows = LateJustification.objects.filter(
        employee=employee,
        date__gte=start,
        date__lte=end,
    )
    return {row.date: row for row in rows}


def justification_display_for_day(justification):
    if not justification:
        return None
    status = justification.approval_status
    labels = {
        'pending': _('Justification en attente'),
        'approved': _('Retard justifié'),
        'rejected': _('Justification rejetée'),
    }
    css = {
        'pending': 'pending',
        'approved': 'approved',
        'rejected': 'rejected',
    }
    return {
        'pk': justification.pk,
        'status': status,
        'label': labels.get(status, status),
        'badge_class': css.get(status, 'pending'),
        'read_url': justification.get_absolute_url(),
    }


def can_request_justification(employee, day, detail, justification=None):
    if day.weekday() >= 5:
        return False
    if justification and justification.approval_status in ('pending', 'approved'):
        return False
    if justification and justification.approval_status == 'rejected':
        return _day_has_justifiable_anomaly(detail, day)
    return _day_has_justifiable_anomaly(detail, day)


def create_late_justification(employee, day, reason, document=None, requested_by=None):
    evaluation = validate_late_day_for_employee(employee, day)
    if evaluation.get('error'):
        raise ValueError(str(evaluation['error']))

    existing = LateJustification.objects.filter(employee=employee, date=day).first()
    if existing and existing.approval_status in ('pending', 'approved'):
        raise ValueError(_('Une justification existe déjà pour cette date.'))

    if existing and existing.approval_status == 'rejected':
        justification = existing
        justification.reason = reason
        justification.document = document or justification.document
        justification.delay_minutes = evaluation['delay_minutes']
        justification.morning_punch_time = evaluation['morning_punch_time']
        justification.save()
        justification.approbations().delete()
    else:
        justification = LateJustification.objects.create(
            employee=employee,
            date=day,
            reason=reason,
            document=document,
            delay_minutes=evaluation['delay_minutes'],
            morning_punch_time=evaluation['morning_punch_time'],
        )

    approver = resolve_n_plus_one(employee)
    if not approver:
        justification.delete()
        raise ValueError(
            _('Aucun responsable N+1 trouvé pour votre direction. Contactez les RH.')
        )

    content_type = ContentType.objects.get_for_model(LateJustification)
    Approbation.objects.create(
        content_type=content_type,
        object_id=justification.pk,
        user=approver,
    )
    return justification


def is_day_late_excused(employee, day):
    justification = LateJustification.objects.filter(employee=employee, date=day).first()
    return bool(justification and justification.approval_status == 'approved')
