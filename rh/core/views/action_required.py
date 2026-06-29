from django.shortcuts import render
from django.apps import apps
from .base import BaseView

#from core.models import Approbation


class ActionRequired(BaseView):
    def get(self, request):
        #models = apps.all_models
        #models = [models[model] for model in models]
        #models = [list(model.values()) for model in models if model.values()]
        
        #models = reduce(lambda x,y:x+y, models)
        #models = [model.objects.filter(approvers__in=[request.user]).exclude(approvals__in=[request.user])
        #          for model in models if hasattr(model, 'approvers') and hasattr(model, 'approvals')]
        
        #models = [model.all() for model in models if model.exists()]
        #qs = reduce(lambda x,y:list(x)+list(y), models) if models else []
        Approbation = apps.get_model('core', 'approbation')
        qs = Approbation.objects.filter(user=request.user, action__isnull=True)
        return render(request, 'action_required.html', locals())
    
    def post(self, request):
        return render(request, 'action_required.html', locals())