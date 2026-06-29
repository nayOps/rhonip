from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.utils import timezone
from django.views import View

from employee.utils.agents_directory import render_agents_directory_pdf


class AgentsDirectoryExport(UserPassesTestMixin, LoginRequiredMixin, View):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get(self, request):
        pdf_bytes = render_agents_directory_pdf()
        filename = f'annuaire-agents-{timezone.localtime():%Y%m%d-%H%M%S}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
