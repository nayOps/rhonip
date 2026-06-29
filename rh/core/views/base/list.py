from core.filters import filter_set_factory
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.shortcuts import render
from django.apps import apps
from .base import BaseView


class List(BaseView):
    qs = None
    action = ["view"]
    template_name = "list.html"

    def get(self, request, app, model):
        try:
            model = apps.get_model(app, model_name=model)
        except LookupError:
            from django.http import Http404
            raise Http404(f"Le modèle {app}.{model} n'existe pas.")

        if hasattr(model, 'list_url'):
            return redirect(getattr(model, 'list_url'))

        list_filter = getattr(model, 'list_filter', [])
        list_display = [field for field in model._meta.fields if field.name in getattr(model, 'list_display', [])]
        
        self.qs = model.objects.select_related().prefetch_related()#.order_by('-created_at')
        try:
            # Cas spécial pour Employee: si l'utilisateur est un employé normal, filtrer pour son employé
            if model._meta.label == 'employee.Employee' and not request.user.is_superuser and not request.user.is_staff:
                if request.user.employee:
                    self.qs = self.qs.filter(id=request.user.employee.id)
                else:
                    self.qs = self.qs.none()
            else:
                self.qs = self.qs.all(user=request.user)
        except Exception:
            self.qs = self.qs.all()
        
        # Hard filter
        query = {k:v for k, v in request.GET.dict().items() if v}
        fields = [field.name for field in model._meta.fields if field.name]
        self.qs = self.qs.filter(**{k:v for k, v in query.items() if k.split("__")[0] in fields})

        # Soft filter
        qs_filter = filter_set_factory(model, fields=list_filter)
        qs_filter = qs_filter(request.GET, queryset=self.qs)
        self.qs = qs_filter.qs.order_by('-id')

        if model._meta.label == 'employee.Employee':
            self.qs = self.qs.select_related(
                'designation', 'direction', 'service', 'agreement', 'branch'
            )

        paginator = Paginator(self.qs, 25)
        page_num = request.GET.get('page', 1)
        try:
            page_num = max(1, int(page_num))
        except (TypeError, ValueError):
            page_num = 1
        page_obj = paginator.get_page(page_num)

        app_label = model._meta.app_label
        model_name = model._meta.model_name
        add_perm = f'{app_label}.add_{model_name}'
        show_create_button = (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.has_perm(add_perm)
        )
        if not request.user.is_superuser and not request.user.is_staff:
            if model._meta.label == 'mission.Mission':
                show_create_button = False

        page_title = getattr(model, 'agent_list_title', None)

        return render(
            request,
            getattr(model, 'change_list_template', self.template_name),
            locals(),
        )