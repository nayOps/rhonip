from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta

from django.utils.translation import gettext as gettext_lazy

from employee.models import Direction, Employee
from employee.utils.roster import apply_roster_filter
from employee.utils.attendance_stats import (
    MONTH_NAMES,
    WEEKDAY_SHORT,
    _day_detail,
    _shift_month,
    _weekdays_in_month,
    parse_attendance_period,
)
from employee.utils.company_attendance import _bulk_attendance, _summarize_employee

_ = gettext_lazy


def _employees_for_direction(direction):
    return list(
        apply_roster_filter(
            Employee.objects.select_related('designation').filter(
                direction=direction,
            )
        )
    )


def _heatmap_level(minutes):
    if minutes <= 0:
        return 0
    if minutes <= 5:
        return 1
    if minutes <= 15:
        return 2
    return 3


def _empty_calendar_cell():
    return {
        'day_number': None,
        'level': 0,
        'is_padding': True,
    }


def build_direction_report(direction, year, month):
    employees = _employees_for_direction(direction)
    employee_ids = [employee.pk for employee in employees]
    days_in_month = monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)
    month_bulk = _bulk_attendance(employee_ids, month_start, month_end)

    summaries = [
        _summarize_employee(employee, year, month, month_bulk.get(employee.pk, {}))
        for employee in employees
    ]

    prev = _shift_month(year, month, -1)
    prev_days = monthrange(prev['year'], prev['month'])[1]
    prev_bulk = _bulk_attendance(
        employee_ids,
        date(prev['year'], prev['month'], 1),
        date(prev['year'], prev['month'], prev_days),
    )
    prev_summaries = [
        _summarize_employee(employee, prev['year'], prev['month'], prev_bulk.get(employee.pk, {}))
        for employee in employees
    ]

    total_lates = sum(item['late_count'] for item in summaries)
    prev_total_lates = sum(item['late_count'] for item in prev_summaries)
    total_late_minutes = sum(item['total_late_minutes'] for item in summaries)
    agent_count = len(employees) or 1
    avg_per_agent = round(total_late_minutes / agent_count, 1)

    late_trend_pct = 0
    if prev_total_lates:
        late_trend_pct = round((total_lates - prev_total_lates) * 100 / prev_total_lates)

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    prev_week_start = week_start - timedelta(days=7)
    week_end = week_start + timedelta(days=6)
    prev_week_end = week_start - timedelta(days=1)

    week_bulk = _bulk_attendance(employee_ids, week_start, week_end)
    prev_week_bulk = _bulk_attendance(employee_ids, prev_week_start, prev_week_end)

    week_lates = 0
    current = week_start
    while current <= week_end:
        if current.weekday() < 5:
            for employee in employees:
                detail = _day_detail(week_bulk.get(employee.pk, {}), current)
                if detail['status'] == 'late':
                    week_lates += 1
        current += timedelta(days=1)

    prev_week_lates = 0
    current = prev_week_start
    while current <= prev_week_end:
        if current.weekday() < 5:
            for employee in employees:
                detail = _day_detail(prev_week_bulk.get(employee.pk, {}), current)
                if detail['status'] == 'late':
                    prev_week_lates += 1
        current += timedelta(days=1)

    weekly_trend_pct = 0
    if prev_week_lates:
        weekly_trend_pct = round((week_lates - prev_week_lates) * 100 / prev_week_lates)
    weekly_trend_label = _('Amélioration') if weekly_trend_pct <= 0 else _('Dégradation')

    day_delays = defaultdict(int)
    for day_num in range(1, days_in_month + 1):
        day = date(year, month, day_num)
        if day.weekday() >= 5:
            continue
        max_delay = 0
        for employee in employees:
            detail = _day_detail(month_bulk.get(employee.pk, {}), day)
            max_delay = max(max_delay, detail.get('delay_minutes', 0))
        day_delays[day] = max_delay

    cells = []
    leading_blanks = month_start.weekday()
    cells.extend([_empty_calendar_cell() for _range in range(leading_blanks)])

    for day_num in range(1, days_in_month + 1):
        day = date(year, month, day_num)
        if day.weekday() >= 5:
            cells.append(
                {
                    'day_number': day_num,
                    'level': 0,
                    'is_padding': False,
                    'is_weekend': True,
                }
            )
        else:
            delay = day_delays.get(day, 0)
            cells.append(
                {
                    'day_number': day_num,
                    'level': _heatmap_level(delay),
                    'is_padding': False,
                    'is_weekend': False,
                }
            )

    trailing = (7 - (len(cells) % 7)) % 7
    cells.extend([_empty_calendar_cell() for _range in range(trailing)])
    heatmap_weeks = [cells[index:index + 7] for index in range(0, len(cells), 7)]

    top_agents = sorted(
        [
            {
                'employee': item['employee'],
                'role': str(item['employee'].designation) if item['employee'].designation else '—',
                'total_minutes': item['total_late_minutes'],
                'frequency': item['late_count'],
            }
            for item in summaries
            if item['total_late_minutes'] > 0
        ],
        key=lambda row: row['total_minutes'],
        reverse=True,
    )[:5]

    if late_trend_pct > 5:
        prediction = _(
            'Prévision : hausse de %(pct)s%% des retards le mois prochain selon la tendance actuelle.'
        ) % {'pct': abs(late_trend_pct)}
        recommendation = _(
            'Recommandation : envisager des plages d\'arrivée flexibles pour les équipes les plus impactées.'
        )
    elif late_trend_pct < -5:
        prediction = _('Prévision : amélioration continue de la ponctualité sur la période suivante.')
        recommendation = _('Recommandation : maintenir les bonnes pratiques observées ce mois-ci.')
    else:
        prediction = _('Prévision : niveau de retards stable pour la période suivante.')
        recommendation = _('Recommandation : surveiller les agents du top 5 et planifier un point d\'équipe.')

    return {
        'direction': direction,
        'year': year,
        'month': month,
        'month_label': MONTH_NAMES[month - 1],
        'period_label': f'{MONTH_NAMES[month - 1]} {year}',
        'total_lates': total_lates,
        'late_trend_pct': late_trend_pct,
        'avg_per_agent': avg_per_agent,
        'weekly_trend_pct': weekly_trend_pct,
        'weekly_trend_label': weekly_trend_label,
        'agent_count': len(employees),
        'heatmap_weeks': heatmap_weeks,
        'weekday_headers': WEEKDAY_SHORT,
        'top_agents': top_agents,
        'prediction': prediction,
        'recommendation': recommendation,
        'service_notes': [
            {
                'title': _('Entretien de recadrage'),
                'meta': _('Planifié · RH'),
            },
            {
                'title': _('Point équipe'),
                'meta': _('Hebdomadaire · Manager'),
            },
        ],
        'prev': _shift_month(year, month, -1),
        'next': _shift_month(year, month, 1),
    }


def build_direction_schedule_hub(request):
    year, month, _week_start = parse_attendance_period(request)
    directions = Direction.objects.order_by('name')
    rows = []

    for direction in directions:
        report = build_direction_report(direction, year, month)
        rows.append(
            {
                'direction': direction,
                'agent_count': report['agent_count'],
                'total_lates': report['total_lates'],
                'avg_per_agent': report['avg_per_agent'],
                'period_label': report['period_label'],
            }
        )

    return {
        'year': year,
        'month': month,
        'month_label': MONTH_NAMES[month - 1],
        'rows': rows,
        'prev': _shift_month(year, month, -1),
        'next': _shift_month(year, month, 1),
    }
