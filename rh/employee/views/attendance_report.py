from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from employee.models import Employee
from employee.utils.attendance_stats import build_attendance_report, parse_attendance_period


class EmployeeAttendanceMixin(LoginRequiredMixin):
    def _get_employee(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        if not request.user.is_superuser and not request.user.is_staff:
            if request.user.employee and int(pk) != request.user.employee.id:
                from django.http import Http404
                raise Http404("Vous n'avez pas accès à cet employé")
        return employee

    def _period_query(self, request):
        year, month, _ = parse_attendance_period(request)
        return year, month


class AttendanceReport(EmployeeAttendanceMixin, View):
    template_name = 'employee/attendance_report.html'

    def get(self, request, pk):
        employee = self._get_employee(request, pk)
        year, month = self._period_query(request)
        report = build_attendance_report(employee, year, month)
        return render(
            request,
            self.template_name,
            {
                'obj': employee,
                'report': report,
            },
        )


class AttendanceReportSchedule(EmployeeAttendanceMixin, View):
    template_name = 'employee/attendance_report_schedule.html'

    FREQUENCIES = (
        ('monthly', _('Mensuel')),
        ('weekly', _('Hebdomadaire')),
    )
    FORMATS = (
        ('pdf', _('PDF')),
        ('email', _('Email')),
    )

    def _render_form(self, request, employee, year, month, form_data):
        report = build_attendance_report(employee, year, month)
        return render(
            request,
            self.template_name,
            {
                'obj': employee,
                'report': report,
                'frequencies': self.FREQUENCIES,
                'formats': self.FORMATS,
                'form_data': form_data,
            },
        )

    def get(self, request, pk):
        employee = self._get_employee(request, pk)
        year, month = self._period_query(request)
        return self._render_form(
            request,
            employee,
            year,
            month,
            {
                'frequency': 'monthly',
                'format': 'pdf',
                'send_day': '1',
                'recipient': employee.email_professional or employee.email or '',
                'active': True,
            },
        )

    def post(self, request, pk):
        employee = self._get_employee(request, pk)
        year, month = self._period_query(request)
        frequency = request.POST.get('frequency', 'monthly')
        output_format = request.POST.get('format', 'pdf')
        recipient = request.POST.get('recipient', '').strip()
        active = request.POST.get('active') == 'on'

        form_data = {
            'frequency': frequency,
            'format': output_format,
            'send_day': request.POST.get('send_day', '1'),
            'recipient': recipient,
            'active': active,
        }

        if active and not recipient:
            messages.error(request, _('Indiquez un destinataire email pour activer la programmation.'))
            return self._render_form(request, employee, year, month, form_data)

        report = build_attendance_report(employee, year, month)
        messages.success(
            request,
            _('Programmation enregistrée pour %(name)s (%(period)s).')
            % {
                'name': employee.short_name(),
                'period': report['period_label'],
            },
        )
        return redirect(
            reverse('employee:attendance_report', kwargs={'pk': pk})
            + f'?year={year}&month={month}'
        )
