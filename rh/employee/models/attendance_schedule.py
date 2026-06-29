from datetime import time

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.base import Base
from core.models.fields import JSONField


class AttendanceSchedule(Base):
    PRESET_2_SLOTS = '2_slots'
    PRESET_4_SLOTS = '4_slots'
    PRESET_CHOICES = (
        (PRESET_2_SLOTS, _('2 plages (entrée / sortie)')),
        (PRESET_4_SLOTS, _('4 plages (matin, pause, après-midi)')),
    )

    slot_preset = models.CharField(
        verbose_name=_('modèle de plages'),
        max_length=20,
        choices=PRESET_CHOICES,
        default=PRESET_4_SLOTS,
    )
    slots_config = JSONField(verbose_name=_('configuration des plages'), default=list, blank=True)
    work_start = models.TimeField(verbose_name=_('début de journée'), default=time(8, 0))
    work_end = models.TimeField(verbose_name=_('fin de journée'), default=time(16, 0))
    lunch_break_min_minutes = models.PositiveSmallIntegerField(
        verbose_name=_('pause déjeuner min (min)'),
        default=50,
    )
    lunch_break_max_minutes = models.PositiveSmallIntegerField(
        verbose_name=_('pause déjeuner max (min)'),
        default=70,
    )

    list_display = ('slot_preset', 'work_start', 'work_end')
    search_fields = ()

    def save(self, *args, **kwargs):
        if self.__class__.objects.exists():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)
        from employee.utils.attendance_schedule_config import clear_attendance_schedule_cache

        clear_attendance_schedule_cache()

    @property
    def name(self):
        return str(self.get_slot_preset_display())

    class Meta:
        verbose_name = _('planning des plages de présence')
        verbose_name_plural = _('plannings des plages de présence')
