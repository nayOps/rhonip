"""Statistiques de présence — effectif réel, segments et projections."""

from __future__ import annotations

from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
import json
from urllib.parse import urlencode

from django.db import connection
from django.db.models import Q
from django.utils.translation import gettext as _

from employee.models import Direction, Employee
from employee.utils.attendance_slots import evaluate_day_slots
from employee.utils.attendance_stats import MONTH_NAMES, bulk_attendance_details
from employee.utils.report_pdf_common import build_pdf_filename, logo_data_uri
from employee.utils.roster import apply_roster_filter

REAL_AGENT_THRESHOLD = 60
MORNING_SLOT = 'MORNING_IN'
EVENING_SLOT = 'EVENING_OUT'


def _employee_display_name(employee) -> str:
    label = employee.full_name() if callable(getattr(employee, 'full_name', None)) else getattr(employee, 'full_name', '')
    return str(label or '').strip() or '—'


def _text_key(value) -> str:
    if callable(value):
        value = value()
    return str(value or '').casefold()


def _format_punch_label(last_punch) -> str:
    """Attendance.time est un TextField — date/heure peuvent être date/time ou str."""
    if not last_punch:
        return '—'
    punch_date, punch_time = last_punch
    if hasattr(punch_date, 'strftime'):
        date_label = punch_date.strftime('%d/%m/%Y')
    else:
        raw = str(punch_date or '').strip()
        try:
            date_label = date.fromisoformat(raw[:10]).strftime('%d/%m/%Y')
        except ValueError:
            date_label = raw or '—'

    raw_time = str(punch_time or '').strip()
    if hasattr(punch_time, 'strftime'):
        time_label = punch_time.strftime('%H:%M')
    elif len(raw_time) >= 5:
        time_label = raw_time[:5]
    else:
        time_label = raw_time or '—'

    if date_label == '—' and time_label == '—':
        return '—'
    return f'{date_label} {time_label}'.strip()

SEGMENT_CHOICES = (
    ('all', _('Tous les segments')),
    ('ghost', _('Fantômes (enrôlé, jamais pointé)')),
    ('nominal', _('De nom (sans empreinte, jamais pointé)')),
    ('never_punched', _('Jamais pointé (période)')),
    ('morning_only', _('Matin seulement')),
    ('rare_evening', _('Sortie soir rare')),
    ('regular_complete', _('Complet régulier (entrée + sortie)')),
    ('daily', _('Quotidien (≥ 95 %)')),
    ('irregular', _('Irrégulier (10–50 %)')),
    ('chronic_absent', _('Absent chronique (< 10 %)')),
    ('real_agent', _('Agent réel (≥ 60 %)')),
    ('two_slots_daily', _('≥ 2 pointages/jour (matin + soir)')),
)

THRESHOLD_CURVE = (40, 50, 60, 70, 80, 90)


def parse_presence_statistics_filters(
    *,
    year=None,
    month=None,
    direction_id=None,
    segment='all',
    search_query='',
    page=1,
    today=None,
):
    today = today or date.today()
    year = int(year or today.year)
    month = int(month or today.month)
    month = max(1, min(12, month))

    direction_pk = None
    if direction_id not in (None, ''):
        try:
            direction_pk = int(direction_id)
        except (TypeError, ValueError):
            direction_pk = None

    segment = (segment or 'all').strip()
    valid_segments = {code for code, _ in SEGMENT_CHOICES}
    if segment not in valid_segments:
        segment = 'all'

    search_query = (search_query or '').strip()
    try:
        page = max(1, int(page or 1))
    except (TypeError, ValueError):
        page = 1

    month_start = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]
    month_end = date(year, month, days_in_month)
    period_end = min(month_end, today) if (year, month) == (today.year, today.month) else month_end

    return {
        'year': year,
        'month': month,
        'month_start': month_start,
        'month_end': month_end,
        'period_end': period_end,
        'direction_id': direction_pk,
        'segment': segment,
        'search_query': search_query,
        'page': page,
    }


def build_query_string(**filters) -> str:
    params = {}
    if filters.get('year'):
        params['year'] = filters['year']
    if filters.get('month'):
        params['month'] = filters['month']
    if filters.get('direction_id'):
        params['direction'] = filters['direction_id']
    if filters.get('segment') and filters['segment'] != 'all':
        params['segment'] = filters['segment']
    if filters.get('search_query'):
        params['q'] = filters['search_query']
    if filters.get('page') and int(filters['page']) > 1:
        params['page'] = filters['page']
    return urlencode(params)


def _weekdays_between(start: date, end: date) -> list[date]:
    if end < start:
        return []
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def _bulk_enrollment_counts(registration_numbers: list[str]) -> dict[str, int]:
    numbers = [number for number in registration_numbers if number]
    if not numbers:
        return {}

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT registration_number, COUNT(*)
            FROM fgp_fingerprints
            WHERE capture_status = 'CAPTURED'
              AND registration_number = ANY(%s)
            GROUP BY registration_number
            """,
            [numbers],
        )
        return {row[0]: int(row[1]) for row in cursor.fetchall()}


def _bulk_punch_sources(employee_ids, start, end) -> dict[int, Counter]:
    from employee.models import Attendance

    if not employee_ids:
        return {}

    rows = Attendance.objects.filter(
        employee_id__in=employee_ids,
        date__gte=start,
        date__lte=end,
    ).values_list('employee_id', 'source')

    grouped = defaultdict(Counter)
    for employee_id, source in rows:
        grouped[employee_id][source or 'manual'] += 1
    return grouped


def _bulk_last_punch(employee_ids, start, end) -> dict[int, tuple[date, time]]:
    from employee.models import Attendance

    if not employee_ids:
        return {}

    rows = (
        Attendance.objects.filter(
            employee_id__in=employee_ids,
            date__gte=start,
            date__lte=end,
        )
        .order_by('employee_id', '-date', '-time')
        .values_list('employee_id', 'date', 'time')
    )
    last = {}
    for employee_id, punch_date, punch_time in rows:
        if employee_id not in last:
            last[employee_id] = (punch_date, punch_time)
    return last


def _slot_punched(slots: dict, code: str) -> bool:
    slot = slots.get(code) or {}
    return slot.get('punch_time') is not None


def _dominant_source(counter: Counter) -> str:
    if not counter:
        return '—'
    source, _count = counter.most_common(1)[0]
    labels = {
        'fingerprint': _('Empreinte'),
        'manual': _('Manuel'),
        'import': _('Import'),
    }
    return str(labels.get(source, source))


def _compute_agent_row(
    employee,
    working_days: list[date],
    attendance_by_date: dict,
    enrolled_count: int,
    source_counter: Counter,
    last_punch,
) -> dict:
    working_count = len(working_days) or 1
    present_days = 0
    morning_days = 0
    evening_days = 0
    both_days = 0
    two_slot_days = 0
    total_raw_punches = 0
    late_days = 0
    partial_days = 0
    days_morning_no_evening = 0

    for day in working_days:
        punch_times = attendance_by_date.get(day, [])
        total_raw_punches += len(punch_times)
        detail = evaluate_day_slots(day, punch_times)
        if detail['status'] == 'weekend':
            continue

        slots = detail.get('slots', {})
        has_morning = _slot_punched(slots, MORNING_SLOT)
        has_evening = _slot_punched(slots, EVENING_SLOT)
        validated = detail.get('validated_slots', 0)

        if validated > 0 or punch_times:
            present_days += 1
        if has_morning:
            morning_days += 1
        if has_evening:
            evening_days += 1
        if has_morning and has_evening:
            both_days += 1
            two_slot_days += 1
        elif has_morning and not has_evening:
            days_morning_no_evening += 1
        if detail['status'] == 'late':
            late_days += 1
        elif detail['status'] == 'partial':
            partial_days += 1

    presence_rate = round(present_days * 1000 / working_count) / 10
    both_rate = round(both_days * 1000 / working_count) / 10
    morning_only_rate = 0.0
    evening_on_present_rate = 0.0

    if present_days:
        morning_only_rate = round(days_morning_no_evening * 1000 / present_days) / 10
        evening_on_present_rate = round(evening_days * 1000 / present_days) / 10

    avg_punches = round(total_raw_punches * 10 / present_days) / 10 if present_days else 0.0
    real_score = min(
        100,
        round(
            presence_rate * 0.6
            + both_rate * 0.3
            + min(enrolled_count, 10) * 1.0
        ),
    )

    last_label = _format_punch_label(last_punch)

    row = {
        'employee': employee,
        'matricule': employee.registration_number or '—',
        'full_name': _employee_display_name(employee),
        'direction': str(employee.direction) if employee.direction else '—',
        'enrolled_count': enrolled_count,
        'enrollment_label': f'{enrolled_count}/10',
        'working_days': working_count,
        'present_days': present_days,
        'absent_days': working_count - present_days,
        'morning_days': morning_days,
        'evening_days': evening_days,
        'both_days': both_days,
        'two_slot_days': two_slot_days,
        'presence_rate': presence_rate,
        'both_rate': both_rate,
        'morning_only_rate': morning_only_rate,
        'evening_on_present_rate': evening_on_present_rate,
        'avg_punches': avg_punches,
        'late_days': late_days,
        'partial_days': partial_days,
        'total_punches': total_raw_punches,
        'dominant_source': _dominant_source(source_counter),
        'last_punch_label': last_label,
        'real_score': real_score,
        'is_real_agent': presence_rate >= REAL_AGENT_THRESHOLD,
    }
    row['segment'] = classify_segment(row)
    row['segment_label'] = dict(SEGMENT_CHOICES).get(row['segment'], row['segment'])
    return row


def classify_segment(row: dict) -> str:
    if row['total_punches'] == 0:
        if row['enrolled_count'] >= 1:
            return 'ghost'
        return 'nominal'

    rate = row['presence_rate']
    if rate < 10:
        return 'chronic_absent'
    if row['present_days'] >= 3 and row['morning_only_rate'] >= 70:
        return 'morning_only'
    if row['present_days'] >= 3 and row['evening_on_present_rate'] < 30:
        return 'rare_evening'
    if rate >= 95:
        return 'daily'
    if row['both_rate'] >= 80:
        return 'regular_complete'
    if row['two_slot_days'] >= row['present_days'] * 0.8 and row['present_days'] >= 3:
        return 'two_slots_daily'
    if 10 <= rate < 50:
        return 'irregular'
    if rate >= REAL_AGENT_THRESHOLD:
        return 'real_agent'
    return 'irregular'


def _exclusive_segment(row: dict) -> str:
    """Classification exclusive pour le graphique donut."""
    order = (
        'ghost',
        'nominal',
        'chronic_absent',
        'morning_only',
        'rare_evening',
        'irregular',
        'daily',
        'regular_complete',
        'two_slots_daily',
        'real_agent',
    )
    segment = row['segment']
    if segment in order:
        return segment
    return 'irregular'


def _build_kpis(rows: list[dict]) -> dict:
    total = len(rows)
    enrolled_complete = sum(1 for row in rows if row['enrolled_count'] >= 10)
    enrolled_partial = sum(1 for row in rows if 1 <= row['enrolled_count'] < 10)
    no_fingerprint = sum(1 for row in rows if row['enrolled_count'] == 0)
    punched_once = sum(1 for row in rows if row['total_punches'] > 0)
    never_punched = sum(1 for row in rows if row['total_punches'] == 0)
    real_agents = sum(1 for row in rows if row['is_real_agent'])

    return {
        'total_active': total,
        'enrolled_complete': enrolled_complete,
        'enrolled_partial': enrolled_partial,
        'no_fingerprint': no_fingerprint,
        'punched_at_least_once': punched_once,
        'never_punched': never_punched,
        'real_agents': real_agents,
        'real_agents_rate': round(real_agents * 1000 / total) / 10 if total else 0,
    }


def _build_threshold_curve(rows: list[dict]) -> list[dict]:
    return [
        {
            'threshold': threshold,
            'count': sum(1 for row in rows if row['presence_rate'] >= threshold),
        }
        for threshold in THRESHOLD_CURVE
    ]


def _build_segment_donut(rows: list[dict]) -> list[dict]:
    counts = Counter(_exclusive_segment(row) for row in rows)
    labels = dict(SEGMENT_CHOICES)
    palette = {
        'ghost': '#94a3b8',
        'nominal': '#64748b',
        'chronic_absent': '#ef4444',
        'morning_only': '#f59e0b',
        'rare_evening': '#fb923c',
        'irregular': '#eab308',
        'daily': '#22c55e',
        'regular_complete': '#16a34a',
        'two_slots_daily': '#059669',
        'real_agent': '#0ea5e9',
    }
    segments = []
    for code, count in counts.most_common():
        if count <= 0:
            continue
        segments.append(
            {
                'code': code,
                'label': str(labels.get(code, code)),
                'count': count,
                'color': palette.get(code, '#64748b'),
            }
        )
    return segments


def _build_direction_breakdown(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['direction']].append(row)

    breakdown = []
    for direction, items in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        total = len(items)
        breakdown.append(
            {
                'direction': direction,
                'total': total,
                'real_agents': sum(1 for row in items if row['is_real_agent']),
                'ghosts': sum(1 for row in items if row['segment'] == 'ghost'),
                'nominal': sum(1 for row in items if row['segment'] == 'nominal'),
                'never_punched': sum(1 for row in items if row['total_punches'] == 0),
                'avg_presence': round(
                    sum(row['presence_rate'] for row in items) * 10 / total
                ) / 10 if total else 0,
            }
        )
    return breakdown


def _build_projection(rows: list[dict], working_days: list[date], month_end: date) -> dict:
    elapsed = len(working_days) or 1
    remaining_days = len(_weekdays_between(working_days[-1] + timedelta(days=1), month_end)) if working_days else 0
    avg_rate = (
        round(sum(row['presence_rate'] for row in rows) * 10 / len(rows)) / 10
        if rows
        else 0
    )
    real_now = sum(1 for row in rows if row['is_real_agent'])
    return {
        'elapsed_working_days': elapsed,
        'remaining_working_days': remaining_days,
        'avg_presence_rate': avg_rate,
        'real_agents_now': real_now,
        'real_threshold': REAL_AGENT_THRESHOLD,
    }


def _filter_rows(rows: list[dict], segment: str, search_query: str) -> list[dict]:
    filtered = rows
    if segment and segment != 'all':
        if segment == 'never_punched':
            filtered = [row for row in filtered if row['total_punches'] == 0]
        else:
            filtered = [row for row in filtered if row['segment'] == segment]

    if search_query:
        query = search_query.casefold()
        filtered = [
            row
            for row in filtered
            if query in _text_key(row['full_name'])
            or query in row['matricule'].casefold()
            or query in row['direction'].casefold()
        ]
    return filtered


def paginate_rows(rows: list[dict], page: int, per_page: int = 25) -> dict:
    total = len(rows)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = min(max(1, page), total_pages)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        'rows': rows[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_previous': page > 1,
        'has_next': page < total_pages,
    }


def build_agent_rows(
    *,
    year=None,
    month=None,
    direction_id=None,
    today=None,
) -> tuple[list[dict], dict]:
    """Calcule les lignes agents + métadonnées de période."""
    filters = parse_presence_statistics_filters(
        year=year,
        month=month,
        direction_id=direction_id,
        today=today,
    )

    employees_qs = apply_roster_filter(
        Employee.objects.filter(agent_situation='active')
        .select_related('direction')
        .order_by('last_name', 'first_name', 'middle_name', 'registration_number')
    )
    if filters['direction_id']:
        employees_qs = employees_qs.filter(direction_id=filters['direction_id'])

    employees = list(employees_qs)
    employee_ids = [employee.pk for employee in employees]
    registration_numbers = [employee.registration_number for employee in employees if employee.registration_number]

    working_days = _weekdays_between(filters['month_start'], filters['period_end'])
    bulk_attendance, source_map, last_punch_map = bulk_attendance_details(
        employee_ids,
        filters['month_start'],
        filters['period_end'],
    )
    enrollment_map = _bulk_enrollment_counts(registration_numbers)

    rows = []
    for employee in employees:
        enrolled_count = enrollment_map.get(employee.registration_number, 0)
        rows.append(
            _compute_agent_row(
                employee,
                working_days,
                bulk_attendance.get(employee.pk, {}),
                enrolled_count,
                source_map.get(employee.pk, Counter()),
                last_punch_map.get(employee.pk),
            )
        )

    rows.sort(key=lambda row: (-row['presence_rate'], _text_key(row['full_name'])))
    meta = {**filters, 'working_days': working_days}
    return rows, meta


def build_presence_statistics(
    *,
    year=None,
    month=None,
    direction_id=None,
    segment='all',
    search_query='',
    page=1,
    today=None,
) -> dict:
    filters = parse_presence_statistics_filters(
        year=year,
        month=month,
        direction_id=direction_id,
        segment=segment,
        search_query=search_query,
        page=page,
        today=today,
    )

    rows, meta = build_agent_rows(
        year=filters['year'],
        month=filters['month'],
        direction_id=filters['direction_id'],
        today=today,
    )
    working_days = meta['working_days']

    kpis = _build_kpis(rows)
    all_rows_for_charts = list(rows)
    filtered_rows = _filter_rows(rows, filters['segment'], filters['search_query'])
    pagination = paginate_rows(filtered_rows, filters['page'])
    pagination['previous_page'] = pagination['page'] - 1
    pagination['next_page'] = pagination['page'] + 1

    threshold_curve = _build_threshold_curve(all_rows_for_charts)
    segment_donut = _build_segment_donut(all_rows_for_charts)

    period_label = f"{MONTH_NAMES[filters['month'] - 1]} {filters['year']}"
    query_string = build_query_string(
        year=filters['year'],
        month=filters['month'],
        direction_id=filters['direction_id'],
        segment=filters['segment'],
        search_query=filters['search_query'],
    )

    directions = Direction.objects.order_by('name')

    return {
        'title': _('Statistiques de présence'),
        'period_label': period_label,
        'year': filters['year'],
        'month': filters['month'],
        'month_start': filters['month_start'],
        'period_end': filters['period_end'],
        'working_days_count': len(working_days),
        'selected_direction_id': filters['direction_id'],
        'segment': filters['segment'],
        'search_query': filters['search_query'],
        'segment_choices': SEGMENT_CHOICES,
        'directions': directions,
        'kpis': kpis,
        'threshold_curve': threshold_curve,
        'threshold_curve_json': json.dumps(threshold_curve),
        'segment_donut': segment_donut,
        'segment_donut_json': json.dumps(segment_donut),
        'direction_breakdown': _build_direction_breakdown(all_rows_for_charts),
        'projection': _build_projection(all_rows_for_charts, working_days, filters['month_end']),
        'real_threshold': REAL_AGENT_THRESHOLD,
        'rows': pagination['rows'],
        'filtered_rows': filtered_rows,
        'pagination': pagination,
        'query_string': query_string,
        'generated_at_label': date.today().strftime('%d/%m/%Y'),
        'pdf_filename': build_pdf_filename(
            'statistiques-presence',
            year=filters['year'],
            month=filters['month'],
        ),
        'segment_label': dict(SEGMENT_CHOICES).get(filters['segment'], filters['segment']),
        'direction_label': (
            next(
                (str(d.name) for d in directions if d.pk == filters['direction_id']),
                _('Toutes les directions'),
            )
            if filters['direction_id']
            else _('Toutes les directions')
        ),
        'logo_uri': logo_data_uri(),
        'report_title_line1': _('Statistiques de présence'),
        'report_title_line2': period_label,
        'report_ref': f"REF-RH-STATS-{filters['year']}{filters['month']:02d}",
    }


def build_presence_statistics_pdf_context(**kwargs) -> dict:
    """Contexte PDF : tous les agents filtrés (sans pagination, 1 seul calcul)."""
    report = build_presence_statistics(**{**kwargs, 'page': 1})
    filtered = list(report.get('filtered_rows') or [])
    for index, row in enumerate(filtered, start=1):
        row['numero_display'] = f'{index:03d}'
    report['rows'] = filtered
    report['pdf_rows_count'] = len(filtered)
    report['logo_uri'] = report.get('logo_uri') or logo_data_uri()
    return report


def render_presence_statistics_html(**kwargs) -> str:
    from django.template.loader import render_to_string

    report = build_presence_statistics_pdf_context(**kwargs)
    return render_to_string('employee/presence_statistics_pdf.html', report)


def render_presence_statistics_pdf(**kwargs) -> bytes:
    from employee.utils.html_pdf_renderer import render_html_to_pdf

    html = render_presence_statistics_html(**kwargs)
    return render_html_to_pdf(html)
