from django.db import models
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Layout

from core.models import Base


class StudyLevel(Base):
    code = models.CharField(_('code'), max_length=50, unique=True)
    name = models.CharField(_('libellé'), max_length=255, unique=True)
    sort_order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    is_system = models.BooleanField(_('système'), default=True)

    search_fields = ('code', 'name')
    list_display = ('sort_order', 'code', 'name', 'is_system')
    layout = Layout('code', 'name', 'sort_order', 'is_system')

    class Meta:
        verbose_name = _('niveau d\'étude')
        verbose_name_plural = _('niveaux d\'étude')
        ordering = ('sort_order', 'name')

    def __str__(self):
        return self.name


class Degree(Base):
    code = models.CharField(_('code'), max_length=50, unique=True)
    name = models.CharField(_('libellé'), max_length=255, unique=True)
    sort_order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    is_system = models.BooleanField(_('système'), default=True)

    search_fields = ('code', 'name')
    list_display = ('sort_order', 'code', 'name', 'is_system')
    layout = Layout('code', 'name', 'sort_order', 'is_system')

    class Meta:
        verbose_name = _('diplôme')
        verbose_name_plural = _('diplômes')
        ordering = ('sort_order', 'name')

    def __str__(self):
        return self.name


class FieldOfStudy(Base):
    code = models.CharField(_('code'), max_length=50, unique=True)
    name = models.CharField(_('libellé'), max_length=255, unique=True)
    sort_order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    is_system = models.BooleanField(_('système'), default=True)

    search_fields = ('code', 'name')
    list_display = ('sort_order', 'code', 'name', 'is_system')
    layout = Layout('code', 'name', 'sort_order', 'is_system')

    class Meta:
        verbose_name = _('domaine de formation')
        verbose_name_plural = _('domaines de formation')
        ordering = ('sort_order', 'name')

    def __str__(self):
        return self.name


class Institution(Base):
    INSTITUTION_TYPES = (
        ('public', _('Publique')),
        ('private', _('Privée')),
        ('other', _('Autre')),
    )

    code = models.CharField(_('code'), max_length=50, unique=True)
    name = models.CharField(_('libellé'), max_length=255, unique=True)
    institution_type = models.CharField(
        _('type'),
        max_length=20,
        choices=INSTITUTION_TYPES,
        default='other',
    )
    sort_order = models.PositiveSmallIntegerField(_('ordre'), default=0)
    is_system = models.BooleanField(_('système'), default=True)

    search_fields = ('code', 'name')
    list_display = ('sort_order', 'code', 'name', 'institution_type', 'is_system')
    list_filter = ('institution_type', 'is_system')
    layout = Layout('code', 'name', 'institution_type', 'sort_order', 'is_system')

    class Meta:
        verbose_name = _('établissement')
        verbose_name_plural = _('établissements')
        ordering = ('sort_order', 'name')

    def __str__(self):
        return self.name
