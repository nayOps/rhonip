from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View

from employee.utils.attendance_stats import get_employee_attendance_context
from employee.utils.profile_dossier import build_profile_dossier


class MyAttendance(LoginRequiredMixin, View):
    """Présences de l’agent connecté — réservé aux comptes liés à un employé."""

    template_name = 'employee/my_attendance.html'

    def get(self, request):
        employee = getattr(request.user, 'employee', None)
        if not employee:
            raise Http404("Aucun profil d'employé associé à votre compte")

        can_edit = request.user.has_perm('employee.change_employee')
        edit_url = reverse_lazy('employee:change', kwargs={'pk': employee.pk}) if can_edit else None

        return render(
            request,
            self.template_name,
            {
                'employee': employee,
                'obj': employee,
                'dossier': build_profile_dossier(employee),
                'can_edit': can_edit,
                'edit_url': edit_url,
                'show_employee_attendance_nav': True,
                **get_employee_attendance_context(request, employee),
            },
        )
