from django.utils.translation import gettext as _
from django.db import models

from core.models.fields import AceField, ModelSelect2Multiple
from django.template import Context, Template
from core.models import Base

from crispy_forms.layout import Layout, Row, Column


class Widget(Base):
    name = models.CharField(verbose_name=_('nom'), max_length=100)
    description = models.CharField(verbose_name=_('description'), max_length=250)

    permissions = ModelSelect2Multiple('auth.permission', verbose_name=_('permissions'))
    template = AceField(mode='html', verbose_name=_('template'))
    view = AceField(mode='python', verbose_name=_('view'))

    list_display = ('id', 'name', 'description', 'updated_at')
    layout = Layout(
        Row(
            Column('name', css_class='col-md-6'),
            Column('description', css_class='col-md-6'),
        ),
        'permissions',
        Row(
            Column('template', css_class='col-md-6'),
            Column('view', css_class='col-md-6'),
        ),
    )

    def render(self, request=None):
        template = Template(self.template)
        context_vars = {'request': request}
        exec(self.view, globals(), context_vars)
        return template.render(Context(context_vars))

    class Meta:
        verbose_name = _('widget')
        verbose_name_plural = _('widgets')