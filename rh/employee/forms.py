from dal import autocomplete
from django import forms
from django.core.exceptions import ValidationError
from core.forms import modelform_factory as base_modelform_factory
from employee.choices.countries import DEFAULT_COUNTRY, COUNTRY_CHOICES
from employee.choices.country_field import CountryChoiceField
from employee.models.education_references import Degree, FieldOfStudy, Institution, StudyLevel
from employee.utils.education_references import get_autres_pk, is_autres_code, resolve_reference
from employee.utils.employee_form import (
    ADMIN_ONLY_EDITABLE_EMPLOYEE_FIELDS,
    is_employee_admin,
)

_COUNTRY_WIDGET = autocomplete.ListSelect2(
    attrs={
        'data-minimum-input-length': 0,
        'theme': 'bootstrap-5',
    },
)

_EDUCATION_SELECT_ATTRS = {
    'class': 'form-select onip-education-ref-select onip-uppercase-select onip-step-field',
}

_INSTITUTION_WIDGET_BASE = {
    'data-minimum-input-length': 0,
    'theme': 'bootstrap-5',
}

_EDUCATION_OTHER_FIELDS = (
    ('study_level', StudyLevel, 'study_level_other'),
    ('degree', Degree, 'degree_other'),
    ('field_of_study', FieldOfStudy, 'field_of_study_other'),
    ('institution', Institution, 'institution_other'),
)


class UppercaseLabelModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.name).upper()


def make_all_fields_optional(form_class, user=None):
    class OptionalForm(form_class):
        def __init__(self, *args, **kwargs):
            self._form_user = kwargs.pop('user', user)
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.required = False
            self._prepare_country_fields()
            self._lock_admin_only_fields()

        def _lock_admin_only_fields(self):
            if not getattr(self.instance, 'pk', None):
                return
            locked = not is_employee_admin(self._form_user)
            for name in ADMIN_ONLY_EDITABLE_EMPLOYEE_FIELDS:
                if name not in self.fields:
                    continue
                field = self.fields[name]
                field.disabled = locked
                css = field.widget.attrs.get('class', '')
                if locked:
                    field.widget.attrs['class'] = f'{css} onip-field-locked'.strip()
                elif 'onip-field-locked' in css:
                    field.widget.attrs['class'] = css.replace('onip-field-locked', '').strip()

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
            if getattr(self.instance, 'pk', None) and not is_employee_admin(self._form_user):
                for name in ADMIN_ONLY_EDITABLE_EMPLOYEE_FIELDS:
                    if name in self.fields:
                        cleaned_data[name] = getattr(self.instance, name)
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


def employee_modelform_factory(model, fields, layout=None, user=None):
    from crispy_forms.layout import Layout

    form_class = base_modelform_factory(model, fields, layout or Layout(), wrap_employee_form=False)
    form_class.Meta.widgets = {
        **getattr(form_class.Meta, 'widgets', {}),
        'citizenship': _COUNTRY_WIDGET,
        'home_country': _COUNTRY_WIDGET,
    }
    return make_all_fields_optional(form_class, user=user)


def optional_inline_formset_factory(parent_model, model, **kwargs):
    from django.forms import inlineformset_factory

    fields = kwargs.pop('fields', '__all__')
    inline_form_class = base_modelform_factory(model, fields)

    if model._meta.label_lower == 'employee.education':
        class EducationInlineForm(inline_form_class):
            def __init__(self, *args, **inner_kwargs):
                super().__init__(*args, **inner_kwargs)
                self._prepare_education_reference_fields()

            def _prepare_education_reference_fields(self):
                for field_name, ref_model, other_name in _EDUCATION_OTHER_FIELDS:
                    if field_name not in self.fields:
                        continue

                    autres_pk = get_autres_pk(ref_model)
                    queryset = ref_model.objects.all().order_by('sort_order', 'name')
                    ref_attrs = {
                        'data-autres-pk': str(autres_pk or ''),
                        'data-ref-field': field_name,
                    }
                    widget = autocomplete.ListSelect2(
                        attrs={
                            **_INSTITUTION_WIDGET_BASE,
                            'class': 'onip-education-ref-select onip-uppercase-select onip-step-field',
                            **ref_attrs,
                        },
                    )
                    self.fields[field_name] = UppercaseLabelModelChoiceField(
                        queryset=queryset,
                        required=False,
                        label=self.fields[field_name].label,
                        widget=widget,
                    )
                    self.fields[other_name] = forms.CharField(
                        required=False,
                        label='',
                        widget=forms.TextInput(
                            attrs={
                                'class': 'form-control onip-education-other-input onip-uppercase-select',
                                'placeholder': 'SAISIR LA VALEUR',
                                'data-other-for': field_name,
                                'style': 'display:none;',
                            },
                        ),
                    )

                self._reorder_education_fields()
                self._style_education_plain_fields()

            def _style_education_plain_fields(self):
                for name in ('diploma_year', 'start_date', 'end_date'):
                    if name not in self.fields:
                        continue
                    field = self.fields[name]
                    css = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f'form-control onip-step-field {css}'.strip()
                    if name == 'diploma_year':
                        field.widget.attrs.setdefault('placeholder', '2024')
                        field.widget.attrs.setdefault('min', '1950')
                        field.widget.attrs.setdefault('max', '2100')

            def _reorder_education_fields(self):
                from collections import OrderedDict

                order = []
                for name in list(self.fields.keys()):
                    if name.endswith('_other'):
                        continue
                    order.append(name)
                    other_name = next(
                        (other for field_name, _ref_model, other in _EDUCATION_OTHER_FIELDS if field_name == name),
                        None,
                    )
                    if other_name and other_name in self.fields:
                        order.append(other_name)
                for name in self.fields:
                    if name not in order:
                        order.append(name)
                self.fields = OrderedDict((name, self.fields[name]) for name in order)

            def clean(self):
                cleaned_data = super().clean()
                for field_name, ref_model, other_name in _EDUCATION_OTHER_FIELDS:
                    if field_name not in cleaned_data:
                        continue
                    selected = cleaned_data.get(field_name)
                    other_value = (cleaned_data.get(other_name) or '').strip()
                    if selected and is_autres_code(getattr(selected, 'code', None)):
                        if not other_value:
                            self.add_error(
                                other_name,
                                ValidationError('Veuillez préciser la valeur pour « Autres ».'),
                            )
                            continue
                        cleaned_data[field_name] = resolve_reference(
                            ref_model,
                            other_value,
                            create_if_missing=True,
                        )
                    cleaned_data.pop(other_name, None)
                return cleaned_data

        inline_form_class = EducationInlineForm

    inline_form_class = make_all_fields_optional(inline_form_class)
    kwargs.setdefault('can_delete', True)
    kwargs.setdefault('extra', 1)
    return inlineformset_factory(parent_model, model, form=inline_form_class, **kwargs)
