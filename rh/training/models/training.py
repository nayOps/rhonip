from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from core.models.fields import DateField
from core.models import Base
from django.db import models

class Training(Base):
    name = models.CharField(verbose_name=_('nom'), max_length=255)
    description = models.TextField(verbose_name=_('description'), null=True)

    place_of_training = models.CharField(verbose_name=_('lieu de formation'), max_length=255, null=True)
    trainer = models.CharField(verbose_name=_('formateur'), max_length=255, null=True)

    has_certificate = models.BooleanField(verbose_name=_('certificat'), help_text=_('A la fin de la formation, un certificat est délivré.'), default=False)
    is_completed = models.BooleanField(verbose_name=_('terminé'), help_text=_('La formation est-elle achevée ?'), default=False)

    start_date = DateField(verbose_name=_('date de début'), null=True)
    end_date = DateField(verbose_name=_('date de fin'), null=True)

    list_display = ['name', 'description', 'place_of_training', 'trainer', 'start_date', 'is_completed']
    layout = Layout(
        'name',
        'description',
        Row(
            Column('place_of_training', css_class='col-md-6'),
            Column('trainer', css_class='col-md-6'),
        ),
        Row(
            Column('start_date', css_class='col-md-6'),
            Column('end_date', css_class='col-md-6'),
        ),
        Row(
            Column('has_certificate', css_class='col-md-6'),
            Column('is_completed', css_class='col-md-6'),
        )
    )

    class Meta:
        verbose_name = _('formation')
        verbose_name_plural = _('formations')