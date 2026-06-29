from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views import View

from employee.models import AttendanceSchedule
from employee.utils.attendance_schedule_config import (
    PRESET_CONFIGS,
    clear_attendance_schedule_cache,
    deserialize_slot,
    serialize_slot,
)


class AttendanceScheduleSettings(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'employee/attendance_schedule_settings.html'

    def test_func(self):
        return self.request.user.is_staff

    def _get_schedule(self):
        row = AttendanceSchedule.objects.first()
        if not row:
            row = AttendanceSchedule.objects.create(
                slot_preset=AttendanceSchedule.PRESET_4_SLOTS,
                slots_config=PRESET_CONFIGS[AttendanceSchedule.PRESET_4_SLOTS],
            )
        return row

    def _build_form_slots(self, schedule, preset):
        stored = {slot['code']: slot for slot in (schedule.slots_config or [])}
        slots = []
        for slot in PRESET_CONFIGS[preset]:
            merged = dict(slot)
            if slot['code'] in stored:
                merged.update(stored[slot['code']])
            if preset == AttendanceSchedule.PRESET_2_SLOTS and slot['code'] == 'EVENING_OUT':
                merged.pop('reference', None)
            slots.append(merged)
        return slots

    def _reference_from_post(self, preset, code, template_slot, raw):
        if preset == AttendanceSchedule.PRESET_2_SLOTS and code == 'EVENING_OUT':
            return None
        raw = (raw or '').strip()
        if not raw or raw in ('00:00', '00:00:00'):
            return template_slot.get('reference')
        return raw

    def _render(self, request, schedule, preset=None):
        preset = preset or schedule.slot_preset
        return render(
            request,
            self.template_name,
            {
                'schedule': schedule,
                'preset': preset,
                'preset_choices': AttendanceSchedule.PRESET_CHOICES,
                'slots': self._build_form_slots(schedule, preset),
                'work_start': schedule.work_start.strftime('%H:%M'),
                'work_end': schedule.work_end.strftime('%H:%M'),
                'lunch_break_min_minutes': schedule.lunch_break_min_minutes,
                'lunch_break_max_minutes': schedule.lunch_break_max_minutes,
            },
        )

    def get(self, request):
        schedule = self._get_schedule()
        preset = request.GET.get('preset') or schedule.slot_preset
        if preset not in PRESET_CONFIGS:
            preset = schedule.slot_preset
        return self._render(request, schedule, preset)

    def post(self, request):
        schedule = self._get_schedule()
        preset = request.POST.get('slot_preset', AttendanceSchedule.PRESET_4_SLOTS)

        if request.POST.get('reload_preset'):
            if preset not in PRESET_CONFIGS:
                preset = AttendanceSchedule.PRESET_4_SLOTS
            return self._render(request, schedule, preset)
        if preset not in PRESET_CONFIGS:
            preset = AttendanceSchedule.PRESET_4_SLOTS

        slots_config = []
        for index, template_slot in enumerate(PRESET_CONFIGS[preset]):
            code = template_slot['code']
            prefix = f'slot_{index}_'
            slots_config.append(
                serialize_slot(
                    {
                        'code': code,
                        'label': request.POST.get(f'{prefix}label', template_slot['label']),
                        'target': request.POST.get(f'{prefix}target', template_slot['target']),
                        'accept_from': request.POST.get(f'{prefix}accept_from', template_slot['accept_from']),
                        'accept_until': request.POST.get(f'{prefix}accept_until', template_slot['accept_until']),
                        'reference': self._reference_from_post(
                            preset,
                            code,
                            template_slot,
                            request.POST.get(f'{prefix}reference'),
                        ),
                        'ui_header': request.POST.get(f'{prefix}ui_header', template_slot.get('ui_header', '')),
                    }
                )
            )

        try:
            for slot in slots_config:
                deserialize_slot(slot)
        except ValueError as exc:
            messages.error(request, _('Horaires invalides : %(error)s') % {'error': exc})
            return redirect('employee:attendance_schedule_settings')

        schedule.slot_preset = preset
        schedule.slots_config = slots_config
        schedule.work_start = datetime.strptime(request.POST.get('work_start', '08:00'), '%H:%M').time()
        schedule.work_end = datetime.strptime(request.POST.get('work_end', '16:00'), '%H:%M').time()
        schedule.lunch_break_min_minutes = int(request.POST.get('lunch_break_min_minutes', 50) or 50)
        schedule.lunch_break_max_minutes = int(request.POST.get('lunch_break_max_minutes', 70) or 70)
        schedule.save()
        clear_attendance_schedule_cache()

        messages.success(request, _('Plages de présence mises à jour. La configuration s\'applique sur toute l\'application.'))
        return redirect('employee:attendance_schedule_settings')
