from django.urls import reverse_lazy
from dal import forward
from dal import autocomplete

from .model_select_field import ModelSelect


class CascadeModelSelect(ModelSelect):
    """ForeignKey avec filtrage Select2 via champs parents (django-autocomplete-light)."""

    def __init__(self, *args, forward_fields=None, **kwargs):
        self._forward_fields = forward_fields or []
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        to_field = getattr(self, 'foreign_related_fields', None)
        to_field = to_field[0].name if to_field else 'pk'
        kwargs['widget'] = autocomplete.ModelSelect2(
            url=reverse_lazy('api:autocomplete', kwargs={
                'to_field': to_field,
                'app': self.remote_field.model._meta.app_label,
                'model': self.remote_field.model._meta.model_name,
            }),
            forward=[forward.Field(source, dest) for source, dest in self._forward_fields],
            attrs={
                'data-minimum-input-length': 0,
                'theme': 'bootstrap-5',
            },
        )
        return super().formfield(**kwargs)
