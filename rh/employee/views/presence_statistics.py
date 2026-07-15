import csv

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views import View

from employee.utils.presence_statistics import (
    _filter_rows,
    build_agent_rows,
    build_presence_statistics,
)


class StaffStatisticsMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser


def _stats_kwargs(request):
    source = request.GET
    return {
        'year': source.get('year'),
        'month': source.get('month'),
        'direction_id': source.get('direction'),
        'segment': source.get('segment', 'all'),
        'search_query': source.get('q', ''),
        'page': source.get('page', 1),
    }


class PresenceStatistics(StaffStatisticsMixin, View):
    template_name = 'employee/presence_statistics.html'

    def get(self, request):
        report = build_presence_statistics(**_stats_kwargs(request))
        return render(request, self.template_name, {'report': report})


class PresenceStatisticsExport(StaffStatisticsMixin, View):
    def get(self, request):
        kwargs = _stats_kwargs(request)
        rows, meta = build_agent_rows(
            year=kwargs.get('year'),
            month=kwargs.get('month'),
            direction_id=kwargs.get('direction_id'),
        )
        rows = _filter_rows(rows, kwargs.get('segment', 'all'), kwargs.get('search_query', ''))

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f'statistiques-presence-{meta["year"]}-{meta["month"]:02d}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            _('Matricule'),
            _('Nom'),
            _('Direction'),
            _('Empreintes'),
            _('Jours ouvrés'),
            _('Jours présents'),
            _('Taux présence %'),
            _('Matin'),
            _('Soir'),
            _('Entrée+sortie'),
            _('Moy. pointages/j'),
            _('Segment'),
            _('Score réel'),
            _('Dernier pointage'),
            _('Source dominante'),
        ])
        for row in rows:
            writer.writerow([
                row['matricule'],
                row['full_name'],
                row['direction'],
                row['enrollment_label'],
                row['working_days'],
                row['present_days'],
                row['presence_rate'],
                row['morning_days'],
                row['evening_days'],
                row['both_days'],
                row['avg_punches'],
                row['segment_label'],
                row['real_score'],
                row['last_punch_label'],
                row['dominant_source'],
            ])
        return response
