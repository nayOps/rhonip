from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views import View

from employee.utils.company_attendance import build_company_attendance_dashboard


class CompanyAttendance(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'employee/company_attendance.html'

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def get(self, request):
        dashboard = build_company_attendance_dashboard(request)
        return render(request, self.template_name, {'dashboard': dashboard})
