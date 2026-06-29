from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.contrib import messages
from django.urls import reverse
from django.http import Http404
from django.apps import apps

from core.forms import modelform_factory
from core.views import BaseView
from core import models

class Approbation(BaseView):
    action = ["change"]

    def get(self, request, action, app, model, pk):
        form = modelform_factory(models.Approbation, fields=['comment'])
        model = apps.get_model(app, model_name=model)
        obj = get_object_or_404(model, pk=pk)
        return render(request, "approve.html", locals())

    def post(self, request, action, app, model, pk):
        model = apps.get_model(app, model)
        obj = get_object_or_404(model, id=pk)
        approbations = self.approbations()
        
        if request.user.id not in approbations.users():
            messages.warning(request, _('Vous n\'êtes pas désigné comme approbateur'))
            return redirect(obj.get_absolute_url())
        
        form = modelform_factory(models.Approbation, fields=['comment'])
        form = form(request.POST)
        comment = request.POST.get('comment', None)
        
        # To-Do: Review this code to not allow all user to approve
        if action.upper() not in ['APPROVED', 'REJECTED']: raise Http404
        approbation = approbations.filter(user=request.user, action=None).update(action=action.upper(), comment=comment)
        messages.success(request, _('Vous avez approuvé le %(model)s #%(id)s') % {'model': model._meta.verbose_name, 'id': obj.pk})

        #obj = self.approvers_from_process(model, obj)
        #notified_on_approved(model._meta.app_label, model._meta.model_name, obj.pk, False)

        next = request.GET.get('next', obj.get_absolute_url())
        return redirect(next)