from django.utils.translation import gettext as _

from core.approval_status import approval_status_code


def early_leaves_by_date(employee, start, end):
    from leave.models import EarlyLeave

    if not employee:
        return {}

    rows = EarlyLeave.objects.filter(
        employee=employee,
        date__gte=start,
        date__lte=end,
    ).select_related('employee')

    return {row.date: row for row in rows}


def early_leave_display_for_day(early_leave):
    if not early_leave:
        return None

    status = approval_status_code(early_leave)
    status_labels = {
        'pending': _('En attente'),
        'approved': _('Validé'),
        'rejected': _('Rejeté'),
    }
    badge_classes = {
        'pending': 'early-leave-pending',
        'approved': 'early-leave-approved',
        'rejected': 'early-leave-rejected',
    }

    return {
        'label': early_leave.get_departure_type_display(),
        'status': status,
        'status_label': status_labels.get(status, status),
        'badge_class': badge_classes.get(status, 'early-leave-pending'),
        'time_range': f'{early_leave.start_time or "—"} → {early_leave.end_time or "—"}',
        'read_url': str(early_leave.get_absolute_url()),
    }
