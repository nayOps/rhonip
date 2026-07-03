from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
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
from employee.utils.reports_registry import REPORT_CATALOG


class StaffReportsMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser


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
                'filter': params['filter_status'],
                'situation': params['situation_filter'],
                'q': params['search_query'],
                'date_from': params['date_from_value'],
                'date_to': params['date_to_value'],
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
            'filter': params['filter_status'],
            'situation': params['situation_filter'],
            'q': params['search_query'],
            'date_from': params['date_from_value'],
            'date_to': params['date_to_value'],
        }

        if form_data['active'] and not form_data['recipient']:
            messages.error(request, _('Indiquez un destinataire email pour activer la programmation.'))
            return self._render(request, report, form_data)

        messages.success(
            request,
            _('Programmation du rapport « Enregistrement biométrique » enregistrée.'),
        )
        return _redirect_to_report(params)
