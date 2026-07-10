import re
import unicodedata

from employee.choices.education_catalog import (
    AUTRE_CODE,
    AUTRES_CODE,
    DEGREE_ALIASES,
    DEGREES,
    FIELD_OF_STUDY_ALIASES,
    FIELDS_OF_STUDY,
    INSTITUTION_ALIASES,
    INSTITUTIONS_OTHER,
    INSTITUTIONS_PRIVATE,
    INSTITUTIONS_PUBLIC,
    STUDY_LEVEL_ALIASES,
    STUDY_LEVELS,
)

_FRENCH_PARTICLES = frozenset({'de', 'du', 'des', 'le', 'la', 'les', 'et', 'au', 'en', 'd'})


def normalize_lookup_key(value):
    if not value:
        return ''
    text = unicodedata.normalize('NFD', str(value).strip().lower())
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return ' '.join(text.split())


def slugify_code(label, max_length=50):
    text = unicodedata.normalize('NFD', str(label).strip())
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    text = re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').upper()
    if not text:
        text = 'VALEUR'
    return text[:max_length]


def normalize_display_name(raw):
    text = ' '.join(str(raw or '').split())
    if not text:
        return text
    words = text.title().split()
    normalized = []
    for index, word in enumerate(words):
        lower = word.lower()
        if index > 0 and lower in _FRENCH_PARTICLES:
            normalized.append(lower)
        else:
            normalized.append(word)
    return ' '.join(normalized)


def ensure_unique_code(model, base_code):
    code = base_code[:50] or 'VALEUR'
    if not model.objects.filter(code=code).exists():
        return code
    suffix = 2
    while model.objects.filter(code=f'{code}_{suffix}'[:50]).exists():
        suffix += 1
    return f'{code}_{suffix}'[:50]


def _get_model(model_or_label, apps=None):
    if isinstance(model_or_label, str):
        app_label, model_name = model_or_label.split('.')
        if apps is not None:
            return apps.get_model(app_label, model_name)
        from django.apps import apps as django_apps
        return django_apps.get_model(app_label, model_name)
    return model_or_label


def _alias_map_for_model(model_label):
    if model_label == 'employee.studylevel':
        return STUDY_LEVEL_ALIASES
    if model_label == 'employee.degree':
        return DEGREE_ALIASES
    if model_label == 'employee.fieldofstudy':
        return FIELD_OF_STUDY_ALIASES
    if model_label == 'employee.institution':
        return INSTITUTION_ALIASES
    return {}


def resolve_reference(model_or_label, raw_value, *, apps=None, create_if_missing=True):
    model = _get_model(model_or_label, apps=apps)
    if raw_value in (None, ''):
        return None

    if hasattr(raw_value, 'pk'):
        return raw_value

    raw = str(raw_value).strip()
    if not raw:
        return None

    lookup_key = normalize_lookup_key(raw)
    if lookup_key in ('autres', 'autre', 'other'):
        return model.objects.filter(code__in=(AUTRES_CODE, AUTRE_CODE)).order_by('sort_order').first()

    alias_code = _alias_map_for_model(model._meta.label_lower).get(lookup_key)
    if alias_code:
        found = model.objects.filter(code=alias_code).first()
        if found:
            return found

    code = slugify_code(raw)
    found = model.objects.filter(code=code).first()
    if found:
        return found

    found = model.objects.filter(name__iexact=raw).first()
    if found:
        return found

    display_name = normalize_display_name(raw)
    found = model.objects.filter(name__iexact=display_name).first()
    if found:
        return found

    if not create_if_missing:
        return None

    extra_fields = {}
    if model._meta.label_lower == 'employee.institution':
        extra_fields['institution_type'] = 'other'

    return model.objects.create(
        code=ensure_unique_code(model, code),
        name=display_name or raw,
        is_system=False,
        sort_order=9000,
        **extra_fields,
    )


def seed_reference_rows(model_or_label, rows, *, apps=None, extra_defaults=None):
    model = _get_model(model_or_label, apps=apps)
    extra_defaults = extra_defaults or {}
    for code, name, sort_order in rows:
        model.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'sort_order': sort_order,
                'is_system': True,
                **extra_defaults,
            },
        )


def seed_all_references(*, apps=None):
    seed_reference_rows('employee.StudyLevel', STUDY_LEVELS, apps=apps)
    seed_reference_rows('employee.Degree', DEGREES, apps=apps)
    seed_reference_rows('employee.FieldOfStudy', FIELDS_OF_STUDY, apps=apps)
    seed_reference_rows(
        'employee.Institution',
        INSTITUTIONS_PUBLIC,
        apps=apps,
        extra_defaults={'institution_type': 'public'},
    )
    seed_reference_rows(
        'employee.Institution',
        INSTITUTIONS_PRIVATE,
        apps=apps,
        extra_defaults={'institution_type': 'private'},
    )
    seed_reference_rows(
        'employee.Institution',
        INSTITUTIONS_OTHER,
        apps=apps,
        extra_defaults={'institution_type': 'other'},
    )


def migrate_education_char_to_fk(*, apps):
    Education = apps.get_model('employee', 'Education')
    StudyLevel = apps.get_model('employee', 'StudyLevel')
    Degree = apps.get_model('employee', 'Degree')
    FieldOfStudy = apps.get_model('employee', 'FieldOfStudy')
    Institution = apps.get_model('employee', 'Institution')

    for education in Education.objects.all().iterator():
        updates = {}
        legacy_study_level = getattr(education, 'study_level_legacy', None)
        legacy_degree = getattr(education, 'degree_legacy', None)
        legacy_field = getattr(education, 'field_of_study_legacy', None)
        legacy_institution = getattr(education, 'institution_legacy', None)

        if legacy_study_level:
            updates['study_level_ref_id'] = resolve_reference(
                StudyLevel, legacy_study_level, apps=apps, create_if_missing=True,
            ).pk
        if legacy_degree:
            updates['degree_ref_id'] = resolve_reference(
                Degree, legacy_degree, apps=apps, create_if_missing=True,
            ).pk
        if legacy_field:
            updates['field_of_study_ref_id'] = resolve_reference(
                FieldOfStudy, legacy_field, apps=apps, create_if_missing=True,
            ).pk
        if legacy_institution:
            updates['institution_ref_id'] = resolve_reference(
                Institution, legacy_institution, apps=apps, create_if_missing=True,
            ).pk

        if updates:
            Education.objects.filter(pk=education.pk).update(**updates)


def is_autres_code(code):
    return code in (AUTRES_CODE, AUTRE_CODE)


def get_autres_pk(model_or_label, *, apps=None):
    model = _get_model(model_or_label, apps=apps)
    codes = (AUTRES_CODE, AUTRE_CODE)
    row = model.objects.filter(code__in=codes).order_by('sort_order').first()
    return row.pk if row else None
