from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View

from employee.utils.biometric_enrollment_report import (
    FILTER_CHOICES,
    build_biometric_enrollment_report,
    render_biometric_enrollment_pdf,
)
from employee.utils.reports_registry import REPORT_CATALOG


class StaffReportsMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser


class ReportsHub(StaffReportsMixin, View):
    template_name = 'employee/reports_hub.html'

    def get(self, request):
        reports = []
        for item in REPORT_CATALOG:
            reports.append(
                {
                    **item,
                    'preview_url': reverse(item['preview_name']),
                    'schedule_url': reverse(item['schedule_name']),
                    'export_url': reverse(item['export_name']),
                }
            )
        return render(request, self.template_name, {'reports': reports})


class BiometricEnrollmentReport(StaffReportsMixin, View):
    template_name = 'employee/biometric_enrollment_report.html'

    def get(self, request):
        filter_status = request.GET.get('filter', 'all')
        valid_filters = {code for code, _ in FILTER_CHOICES}
        if filter_status not in valid_filters:
            filter_status = 'all'
        report = build_biometric_enrollment_report(filter_status=filter_status)
        return render(request, self.template_name, {'report': report})


class BiometricEnrollmentReportExport(StaffReportsMixin, View):
    def get(self, request):
        filter_status = request.GET.get('filter', 'all')
        valid_filters = {code for code, _ in FILTER_CHOICES}
        if filter_status not in valid_filters:
            filter_status = 'all'
        report = build_biometric_enrollment_report(filter_status=filter_status)
        pdf_bytes = render_biometric_enrollment_pdf(report)
        filename = f'enregistrement-biometrique-{timezone.localtime():%Y%m%d-%H%M%S}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class BiometricEnrollmentReportSchedule(StaffReportsMixin, View):
    template_name = 'employee/biometric_enrollment_report_schedule.html'

    FREQUENCIES = (
        ('monthly', _('Mensuel')),
        ('weekly', _('Hebdomadaire')),
    )
    FORMATS = (
        ('pdf', _('PDF')),
        ('email', _('Email')),
    )

    def _render(self, request, report, form_data):
        return render(
            request,
            self.template_name,
            {
                'report': report,
                'frequencies': self.FREQUENCIES,
                'formats': self.FORMATS,
                'form_data': form_data,
            },
        )

    def get(self, request):
        filter_status = request.GET.get('filter', 'all')
        report = build_biometric_enrollment_report(filter_status=filter_status)
        return self._render(
            request,
            report,
            {
                'frequency': 'monthly',
                'format': 'pdf',
                'send_day': '1',
                'recipient': request.user.email or '',
                'active': True,
                'filter': filter_status,
            },
        )

    def post(self, request):
        filter_status = request.POST.get('filter', 'all')
        report = build_biometric_enrollment_report(filter_status=filter_status)
        form_data = {
            'frequency': request.POST.get('frequency', 'monthly'),
            'format': request.POST.get('format', 'pdf'),
            'send_day': request.POST.get('send_day', '1'),
            'recipient': request.POST.get('recipient', '').strip(),
            'active': request.POST.get('active') == 'on',
            'filter': filter_status,
        }

        if form_data['active'] and not form_data['recipient']:
            messages.error(request, _('Indiquez un destinataire email pour activer la programmation.'))
            return self._render(request, report, form_data)

        messages.success(
            request,
            _('Programmation du rapport « Enregistrement biométrique » enregistrée.'),
        )
        return redirect(
            reverse('employee:biometric_enrollment_report') + f'?filter={filter_status}'
        )
