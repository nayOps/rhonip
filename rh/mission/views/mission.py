from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
from crispy_forms.layout import Layout
from django.urls import reverse_lazy
from django.contrib import messages
from django.apps import apps

from core.forms import modelform_factory, InlineFormSetHelper
from django.contrib.admin.models import CHANGE

from core.views import BaseView, Change
from mission import models

class Mission(BaseView):
    next = None
    action = ["change"]
    template_name = "change.html"
    inline_formset_helper = InlineFormSetHelper()

    def get(self, request, pk):
        app = models.Mission._meta.app_label
        model = models.Mission

        self.kwargs['app'] = app
        self.kwargs['model'] = model._meta.model_name

        obj = get_object_or_404(model, pk=pk)
        
        fields = getattr(model, 'layout', '__all__')
        fields = [field.name for field in fields.get_field_names()]
        fields.remove('employees')
        
        form = modelform_factory(model, fields=fields)
        form = form(instance=obj)

        formsets = [inlineformset_factory(model, models.Report, fields=getattr(models.Report, 'inline_form_fields', '__all__'), can_delete=False, extra=0)]
        formsets = [formset(instance=obj) for formset in formsets]
        
        inline_formset_helper = self.inline_formset_helper
        return render(request, self.template_name, locals())
        app = models.Mission._meta.app_label
        model = models.Mission

        self.kwargs['app'] = app
        self.kwargs['model'] = model._meta.model_name

        obj = get_object_or_404(model, pk=pk)
                
        fields = getattr(model, 'layout', '__all__')
        fields = [field.name for field in fields.get_field_names()]
        fields.remove('employees')
        
        form = modelform_factory(model, fields=fields)
        form = form(request.POST or None, request.FILES or None, instance=obj)

        formsets = [inlineformset_factory(model, models.Report, fields=getattr(models.Report, 'inline_form_fields', '__all__'), can_delete=False, extra=0)]
        formsets = [formset(request.POST or None, request.FILES or None, instance=obj) for formset in formsets]
        
        if not form.is_valid() or False in [formset.is_valid() for formset in formsets]:
            for error in form.errors: messages.error(request, str(error))
            inline_formset_helper = self.inline_formset_helper
            return render(request, self.template_name, locals())

        form.save()
        [formset.save() for formset in formsets]

        self.log(model, form, action=CHANGE, formsets=formsets)
        messages.add_message(request, messages.SUCCESS, _('Le %(model)s #%(pk)s a été mis à jour avec succès') % {'model': model._meta.model_name, 'pk': pk})

        next = request.GET.dict().get('next', reverse_lazy('core:list', kwargs={'app': app, 'model': model._meta.model_name}))
        return self.next if self.next else redirect(next)