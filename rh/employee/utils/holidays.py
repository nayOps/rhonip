"""Jours fériés (leave.Holiday) pour la présence."""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache


def clear_holiday_cache():
    holiday_ranges_cached.cache_clear()


@lru_cache(maxsize=8)
def holiday_ranges_cached(version_key: str = 'v1'):
    """Liste (start, end, name) des fériés. version_key force invalidation via clear."""
    del version_key  # unused; key only for cache namespace
    try:
        from leave.models import Holiday
    except Exception:
        return tuple()
    rows = []
    for h in Holiday.objects.all().only('start_dt', 'end_dt', 'name'):
        if h.start_dt and h.end_dt:
            start = min(h.start_dt, h.end_dt)
            end = max(h.start_dt, h.end_dt)
            rows.append((start, end, h.name or ''))
    return tuple(rows)


def iter_holiday_dates(start: date, end: date):
    if end < start:
        return
    for h_start, h_end, _name in holiday_ranges_cached():
        cur = max(h_start, start)
        last = min(h_end, end)
        while cur <= last:
            yield cur
            cur += timedelta(days=1)


def holiday_dates_in_range(start: date, end: date) -> set[date]:
    return set(iter_holiday_dates(start, end))


def is_public_holiday(day: date) -> bool:
    for h_start, h_end, _name in holiday_ranges_cached():
        if h_start <= day <= h_end:
            return True
    return False


def is_non_working_day(day: date) -> bool:
    return day.weekday() >= 5 or is_public_holiday(day)


def holiday_name_for_day(day: date) -> str:
    for h_start, h_end, name in holiday_ranges_cached():
        if h_start <= day <= h_end:
            return name or ''
    return ''
