from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from core.views.base import BaseView
from django.contrib import messages

class Notification(BaseView):
    action = ["change"]

    def get(self, request, pk):
        notification = request.user.notifications.filter(pk=pk)
        notification.mark_all_as_read(request.user)
        notification = notification.first()
        
        try:
            reverse_url = reverse_lazy('core:change', kwargs={
                'model': notification.target._meta.model_name,
                'app': notification.target._meta.app_label,
                'pk': notification.target.pk
            })
        except:
            reverse_url = reverse_lazy('core:notifications')
            messages.warning(request, _('Cette notification n\'est plus valable.'))
            return HttpResponseRedirect(reverse_url)
        return HttpResponseRedirect(notification.data.get('url', reverse_url))