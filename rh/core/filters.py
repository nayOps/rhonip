from django.utils.translation import gettext as _
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from datetime import datetime
from functools import reduce
from django_filters import *
from django import forms



class AdvanceFilterSet(FilterSet):
    q = CharFilter("", label="", method='search', widget=forms.TextInput(attrs={'class': 'd-none'}))
    retire_period = CharFilter("", method="retire", label=_('Retire Period'), widget=forms.TextInput(attrs={'type': 'month'}), help_text=_('YYYY-MM'))

    def search(self, queryset, name, value):
        fields = getattr(self._meta.model, 'search_fields', [])
        fields = fields if fields else [field.name for field in self._meta.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField']]
        return queryset.filter(reduce(lambda q, field: q | Q(**{f'{field}__icontains': value}), fields, Q()))
    
    def retire(self, queryset, name, value):
        value = datetime.strptime(value, '%Y-%m').date()
        career = value - relativedelta(years=35)
        age = value - relativedelta(years=65)

        queryset = queryset.filter(
                (Q(date_of_join__year=career.year) & Q(date_of_join__month=career.month)) |
                (Q(date_of_birth__year=age.year) & Q(date_of_birth__month=age.month)))
        return queryset


def filter_set_factory(model, fields):
    attrs = {}
    meta = type(str("Meta"), (object,), {"model": model, "fields": fields})

    for field in model._meta.fields:
        if field.name not in fields: continue
        if field.get_internal_type() not in ['DateTimeField', 'DateField']: continue
        _class = eval(field.get_internal_type().replace("Field", "FromToRangeFilter"))
        attrs[field.name] = _class(help_text=_('YYYY-MM-DD'))
    if model._meta.model_name != 'employee': attrs['retire_period'] = None
    
    attrs['Meta'] = meta
    return type(str("%sFilterSet" % model._meta.object_name), (AdvanceFilterSet,), attrs)
