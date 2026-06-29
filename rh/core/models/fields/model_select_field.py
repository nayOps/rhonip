from django.urls import reverse_lazy
from django.db import models
from dal import autocomplete


class ModelSelect(models.ForeignKey):
    def __init__(self, to, *args, autocomplete_min_length=2, **kwargs):
        self.autocomplete_min_length = autocomplete_min_length
        super().__init__(to, *args, **kwargs)

    def formfield(self, **kwargs):
        if 'widget' not in kwargs:
            to_field = getattr(self, 'foreign_related_fields', None)
            to_field = to_field[0].name if to_field else 'pk'
            kwargs['widget'] = autocomplete.ModelSelect2(
                url=reverse_lazy('api:autocomplete', kwargs={
                    'to_field': to_field,
                    'app': self.remote_field.model._meta.app_label,
                    'model': self.remote_field.model._meta.model_name,
                }),
                attrs={
                    'data-minimum-input-length': self.autocomplete_min_length,
                    'theme': 'bootstrap-5',
                },
            )
        return super().formfield(**kwargs)
