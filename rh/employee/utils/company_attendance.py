from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta, time as dt_time
from urllib.parse import urlencode

from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext as _

from employee.models import Direction, Employee
from employee.utils.attendance_schedule_config import get_slot_codes, get_slot_ui_headers, get_total_slots
from employee.utils.attendance_slots import slots_display_row
from employee.utils.roster import apply_roster_filter
from employee.utils.attendance_stats import (
    MONTH_NAMES,
    MONTH_SHORT,
    WEEKDAY_FULL,
    WEEKDAY_SHORT,
    _day_detail,
    _shift_month,
    _weekdays_in_month,
    bulk_punches_by_employee,
    parse_attendance_period,
)


def _bulk_attendance(employee_ids, start, end):
    return bulk_punches_by_employee(employee_ids, start, end)


STATUS_DISPLAY = {
    'present': _('Présent'),
    'late': _('Retard'),
    'partial': _('Partiel'),
    'absent': _('Absent'),
    'weekend': _('Week-end'),
}


def _employee_initials(employee):
    first = (employee.first_name or '').strip()[:1]
    last = (employee.last_name or '').strip()[:1]
    text = f'{first}{last}'.upper()
    return text or '?'


def _morning_punch_on_day(attendance_by_date, day):
    detail = _day_detail(attendance_by_date, day)
    return detail.get('slots', {}).get('MORNING_IN', {}).get('punch_time')


def _has_marked_presence_on_day(attendance_by_date, day):
    if attendance_by_date.get(day):
        return True
    return _day_detail(attendance_by_date, day).get('validated_slots', 0) > 0


def _has_marked_presence_in_range(attendance_by_date, start, end):
    current = start
    while current <= end:
        if _has_marked_presence_on_day(attendance_by_date, current):
            return True
        current += timedelta(days=1)
    return False


def _arrival_sort_key(row):
    """Présents triés par heure d'arrivée (Matin : Entrée 1), absents en fin de liste."""
    punch = row.get('morning_punch_time')
    if punch is None:
        return (1, dt_time.max, _employee_name_key(row['employee']))
    return (0, punch, ())


def _employee_name_key(employee):
    return (
        (employee.last_name or '').casefold(),
        (employee.first_name or '').casefold(),
        (employee.middle_name or '').casefold(),
        (employee.registration_number or '').casefold(),
    )


def _text_value(value):
    if value is None:
        return ''
    return str(value).strip()


def _employee_search_text(employee):
    parts = [
        _text_value(employee.registration_number),
        _text_value(employee.last_name),
        _text_value(employee.middle_name),
        _text_value(employee.first_name),
        _text_value(employee.direction),
        _text_value(employee.designation),
        _text_value(getattr(employee, 'service', None)),
        _text_value(employee.telephone_number),
        _text_value(employee.mobile_number),
        _text_value(employee.email),
        _text_value(employee.email_professional),
    ]
    return ' '.join(part for part in parts if part).casefold()


def _filter_employees_by_search(queryset, query):
    query = (query or '').strip()
    if not query:
        return queryset

    for term in query.split():
        queryset = queryset.filter(
            Q(registration_number__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(middle_name__icontains=term)
            | Q(telephone_number__icontains=term)
            | Q(mobile_number__icontains=term)
            | Q(email__icontains=term)
            | Q(email_professional__icontains=term)
            | Q(designation__name__icontains=term)
            | Q(direction__name__icontains=term)
            | Q(service__name__icontains=term)
        )
    return queryset.distinct()


def _company_employees_queryset(request):
    queryset = apply_roster_filter(
        Employee.objects.select_related(
            'direction', 'designation', 'service', 'grade'
        )
    ).order_by('last_name', 'first_name', 'middle_name', 'registration_number')
    direction_id = request.GET.get('direction')
    if direction_id:
        queryset = queryset.filter(direction_id=direction_id)
    return _filter_employees_by_search(queryset, request.GET.get('q'))


def _paginate_rows(rows, request, page_size=10):
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        page = 1

    total = len(rows)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, total_pages)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    page_numbers = list(range(max(1, page - 1), min(total_pages, page + 2) + 1))
    query = request.GET.copy()

    def _page_query(target_page):
        query['page'] = target_page
        return query.urlencode()

    return {
        'items': rows[start_index:end_index],
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': total_pages,
        'start': start_index + 1 if total else 0,
        'end': min(end_index, total),
        'page_numbers': page_numbers,
        'prev_query': _page_query(page - 1) if page > 1 else '',
        'next_query': _page_query(page + 1) if page < total_pages else '',
        'page_links': [{'num': num, 'query': _page_query(num)} for num in page_numbers],
    }


def _registry_query(request, **overrides):
    params = request.GET.copy()
    for key, value in overrides.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = str(value)
    return urlencode(params)


def _parse_registry_params(request, today=None):
    today = today or date.today()
    period_view = request.GET.get('period_view', 'daily')
    if period_view not in ('daily', 'weekly', 'monthly'):
        period_view = 'daily'
    display_mode = request.GET.get('display_mode', 'list')
    if display_mode not in ('list', 'calendar'):
        display_mode = 'list'

    day_param = request.GET.get('day')
    if day_param:
        try:
            focus_day = date.fromisoformat(day_param)
        except ValueError:
            focus_day = today
    else:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        month = max(1, min(12, month))
        if year == today.year and month == today.month:
            focus_day = today
        else:
            focus_day = date(year, month, 1)

    if focus_day > today:
        focus_day = today

    year = focus_day.year
    month = focus_day.month
    week_param = request.GET.get('week')
    if week_param:
        try:
            week_start = date.fromisoformat(week_param)
        except ValueError:
            week_start = focus_day - timedelta(days=focus_day.weekday())
    else:
        week_start = focus_day - timedelta(days=focus_day.weekday())

    return year, month, week_start, period_view, display_mode, focus_day


def _aggregate_day_counts(employees, bulk, day):
    counts = defaultdict(int)
    for employee in employees:
        detail = _day_detail(bulk.get(employee.pk, {}), day)
        counts[detail['status']] += 1
    return counts


def _aggregate_status(counts, employees_count, day):
    if day.weekday() >= 5:
        return 'weekend'
    if employees_count == 0:
        return 'absent'
    attended = counts.get('present', 0) + counts.get('late', 0) + counts.get('partial', 0)
    if attended == 0:
        return 'absent'
    if counts.get('absent', 0) >= employees_count / 2:
        return 'absent'
    if counts.get('late', 0) > counts.get('present', 0):
        return 'late'
    if counts.get('partial', 0) > 0:
        return 'partial'
    return 'present'


def _employee_row_link(employee, year, month):
    return reverse('employee:change', kwargs={'pk': employee.pk}) + f'?year={year}&month={month}'


def build_company_registry(request, employees, year, month, week_start):
    period_view, display_mode, focus_day = _parse_registry_params(request)[3:6]
    base = {
        'direction': request.GET.get('direction', ''),
        'zone_period': request.GET.get('zone_period', 'week'),
        'period_view': period_view,
        'display_mode': display_mode,
        'q': request.GET.get('q', ''),
    }
    employee_ids = [employee.pk for employee in employees]
    week_end = week_start + timedelta(days=6)
    days_in_month = monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)

    daily_bulk = _bulk_attendance(employee_ids, focus_day, focus_day)
    week_bulk = _bulk_attendance(employee_ids, week_start, week_end)
    month_bulk = _bulk_attendance(employee_ids, month_start, month_end)

    daily_list_rows = []
    present_morning = 0
    for employee in employees:
        emp_bulk = daily_bulk.get(employee.pk, {})
        punch_times = emp_bulk.get(focus_day, [])
        detail = _day_detail(emp_bulk, focus_day)
        if detail.get('validated_slots', 0) <= 0 and not punch_times:
            continue
        slots = detail.get('slots', {})
        morning_punch = _morning_punch_on_day(daily_bulk.get(employee.pk, {}), focus_day)
        if morning_punch:
            present_morning += 1
        daily_list_rows.append(
            {
                'employee': employee,
                'initials': _employee_initials(employee),
                'direction': str(employee.direction) if employee.direction else '—',
                'registration_number': employee.registration_number or '—',
                'search_text': _employee_search_text(employee),
                'morning_punch_time': morning_punch,
                'status': detail['status'],
                'status_label': STATUS_DISPLAY.get(detail['status'], detail['status']),
                'validated_slots': detail.get('validated_slots', 0),
                'total_slots': detail.get('total_slots', get_total_slots()),
                'schedule': detail.get('schedule', ''),
                'note': detail.get('note', ''),
                'detail_url': _employee_row_link(employee, year, month),
                'slots': slots_display_row(slots),
            }
        )

    daily_list_rows.sort(key=_arrival_sort_key)

    daily_counts = _aggregate_day_counts(employees, daily_bulk, focus_day)
    daily_attended = (
        daily_counts.get('present', 0)
        + daily_counts.get('late', 0)
        + daily_counts.get('partial', 0)
    )
    daily_aggregate = {
        'present': daily_counts.get('present', 0),
        'late': daily_counts.get('late', 0),
        'partial': daily_counts.get('partial', 0),
        'absent': daily_counts.get('absent', 0),
        'attended': daily_attended,
        'total': len(employees),
        'present_morning': present_morning,
        'present_morning_pct': round(present_morning * 1000 / len(employees)) / 10 if employees else 0,
        'rate': round(daily_attended * 1000 / len(employees)) / 10 if employees else 0,
        'status': _aggregate_status(daily_counts, len(employees), focus_day),
    }

    weekly_list_rows = []
    for employee in employees:
        week_attendance = week_bulk.get(employee.pk, {})
        if not _has_marked_presence_in_range(week_attendance, week_start, week_end):
            continue
        days = []
        for offset in range(7):
            day = week_start + timedelta(days=offset)
            detail = _day_detail(week_bulk.get(employee.pk, {}), day)
            days.append(
                {
                    'date': day,
                    'weekday_short': WEEKDAY_SHORT[day.weekday()],
                    'status': detail['status'],
                    'validated_slots': detail.get('validated_slots', 0),
                'total_slots': detail.get('total_slots', get_total_slots()),
                    'schedule': detail.get('schedule', ''),
                    'is_weekend': day.weekday() >= 5,
                }
            )
        weekly_list_rows.append(
            {
                'employee': employee,
                'initials': _employee_initials(employee),
                'direction': str(employee.direction) if employee.direction else '—',
                'registration_number': employee.registration_number or '—',
                'search_text': _employee_search_text(employee),
                'morning_punch_time': _morning_punch_on_day(week_attendance, focus_day),
                'days': days,
                'detail_url': _employee_row_link(employee, year, month),
            }
        )

    weekly_list_rows.sort(key=_arrival_sort_key)

    weekly_calendar_days = []
    for offset in range(7):
        day = week_start + timedelta(days=offset)
        counts = _aggregate_day_counts(employees, week_bulk, day)
        attended = counts.get('present', 0) + counts.get('late', 0) + counts.get('partial', 0)
        weekly_calendar_days.append(
            {
                'date': day,
                'weekday_short': WEEKDAY_SHORT[day.weekday()],
                'day_number': day.day,
                'status': _aggregate_status(counts, len(employees), day),
                'present_count': attended,
                'total': len(employees),
                'is_weekend': day.weekday() >= 5,
                'is_selected': day == focus_day,
                'day_url': _registry_query(
                    request,
                    **{
                        **base,
                        'day': day.isoformat(),
                        'year': day.year,
                        'month': day.month,
                        'week': week_start.isoformat(),
                    },
                ),
            }
        )

    monthly_list_rows = []
    for employee in employees:
        month_attendance = month_bulk.get(employee.pk, {})
        if not _has_marked_presence_in_range(month_attendance, month_start, month_end):
            continue
        summary = _summarize_employee(employee, year, month, month_attendance)
        monthly_list_rows.append(
            {
                'employee': employee,
                'initials': _employee_initials(employee),
                'direction': str(employee.direction) if employee.direction else '—',
                'registration_number': employee.registration_number or '—',
                'search_text': _employee_search_text(employee),
                'morning_punch_time': _morning_punch_on_day(month_attendance, focus_day),
                'presence_rate': summary['presence_rate'],
                'present_days': summary['present_days'],
                'late_count': summary['late_count'],
                'absence_count': summary['absence_count'],
                'detail_url': _employee_row_link(employee, year, month),
            }
        )

    monthly_list_rows.sort(key=_arrival_sort_key)

    month_cells = []
    leading_blanks = month_start.weekday()
    for _blank in range(leading_blanks):
        month_cells.append({'is_padding': True})

    for day_num in range(1, days_in_month + 1):
        day = date(year, month, day_num)
        counts = _aggregate_day_counts(employees, month_bulk, day)
        attended = counts.get('present', 0) + counts.get('late', 0) + counts.get('partial', 0)
        status = _aggregate_status(counts, len(employees), day)
        month_cells.append(
            {
                'is_padding': False,
                'date': day,
                'day_number': day_num,
                'weekday_short': WEEKDAY_SHORT[day.weekday()],
                'status': status,
                'status_label': STATUS_DISPLAY.get(status, ''),
                'present_count': attended,
                'total': len(employees),
                'is_weekend': day.weekday() >= 5,
                'is_selected': day == focus_day,
                'day_url': _registry_query(
                    request,
                    **{
                        **base,
                        'day': day.isoformat(),
                        'year': year,
                        'month': month,
                        'week': week_start.isoformat(),
                    },
                ),
            }
        )

    trailing = (7 - (len(month_cells) % 7)) % 7
    month_cells.extend({'is_padding': True} for _blank in range(trailing))
    month_weeks = [month_cells[index : index + 7] for index in range(0, len(month_cells), 7)]

    prev_day = focus_day - timedelta(days=1)
    next_day = focus_day + timedelta(days=1)
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    prev_month = _shift_month(year, month, -1)
    next_month = _shift_month(year, month, 1)

    week_late = 0
    week_absent = 0
    week_present_morning = 0
    for employee in employees:
        for offset in range(7):
            day = week_start + timedelta(days=offset)
            if day.weekday() >= 5:
                continue
            detail = _day_detail(week_bulk.get(employee.pk, {}), day)
            slots = detail.get('slots', {})
            if slots.get('MORNING_IN', {}).get('punch_time'):
                week_present_morning += 1
            if detail['status'] == 'late':
                week_late += 1
            elif detail['status'] == 'absent':
                week_absent += 1

    month_late = sum(row['late_count'] for row in monthly_list_rows)
    month_absent = sum(row['absence_count'] for row in monthly_list_rows)
    month_present_morning = sum(row['present_days'] for row in monthly_list_rows)

    sheet_kpis = {
        'daily': {
            'total': len(employees),
            'present_morning': present_morning,
            'present_morning_pct': daily_aggregate['present_morning_pct'],
            'late': daily_aggregate['late'],
            'absent': daily_aggregate['absent'],
        },
        'weekly': {
            'total': len(employees),
            'present_morning': week_present_morning,
            'present_morning_pct': round(week_present_morning * 1000 / max(len(employees) * 5, 1)) / 10,
            'late': week_late,
            'absent': week_absent,
        },
        'monthly': {
            'total': len(employees),
            'present_morning': month_present_morning,
            'present_morning_pct': round(month_present_morning * 1000 / max(len(employees) * 22, 1)) / 10,
            'late': month_late,
            'absent': month_absent,
        },
    }

    daily_pagination = _paginate_rows(daily_list_rows, request)
    weekly_pagination = _paginate_rows(weekly_list_rows, request)
    monthly_pagination = _paginate_rows(monthly_list_rows, request)

    today = date.today()
    week_end = week_start + timedelta(days=6)
    month_last_day = date(year, month, monthrange(year, month)[1])
    if period_view == 'daily':
        can_go_next = focus_day < today
        period_nav_label = focus_day.strftime('%d/%m/%Y')
    elif period_view == 'weekly':
        can_go_next = week_end < today
        period_nav_label = (
            f'{week_start.day} {MONTH_SHORT[week_start.month - 1]} — '
            f'{week_end.day} {MONTH_SHORT[week_end.month - 1]} {week_end.year}'
        )
    else:
        can_go_next = month_last_day < today
        period_nav_label = f'{MONTH_NAMES[month - 1]} {year}'

    today_week = today - timedelta(days=today.weekday())

    return {
        'period_view': period_view,
        'display_mode': display_mode,
        'focus_day': focus_day,
        'is_today': focus_day == today,
        'today_iso': today.isoformat(),
        'can_go_next': can_go_next,
        'period_nav_label': period_nav_label,
        'focus_day_label': focus_day.strftime('%d/%m/%Y'),
        'focus_day_long_label': (
            f'{WEEKDAY_FULL[focus_day.weekday()]}, {focus_day.day} '
            f'{MONTH_NAMES[focus_day.month - 1]} {focus_day.year}'
        ),
        'week_range_label': (
            f'{week_start.day} {MONTH_SHORT[week_start.month - 1]} — '
            f'{week_end.day} {MONTH_SHORT[week_end.month - 1]} {week_end.year}'
        ),
        'month_label': MONTH_NAMES[month - 1],
        'urls': {
            'clear_search': _registry_query(request, **{**base, 'q': None, 'page': 1}),
            'go_today': _registry_query(
                request,
                **{
                    **base,
                    'day': today.isoformat(),
                    'year': today.year,
                    'month': today.month,
                    'week': today_week.isoformat(),
                    'page': 1,
                },
            ),
            'period_daily': _registry_query(request, **{**base, 'period_view': 'daily'}),
            'period_weekly': _registry_query(request, **{**base, 'period_view': 'weekly'}),
            'period_monthly': _registry_query(request, **{**base, 'period_view': 'monthly'}),
            'display_list': _registry_query(request, **{**base, 'display_mode': 'list'}),
            'display_calendar': _registry_query(request, **{**base, 'display_mode': 'calendar'}),
            'prev_day': _registry_query(
                request, day=prev_day.isoformat(), year=prev_day.year, month=prev_day.month, **base
            ),
            'next_day': _registry_query(
                request, day=next_day.isoformat(), year=next_day.year, month=next_day.month, **base
            ),
            'prev_week': _registry_query(
                request, week=prev_week.isoformat(), year=prev_week.year, month=prev_week.month, **base
            ),
            'next_week': _registry_query(
                request, week=next_week.isoformat(), year=next_week.year, month=next_week.month, **base
            ),
            'prev_month': _registry_query(
                request,
                year=prev_month['year'],
                month=prev_month['month'],
                week=week_start.isoformat(),
                **base,
            ),
            'next_month': _registry_query(
                request,
                year=next_month['year'],
                month=next_month['month'],
                week=week_start.isoformat(),
                **base,
            ),
        },
        'daily': {
            'list_rows': daily_list_rows,
            'pagination': daily_pagination,
            'aggregate': daily_aggregate,
        },
        'weekly': {
            'list_rows': weekly_list_rows,
            'pagination': weekly_pagination,
            'calendar_days': weekly_calendar_days,
            'weekday_headers': WEEKDAY_SHORT,
        },
        'monthly': {
            'list_rows': monthly_list_rows,
            'pagination': monthly_pagination,
            'weekday_headers': WEEKDAY_SHORT,
            'weeks': month_weeks,
        },
        'sheet_kpis': sheet_kpis,
        'sheet_kpis_current': sheet_kpis.get(period_view, sheet_kpis['daily']),
        'slot_headers': list(get_slot_ui_headers()),
        'total_slots': get_total_slots(),
    }


def _summarize_employee(employee, year, month, attendance_by_date):
    working_days = _weekdays_in_month(year, month)
    present_days = 0
    late_count = 0
    absence_count = 0
    total_late_minutes = 0

    for day in working_days:
        detail = _day_detail(attendance_by_date, day)
        if detail['status'] == 'absent':
            absence_count += 1
        elif detail['status'] in ('present', 'late', 'partial'):
            present_days += 1
            if detail['status'] == 'late':
                late_count += 1
                total_late_minutes += detail['delay_minutes']

    total_working = len(working_days) or 1
    presence_rate = round(present_days * 1000 / total_working) / 10

    return {
        'employee': employee,
        'presence_rate': presence_rate,
        'late_count': late_count,
        'absence_count': absence_count,
        'present_days': present_days,
        'on_time_days': sum(
            1
            for day in working_days
            if _day_detail(attendance_by_date, day)['status'] == 'present'
        ),
        'total_late_minutes': total_late_minutes,
        'working_days_count': len(working_days),
    }


def _count_lates_in_range(attendance_by_date, start, end):
    late_count = 0
    current = start
    while current <= end:
        if current.weekday() < 5:
            detail = _day_detail(attendance_by_date, current)
            if detail['status'] == 'late':
                late_count += 1
        current += timedelta(days=1)
    return late_count


def build_company_attendance_dashboard(request):
    today = date.today()
    year, month, week_start, period_view, display_mode, focus_day = _parse_registry_params(request, today)
    zone_period = request.GET.get('zone_period', 'week')
    search_query = (request.GET.get('q') or '').strip()

    employees = list(_company_employees_queryset(request))
    employee_ids = [employee.pk for employee in employees]

    days_in_month = monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)
    month_bulk = _bulk_attendance(employee_ids, month_start, month_end)

    summaries = [
        _summarize_employee(
            employee,
            year,
            month,
            month_bulk.get(employee.pk, {}),
        )
        for employee in employees
    ]

    prev = _shift_month(year, month, -1)
    prev_days_in_month = monthrange(prev['year'], prev['month'])[1]
    prev_bulk = _bulk_attendance(
        employee_ids,
        date(prev['year'], prev['month'], 1),
        date(prev['year'], prev['month'], prev_days_in_month),
    )
    prev_summaries = [
        _summarize_employee(
            employee,
            prev['year'],
            prev['month'],
            prev_bulk.get(employee.pk, {}),
        )
        for employee in employees
    ]

    total_working = sum(item['working_days_count'] for item in summaries) or 1
    total_present = sum(item['present_days'] for item in summaries)
    total_lates = sum(item['late_count'] for item in summaries)
    total_absences = sum(item['absence_count'] for item in summaries)
    total_late_minutes = sum(item['total_late_minutes'] for item in summaries)

    prev_total_working = sum(item['working_days_count'] for item in prev_summaries) or 1
    prev_total_present = sum(item['present_days'] for item in prev_summaries)
    prev_rate = round(prev_total_present * 1000 / prev_total_working) / 10
    global_rate = round(total_present * 1000 / total_working) / 10
    rate_delta = round(global_rate - prev_rate, 1)

    avg_late_minutes = round(total_late_minutes / total_lates) if total_lates else 0

    prev_total_lates = sum(item['late_count'] for item in prev_summaries)
    late_trend = 0
    if prev_total_lates:
        late_trend = round((total_lates - prev_total_lates) * 100 / prev_total_lates)

    prev_total_absences = sum(item['absence_count'] for item in prev_summaries)
    absence_trend_label = _('Stable')
    if prev_total_absences and total_absences < prev_total_absences:
        reduction = round((prev_total_absences - total_absences) * 100 / prev_total_absences)
        absence_trend_label = _('Réduction de %(pct)s%% vs S-1') % {'pct': reduction}
    elif total_absences > prev_total_absences:
        absence_trend_label = _('Hausse vs S-1')

    departments = defaultdict(
        lambda: {
            'name': '',
            'present': 0,
            'late': 0,
            'absent': 0,
            'working': 0,
        }
    )
    for item in summaries:
        employee = item['employee']
        key = employee.direction_id or 0
        departments[key]['name'] = str(employee.direction) if employee.direction else _('Sans direction')
        departments[key]['present'] += item['on_time_days']
        departments[key]['late'] += item['late_count']
        departments[key]['absent'] += item['absence_count']
        departments[key]['working'] += item['working_days_count']

    department_rows = []
    for direction_id, data in departments.items():
        working = data['working'] or 1
        department_rows.append(
            {
                'direction_id': direction_id or None,
                'name': data['name'],
                'presence_rate': round(data['present'] * 100 / working),
                'present_pct': round(data['present'] * 100 / working, 1),
                'late_pct': round(data['late'] * 100 / working, 1),
                'absent_pct': round(data['absent'] * 100 / working, 1),
            }
        )
    department_rows.sort(key=lambda row: row['presence_rate'], reverse=True)

    present_agents = 0
    late_agents = 0
    absent_agents = 0
    for item in summaries:
        if item['absence_count'] > 0:
            absent_agents += 1
        elif item['late_count'] > 0:
            late_agents += 1
        else:
            present_agents += 1

    week_end = week_start + timedelta(days=6)
    week_bulk = _bulk_attendance(employee_ids, week_start, week_end)
    red_zone = []
    for employee in employees:
        if zone_period == 'month':
            item = next(summary for summary in summaries if summary['employee'].pk == employee.pk)
            score = item['late_count']
            label = _('%(count)s retards') % {'count': score}
        else:
            score = _count_lates_in_range(week_bulk.get(employee.pk, {}), week_start, week_end)
            label = _('%(count)s retards') % {'count': score}
        if score > 0:
            red_zone.append(
                {
                    'employee': employee,
                    'score': score,
                    'label': label,
                    'direction': str(employee.direction) if employee.direction else '—',
                }
            )
    red_zone.sort(key=lambda row: row['score'], reverse=True)
    red_zone = red_zone[:5]

    selected_direction = None
    direction_id = request.GET.get('direction')
    if direction_id:
        selected_direction = Direction.objects.filter(pk=direction_id).first()

    agent_total = len(employees) or 1
    donut_present_angle = round(present_agents * 360 / agent_total, 1)
    donut_late_angle = round(late_agents * 360 / agent_total, 1)
    donut_absent_angle = round(absent_agents * 360 / agent_total, 1)
    donut_late_end = round(donut_present_angle + donut_late_angle, 1)

    return {
        'year': year,
        'month': month,
        'month_label': MONTH_NAMES[month - 1],
        'week_start': week_start,
        'zone_period': zone_period,
        'directions': Direction.objects.order_by('name'),
        'selected_direction': selected_direction,
        'selected_direction_id': direction_id or '',
        'search_query': search_query,
        'global_rate': global_rate,
        'global_rate_angle': round(global_rate * 3.6, 1),
        'rate_delta': rate_delta,
        'prev_rate': prev_rate,
        'total_lates': total_lates,
        'late_trend': late_trend,
        'avg_late_minutes': avg_late_minutes,
        'total_absences': total_absences,
        'absence_trend_label': absence_trend_label,
        'total_agents': len(employees),
        'present_agents': present_agents,
        'late_agents': late_agents,
        'absent_agents': absent_agents,
        'donut_present_angle': donut_present_angle,
        'donut_late_angle': donut_late_angle,
        'donut_late_end': donut_late_end,
        'donut_absent_angle': donut_absent_angle,
        'department_rows': department_rows,
        'red_zone': red_zone,
        'prev': _shift_month(year, month, -1),
        'next': _shift_month(year, month, 1),
        'registry': build_company_registry(request, employees, year, month, week_start),
        'total_slots': get_total_slots(),
    }
