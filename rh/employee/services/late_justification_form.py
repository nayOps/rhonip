from django import forms
from django.utils.translation import gettext as _


class LateJustificationForm(forms.Form):
    employee = forms.IntegerField(widget=forms.HiddenInput)
    date = forms.DateField(widget=forms.HiddenInput)
    delay_minutes = forms.IntegerField(widget=forms.HiddenInput, required=False)
    reason = forms.CharField(
        label=_('Motif du retard'),
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': _('Décrivez la raison du retard…')}),
    )
    document = forms.FileField(
        label=_('Pièce justificative (optionnel)'),
        required=False,
    )

    def clean_reason(self):
        reason = (self.cleaned_data.get('reason') or '').strip()
        if len(reason) < 10:
            raise forms.ValidationError(_('Le motif doit contenir au moins 10 caractères.'))
        return reason
