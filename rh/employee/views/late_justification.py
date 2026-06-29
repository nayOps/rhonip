from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from employee.models import Employee, LateJustification
from employee.services.late_justification_form import LateJustificationForm
from employee.utils.hierarchy import resolve_n_plus_one
from employee.utils.late_justification import (
    create_late_justification,
    validate_late_day_for_employee,
)


class LateJustificationCreate(LoginRequiredMixin, View):
    template_name = 'employee/late_justification_form.html'

    def _resolve_employee(self, request):
        employee_pk = request.GET.get('employee') or request.POST.get('employee')
        if request.user.is_staff or request.user.is_superuser:
            if employee_pk:
                return get_object_or_404(Employee, pk=employee_pk)
            if request.user.employee_id:
                return request.user.employee
            raise Http404
        if not request.user.employee_id:
            raise Http404
        employee = request.user.employee
        if employee_pk and int(employee_pk) != employee.pk:
            raise Http404(_('Vous ne pouvez justifier que vos propres retards.'))
        return employee

    def _resolve_day(self, request):
        raw = request.GET.get('date') or request.POST.get('date')
        if not raw:
            raise Http404(_('Date du retard manquante.'))
        try:
            return date.fromisoformat(raw)
        except ValueError as exc:
            raise Http404(_('Date invalide.')) from exc

    def get(self, request):
        employee = self._resolve_employee(request)
        day = self._resolve_day(request)
        evaluation = validate_late_day_for_employee(employee, day)
        if evaluation.get('error'):
            messages.error(request, evaluation['error'])
            return redirect(reverse('employee:change', kwargs={'pk': employee.pk}))

        approver = resolve_n_plus_one(employee)
        form = LateJustificationForm(
            initial={
                'employee': employee.pk,
                'date': day.isoformat(),
                'delay_minutes': evaluation.get('delay_minutes', 0),
            }
        )
        return render(
            request,
            self.template_name,
            {
                'form': form,
                'employee': employee,
                'day': day,
                'evaluation': evaluation,
                'approver': approver,
            },
        )

    def post(self, request):
        employee = self._resolve_employee(request)
        day = self._resolve_day(request)
        form = LateJustificationForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    'form': form,
                    'employee': employee,
                    'day': day,
                    'evaluation': validate_late_day_for_employee(employee, day),
                    'approver': resolve_n_plus_one(employee),
                },
            )

        try:
            justification = create_late_justification(
                employee=employee,
                day=day,
                reason=form.cleaned_data['reason'],
                document=form.cleaned_data.get('document'),
                requested_by=request.user,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect(reverse('employee:change', kwargs={'pk': employee.pk}))

        messages.success(
            request,
            _('Votre justification a été envoyée au responsable N+1 pour validation.'),
        )
        return redirect(justification.get_absolute_url())
