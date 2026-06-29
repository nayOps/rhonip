from django.db import models
from django import forms


class DateField(models.DateField):
    def formfield(self, **kwargs):
        kwargs.setdefault(
            'widget',
            forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control onip-date-input',
                },
            ),
        )
        kwargs.setdefault('input_formats', ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'])
        return super().formfield(**kwargs)
