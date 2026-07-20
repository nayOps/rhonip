from datetime import date, time

from django.test import SimpleTestCase
from unittest.mock import patch

from employee.utils.attendance_slots import (
    assign_punches_to_slots,
    evaluate_day_slots,
    validate_punch_allowed,
)

TWO_SLOT_PRESET = [
    {
        'code': 'MORNING_IN',
        'label': 'Entrée',
        'target': time(8, 0),
        'accept_from': time(8, 0),
        'accept_until': time(10, 0),
        'reference': time(8, 0),
        'ui_header': 'Entrée',
    },
    {
        'code': 'EVENING_OUT',
        'label': 'Sortie',
        'target': time(16, 0),
        'accept_from': time(16, 0),
        'accept_until': time(23, 59),
        'ui_header': 'Sortie',
    },
]


class AttendancePunchRulesTests(SimpleTestCase):
    def setUp(self):
        self.day = date(2026, 7, 21)  # apres SCHEDULE_RULES_EFFECTIVE_FROM
        patcher = patch(
            'employee.utils.attendance_slots.get_presence_slots',
            return_value=TWO_SLOT_PRESET,
        )
        self.addCleanup(patcher.stop)
        patcher.start()
        patcher2 = patch(
            'employee.utils.attendance_slots.get_total_slots',
            return_value=2,
        )
        self.addCleanup(patcher2.stop)
        patcher2.start()
        patcher3 = patch(
            'employee.utils.attendance_slots.has_lunch_slots',
            return_value=False,
        )
        self.addCleanup(patcher3.stop)
        patcher3.start()
        patcher4 = patch(
            'employee.utils.attendance_slots.get_work_end',
            return_value=time(16, 0),
        )
        self.addCleanup(patcher4.stop)
        patcher4.start()
        patcher5 = patch(
            'employee.utils.attendance_slots.get_lunch_break_limits',
            return_value=(50, 70),
        )
        self.addCleanup(patcher5.stop)
        patcher5.start()
        patcher6 = patch(
            'employee.utils.attendance_slots.first_slot_code',
            return_value='MORNING_IN',
        )
        self.addCleanup(patcher6.stop)
        patcher6.start()

    def test_before_8h_entry_rejected(self):
        msg = validate_punch_allowed(self.day, time(7, 30), [])
        self.assertIn('à partir de', msg.lower())
        self.assertIn('08:00', msg)

    def test_morning_entry_from_8h_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(8, 0), []))

    def test_morning_entry_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(9, 0), []))

    def test_second_morning_punch_rejected(self):
        msg = validate_punch_allowed(self.day, time(9, 30), [time(8, 15)])
        self.assertIn('entrée déjà enregistrée', msg.lower())

    def test_midday_blocked_after_morning_entry(self):
        msg = validate_punch_allowed(self.day, time(11, 0), [time(8, 15)])
        self.assertIn('aucun pointage', msg.lower())

    def test_midday_first_punch_allowed_without_morning(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(11, 30), []))

    def test_midday_second_punch_rejected_after_late_first(self):
        msg = validate_punch_allowed(self.day, time(12, 45), [time(11, 30)])
        self.assertIn('aucun pointage', msg.lower())

    def test_exit_before_16h_rejected(self):
        msg = validate_punch_allowed(self.day, time(15, 30), [time(8, 15)])
        self.assertIn('sortie à partir de', msg.lower())
        self.assertIn('16:00', msg)

    def test_exit_from_16h_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(16, 0), [time(8, 15)]))

    def test_exit_late_evening_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(17, 30), [time(8, 15)]))
        self.assertIsNone(validate_punch_allowed(self.day, time(18, 45), [time(8, 15)]))

    def test_exit_without_entry_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(16, 0), []))

    def test_exit_only_assigns_evening_slot(self):
        assigned = assign_punches_to_slots([time(16, 30)])
        self.assertIsNone(assigned['MORNING_IN'])
        self.assertEqual(assigned['EVENING_OUT'], time(16, 30))

    def test_assign_ignores_midday_punch_when_morning_exists(self):
        assigned = assign_punches_to_slots([time(8, 15), time(11, 30), time(16, 0)])
        self.assertEqual(assigned['MORNING_IN'], time(8, 15))
        self.assertEqual(assigned['EVENING_OUT'], time(16, 0))

    def test_assign_late_first_entry_in_blocked_zone(self):
        assigned = assign_punches_to_slots([time(11, 30), time(16, 0)])
        self.assertEqual(assigned['MORNING_IN'], time(11, 30))
        self.assertEqual(assigned['EVENING_OUT'], time(16, 0))

    def test_exit_after_late_first_entry_allowed(self):
        self.assertIsNone(
            validate_punch_allowed(self.day, time(16, 30), [time(11, 30)])
        )

    def test_on_time_at_official_8h(self):
        with patch('employee.utils.attendance_slots.timezone') as mock_tz:
            from datetime import datetime
            from django.utils import timezone as dj_tz

            mock_tz.localtime.return_value = dj_tz.make_aware(
                datetime.combine(self.day, time(12, 0))
            )
            result = evaluate_day_slots(self.day, [time(8, 0)])
        entry = result['slots']['MORNING_IN']
        self.assertEqual(entry['status'], 'ok')
        self.assertEqual(entry['delay_minutes'], 0)

    def test_late_after_official_8h(self):
        with patch('employee.utils.attendance_slots.timezone') as mock_tz:
            from datetime import datetime
            from django.utils import timezone as dj_tz

            mock_tz.localtime.return_value = dj_tz.make_aware(
                datetime.combine(self.day, time(12, 0))
            )
            result = evaluate_day_slots(self.day, [time(8, 45)])
        entry = result['slots']['MORNING_IN']
        self.assertEqual(entry['status'], 'late')
        self.assertEqual(entry['delay_minutes'], 45)

    def test_exit_only_day_is_partial(self):
        with patch('employee.utils.attendance_slots.timezone') as mock_tz:
            from datetime import datetime
            from django.utils import timezone as dj_tz

            mock_tz.localtime.return_value = dj_tz.make_aware(
                datetime.combine(self.day, time(17, 0))
            )
            result = evaluate_day_slots(self.day, [time(16, 30)])
        self.assertEqual(result['status'], 'partial')
        self.assertIsNone(result['slots']['MORNING_IN']['punch_time'])
        self.assertEqual(result['slots']['EVENING_OUT']['punch_time'], time(16, 30))

    def test_evening_punch_17h_is_ok(self):
        with patch('employee.utils.attendance_slots.timezone') as mock_tz:
            from datetime import datetime
            from django.utils import timezone as dj_tz

            mock_tz.localtime.return_value = dj_tz.make_aware(
                datetime.combine(self.day, time(18, 0))
            )
            result = evaluate_day_slots(self.day, [time(8, 10), time(17, 15)])
        evening = result['slots']['EVENING_OUT']
        self.assertEqual(evening['punch_time'], time(17, 15))
        self.assertEqual(evening['status'], 'ok')


from employee.utils.attendance_schedule_config import preset_slots


def _two_slot_schedule(*, legacy=False):
    return {
        'slot_preset': '2_slots',
        'slots': preset_slots('2_slots', legacy=legacy),
        'work_start': time(8, 0),
        'work_end': time(16, 30) if legacy else time(16, 0),
        'lunch_break_min_minutes': 50,
        'lunch_break_max_minutes': 70,
    }


class LegacyScheduleCutoffTests(SimpleTestCase):
    """Avant le 20/07/2026 : anciennes plages (sortie des 15h acceptee)."""

    def test_legacy_exit_at_1530_is_ok(self):
        with patch(
            'employee.utils.attendance_schedule_config.get_attendance_schedule',
            return_value=_two_slot_schedule(),
        ):
            result = evaluate_day_slots(date(2026, 7, 14), [time(8, 0), time(15, 31)])
        evening = result['slots']['EVENING_OUT']
        self.assertEqual(evening['punch_time'], time(15, 31))
        self.assertEqual(evening['status'], 'ok')

    def test_new_rules_reject_exit_before_16h(self):
        with patch(
            'employee.utils.attendance_schedule_config.get_attendance_schedule',
            return_value=_two_slot_schedule(),
        ):
            result = evaluate_day_slots(date(2026, 7, 21), [time(8, 0), time(15, 31)])
        evening = result['slots']['EVENING_OUT']
        self.assertEqual(evening['status'], 'early_exit')
