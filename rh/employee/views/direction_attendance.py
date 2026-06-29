from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from employee.models import Direction
from employee.utils.attendance_stats import parse_attendance_period
from employee.utils.direction_attendance import build_direction_report, build_direction_schedule_hub


class StaffAttendanceMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def _period_query(self, request):
        year, month, _week_start = parse_attendance_period(request)
        return year, month


class DirectionReportHub(StaffAttendanceMixin, View):
    template_name = 'employee/direction_report_hub.html'

    def get(self, request):
        hub = build_direction_schedule_hub(request)
        return render(request, self.template_name, {'hub': hub})


class DirectionAttendanceReport(StaffAttendanceMixin, View):
    template_name = 'employee/direction_attendance_report.html'

    def get(self, request, direction_id):
        direction = get_object_or_404(Direction, pk=direction_id)
        year, month = self._period_query(request)
        report = build_direction_report(direction, year, month)
        return render(request, self.template_name, {'report': report})


class DirectionReportSchedule(StaffAttendanceMixin, View):
    template_name = 'employee/direction_report_schedule.html'

    FREQUENCIES = (
        ('monthly', _('Mensuel')),
        ('weekly', _('Hebdomadaire')),
    )
    FORMATS = (
        ('pdf', _('PDF')),
        ('email', _('Email')),
    )

    def _render(self, request, direction, year, month, form_data):
        report = build_direction_report(direction, year, month)
        return render(
            request,
            self.template_name,
            {
                'direction': direction,
                'report': report,
                'frequencies': self.FREQUENCIES,
                'formats': self.FORMATS,
                'form_data': form_data,
            },
        )

    def get(self, request, direction_id):
        direction = get_object_or_404(Direction, pk=direction_id)
        year, month = self._period_query(request)
        return self._render(
            request,
            direction,
            year,
            month,
            {
                'frequency': 'monthly',
                'format': 'pdf',
                'send_day': '1',
                'recipient': request.user.email or '',
                'active': True,
            },
        )

    def post(self, request, direction_id):
        direction = get_object_or_404(Direction, pk=direction_id)
        year, month = self._period_query(request)
        form_data = {
            'frequency': request.POST.get('frequency', 'monthly'),
            'format': request.POST.get('format', 'pdf'),
            'send_day': request.POST.get('send_day', '1'),
            'recipient': request.POST.get('recipient', '').strip(),
            'active': request.POST.get('active') == 'on',
        }

        if form_data['active'] and not form_data['recipient']:
            messages.error(request, _('Indiquez un destinataire email pour activer la programmation.'))
            return self._render(request, direction, year, month, form_data)

        report = build_direction_report(direction, year, month)
        messages.success(
            request,
            _('Programmation enregistrée pour %(direction)s (%(period)s).')
            % {'direction': direction.name, 'period': report['period_label']},
        )
        return redirect(
            reverse('employee:direction_attendance_report', kwargs={'direction_id': direction_id})
            + f'?year={year}&month={month}'
        )
