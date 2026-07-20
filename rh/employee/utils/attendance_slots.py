from datetime import date, datetime, time

from django.utils import timezone
from django.utils.translation import gettext as _

from employee.utils.attendance_schedule_config import (
    get_lunch_break_limits,
    get_presence_slots,
    get_slot_codes,
    get_total_slots,
    get_work_end,
    has_lunch_slots,
    first_slot_code,
)

VALIDATED_SLOT_STATUSES = frozenset(
    {'ok', 'late', 'missed_entry', 'early_exit', 'outside_slot'}
)


def slot_display_cell(slot_data, slot_code):
    if not slot_data:
        slot_data = {'punch_label': '--:--', 'status': 'missed'}

    status = slot_data.get('status', 'missed')
    punch_label = slot_data.get('punch_label', '--:--')
    status_note = slot_data.get('status_note', '')

    def _cell(time_label, badge, badge_class, note=''):
        payload = {
            'time': time_label,
            'badge': badge,
            'badge_class': badge_class,
        }
        if note:
            payload['status_note'] = note
        return payload

    if status == 'pending':
        return _cell('--:--', _('EN COURS'), 'pending')

    if status in ('missing', 'missed'):
        if slot_code == 'EVENING_OUT':
            return _cell('--:--', _('SORTIE MANQUÉE'), 'missed')
        if slot_code == 'MORNING_IN':
            return _cell('--:--', _('ENTRÉE MANQUÉE'), 'missed')
        return _cell('--:--', _('MANQUÉE'), 'missed')

    if status == 'missed_entry':
        return _cell(
            punch_label,
            _('ENTRÉE RATÉE'),
            'missed',
            status_note or _('Hors plage matin (après 10h)'),
        )

    if status == 'early_exit':
        return _cell(
            punch_label,
            _('SORTIE EN AVANCE'),
            'missed',
            status_note or _('Avant 16h00'),
        )

    if status == 'outside_slot':
        return _cell(
            punch_label,
            _('HORS PLAGE'),
            'warning',
            status_note or _('Hors plage de sortie'),
        )

    if status == 'late':
        note = status_note
        if slot_code == 'MORNING_IN' and not note:
            delay = slot_data.get('delay_minutes', 0)
            if delay:
                note = _('Retard de %(delay)s min') % {'delay': delay}
        return _cell(punch_label, _('RETARD'), 'late', note)

    if slot_code in ('LUNCH_OUT', 'EVENING_OUT'):
        return _cell(punch_label, _('SORTIE OK'), 'ok', status_note)

    return _cell(punch_label, _('À L\'HEURE'), 'ok', status_note)


def slots_display_row(slots_by_code):
    return [
        slot_display_cell(slots_by_code.get(code), code)
        for code in get_slot_codes()
    ]


def _coerce_time(value):
    if value is None:
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, str):
        text = value.strip()
        for fmt in ('%H:%M:%S', '%H:%M'):
            try:
                return datetime.strptime(text, fmt).time()
            except ValueError:
                continue
    raise TypeError(f'Heure de pointage invalide: {value!r}')


def _is_two_slot_mode(day=None):
    return get_total_slots(day) == 2 and not has_lunch_slots(day)


class PunchRejectedError(ValueError):
    """Pointage refusé (plage horaire ou règle métier)."""


def get_two_slot_blocked_interval(day=None):
    """Zone interdite entre fin plage entrée et début plage sortie (ex. 10h01–14h59)."""
    if not _is_two_slot_mode(day):
        return None
    slots = get_presence_slots(day)
    if len(slots) != 2:
        return None
    entry_slot, exit_slot = slots[0], slots[1]
    return entry_slot['accept_until'], exit_slot['accept_from']


def _in_blocked_interval(punch_time, blocked):
    if not blocked:
        return False
    blocked_after, blocked_before = blocked
    return punch_time > blocked_after and punch_time < blocked_before


def validate_punch_allowed(punch_date, punch_time, existing_punch_times):
    """
    Règles mode 2 plages :
    - Entrée : à partir de 08h00, plage normale jusqu'à 10h00 (référence 08h00).
    - Zone bloquée (10h01–15h59) : refus seulement si une entrée est déjà
      enregistrée (matin ou unique entrée de secours dans cette zone).
    - Sans entrée matin : une seule pointe autorisée entre 10h et 16h (1er pointage).
    - Sortie : à partir de 16h00 (17h, 18h… autorisés) ; même sans entrée matin.
    - Une seconde pointe le matin ne compte pas.
    - Avant 08h00 : entrée refusée.
    """
    if not _is_two_slot_mode(punch_date):
        return None

    slots = get_presence_slots(punch_date)
    if len(slots) != 2:
        return None

    entry_slot, exit_slot = slots[0], slots[1]
    punch_time = _coerce_time(punch_time)
    blocked = get_two_slot_blocked_interval(punch_date)

    assigned = assign_punches_to_slots(existing_punch_times or [], day=punch_date)
    entry_code = entry_slot['code']
    exit_code = exit_slot['code']
    has_entry = assigned.get(entry_code) is not None
    has_exit = assigned.get(exit_code) is not None

    if has_entry and has_exit:
        return _('Pointage refusé : entrée et sortie déjà enregistrées aujourd\'hui.')

    if _in_blocked_interval(punch_time, blocked) and has_entry:
        blocked_after, blocked_before = blocked
        return _(
            'Pointage refusé : aucun pointage entre %(start)s et %(end)s.'
        ) % {
            'start': blocked_after.strftime('%H:%M'),
            'end': blocked_before.strftime('%H:%M'),
        }

    if not has_entry:
        if punch_fits_slot(punch_time, entry_slot):
            return None
        if _in_blocked_interval(punch_time, blocked):
            return None
        if punch_fits_slot(punch_time, exit_slot):
            return None
        if punch_time >= exit_slot['accept_from']:
            return _(
                'Pointage refusé : sortie uniquement jusqu\'à %(time)s.'
            ) % {'time': exit_slot['accept_until'].strftime('%H:%M')}
        if punch_time < entry_slot['accept_from']:
            return _(
                'Pointage refusé : entrée à partir de %(time)s.'
            ) % {'time': entry_slot['accept_from'].strftime('%H:%M')}
        return _(
            'Pointage refusé : entrée uniquement jusqu\'à %(time)s.'
        ) % {'time': entry_slot['accept_until'].strftime('%H:%M')}

    # Entrée déjà enregistrée — seule la sortie (plage après-midi) est acceptée
    if punch_fits_slot(punch_time, entry_slot):
        return _('Pointage refusé : entrée déjà enregistrée ce matin.')

    if punch_time < exit_slot['accept_from']:
        return _(
            'Pointage refusé : sortie à partir de %(time)s.'
        ) % {'time': exit_slot['accept_from'].strftime('%H:%M')}

    return None


def punch_fits_slot(punch_time, slot):
    """Vérifie si un pointage peut être affecté à cette plage (sans cascade)."""
    return slot['accept_from'] <= punch_time <= slot['accept_until']


def _assign_two_slot_punches(punches, presence_slots, day=None):
    entry_slot = presence_slots[0]
    exit_slot = presence_slots[1]
    entry_code = entry_slot['code']
    exit_code = exit_slot['code']
    assigned = {entry_code: None, exit_code: None}
    ordered = sorted(_coerce_time(t) for t in (punches or []) if t is not None)

    blocked = get_two_slot_blocked_interval(day)

    for punch_time in ordered:
        if assigned[entry_code] is None and punch_fits_slot(punch_time, entry_slot):
            assigned[entry_code] = punch_time

    if assigned[entry_code] is None and blocked:
        blocked_after, blocked_before = blocked
        for punch_time in ordered:
            if punch_time > blocked_after and punch_time < blocked_before:
                assigned[entry_code] = punch_time
                break

    for punch_time in reversed(ordered):
        if punch_fits_slot(punch_time, exit_slot):
            assigned[exit_code] = punch_time
            break

    return assigned


def assign_punches_to_slots(punch_times, day=None):
    """
    Affecte les pointages du jour aux plages configurées.
    Mode 2 plages : 1er pointage = entrée, dernier = sortie.
    Mode 4 plages : ordre chronologique + fenêtres acceptées.
    """
    presence_slots = get_presence_slots(day)
    punches = sorted(_coerce_time(t) for t in (punch_times or []) if t is not None)

    if _is_two_slot_mode(day) and len(presence_slots) == 2:
        return _assign_two_slot_punches(punches, presence_slots, day=day)

    assigned = {slot['code']: None for slot in presence_slots}
    used_indices = set()

    for slot in presence_slots:
        for index, punch_time in enumerate(punches):
            if index in used_indices:
                continue
            if punch_fits_slot(punch_time, slot):
                assigned[slot['code']] = punch_time
                used_indices.add(index)
                break

    return assigned


def _minutes_between(day, start_time, end_time):
    if not start_time or not end_time:
        return 0
    start_dt = datetime.combine(day, start_time)
    end_dt = datetime.combine(day, end_time)
    if end_dt < start_dt:
        return 0
    return int((end_dt - start_dt).total_seconds() // 60)


def _delay_after_reference(day, punch_time, reference):
    if not punch_time or not reference:
        return 0
    punch_dt = datetime.combine(day, punch_time)
    ref_dt = datetime.combine(day, reference)
    if punch_dt <= ref_dt:
        return 0
    return int((punch_dt - ref_dt).total_seconds() // 60)


def _unpunched_slot_status(day, slot, now=None):
    """Plage sans pointage : en cours si la fenêtre n'est pas expirée, sinon manquée."""
    now = now or timezone.localtime()
    today = now.date()
    now_time = now.time()

    if day < today:
        return 'missed'
    if day > today:
        return 'pending'
    if now_time > slot['accept_until']:
        return 'missed'
    return 'pending'


def _entry_slot_status(day, punch_time, reference, slot):
    """Avant la référence : à l'heure. À partir de la référence : retard si dans la plage."""
    if not punch_time:
        return _unpunched_slot_status(day, slot), 0, ''

    accept_until = slot['accept_until']
    if punch_time > accept_until:
        delay_minutes = _delay_after_reference(day, punch_time, reference)
        return (
            'missed_entry',
            delay_minutes,
            _('Entrée hors plage matin — pointage à %(time)s (après 10h00)')
            % {'time': punch_time.strftime('%H:%M')},
        )

    if punch_time < reference:
        return 'ok', 0, ''

    delay_minutes = _delay_after_reference(day, punch_time, reference)
    if delay_minutes > 0:
        return (
            'late',
            delay_minutes,
            _('Retard de %(delay)s min') % {'delay': delay_minutes},
        )
    return 'ok', 0, ''


def _exit_slot_status(day, punch_time, slot, now=None):
    if not punch_time:
        status = _unpunched_slot_status(day, slot, now)
        if status == 'missed':
            return 'missed', _('Sortie manquée')
        return status, ''

    accept_from = slot['accept_from']
    accept_until = slot['accept_until']

    if punch_time < accept_from:
        return (
            'early_exit',
            _('Sortie en avance à %(time)s (avant %(from)s) — sortie manquée dans la plage')
            % {
                'time': punch_time.strftime('%H:%M'),
                'from': accept_from.strftime('%H:%M'),
            },
        )

    if punch_time > accept_until:
        return (
            'outside_slot',
            _('Sortie à %(time)s (hors plage, après %(until)s)')
            % {
                'time': punch_time.strftime('%H:%M'),
                'until': accept_until.strftime('%H:%M'),
            },
        )

    return 'ok', ''


def _legacy_entry_slot_status(day, punch_time, reference, slot):
    if not punch_time:
        return _unpunched_slot_status(day, slot), 0, ''
    delay_minutes = _delay_after_reference(day, punch_time, reference)
    if punch_time < reference:
        return 'ok', 0, ''
    if delay_minutes > 0:
        return 'late', delay_minutes, _('Retard de %(delay)s min') % {'delay': delay_minutes}
    return 'ok', 0, ''


def _build_slot_row(slot, punch_time, slot_status, delay_minutes, status_note, now):
    return {
        'code': slot['code'],
        'label': slot['label'],
        'target': slot['target'],
        'accept_from': slot['accept_from'],
        'accept_until': slot['accept_until'],
        'punch_time': punch_time,
        'punch_label': punch_time.strftime('%H:%M') if punch_time else '—',
        'status': slot_status,
        'delay_minutes': delay_minutes,
        'status_note': status_note,
    }


def evaluate_day_slots(day, punch_times):
    total_slots = get_total_slots(day)
    work_end = get_work_end(day)
    lunch_min, lunch_max = get_lunch_break_limits(day)
    presence_slots = get_presence_slots(day)
    entry_code = first_slot_code(day)
    two_slot_mode = _is_two_slot_mode(day)

    if day.weekday() >= 5:
        return {
            'status': 'weekend',
            'status_label': '',
            'schedule': '',
            'note': '',
            'delay_minutes': 0,
            'worked_minutes': 0,
            'slots': {},
            'validated_slots': 0,
            'total_slots': total_slots,
            'missing_slots': [],
        }

    assigned = assign_punches_to_slots(punch_times, day=day)
    slots = []
    now = timezone.localtime()

    for slot in presence_slots:
        punch_time = assigned[slot['code']]
        delay_minutes = 0
        status_note = ''
        slot_status = _unpunched_slot_status(day, slot, now)

        if punch_time:
            reference = slot.get('reference')
            if two_slot_mode and slot['code'] == entry_code and reference:
                slot_status, delay_minutes, status_note = _entry_slot_status(
                    day, punch_time, reference, slot
                )
            elif two_slot_mode and slot['code'] == 'EVENING_OUT':
                slot_status, status_note = _exit_slot_status(day, punch_time, slot, now)
            elif slot['code'] == entry_code and reference:
                slot_status, delay_minutes, status_note = _legacy_entry_slot_status(
                    day, punch_time, reference, slot
                )
            elif reference:
                slot_status = 'ok'
                delay_minutes = _delay_after_reference(day, punch_time, reference)
                if delay_minutes > 0 and slot['code'] != 'EVENING_OUT':
                    slot_status = 'late'
                    status_note = _('Retard de %(delay)s min') % {'delay': delay_minutes}
            else:
                slot_status = 'ok'

        slots.append(
            _build_slot_row(slot, punch_time, slot_status, delay_minutes, status_note, now)
        )

    slots_by_code = {slot['code']: slot for slot in slots}
    entry_slot = slots_by_code.get(entry_code, {})
    lunch_out = slots_by_code.get('LUNCH_OUT', {})
    lunch_in = slots_by_code.get('LUNCH_IN', {})
    evening = slots_by_code.get('EVENING_OUT', slots[-1] if slots else {})

    missing_slots = []
    for slot in slots:
        if slot['status'] != 'missed':
            continue
        if slot['code'] == 'EVENING_OUT':
            missing_slots.append(_('Sortie'))
        elif slot['code'] == 'MORNING_IN':
            missing_slots.append(_('Entrée'))
        else:
            missing_slots.append(slot['label'])

    validated_slots = sum(1 for slot in slots if slot['status'] in VALIDATED_SLOT_STATUSES)

    day_start = entry_slot.get('punch_time') or lunch_out.get('punch_time')
    worked_minutes = 0
    if day_start and evening.get('punch_time'):
        worked_minutes = _minutes_between(day, day_start, evening['punch_time'])
        if lunch_out.get('punch_time') and lunch_in.get('punch_time'):
            break_minutes = _minutes_between(day, lunch_out['punch_time'], lunch_in['punch_time'])
            worked_minutes = max(0, worked_minutes - break_minutes)

    schedule_parts = [slot['punch_label'] for slot in slots if slot['punch_time']]
    schedule = ' · '.join(schedule_parts) if schedule_parts else ''

    notes = []
    delay_minutes = entry_slot.get('delay_minutes', 0)

    if not entry_slot.get('punch_time') and validated_slots == 0:
        entry_status = entry_slot.get('status')
        if day == now.date() and entry_status == 'pending':
            return {
                'status': 'partial',
                'status_label': _('EN COURS'),
                'schedule': schedule,
                'note': _('Journée en cours'),
                'delay_minutes': 0,
                'worked_minutes': 0,
                'slots': slots_by_code,
                'validated_slots': validated_slots,
                'total_slots': total_slots,
                'missing_slots': missing_slots,
            }
        return {
            'status': 'absent',
            'status_label': _('ABSENT'),
            'schedule': schedule,
            'note': _('Entrée manquante — absence non justifiée'),
            'delay_minutes': 0,
            'worked_minutes': 0,
            'slots': slots_by_code,
            'validated_slots': validated_slots,
            'total_slots': total_slots,
            'missing_slots': missing_slots,
        }

    for slot in slots:
        if slot.get('status_note'):
            notes.append(str(slot['status_note']))

    if has_lunch_slots(day) and lunch_out.get('punch_time') and lunch_in.get('punch_time'):
        break_minutes = _minutes_between(day, lunch_out['punch_time'], lunch_in['punch_time'])
        if break_minutes < lunch_min or break_minutes > lunch_max:
            notes.append(
                _('Pause %(minutes)s min (attendu ~60 min)')
                % {'minutes': break_minutes}
            )

    if (
        not two_slot_mode
        and evening.get('punch_time')
        and evening['punch_time'] < work_end
    ):
        notes.append(
            _('Sortie anticipée à %(time)s')
            % {'time': evening['punch_time'].strftime('%H:%M')}
        )

    if missing_slots and not two_slot_mode:
        notes.append(
            _('Plages manquantes : %(slots)s')
            % {'slots': ', '.join(str(label) for label in missing_slots)}
        )

    if (
        delay_minutes > 0
        and entry_slot.get('punch_time')
        and entry_slot.get('status') == 'late'
        and not any(_('Retard') in note for note in notes)
    ):
        notes.insert(
            0,
            _('Arrivée %(time)s (retard de %(delay)s min)')
            % {
                'time': entry_slot['punch_time'].strftime('%H:%M'),
                'delay': delay_minutes,
            },
        )

    note = ' · '.join(dict.fromkeys(notes))

    if not entry_slot.get('punch_time'):
        status = 'partial'
    elif entry_slot.get('status') == 'missed_entry' or delay_minutes > 0:
        status = 'late'
    elif missing_slots:
        status = 'partial'
    elif evening.get('status') == 'early_exit':
        status = 'partial'
    else:
        status = 'present'

    status_labels = {
        'present': _('PRÉSENT'),
        'late': _('RETARD'),
        'partial': _('PARTIEL'),
    }

    return {
        'status': status,
        'status_label': status_labels[status],
        'schedule': schedule,
        'note': note,
        'delay_minutes': delay_minutes,
        'worked_minutes': worked_minutes,
        'slots': slots_by_code,
        'validated_slots': validated_slots,
        'total_slots': total_slots,
        'missing_slots': missing_slots,
    }
