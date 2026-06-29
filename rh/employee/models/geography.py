from django.db import models
from django.utils.translation import gettext as _
from crispy_forms.layout import Layout

from core.models import Base
from core.models.fields import ModelSelect


class Province(Base):
    source_id = models.IntegerField(_('identifiant source'), unique=True, null=True, blank=True)
    name = models.CharField(_('nom'), max_length=200, unique=True)

    search_fields = ('name',)
    list_display = ('id', 'source_id', 'name')
    layout = Layout('source_id', 'name')

    class Meta:
        verbose_name = _('province')
        verbose_name_plural = _('provinces')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Territory(Base):
    source_id = models.IntegerField(_('identifiant source'), null=True, blank=True)
    province = ModelSelect(Province, verbose_name=_('province'), on_delete=models.CASCADE)
    name = models.CharField(_('nom'), max_length=200)
    type_name = models.CharField(_('type'), max_length=20, blank=True, default='')

    search_fields = ('name', 'province__name')
    list_display = ('id', 'source_id', 'province', 'name', 'type_name')
    list_filter = ('province',)
    layout = Layout('province', 'source_id', 'name', 'type_name')

    class Meta:
        verbose_name = _('territoire')
        verbose_name_plural = _('territoires')
        ordering = ('province__name', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=['province', 'source_id'],
                name='uniq_territory_source_per_province',
            ),
        ]

    def __str__(self):
        return self.name


class Sector(Base):
    source_id = models.IntegerField(_('identifiant source'), null=True, blank=True)
    territory = ModelSelect(Territory, verbose_name=_('territoire'), on_delete=models.CASCADE)
    name = models.CharField(_('nom'), max_length=200)
    type_name = models.CharField(_('type'), max_length=20, blank=True, default='')

    search_fields = ('name', 'territory__name')
    list_display = ('id', 'source_id', 'territory', 'name', 'type_name')
    list_filter = ('territory__province', 'territory')
    layout = Layout('territory', 'source_id', 'name', 'type_name')

    class Meta:
        verbose_name = _('secteur')
        verbose_name_plural = _('secteurs')
        ordering = ('territory__name', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=['territory', 'source_id'],
                name='uniq_sector_source_per_territory',
            ),
        ]

    def __str__(self):
        return self.name


class Groupement(Base):
    source_id = models.IntegerField(_('identifiant source'), null=True, blank=True)
    sector = ModelSelect(Sector, verbose_name=_('secteur'), on_delete=models.CASCADE)
    name = models.CharField(_('nom'), max_length=200)
    type_name = models.CharField(_('type'), max_length=20, blank=True, default='')

    search_fields = ('name', 'sector__name')
    list_display = ('id', 'source_id', 'sector', 'name', 'type_name')
    list_filter = ('sector__territory__province', 'sector__territory')
    layout = Layout('sector', 'source_id', 'name', 'type_name')

    class Meta:
        verbose_name = _('groupement')
        verbose_name_plural = _('groupements')
        ordering = ('sector__name', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=['sector', 'source_id'],
                name='uniq_groupement_source_per_sector',
            ),
        ]

    def __str__(self):
        return self.name


class Village(Base):
    source_id = models.IntegerField(_('identifiant source'), unique=True, null=True, blank=True)
    groupement = ModelSelect(Groupement, verbose_name=_('groupement'), on_delete=models.CASCADE)
    name = models.CharField(_('nom'), max_length=200)
    locality_name = models.CharField(_('localité'), max_length=200, blank=True, default='')
    latitude = models.FloatField(_('latitude'), null=True, blank=True)
    longitude = models.FloatField(_('longitude'), null=True, blank=True)

    search_fields = ('name', 'locality_name', 'groupement__name')
    list_display = ('id', 'source_id', 'groupement', 'name')
    list_filter = ('groupement__sector__territory__province',)
    layout = Layout('groupement', 'source_id', 'name', 'locality_name', 'latitude', 'longitude')

    class Meta:
        verbose_name = _('village')
        verbose_name_plural = _('villages')
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['groupement', 'name'],
                name='uniq_village_per_groupement',
            ),
        ]
        indexes = [
            models.Index(fields=['name'], name='employee_village_name_idx'),
        ]

    def __str__(self):
        return self.name

    @property
    def sector(self):
        return self.groupement.sector

    @property
    def territory(self):
        return self.groupement.sector.territory

    @property
    def province(self):
        return self.groupement.sector.territory.province
