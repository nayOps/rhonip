from django.contrib.auth import get_user_model
from django.db.models import Q
from functools import reduce
from django.apps import apps
from django.db import models


class QuerySet(models.QuerySet):
    def all(self, **kwargs):
        Employee = apps.get_model('employee', model_name='employee')
        user = kwargs.get('user', None)
        
        # Vérifier le modèle AVANT d'appeler super().all()
        # car super().all() peut retourner un nouveau queryset
        model_label = self.model._meta.label
        
        # Appeler super().all() pour obtenir le queryset de base
        qs = super(QuerySet, self).all()
        
        # Si pas d'utilisateur, retourner le queryset normal
        if not user: 
            return qs

        # Superusers et staff voient tout
        if user.is_superuser: 
            return qs
        if user.is_staff: 
            return qs
        
        # Cas spécial: Si le modèle est Employee, utiliser la relation inverse
        if model_label == 'employee.Employee':
            if user.employee:
                # Filtrer pour retourner seulement l'employé de l'utilisateur
                return qs.filter(id=user.employee.id)
            else:
                # Si l'utilisateur n'a pas d'employé associé, retourner un queryset vide
                return qs.none()
        
        filters = {}
        fields = [field for field in self.model._meta.fields if field.is_relation]
        fields = [field for field in fields if field.related_model in [get_user_model(), Employee]]
        
        filters.update({field.name:user for field in fields if field.related_model == get_user_model()})
        filters.update({field.name:user.employee for field in fields if field.related_model == Employee})

        filters.update({f'{field.name}__in': [user] for field in self.model._meta.many_to_many if field.related_model == get_user_model() })
        filters.update({f'{field.name}__in': [user.employee] for field in self.model._meta.many_to_many if field.related_model == Employee and user.employee})

        filters = {key:value for key, value in filters.items() if value}
        if filters:
            filters = reduce(lambda q, field: q | Q(**{field: filters.get(field)}), filters.keys(), Q())
            return qs.filter(filters).distinct().order_by('-updated_at')
        
        # Si aucun filtre n'a été trouvé, retourner un queryset vide pour les employés normaux
        return qs.none()