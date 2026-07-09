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
        'target': time(8, 30),
        'accept_from': time(6, 0),
        'accept_until': time(10, 0),
        'reference': time(8, 30),
        'ui_header': 'Entrée',
    },
    {
        'code': 'EVENING_OUT',
        'label': 'Sortie',
        'target': time(16, 0),
        'accept_from': time(15, 0),
        'accept_until': time(16, 30),
        'ui_header': 'Sortie',
    },
]


class AttendancePunchRulesTests(SimpleTestCase):
    def setUp(self):
        self.day = date(2026, 7, 3)
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
            return_value=time(16, 30),
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

    def test_early_morning_entry_from_6h(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(6, 30), []))

    def test_morning_entry_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(9, 0), []))

    def test_second_morning_punch_rejected(self):
        msg = validate_punch_allowed(self.day, time(9, 30), [time(7, 0)])
        self.assertIn('entrée déjà enregistrée', msg.lower())

    def test_midday_blocked_after_morning_entry(self):
        msg = validate_punch_allowed(self.day, time(11, 0), [time(7, 0)])
        self.assertIn('aucun pointage', msg.lower())

    def test_midday_first_punch_allowed_without_morning(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(11, 30), []))

    def test_midday_second_punch_rejected_after_late_first(self):
        msg = validate_punch_allowed(self.day, time(12, 45), [time(11, 30)])
        self.assertIn('aucun pointage', msg.lower())

    def test_afternoon_exit_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(15, 30), [time(7, 0)]))

    def test_exit_without_entry_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(16, 0), []))

    def test_exit_only_assigns_evening_slot(self):
        assigned = assign_punches_to_slots([time(15, 30)])
        self.assertIsNone(assigned['MORNING_IN'])
        self.assertEqual(assigned['EVENING_OUT'], time(15, 30))

    def test_assign_ignores_midday_punch(self):
        assigned = assign_punches_to_slots([time(7, 0), time(11, 30), time(16, 0)])
        self.assertEqual(assigned['MORNING_IN'], time(7, 0))
        self.assertEqual(assigned['EVENING_OUT'], time(16, 0))

    def test_assign_late_first_entry_in_blocked_zone(self):
        assigned = assign_punches_to_slots([time(11, 30), time(16, 0)])
        self.assertEqual(assigned['MORNING_IN'], time(11, 30))
        self.assertEqual(assigned['EVENING_OUT'], time(16, 0))

    def test_exit_after_late_first_entry_allowed(self):
        self.assertIsNone(
            validate_punch_allowed(self.day, time(15, 30), [time(11, 30)])
        )

    def test_on_time_before_official_830(self):
        with patch('employee.utils.attendance_slots.timezone') as mock_tz:
            from datetime import datetime
            from django.utils import timezone as dj_tz

            mock_tz.localtime.return_value = dj_tz.make_aware(
                datetime.combine(self.day, time(12, 0))
            )
            result = evaluate_day_slots(self.day, [time(7, 15)])
        entry = result['slots']['MORNING_IN']
        self.assertEqual(entry['status'], 'ok')
        self.assertEqual(entry['delay_minutes'], 0)

    def test_late_after_official_830(self):
        with patch('employee.utils.attendance_slots.timezone') as mock_tz:
            from datetime import datetime
            from django.utils import timezone as dj_tz

            mock_tz.localtime.return_value = dj_tz.make_aware(
                datetime.combine(self.day, time(12, 0))
            )
            result = evaluate_day_slots(self.day, [time(8, 45)])
        entry = result['slots']['MORNING_IN']
        self.assertEqual(entry['status'], 'late')
        self.assertEqual(entry['delay_minutes'], 15)

    def test_exit_only_day_is_partial(self):
        with patch('employee.utils.attendance_slots.timezone') as mock_tz:
            from datetime import datetime
            from django.utils import timezone as dj_tz

            mock_tz.localtime.return_value = dj_tz.make_aware(
                datetime.combine(self.day, time(17, 0))
            )
            result = evaluate_day_slots(self.day, [time(15, 30)])
        self.assertEqual(result['status'], 'partial')
        self.assertIsNone(result['slots']['MORNING_IN']['punch_time'])
        self.assertEqual(result['slots']['EVENING_OUT']['punch_time'], time(15, 30))
