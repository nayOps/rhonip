from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from django.urls import reverse

from employee.utils.attendance_schedule_config import (
    get_presence_slots,
    get_slot_codes,
    get_slot_ui_headers,
    get_total_slots,
)
from employee.utils.attendance_slots import evaluate_day_slots, slot_display_cell, slots_display_row
from employee.utils.late_justification import (
    can_request_justification,
    is_day_late_excused,
    justification_display_for_day,
    justifications_by_date,
)
from leave.utils.early_leave_attendance import (
    early_leave_display_for_day,
    early_leaves_by_date,
)

WEEKDAY_SHORT = ('LUN', 'MAR', 'MER', 'JEU', 'VEN', 'SAM', 'DIM')
WEEKDAY_FULL = (
    _('Lundi'),
    _('Mardi'),
    _('Mercredi'),
    _('Jeudi'),
    _('Vendredi'),
    _('Samedi'),
    _('Dimanche'),
)

MONTH_NAMES = (
    _('Janvier'),
    _('Février'),
    _('Mars'),
    _('Avril'),
    _('Mai'),
    _('Juin'),
    _('Juillet'),
    _('Août'),
    _('Septembre'),
    _('Octobre'),
    _('Novembre'),
    _('Décembre'),
)

MONTH_SHORT = ('Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc')

STATUS_LABELS = {
    'present': _('PRÉSENT'),
    'late': _('RETARD'),
    'partial': _('PARTIEL'),
    'absent': _('ABSENT'),
    'early_leave': _('DÉPART ANTICIPÉ'),
}


def parse_attendance_period(request, today=None):
    today = today or date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    month = max(1, min(12, month))

    week_param = request.GET.get('week')
    if week_param:
        week_start = date.fromisoformat(week_param)
    else:
        ref = date(year, month, min(today.day, monthrange(year, month)[1]))
        if today.year == year and today.month == month:
            ref = today
        week_start = ref - timedelta(days=ref.weekday())

    return year, month, week_start


def bulk_punches_by_employee(employee_ids, start, end):
    from employee.models import Attendance

    if not employee_ids:
        return {}

    rows = (
        Attendance.objects.filter(
            employee_id__in=employee_ids,
            date__gte=start,
            date__lte=end,
        )
        .order_by('employee_id', 'date', 'time')
        .values_list('employee_id', 'date', 'time')
    )

    grouped = defaultdict(lambda: defaultdict(list))
    for employee_id, punch_date, punch_time in rows:
        grouped[employee_id][punch_date].append(punch_time)
    return grouped


def bulk_attendance_details(employee_ids, start, end):
    """Un seul scan Attendance : pointages + sources + dernier pointage."""
    from employee.models import Attendance
    from collections import Counter

    if not employee_ids:
        return {}, {}, {}

    rows = (
        Attendance.objects.filter(
            employee_id__in=employee_ids,
            date__gte=start,
            date__lte=end,
        )
        .order_by('employee_id', 'date', 'time')
        .values_list('employee_id', 'date', 'time', 'source')
    )

    punches = defaultdict(lambda: defaultdict(list))
    sources = defaultdict(Counter)
    last_punch = {}
    for employee_id, punch_date, punch_time, source in rows:
        punches[employee_id][punch_date].append(punch_time)
        sources[employee_id][source or 'manual'] += 1
        last_punch[employee_id] = (punch_date, punch_time)
    return punches, sources, last_punch


def _attendance_by_date(employee, start, end):
    records = bulk_punches_by_employee([employee.pk], start, end)
    return records.get(employee.pk, {})


def _day_detail(attendance_by_date, day):
    punch_times = attendance_by_date.get(day, [])
    if isinstance(punch_times, dict):
        punch_times = [value for value in punch_times.values() if value]
    return evaluate_day_slots(day, punch_times)


def _weekdays_in_month(year, month):
    days_in_month = monthrange(year, month)[1]
    return [
        date(year, month, day)
        for day in range(1, days_in_month + 1)
        if date(year, month, day).weekday() < 5
    ]


def _format_duration(total_minutes):
    hours, minutes = divmod(total_minutes, 60)
    return f'{hours}h {minutes:02d}m'


def _is_attendance_day(status):
    return status in ('present', 'late', 'partial')


def build_month_summary(employee, year, month):
    month_start = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    month_end = date(year, month, days_in_month)
    attendance_by_date = _attendance_by_date(employee, month_start, month_end)
    early_leave_map = early_leaves_by_date(employee, month_start, month_end)

    working_days = _weekdays_in_month(year, month)
    present_days = 0
    late_count = 0
    partial_count = 0
    absence_count = 0
    total_late_minutes = 0
    total_worked_minutes = 0
    early_leave_days = 0

    for day in working_days:
        detail = _day_detail(attendance_by_date, day)
        total_worked_minutes += detail['worked_minutes']
        excused = is_day_late_excused(employee, day)
        early_leave = early_leave_map.get(day)
        early_leave_info = early_leave_display_for_day(early_leave)
        if early_leave_info and early_leave_info['status'] == 'approved':
            early_leave_days += 1
        if detail['status'] == 'absent':
            absence_count += 1
        elif _is_attendance_day(detail['status']):
            present_days += 1
            if detail['status'] == 'late' and not excused:
                late_count += 1
                total_late_minutes += detail['delay_minutes']
            elif detail['status'] == 'partial':
                partial_count += 1
                if detail.get('delay_minutes', 0) > 0 and not excused:
                    late_count += 1
                    total_late_minutes += detail['delay_minutes']

    total_working = len(working_days) or 1
    presence_rate = round(present_days * 1000 / total_working) / 10

    return {
        'year': year,
        'month': month,
        'month_label': MONTH_NAMES[month - 1],
        'is_current_month': date.today().year == year and date.today().month == month,
        'presence_rate': presence_rate,
        'late_count': late_count,
        'partial_count': partial_count,
        'absence_count': absence_count,
        'present_days': present_days,
        'total_late_minutes': total_late_minutes,
        'working_days_count': len(working_days),
        'hours_worked_label': _format_duration(total_worked_minutes),
        'leave_days': early_leave_days,
        'early_leave_days': early_leave_days,
        'prev': _shift_month(year, month, -1),
        'next': _shift_month(year, month, 1),
        'slot_labels': [slot['label'] for slot in get_presence_slots()],
    }


def build_week_view(employee, week_start):
    week_end = week_start + timedelta(days=6)
    attendance_by_date = _attendance_by_date(employee, week_start, week_end)
    justification_map = justifications_by_date(employee, week_start, week_end)
    early_leave_map = early_leaves_by_date(employee, week_start, week_end)

    days = []
    rows = []
    for offset in range(7):
        day = week_start + timedelta(days=offset)
        detail = _day_detail(attendance_by_date, day)
        justification = justification_map.get(day)
        justification_info = justification_display_for_day(justification)
        early_leave = early_leave_map.get(day)
        early_leave_info = early_leave_display_for_day(early_leave)
        display_status = detail['status']
        if justification_info and justification_info['status'] == 'approved' and detail['status'] in ('late', 'partial'):
            display_status = 'justified_late'
        if early_leave_info and early_leave_info['status'] == 'approved':
            display_status = 'early_leave'

        day_status = detail['status']
        if display_status == 'early_leave':
            day_status = 'early_leave'

        days.append(
            {
                'date': day,
                'weekday_short': WEEKDAY_SHORT[day.weekday()],
                'day_number': day.day,
                'status': day_status,
                'early_leave': early_leave_info,
                'is_selected': offset == 0,
            }
        )
        if detail['status'] != 'weekend':
            slots = detail.get('slots', {})
            rows.append(
                {
                    'date': day,
                    'date_label': day.strftime('%d/%m/%Y'),
                    'weekday': WEEKDAY_FULL[day.weekday()],
                    'status': detail['status'],
                    'display_status': display_status,
                    'validated_slots': detail.get('validated_slots', 0),
                    'total_slots': detail.get('total_slots', get_total_slots()),
                    'delay_minutes': detail.get('delay_minutes', 0),
                    'slots_display': slots_display_row(slots),
                    'justification': justification_info,
                    'early_leave': early_leave_info,
                    'can_justify': can_request_justification(
                        employee, day, detail, justification
                    ),
                    'justify_url': (
                        reverse('employee:late_justification_create')
                        + f'?employee={employee.pk}&date={day.isoformat()}'
                    ),
                }
            )

    return {
        'week_start': week_start,
        'week_end': week_end,
        'range_label': (
            f'{week_start.day} {MONTH_SHORT[week_start.month - 1]} — '
            f'{week_end.day} {MONTH_SHORT[week_end.month - 1]} {week_end.year}'
        ),
        'days': days,
        'rows': rows,
        'slot_headers': list(get_slot_ui_headers()),
        'total_slots': get_total_slots(),
        'prev_week': week_start - timedelta(days=7),
        'next_week': week_start + timedelta(days=7),
    }


def _empty_calendar_cell():
    return {
        'date': None,
        'day_number': None,
        'status': 'empty',
        'status_label': '',
        'schedule': '',
        'note': '',
        'is_padding': True,
    }


def build_month_view(employee, year, month):
    days_in_month = monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)
    attendance_by_date = _attendance_by_date(employee, month_start, month_end)
    early_leave_map = early_leaves_by_date(employee, month_start, month_end)

    cells = []
    leading_blanks = month_start.weekday()
    cells.extend([_empty_calendar_cell() for _ in range(leading_blanks)])

    for day_num in range(1, days_in_month + 1):
        day = date(year, month, day_num)
        detail = _day_detail(attendance_by_date, day)
        early_leave = early_leave_map.get(day)
        early_leave_info = early_leave_display_for_day(early_leave)
        cell_status = detail['status']
        cell_note = detail['note']
        cell_status_label = detail['status_label']
        if early_leave_info and early_leave_info['status'] == 'approved':
            cell_status = 'early_leave'
            cell_status_label = STATUS_LABELS['early_leave']
            cell_note = _('{type} · {time}').format(
                type=early_leave_info['label'],
                time=early_leave_info['time_range'],
            )
        elif early_leave_info:
            cell_note = _('Départ anticipé ({status}) : {type}').format(
                status=early_leave_info['status_label'],
                type=early_leave_info['label'],
            )
        cells.append(
            {
                'date': day,
                'day_number': day_num,
                'weekday_short': WEEKDAY_SHORT[day.weekday()],
                'status': cell_status,
                'status_label': cell_status_label,
                'schedule': detail['schedule'],
                'note': cell_note,
                'early_leave': early_leave_info,
                'validated_slots': detail.get('validated_slots', 0),
                'is_padding': False,
            }
        )

    trailing = (7 - (len(cells) % 7)) % 7
    cells.extend([_empty_calendar_cell() for _ in range(trailing)])

    weeks = [cells[index:index + 7] for index in range(0, len(cells), 7)]

    return {
        'weekday_headers': WEEKDAY_SHORT,
        'weeks': weeks,
    }


def build_recent_actions(employee, limit=3):
    content_type = ContentType.objects.get_for_model(employee)
    entries = (
        LogEntry.objects.filter(content_type=content_type, object_id=str(employee.pk))
        .select_related('user')
        .order_by('-action_time')[:limit]
    )

    actions = []
    for entry in entries:
        user_label = getattr(entry.user, 'email', None) or str(entry.user)
        actions.append(
            {
                'date_label': entry.action_time.strftime('%d/%m/%Y'),
                'user': user_label,
                'description': entry.change_message or entry.object_repr,
            }
        )
    return actions


def _shift_month(year, month, delta):
    month += delta
    while month < 1:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return {'year': year, 'month': month}


def build_attendance_report(employee, year, month):
    summary = build_month_summary(employee, year, month)
    prev = _shift_month(year, month, -1)
    prev_summary = build_month_summary(employee, prev['year'], prev['month'])
    rate_delta = round(summary['presence_rate'] - prev_summary['presence_rate'], 1)

    days_in_month = monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)
    attendance_by_date = _attendance_by_date(employee, month_start, month_end)

    rows = []
    observations = []
    for day_num in range(1, days_in_month + 1):
        day = date(year, month, day_num)
        if day.weekday() >= 5:
            continue

        detail = _day_detail(attendance_by_date, day)
        slots = detail.get('slots', {})
        entry_code = get_slot_codes()[0] if get_slot_codes() else 'MORNING_IN'
        entry_slot = slots.get(entry_code, {})

        def _report_slot_value(code):
            slot = slots.get(code) or {}
            cell = slot_display_cell(slot, code)
            if cell['time'] == '--:--':
                return '—'
            if slot.get('status') in ('ok',):
                return cell['time']
            return f"{cell['time']} — {cell['badge']}"

        rows.append(
            {
                'date_label': day.strftime('%d/%m/%Y'),
                'slot_values': [_report_slot_value(code) for code in get_slot_codes()],
                'duration_label': _format_duration(detail['worked_minutes'])
                if detail['worked_minutes']
                else '—',
                'status': detail['status'],
                'status_label': detail['status_label'],
                'note': detail.get('note', ''),
                'is_late_entry': entry_slot.get('status') in ('late', 'missed_entry'),
                'validated_slots': detail.get('validated_slots', 0),
                'total_slots': detail.get('total_slots', get_total_slots()),
            }
        )

        if detail['note'] and detail['status'] in ('late', 'partial', 'absent', 'present'):
            observations.append(f"{day.strftime('%d/%m')}: {detail['note']}")

    generated_at = date.today()
    prev_month_label = MONTH_NAMES[prev['month'] - 1]

    return {
        'summary': summary,
        'rows': rows,
        'visible_rows': rows[:5],
        'hidden_rows_count': max(len(rows) - 5, 0),
        'rate_delta': rate_delta,
        'rate_delta_label': f"{'+' if rate_delta >= 0 else ''}{rate_delta}% vs {prev_month_label}",
        'observations': '\n'.join(observations)
        if observations
        else _('Aucune observation particulière pour cette période.'),
        'generated_at_label': f'{generated_at.day} {MONTH_NAMES[generated_at.month - 1]} {generated_at.year}',
        'report_ref': f'REF-RH-{year}-{employee.pk:05d}',
        'period_label': f"{summary['month_label']} {year}",
        'agent_label': employee.registration_number or f'#{employee.pk}',
        'direction_label': str(employee.direction) if employee.direction else '—',
        'year': year,
        'month': month,
        'slot_headers': [slot.get('ui_header', slot['label']) for slot in get_presence_slots()],
        'slot_codes': list(get_slot_codes()),
    }


def get_employee_attendance_context(request, employee):
    year, month, week_start = parse_attendance_period(request)
    summary = build_month_summary(employee, year, month)
    return {
        'attendance_summary': summary,
        'attendance_week': build_week_view(employee, week_start),
        'attendance_month': build_month_view(employee, year, month),
        'attendance_recent_actions': build_recent_actions(employee),
        'attendance_year': year,
        'attendance_month_num': month,
        'attendance_slots': get_presence_slots(),
        'attendance_total_slots': get_total_slots(),
    }
