from notifications.models import Notification
from core.filters import filter_set_factory
from django.core.paginator import Paginator

from core.views import BaseView
from django.shortcuts import render

class Notifications(BaseView):
    qs = None
    action = ["view"]

    def get(self, request):
        model = Notification
        list_filter = ['level', 'unread', 'timestamp']
        list_display = ['verb', 'description', 'timestamp']
        list_display = [field for field in model._meta.fields if field.name in list_display]
        
        self.qs = request.user.notifications.select_related().prefetch_related().all().order_by('-timestamp')
        qs_filter = filter_set_factory(model, fields=list_filter)
        qs_filter = qs_filter(request.GET, queryset=self.qs)
        self.qs = qs_filter.qs
        
        paginator = Paginator(self.qs, 25)
        qs = paginator.page(int(request.GET.dict().get('page', 1)))
        
        return render(request, "notification/list.html", locals())