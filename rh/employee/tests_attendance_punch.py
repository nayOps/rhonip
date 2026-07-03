from datetime import date, time

from django.test import SimpleTestCase
from unittest.mock import patch

from employee.utils.attendance_slots import (
    assign_punches_to_slots,
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

    def test_morning_entry_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(9, 0), []))

    def test_second_morning_punch_rejected(self):
        msg = validate_punch_allowed(self.day, time(9, 30), [time(8, 30)])
        self.assertIn('entrée déjà enregistrée', msg.lower())

    def test_midday_blocked(self):
        msg = validate_punch_allowed(self.day, time(11, 0), [time(8, 30)])
        self.assertIn('aucun pointage', msg.lower())

    def test_afternoon_exit_allowed(self):
        self.assertIsNone(validate_punch_allowed(self.day, time(15, 30), [time(8, 30)]))

    def test_exit_without_entry_rejected(self):
        msg = validate_punch_allowed(self.day, time(16, 0), [])
        self.assertIn('entrée le matin', msg.lower())

    def test_assign_ignores_midday_punch(self):
        assigned = assign_punches_to_slots([time(8, 0), time(11, 30), time(16, 0)])
        self.assertEqual(assigned['MORNING_IN'], time(8, 0))
        self.assertEqual(assigned['EVENING_OUT'], time(16, 0))
