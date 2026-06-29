from dal import autocomplete

from core.forms import modelform_factory as base_modelform_factory
from employee.choices.countries import DEFAULT_COUNTRY, COUNTRY_CHOICES
from employee.choices.country_field import CountryChoiceField

_COUNTRY_WIDGET = autocomplete.ListSelect2(
    attrs={
        'data-minimum-input-length': 0,
        'theme': 'bootstrap-5',
    },
)


def make_all_fields_optional(form_class):
    class OptionalForm(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.required = False
            self._prepare_country_fields()

        def _prepare_country_fields(self):
            known = {value for value, _label in COUNTRY_CHOICES if value}
            for name in ('citizenship', 'home_country'):
                if name not in self.fields:
                    continue
                field = self.fields[name]
                current = field.initial
                if not current and getattr(self.instance, 'pk', None):
                    current = getattr(self.instance, name, None)
                if current and current not in known:
                    field.choices = [(current, current)] + list(COUNTRY_CHOICES)

        def clean_citizenship(self):
            return CountryChoiceField.normalize(self.cleaned_data.get('citizenship'))

        def clean_home_country(self):
            return CountryChoiceField.normalize(self.cleaned_data.get('home_country'))

        def clean(self):
            cleaned_data = super().clean()
            home_country = cleaned_data.get('home_country')
            if home_country and home_country != DEFAULT_COUNTRY:
                for name in (
                    'home_province',
                    'home_territory',
                    'home_sector',
                    'home_groupement',
                    'home_village',
                ):
                    cleaned_data[name] = None
            return cleaned_data

    OptionalForm.__name__ = form_class.__name__
    OptionalForm.__qualname__ = form_class.__qualname__
    return OptionalForm


def employee_modelform_factory(model, fields, layout=None):
    from crispy_forms.layout import Layout

    form_class = base_modelform_factory(model, fields, layout or Layout())
    form_class.Meta.widgets = {
        **getattr(form_class.Meta, 'widgets', {}),
        'citizenship': _COUNTRY_WIDGET,
        'home_country': _COUNTRY_WIDGET,
    }
    return make_all_fields_optional(form_class)


def optional_inline_formset_factory(parent_model, model, **kwargs):
    from django.forms import inlineformset_factory

    fields = kwargs.pop('fields', '__all__')
    inline_form_class = base_modelform_factory(model, fields)
    inline_form_class = make_all_fields_optional(inline_form_class)
    kwargs.setdefault('can_delete', True)
    kwargs.setdefault('extra', 1)
    return inlineformset_factory(parent_model, model, form=inline_form_class, **kwargs)
