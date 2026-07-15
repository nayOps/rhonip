from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from employee.models import Employee
from employee.utils.biometric_enrollment_report import (
    build_biometric_enrollment_report,
    build_report_query_string,
    paginate_report_rows,
    parse_report_filters,
    render_biometric_enrollment_pdf,
)
from employee.utils.completed_enrollment_day_report import (
    build_completed_enrollment_day_report,
    parse_enrollment_day_filters,
    render_completed_enrollment_day_pdf,
)
from employee.utils.daily_attendance_report import (
    build_daily_attendance_report,
    parse_daily_attendance_filters,
    render_daily_attendance_pdf,
)
from employee.utils.reports_registry import REPORT_CATALOG


class StaffReportsMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser


SCHEDULE_FREQUENCIES = (
    ('monthly', _('Mensuel')),
    ('weekly', _('Hebdomadaire')),
    ('daily', _('Quotidien')),
)
SCHEDULE_FORMATS = (
    ('pdf', _('PDF')),
    ('email', _('Email')),
)


def _report_params(request):
    if request.method == 'POST':
        source = request.POST
    else:
        source = request.GET
    return parse_report_filters(
        filter_status=source.get('filter'),
        situation_filter=source.get('situation'),
        search_query=source.get('q'),
        date_from=source.get('date_from'),
        date_to=source.get('date_to'),
    )


def _report_build_kwargs(params):
    return {
        'filter_status': params['filter_status'],
        'situation_filter': params['situation_filter'],
        'search_query': params['search_query'],
        'date_from': params['date_from_value'],
        'date_to': params['date_to_value'],
    }


def _day_report_params(request):
    if request.method == 'POST':
        source = request.POST
    else:
        source = request.GET
    return parse_enrollment_day_filters(
        target_date=source.get('date'),
        period_from=source.get('period_from'),
        period_to=source.get('period_to'),
    )


def _day_report_build_kwargs(params):
    return {
        'target_date': params['target_date'],
        'period_from': params['period_from'],
        'period_to': params['period_to'],
    }


def _attendance_day_report_params(request):
    if request.method == 'POST':
        source = request.POST
    else:
        source = request.GET
    return parse_daily_attendance_filters(
        target_date=source.get('date'),
        direction=source.get('direction'),
    )


def _attendance_day_report_build_kwargs(params):
    return {
        'target_date': params['target_date'],
        'direction_id': params['direction_id'],
    }


def _redirect_to_report(params, page=None):
    query = build_report_query_string(
        params['filter_status'],
        params['situation_filter'],
        params['search_query'],
        date_from=params.get('date_from'),
        date_to=params.get('date_to'),
        page=page,
    )
    return redirect(f"{reverse('employee:biometric_enrollment_report')}?{query}")



class ReportsHub(StaffReportsMixin, View):
    template_name = 'employee/reports_hub.html'

    def get(self, request):
        reports = []
        for item in REPORT_CATALOG:
            preview_url = reverse(item['preview_name'])
            export_url = reverse(item['export_name'])
            schedule_url = reverse(item['schedule_name'])
            default_query = item.get('default_query') or ''
            if default_query:
                preview_url = f'{preview_url}?{default_query}'
                export_url = f'{export_url}?{default_query}'
                schedule_url = f'{schedule_url}?{default_query}'
            reports.append(
                {
                    **item,
                    'preview_url': preview_url,
                    'schedule_url': schedule_url,
                    'export_url': export_url,
                }
            )
        return render(
            request,
            self.template_name,
            {
                'reports': reports,
                'main_report_url': reverse('employee:biometric_enrollment_report'),
            },
        )


class BiometricEnrollmentReport(StaffReportsMixin, View):
    template_name = 'employee/biometric_enrollment_report.html'

    def get(self, request):
        params = _report_params(request)
        report = build_biometric_enrollment_report(**_report_build_kwargs(params))
        pagination = paginate_report_rows(report['rows'], request)
        report['rows'] = pagination['items']
        return render(
            request,
            self.template_name,
            {'report': report, 'pagination': pagination},
        )

    def post(self, request):
        params = _report_params(request)
        employee_id = request.POST.get('employee_id')
        action = (request.POST.get('action') or '').strip().lower()

        if not employee_id or action not in {'accept', 'reject'}:
            messages.error(request, _('Action invalide.'))
            return _redirect_to_report(params)

        employee = get_object_or_404(Employee, pk=employee_id)
        if action == 'accept':
            employee.agent_situation = 'active'
            label = _('actif')
        else:
            employee.agent_situation = 'inactive'
            label = _('inactif')
        employee.save(update_fields=['agent_situation'])

        messages.success(
            request,
            _('%(name)s est maintenant %(status)s.') % {
                'name': employee.full_name(),
                'status': label,
            },
        )
        page = request.POST.get('page')
        try:
            page = max(1, int(page)) if page else None
        except (TypeError, ValueError):
            page = None
        return _redirect_to_report(params, page=page)


class BiometricEnrollmentReportExport(StaffReportsMixin, View):
    def get(self, request):
        params = _report_params(request)
        report = build_biometric_enrollment_report(**_report_build_kwargs(params))
        pdf_bytes = render_biometric_enrollment_pdf(report)
        filename = report.get('pdf_filename') or 'rapport-rh-onip-enregistrement.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class BiometricEnrollmentReportSchedule(StaffReportsMixin, View):
    template_name = 'employee/biometric_enrollment_report_schedule.html'

    def _render(self, request, report, form_data):
        return render(
            request,
            self.template_name,
            {
                'report': report,
                'frequencies': SCHEDULE_FREQUENCIES,
                'formats': SCHEDULE_FORMATS,
                'form_data': form_data,
            },
        )

    def get(self, request):
        params = _report_params(request)
        report = build_biometric_enrollment_report(**_report_build_kwargs(params))
        return self._render(
            request,
            report,
            {
                'frequency': 'monthly',
                'format': 'pdf',
                'send_day': '1',
                'recipient': request.user.email or '',
                'active': True,
            },
        )

    def post(self, request):
        params = _report_params(request)
        report = build_biometric_enrollment_report(**_report_build_kwargs(params))
        form_data = {
            'frequency': request.POST.get('frequency', 'monthly'),
            'format': request.POST.get('format', 'pdf'),
            'send_day': request.POST.get('send_day', '1'),
            'recipient': request.POST.get('recipient', '').strip(),
            'active': request.POST.get('active') == 'on',
        }

        if form_data['active'] and not form_data['recipient']:
            messages.error(request, _('Indiquez un destinataire email pour activer la programmation.'))
            return self._render(request, report, form_data)

        messages.success(
            request,
            _('Programmation du rapport « Enregistrement biométrique » enregistrée.'),
        )
        return redirect(reverse('employee:reports_hub'))


class EnrollmentDayReport(StaffReportsMixin, View):
    template_name = 'employee/enrollment_day_report.html'

    def get(self, request):
        params = _day_report_params(request)
        report = build_completed_enrollment_day_report(**_day_report_build_kwargs(params))
        return render(request, self.template_name, {'report': report})


class EnrollmentDayReportExport(StaffReportsMixin, View):
    def get(self, request):
        params = _day_report_params(request)
        report = build_completed_enrollment_day_report(**_day_report_build_kwargs(params))
        pdf_bytes = render_completed_enrollment_day_pdf(**_day_report_build_kwargs(params))
        filename = report.get('pdf_filename') or 'rapport-rh-onip-enregistrement-journalier.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class EnrollmentDayReportSchedule(StaffReportsMixin, View):
    template_name = 'employee/enrollment_day_report_schedule.html'

    def _render(self, request, report, form_data):
        return render(
            request,
            self.template_name,
            {
                'report': report,
                'frequencies': SCHEDULE_FREQUENCIES,
                'formats': SCHEDULE_FORMATS,
                'form_data': form_data,
            },
        )

    def get(self, request):
        params = _day_report_params(request)
        report = build_completed_enrollment_day_report(**_day_report_build_kwargs(params))
        return self._render(
            request,
            report,
            {
                'frequency': 'daily',
                'format': 'pdf',
                'send_day': '1',
                'recipient': request.user.email or '',
                'active': True,
            },
        )

    def post(self, request):
        params = _day_report_params(request)
        report = build_completed_enrollment_day_report(**_day_report_build_kwargs(params))
        form_data = {
            'frequency': request.POST.get('frequency', 'daily'),
            'format': request.POST.get('format', 'pdf'),
            'send_day': request.POST.get('send_day', '1'),
            'recipient': request.POST.get('recipient', '').strip(),
            'active': request.POST.get('active') == 'on',
        }

        if form_data['active'] and not form_data['recipient']:
            messages.error(request, _('Indiquez un destinataire email pour activer la programmation.'))
            return self._render(request, report, form_data)

        messages.success(
            request,
            _('Programmation du rapport « Enregistrement journalier 10/10 » enregistrée.'),
        )
        return redirect(reverse('employee:reports_hub'))


class DailyAttendanceReport(StaffReportsMixin, View):
    template_name = 'employee/daily_attendance_report.html'

    def get(self, request):
        params = _attendance_day_report_params(request)
        report = build_daily_attendance_report(**_attendance_day_report_build_kwargs(params))
        return render(request, self.template_name, {'report': report})


class DailyAttendanceReportExport(StaffReportsMixin, View):
    def get(self, request):
        params = _attendance_day_report_params(request)
        report = build_daily_attendance_report(**_attendance_day_report_build_kwargs(params))
        pdf_bytes = render_daily_attendance_pdf(**_attendance_day_report_build_kwargs(params))
        filename = report.get('pdf_filename') or 'rapport-rh-onip-presence-journalier.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
