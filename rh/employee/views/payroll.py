from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render
from django.views import View

from employee.models import PayrollLine, PayrollPeriod


class PayrollList(LoginRequiredMixin, UserPassesTestMixin, View):
    """Liste paie ONIP par période avec recherche multi-champs."""

    template_name = 'employee/payroll_list.html'

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def get(self, request):
        periods = PayrollPeriod.objects.order_by('-id')
        period_id = request.GET.get('period')
        period = None
        if period_id:
            period = periods.filter(pk=period_id).first()
        if not period:
            period = periods.first()

        lines = PayrollLine.objects.select_related('employee', 'period').order_by('line_number')
        if period:
            lines = lines.filter(period=period)

        query = (request.GET.get('q') or '').strip()
        if query:
            lines = lines.filter(
                Q(registration_number__icontains=query)
                | Q(full_name__icontains=query)
                | Q(fonction__icontains=query)
                | Q(employee__first_name__icontains=query)
                | Q(employee__last_name__icontains=query)
                | Q(employee__middle_name__icontains=query)
                | Q(employee__designation__name__icontains=query)
            ).distinct()

        totals = lines.aggregate(
            total_base=Sum('base'),
            total_prime=Sum('prime'),
            total_logement=Sum('logement'),
            total_ipr=Sum('ipr'),
            total_net=Sum('net_a_payer'),
        )

        paginator = Paginator(lines, 50)
        page_obj = paginator.get_page(int(request.GET.get('page', 1)))

        return render(
            request,
            self.template_name,
            {
                'period': period,
                'periods': periods,
                'page_obj': page_obj,
                'query': query,
                'totals': totals,
                'line_count': paginator.count,
            },
        )
