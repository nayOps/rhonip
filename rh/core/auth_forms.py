from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class EmployeeAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_('E-mail professionnel ou matricule'),
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'placeholder': 'prenom.nom@onip.gouv.cd',
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].label = _('Mot de passe')
        self.fields['password'].widget.attrs.setdefault(
            'placeholder',
            _('Matricule ou mot de passe personnel'),
        )
