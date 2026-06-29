from dal import autocomplete

from core.models.fields import ChoiceField

from .countries import COUNTRY_CHOICES, DEFAULT_COUNTRY


class CountryChoiceField(ChoiceField):
    """Select pays (ListSelect2) — nationalité / pays d'origine."""

    LEGACY_ALIASES = {
        'congolaise': DEFAULT_COUNTRY,
        'rdc': DEFAULT_COUNTRY,
        'rd congo': DEFAULT_COUNTRY,
        'congo (rdc)': DEFAULT_COUNTRY,
        'congo': DEFAULT_COUNTRY,
        'republique democratique du congo': DEFAULT_COUNTRY,
        'république démocratique du congo': DEFAULT_COUNTRY,
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', COUNTRY_CHOICES)
        kwargs.setdefault('max_length', 100)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = autocomplete.ListSelect2(
            attrs={
                'data-minimum-input-length': 0,
                'theme': 'bootstrap-5',
            },
        )
        return super(ChoiceField, self).formfield(**kwargs)

    @classmethod
    def normalize(cls, value):
        if value in (None, ''):
            return value
        text = str(value).strip()
        if not text:
            return None
        alias = cls.LEGACY_ALIASES.get(text.casefold())
        return alias or text
