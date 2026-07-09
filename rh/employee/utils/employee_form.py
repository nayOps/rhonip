"""Configuration formulaire employé (champs admin / layout)."""
from __future__ import annotations

from crispy_forms.layout import Column, Div, Field, Fieldset, HTML, Layout, Row

ADMIN_ONLY_EMPLOYEE_FIELDS = frozenset({'agent_situation'})

# Modifiables uniquement par admin/staff sur fiche employé existante.
ADMIN_ONLY_EDITABLE_EMPLOYEE_FIELDS = frozenset({
    'registration_number',
    'designation',
    'email_professional',
})


def is_employee_admin(user) -> bool:
    return bool(user and (user.is_superuser or user.is_staff))


def _filter_layout_node(node, exclude_names: frozenset):
    if isinstance(node, str):
        return None if node in exclude_names else node

    if isinstance(node, Field):
        name = node.fields[0] if node.fields else None
        return None if name in exclude_names else node

    if isinstance(node, HTML):
        return node

    if isinstance(node, (Layout, Fieldset, Row, Column, Div)):
        kept = []
        for child in node.fields:
            filtered = _filter_layout_node(child, exclude_names)
            if filtered is None:
                continue
            if isinstance(filtered, (Row, Column, Div, Fieldset)) and not filtered.fields:
                continue
            kept.append(filtered)
        if not kept:
            return None
        kwargs = {}
        if getattr(node, 'css_class', None):
            kwargs['css_class'] = node.css_class
        if getattr(node, 'css_id', None):
            kwargs['css_id'] = node.css_id
        return type(node)(*kept, **kwargs)

    return node


def layout_without_fields(layout: Layout, exclude_names: frozenset) -> Layout:
    filtered = _filter_layout_node(layout, exclude_names)
    return filtered if isinstance(filtered, Layout) else Layout(*([] if filtered is None else [filtered]))


def get_employee_form_config(model, user):
    admin = is_employee_admin(user)
    layout = model.layout if admin else layout_without_fields(model.layout, ADMIN_ONLY_EMPLOYEE_FIELDS)
    field_names = [field.name for field in layout.get_field_names()]
    if not admin:
        field_names = [name for name in field_names if name not in ADMIN_ONLY_EMPLOYEE_FIELDS]
    return layout, field_names
