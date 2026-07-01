from django.utils.translation import gettext as _
from dal.autocomplete import ListSelect2
from crispy_forms.layout import Layout

from crispy_forms.helper import FormHelper
from django import forms

from django.urls import reverse_lazy
from dal import autocomplete

from django.contrib.auth import get_user_model
from core.models import Flow

approvers_widget = autocomplete.ModelSelect2Multiple(url=reverse_lazy('api:autocomplete', kwargs={'to_field': 'pk', 'app': get_user_model()._meta.app_label, 'model': get_user_model()._meta.model_name}))
approvers = forms.ModelMultipleChoiceField(queryset=get_user_model().objects.all(), widget=approvers_widget)

class InlineForm(forms.Form):
    class Meta:
        fields = '__all__'

    def __init__(self, args, kwargs):
        super(InlineForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False


class InlineFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(InlineFormSetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.template = 'bootstrap5/table_inline_formset.html'

def form_factory(model, fields):
    attrs = {'models': model}
    if fields: attrs['fields'] = fields

    class_name = str("%sForm" % model._meta.object_name)
    return type(class_name, (forms.Form,), fields)

def strip_dal_media_js(form_class):
    """Scripts DAL/Select2 déjà dans base.html — évite double chargement."""
    class FormWithoutDalJs(form_class):
        @property
        def media(self):
            base_media = super().media
            return forms.Media(css=base_media._css)

    FormWithoutDalJs.__name__ = form_class.__name__
    FormWithoutDalJs.__qualname__ = form_class.__qualname__
    return FormWithoutDalJs


def modelform_factory(model, fields, layout=Layout()):
    flow = Flow.objects.filter(content_type__model=model._meta.model_name)
    #if flow.exists(): fields.remove('approvers', None)
    
    attrs = {'model': model}
    if fields: attrs['fields'] = fields

    attrs['widgets'] = {field.name: ListSelect2() for field in model._meta.fields if field.choices}
    Meta = type(str('Meta'), (object,), attrs)

    helper = FormHelper()
    attrs = {'Meta': Meta}
    helper.form_tag = False
    helper.layout = layout or getattr(model, 'layout', layout)
            
    attrs['helper'] = helper
    class_name = str("%sModelForm" % model._meta.object_name)
    form_class = type(class_name, (forms.ModelForm,), attrs)
    form_class = strip_dal_media_js(form_class)

    if model._meta.label_lower == 'employee.employee':
        from employee.forms import make_all_fields_optional
        form_class = make_all_fields_optional(form_class)

    return form_class