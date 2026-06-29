from django.apps import apps
from django.contrib import messages
from django.contrib.admin.models import CHANGE
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext

from core.forms import InlineFormSetHelper
from employee.forms import employee_modelform_factory, optional_inline_formset_factory
from core.views import Change
from employee.utils.attendance_stats import get_employee_attendance_context
from employee.utils.employee_form import get_employee_form_config, is_employee_admin
from employee.utils.profile_dossier import build_profile_dossier


class Employee(Change):
    template_name = "employee/employee.html"
    inline_formset_helper = InlineFormSetHelper()

    def _check_employee_access(self, request, pk):
        if not request.user.is_superuser and not request.user.is_staff:
            if request.user.employee and int(pk) != request.user.employee.id:
                from django.http import Http404
                raise Http404("Vous n'avez pas accès à cet employé")

    def _build_form_context(self, request, obj):
        model = obj._meta.model
        layout, fields = get_employee_form_config(model, request.user)
        return model, fields, layout

    def _render(self, request, obj, form, formsets):
        model = obj._meta.model
        context = {
            'app': 'employee',
            'model': model,
            'obj': obj,
            'employee': obj,
            'form': form,
            'formsets': formsets,
            'dossier': build_profile_dossier(obj),
            'can_edit': True,
            'edit_url': None,
            'full_dossier_url': None,
            'is_employee_admin': is_employee_admin(request.user),
            'inline_formset_helper': self.inline_formset_helper,
            **get_employee_attendance_context(request, obj),
        }
        return render(request, self.template_name, context)

    def get(self, request, pk):
        self.kwargs['app'] = 'employee'
        self.kwargs['model'] = 'employee'
        self._check_employee_access(request, pk)

        model = apps.get_model('employee', model_name='employee')
        obj = get_object_or_404(model, pk=pk)
        model, fields, layout = self._build_form_context(request, obj)

        form = employee_modelform_factory(model, fields=fields, layout=layout)(instance=obj)

        inline_models = [
            apps.get_model(inline.split('.')[0], model_name=inline.split('.')[-1])
            for inline in getattr(model, 'inlines', [])
        ]
        formsets = [
            optional_inline_formset_factory(
                model,
                inline,
                fields=getattr(inline, 'inline_form_fields', '__all__'),
            )(instance=obj)
            for inline in inline_models
        ]

        return self._render(request, obj, form, formsets)

    def post(self, request, pk):
        self.kwargs['app'] = 'employee'
        self.kwargs['model'] = 'employee'
        self._check_employee_access(request, pk)

        model = apps.get_model('employee', model_name='employee')
        obj = get_object_or_404(model, pk=pk)
        model, fields, layout = self._build_form_context(request, obj)

        form = employee_modelform_factory(model, fields=fields, layout=layout)(
            request.POST or None,
            request.FILES or None,
            instance=obj,
        )

        inline_models = [
            apps.get_model(inline.split('.')[0], model_name=inline.split('.')[-1])
            for inline in getattr(model, 'inlines', [])
        ]
        formsets = [
            optional_inline_formset_factory(
                model,
                inline,
                fields=getattr(inline, 'inline_form_fields', '__all__'),
            )(request.POST or None, request.FILES or None, instance=obj)
            for inline in inline_models
        ]

        if not form.is_valid() or False in [formset.is_valid() for formset in formsets]:
            for error in form.errors:
                messages.error(request, str(error))
            return self._render(request, obj, form, formsets)

        form.save()
        [formset.save() for formset in formsets]

        self.log(model, form, action=CHANGE, formsets=formsets)
        messages.add_message(
            request,
            messages.SUCCESS,
            gettext('Le dossier employé #%(pk)s a été mis à jour avec succès')
            % {'pk': pk},
        )

        next_url = request.GET.dict().get(
            'next',
            reverse_lazy('core:list', kwargs={'app': 'employee', 'model': model._meta.model_name}),
        )
        return self.next if self.next else redirect(next_url)
