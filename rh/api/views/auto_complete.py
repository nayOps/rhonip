from django.db.models import Q
from django.apps import apps
from dal import autocomplete

from functools import reduce


class Autocomplete(autocomplete.Select2QuerySetView):
    def get_model(self, app, model):
        try:
            return apps.get_model(app, model_name=model)
        except Exception:
            apps.get_app_config('core').apps.register_model('core', model)
            return apps.get_model(app, model_name=model)

    def _forwarded(self):
        forwarded = getattr(self, 'forwarded', None)
        if forwarded is None:
            return {}
        if isinstance(forwarded, dict):
            return forwarded
        return dict(forwarded)

    def _filter_by_name(self, qs, model):
        if not self.q:
            return qs
        fields = [
            field.name for field in model._meta.fields
            if field.get_internal_type() in ['CharField', 'TextField']
        ]
        if not fields:
            return qs
        return qs.filter(
            reduce(lambda q, field: q | Q(**{f'{field}__icontains': self.q}), fields, Q())
        )

    def get_queryset(self):
        model = self.get_model(self.kwargs.get('app'), self.kwargs.get('model'))

        if not self.request.user.is_authenticated:
            return model.objects.none()

        model_name = model._meta.model_name
        forwarded = self._forwarded()

        if model_name == 'province':
            qs = model.objects.all().order_by('name')
            return self._filter_by_name(qs, model)

        if model_name == 'territory':
            if not forwarded.get('province'):
                return model.objects.none()
            qs = model.objects.filter(province_id=forwarded['province']).order_by('name')
            if not self.q:
                return qs[:200]
            return self._filter_by_name(qs, model)[:200]

        if model_name == 'sector':
            if not forwarded.get('territory'):
                return model.objects.none()
            qs = model.objects.filter(territory_id=forwarded['territory']).order_by('name')
            if not self.q:
                return qs[:200]
            return self._filter_by_name(qs, model)[:200]

        if model_name == 'groupement':
            if not forwarded.get('sector'):
                return model.objects.none()
            qs = model.objects.filter(sector_id=forwarded['sector']).order_by('name')
            if not self.q:
                return qs[:300]
            return self._filter_by_name(qs, model)[:300]

        if model_name == 'village':
            qs = model.objects.select_related(
                'groupement__sector__territory__province',
            )
            q = (self.q or '').strip()
            groupement_id = forwarded.get('groupement')
            sector_id = forwarded.get('sector')
            territory_id = forwarded.get('territory')
            province_id = forwarded.get('province')

            if groupement_id:
                qs = qs.filter(groupement_id=groupement_id)
                if q:
                    qs = qs.filter(name__icontains=q)
                return qs.order_by('name')[:100]

            if len(q) < 2:
                return model.objects.none()

            qs = qs.filter(name__icontains=q)
            if sector_id:
                qs = qs.filter(groupement__sector_id=sector_id)
            elif territory_id:
                qs = qs.filter(groupement__sector__territory_id=territory_id)
            elif province_id:
                qs = qs.filter(groupement__sector__territory__province_id=province_id)
            return qs.order_by('name')[:50]

        # Référentiels RH (direction, grade, …) : liste initiale sans saisie
        if model_name in {
            'direction', 'subdirection', 'service', 'grade', 'designation',
            'agreement', 'branch',
        }:
            qs = model.objects.all().order_by('name')
            if not self.q:
                return qs[:80]
            return self._filter_by_name(qs, model)[:80]

        qs = model.objects.all()
        if not self.q:
            return model.objects.none()
        return self._filter_by_name(qs, model)

    def get_result_label(self, result):
        if result._meta.model_name == 'village':
            try:
                territory = result.groupement.sector.territory
                province = territory.province
                return f'{result.name} — {territory.name}, {province.name}'
            except Exception:
                pass
        return super().get_result_label(result)

    def get_result_value(self, result):
        return getattr(result, self.kwargs.get('to_field', 'pk'), result)
