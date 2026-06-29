from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.contrib import messages

from core.forms import modelform_factory, InlineFormSetHelper
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION
from django.shortcuts import render, redirect
from crispy_forms.layout import Layout
from django.apps import apps
from .base import BaseView

from core.models import Approbation
from core.models import Flow


class Create(BaseView):
    next = None
    action = ["add"]
    template_name = "create.html"
    inline_formset_helper = InlineFormSetHelper()
    
    def get(self, request, app, model):
        model = apps.get_model(app, model_name=model)
        
        fields = getattr(model, 'layout', '__all__')
        fields = [field.name for field in fields.get_field_names()] if isinstance(fields, Layout) else fields

        initial = {field:request.user.employee for field in fields if field == 'employee' and not request.user.is_superuser}
        form = modelform_factory(model, fields=fields)

        if hasattr(model, 'form_clean'): form.clean = model.form_clean
        form = form(initial=initial)

        if not request.user.is_superuser and 'employee' in form.fields:
            form.fields['employee'].widget.attrs['disabled'] = 'disabled'
        
        formsets = [apps.get_model(inline.split('.')[0], model_name=inline.split('.')[-1]) for inline in getattr(model, 'inlines', [])]
        if model._meta.label_lower == 'employee.employee':
            from employee.forms import optional_inline_formset_factory
            formsets = [
                optional_inline_formset_factory(
                    model,
                    inline,
                    fields=getattr(inline, 'inline_form_fields', '__all__'),
                    can_delete=False,
                    extra=1,
                )
                for inline in formsets
            ]
        else:
            formsets = [
                inlineformset_factory(
                    model,
                    inline,
                    fields=getattr(inline, 'inline_form_fields', '__all__'),
                    can_delete=False,
                    extra=1,
                )
                for inline in formsets
            ]
        
        inline_formset_helper = self.inline_formset_helper
        return render(request, self.template_name, locals())
    
    def post(self, request, app, model):
        model = apps.get_model(app, model)

        fields = getattr(model, 'layout', '__all__')
        fields = [field.name for field in fields.get_field_names()] if isinstance(fields, Layout) else fields
        
        initial = {field:request.user.employee for field in fields if field == 'employee' and not request.user.is_superuser}
        form = modelform_factory(model, fields=fields)

        if hasattr(model, 'form_clean'): form.clean = model.form_clean
        form = form(request.POST or None, request.FILES or None, initial=initial)

        if not request.user.is_superuser and 'employee' in form.fields:
            form.fields['employee'].widget.attrs['disabled'] = 'disabled'

        formsets = [apps.get_model(inline.split('.')[0], model_name=inline.split('.')[-1]) for inline in getattr(model, 'inlines', [])]
        if model._meta.label_lower == 'employee.employee':
            from employee.forms import optional_inline_formset_factory
            formsets = [
                optional_inline_formset_factory(
                    model,
                    inline,
                    fields=getattr(inline, 'inline_form_fields', '__all__'),
                    can_delete=False,
                    extra=1,
                )
                for inline in formsets
            ]
        else:
            formsets = [
                inlineformset_factory(
                    model,
                    inline,
                    fields=getattr(inline, 'inline_form_fields', '__all__'),
                    can_delete=False,
                    extra=1,
                )
                for inline in formsets
            ]
        formsets = [formset(request.POST or None, request.FILES or None) for formset in formsets]

        if not form.is_valid() or False in [formset.is_valid() for formset in formsets]:
            [messages.error(request, str(error)) for error in form.errors]
            inline_formset_helper = self.inline_formset_helper
            return render(request, self.template_name, locals())
        form.save()

        # Add approvers - Logique intelligente selon le rôle de l'employé
        if model._meta.model_name == 'latejustification':
            employee = getattr(form.instance, 'employee', None)
            approver = None
            if employee:
                from employee.utils.hierarchy import resolve_n_plus_one
                approver = resolve_n_plus_one(employee)
            if approver:
                Approbation.objects.create(
                    content_type=ContentType.objects.get_for_model(model),
                    object_id=form.instance.id,
                    user=approver,
                )
        else:
            flow = Flow.objects.filter(content_type__model=model._meta.model_name).first()

            # Déterminer si l'employé est un directeur ou sous-directeur
            employee = None
            if hasattr(form.instance, 'employee'):
                employee = form.instance.employee
            elif hasattr(form.instance, 'employees'):
                employees = form.instance.employees.all()
                if employees.exists():
                    employee = employees.first()

            is_director_or_subdirector = False
            if employee and employee.designation:
                designation_name = employee.designation.name.lower()
                is_director_or_subdirector = (
                    'directeur' in designation_name
                    or 'sous-directeur' in designation_name
                    or 'sous directeur' in designation_name
                )

            approvers = []
            if flow:
                if is_director_or_subdirector:
                    steps = flow.steps.filter(
                        name__icontains='Directeur RH'
                    ) | flow.steps.filter(
                        name__icontains='Directeur Général'
                    )
                    approvers = steps.values_list('user', flat=True).distinct()
                elif employee and employee.direction:
                    User = apps.get_model('core', 'User')
                    direction_director = User.objects.filter(
                        employee__direction=employee.direction,
                        employee__designation__name__icontains='Directeur',
                    ).exclude(
                        employee__designation__name__icontains='Sous-directeur'
                    ).first()

                    if direction_director:
                        steps = flow.steps.all().order_by('id')
                        approvers = [direction_director.id]
                        for step in steps:
                            if 'Directeur RH' in step.name or 'Directeur Général' in step.name:
                                approvers.append(step.user_id)
                    else:
                        approvers = flow.steps.values_list('user', flat=True).distinct()
                else:
                    approvers = flow.steps.values_list('user', flat=True).distinct()

            approvers = [
                Approbation(
                    content_type=ContentType.objects.get_for_model(model),
                    object_id=form.instance.id,
                    user_id=approver,
                )
                for approver in approvers
            ]
            Approbation.objects.bulk_create(approvers)

        # Save formsets
        for formset in formsets:
            qs = formset.save(commit=False)
            for obj in qs:
                setattr(obj, formset.fk.name, form.instance)
                obj.save()

        # Log
        self.log(model, form, action=ADDITION, formsets=formsets)
        
        messages.add_message(request, messages.SUCCESS, _('Le %(model)s a été créé avec succès') % {'model': model._meta.model_name})
        next = request.GET.dict().get('next', reverse_lazy('core:list', kwargs={'app': app, 'model': model._meta.model_name}))
        return self.next if self.next else redirect(next)