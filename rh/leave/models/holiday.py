from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext as _
from core.models.fields import DateField
from django.db import models

from core.models import Base


class Holiday(Base):
    paid = models.BooleanField(_('payé'), default=True)
    name = models.CharField(_('nom'), max_length=100)
    start_dt = DateField(_('du'))
    end_dt = DateField(_('au'))

    layout = Layout('name', Row(Column('start_dt'), Column('end_dt')), 'paid')
    list_display = ('id', 'name', 'start_dt', 'end_dt', 'paid')
    search_fields = ('name',)
    list_filter = ('paid', 'start_dt')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            from employee.utils.holidays import clear_holiday_cache
            clear_holiday_cache()
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        try:
            from employee.utils.holidays import clear_holiday_cache
            clear_holiday_cache()
        except Exception:
            pass
        return result

    class Meta:
        verbose_name = _('Jour férié')
        verbose_name_plural = _('Jours fériés')
        ordering = ('-start_dt',)
