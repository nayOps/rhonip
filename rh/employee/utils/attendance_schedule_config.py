from datetime import datetime, time
from functools import lru_cache

from django.utils.translation import gettext as _


def _t(label):
    return label


DEFAULT_WORK_START = time(8, 0)
DEFAULT_WORK_END = time(16, 0)
DEFAULT_LUNCH_BREAK_MIN = 50
DEFAULT_LUNCH_BREAK_MAX = 70

PRESET_4_SLOTS_CONFIG = [
    {
        'code': 'MORNING_IN',
        'label': _t('Entrée matin'),
        'target': '08:00',
        'accept_from': '08:00',
        'accept_until': '10:00',
        'reference': '08:00',
        'ui_header': _t('Matin : Entrée 1'),
    },
    {
        'code': 'LUNCH_OUT',
        'label': _t('Sortie pause'),
        'target': '12:00',
        'accept_from': '10:01',
        'accept_until': '12:30',
        'ui_header': _t('Matin : Sortie 1'),
    },
    {
        'code': 'LUNCH_IN',
        'label': _t('Entrée pause'),
        'target': '13:00',
        'accept_from': '12:00',
        'accept_until': '14:00',
        'ui_header': _t('Après-midi : Entrée 2'),
    },
    {
        'code': 'EVENING_OUT',
        'label': _t('Sortie soir'),
        'target': '16:00',
        'accept_from': '16:00',
        'accept_until': '23:59',
        'reference': '16:00',
        'ui_header': _t('Après-midi : Sortie 2'),
    },
]

PRESET_2_SLOTS_CONFIG = [
    {
        'code': 'MORNING_IN',
        'label': _t('Entrée'),
        'target': '08:00',
        'accept_from': '08:00',
        'accept_until': '10:00',
        'reference': '08:00',
        'ui_header': _t('Entrée'),
    },
    {
        'code': 'EVENING_OUT',
        'label': _t('Sortie'),
        'target': '16:00',
        'accept_from': '16:00',
        'accept_until': '23:59',
        'ui_header': _t('Sortie'),
    },
]

PRESET_CONFIGS = {
    '4_slots': PRESET_4_SLOTS_CONFIG,
    '2_slots': PRESET_2_SLOTS_CONFIG,
}


def _parse_time_value(value):
    if value is None:
        return None
    if isinstance(value, time):
        return value
    text = str(value).strip()
    for fmt in ('%H:%M:%S', '%H:%M'):
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    raise ValueError(f'Heure invalide: {value!r}')


def _time_to_str(value):
    if value is None:
        return None
    if isinstance(value, time):
        return value.strftime('%H:%M')
    return str(value)


def _is_meaningful_reference(value):
    if value is None:
        return False
    text = str(value).strip()
    if not text or text in ('00:00', '00:00:00'):
        return False
    parsed = value if isinstance(value, time) else _parse_time_value(value)
    return not (parsed.hour == 0 and parsed.minute == 0 and parsed.second == 0)


def serialize_slot(slot):
    payload = {
        'code': slot['code'],
        'label': str(slot.get('label', slot['code'])),
        'target': _time_to_str(slot.get('target')),
        'accept_from': _time_to_str(slot['accept_from']),
        'accept_until': _time_to_str(slot['accept_until']),
        'ui_header': str(slot.get('ui_header', slot.get('label', slot['code']))),
    }
    if _is_meaningful_reference(slot.get('reference')):
        payload['reference'] = _time_to_str(slot['reference'])
    return payload


def deserialize_slot(slot):
    parsed = {
        'code': slot['code'],
        'label': slot.get('label', slot['code']),
        'target': _parse_time_value(slot.get('target')),
        'accept_from': _parse_time_value(slot['accept_from']),
        'accept_until': _parse_time_value(slot['accept_until']),
        'ui_header': slot.get('ui_header', slot.get('label', slot['code'])),
    }
    if _is_meaningful_reference(slot.get('reference')):
        parsed['reference'] = _parse_time_value(slot['reference'])
    return parsed


def preset_slots(preset_key):
    return [deserialize_slot(item) for item in PRESET_CONFIGS[preset_key]]


def default_schedule_row():
    return {
        'slot_preset': '4_slots',
        'slots_config': [serialize_slot(slot) for slot in preset_slots('4_slots')],
        'work_start': DEFAULT_WORK_START,
        'work_end': DEFAULT_WORK_END,
        'lunch_break_min_minutes': DEFAULT_LUNCH_BREAK_MIN,
        'lunch_break_max_minutes': DEFAULT_LUNCH_BREAK_MAX,
    }


@lru_cache(maxsize=1)
def get_attendance_schedule():
    from employee.models import AttendanceSchedule

    row = AttendanceSchedule.objects.first()
    if not row:
        defaults = default_schedule_row()
        return {
            'slot_preset': defaults['slot_preset'],
            'slots': preset_slots(defaults['slot_preset']),
            'work_start': defaults['work_start'],
            'work_end': defaults['work_end'],
            'lunch_break_min_minutes': defaults['lunch_break_min_minutes'],
            'lunch_break_max_minutes': defaults['lunch_break_max_minutes'],
        }

    slots_raw = row.slots_config or PRESET_CONFIGS.get(row.slot_preset, PRESET_4_SLOTS_CONFIG)
    return {
        'slot_preset': row.slot_preset,
        'slots': [deserialize_slot(slot) for slot in slots_raw],
        'work_start': row.work_start,
        'work_end': row.work_end,
        'lunch_break_min_minutes': row.lunch_break_min_minutes,
        'lunch_break_max_minutes': row.lunch_break_max_minutes,
    }


def clear_attendance_schedule_cache():
    get_attendance_schedule.cache_clear()


def get_presence_slots():
    return get_attendance_schedule()['slots']


def get_slot_by_code():
    return {slot['code']: slot for slot in get_presence_slots()}


def get_slot_codes():
    return tuple(slot['code'] for slot in get_presence_slots())


def get_slot_ui_headers():
    return tuple(slot.get('ui_header', slot['label']) for slot in get_presence_slots())


def get_total_slots():
    return len(get_presence_slots())


def get_work_start():
    return get_attendance_schedule()['work_start']


def get_work_end():
    return get_attendance_schedule()['work_end']


def get_lunch_break_limits():
    schedule = get_attendance_schedule()
    return schedule['lunch_break_min_minutes'], schedule['lunch_break_max_minutes']


def has_lunch_slots():
    codes = set(get_slot_codes())
    return 'LUNCH_OUT' in codes and 'LUNCH_IN' in codes


def first_slot_code():
    codes = get_slot_codes()
    return codes[0] if codes else 'MORNING_IN'
