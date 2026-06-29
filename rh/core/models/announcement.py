from django.db import models
from django.utils.translation import gettext as _
from core.models import Base
from crispy_forms.layout import Layout, Row, Column


class AnnouncementType(models.TextChoices):
    SERVICE_NOTE = "SERVICE_NOTE", _("Note de Service")
    HR_UPDATE = "HR_UPDATE", _("Mise à jour RH")
    GENERAL = "GENERAL", _("Général")


class Announcement(Base):
    title = models.CharField(verbose_name=_('titre'), max_length=200)
    content = models.TextField(verbose_name=_('contenu'))
    type = models.CharField(
        verbose_name=_('type'),
        max_length=20,
        choices=AnnouncementType.choices,
        default=AnnouncementType.GENERAL
    )
    is_active = models.BooleanField(verbose_name=_('actif'), default=True)
    
    list_display = ('id', 'title', 'type', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('type', 'is_active', 'created_at')
    
    layout = Layout(
        Row(
            Column('title', css_class='col-md-8'),
            Column('type', css_class='col-md-4'),
        ),
        'content',
        Row(
            Column('is_active', css_class='col-md-6'),
        ),
    )
    
    class Meta:
        verbose_name = _('annonce')
        verbose_name_plural = _('annonces')
        ordering = ('-created_at',)
    
    def __str__(self):
        return self.title
