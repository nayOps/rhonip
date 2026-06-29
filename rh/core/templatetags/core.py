import re

import urllib

from django import template

from django.utils.safestring import mark_safe



digital_value = re.compile(r"^\d+$")

register = template.Library()





@register.filter('getattr')

def getattribute(value, arg):

    if hasattr(value, str(arg)):

        return getattr(value, arg)

    elif hasattr(value, 'get') and value.get(arg):

        return value[arg]

    elif digital_value.match(str(arg)) and len(value) > int(arg):

        return value[int(arg)]

    return None





@register.filter('urlencode')

def urlencode(value):

    value = {k: v for k, v in value.items() if v}

    return urllib.parse.urlencode(value)





@register.filter('toint')

def toint(value):

    return int(value or 0)





@register.filter('has_perm')

def has_perm_filter(user, permission):

    """Filtre pour vérifier les permissions d'un utilisateur dans les templates"""

    if not user or not user.is_authenticated:

        return False

    return user.has_perm(permission)





@register.simple_tag(takes_context=True)

def query_transform(context, **kwargs):

    query = context['request'].GET.copy()

    for key, value in kwargs.items():

        if value is None:

            query.pop(key, None)

        else:

            query[key] = str(value)

    return query.urlencode()





@register.filter

def employee_initials(employee):

    if not employee:

        return '?'

    first = (employee.first_name or '').strip()[:1]

    last = (employee.last_name or '').strip()[:1]

    text = f'{first}{last}'.upper()

    return text or '?'





@register.filter

def employee_email(employee):

    if not employee:

        return '—'

    return employee.email_professional or employee.email or '—'





@register.simple_tag(takes_context=True)

def render_widget(context, widget):

    """Rend un widget avec le contexte de la requête"""

    request = context.get('request')

    return mark_safe(widget.render(request=request))

