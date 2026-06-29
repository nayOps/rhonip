from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy
from .fields import ModelSelect2Single
from crispy_forms.layout import Layout, Row, Column

from core.models.managers import UserManager
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    first_name, last_name = None, None

    employee = ModelSelect2Single('employee.Employee', verbose_name=_('employé'), on_delete=models.CASCADE, blank=True, null=True, default=None)
    date_joined = models.DateTimeField(_('date d\'inscription'), default=timezone.now)
    
    email = models.EmailField(unique=True, db_index=True, verbose_name=_('email'))
    password = models.CharField(_('mot de passe'), max_length=128, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    list_display = ('id', 'employee', 'email', 'is_active')
    search_fields = ('id', 'email',)
    list_filter = ('is_active',)
    
    layout = Layout(
        Row(
            Column('employee'),
            Column('email')
        ),
        Row(
            Column('user_permissions'),
            Column('groups')
        ),
        Row(
            Column('is_staff'),
            Column('is_active'),
            Column('is_superuser')
        )
    )

    def __str__(self):
        if not self.employee: return self.email
        return self.employee.name

    @property
    def name(self):
        return str(self)

    def get_full_name(self):
        return self.name

    def get_absolute_url(self):
        meta = self._meta
        return reverse_lazy('core:change', kwargs={'app': meta.app_label, 'model': meta.model_name, 'pk': self.pk})