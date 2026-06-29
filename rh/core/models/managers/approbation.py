from django.apps import apps
from django.db import models
from django.contrib.contenttypes.models import ContentType

class ApprobationQueryset(models.QuerySet):
    def for_model(self, model, queryset=None):
        if queryset is None:
            queryset = model.objects.all()
        content_type = ContentType.objects.get_for_model(model)
        # it would be preferable to do a join here if possible
        return self.filter(content_type__pk=content_type.pk, object_id__in=queryset)
    
    def pending(self):
        return self.filter(action__isnull=True)
    
    def approved(self):
        return self.filter(action='APPROVED')
    
    def rejected(self):
        return self.filter(action='REJECTED')

    def users(self):
        return self.values_list('user', flat=True).distinct()
    
    def is_fully_approved(self):
        return self.filter(action='APPROVED').count() == self.users().count()