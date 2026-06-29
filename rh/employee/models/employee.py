from crispy_forms.layout import Layout, Row, Column, Div, Fieldset, HTML
from phonenumber_field.modelfields import PhoneNumberField

from crispy_forms.bootstrap import PrependedText
from django.utils.translation import gettext as _
from core.models.fields import ModelSelect
from core.models.fields import CascadeModelSelect
from core.models.fields import DateField
from django.urls import reverse_lazy
from django.db import models
from django.apps import apps

from .designation import Designation
from .agreement import Agreement
from .grade import Grade
from employee.choices.countries import DEFAULT_COUNTRY
from employee.choices.country_field import CountryChoiceField

from .sub_direction import SubDirection
from .direction import Direction
from .service import Service

from core.models import Base
from datetime import date

from random import randint

default_photo = lambda: "place_pics/default_pic.jpg"

default_registration_number = lambda: randint(100000000, 999999999)

class IdCardType(models.TextChoices):
    DRIVER_LICENSE = 'driver_license', _('permis de conduire')
    VOTE_CARD = 'voter\'s card', _('carte d\'électeur')
    NATIONAL_ID = 'national_id', _('national id')
    PASSPORT = 'passport', _('passeport')
    DOCUMENT = 'document', _('document')
    OTHER = 'other', _('other')

class Employee(Base):
    GENDERS = (('male', _('masculin')), ('female', _('féminin')))

    MARITAl_STATUS = (
        ('maried', _('marié(e)')),
        ('single', _('célibataire')),
        ('divorced', _('divorcé(e)')),
    )

    AGENT_SITUATION = (
        ('active', _('actif')),
        ('inactive', _('inactif')),
    )
    PAYMENT_METHODS = (('cash', _('cash')), ('bank', _('banque')), ('mobile money', _('mobile money')))

    registration_number = models.CharField(
        _('matricule'), max_length=50, unique=True, blank=True, null=True, default=None
    )
    social_security_number = models.CharField(_('numéro de sécurité sociale'), max_length=50, blank=True, null=True, default=None)
    
    agreement = ModelSelect(
        Agreement,
        verbose_name=_('type de contrat'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        autocomplete_min_length=0,
    )
    date_of_join = DateField(_('date d\'engagement'), blank=True, null=True, default=None)
    onip_start_date = DateField(_('date début de travail ONIP'), blank=True, null=True, default=None)
    photo = models.ImageField(_('photo'), blank=True, null=True)

    designation = ModelSelect(Designation, verbose_name=_('position'), blank=True, null=True, on_delete=models.SET_NULL, autocomplete_min_length=0)
    branch = ModelSelect(
        'employee.Branch', verbose_name=_('site'), blank=True, null=True, on_delete=models.SET_NULL, default=None,
        autocomplete_min_length=0,
    )
    grade = ModelSelect(Grade, verbose_name=_('grade'), blank=True, null=True, on_delete=models.SET_NULL, autocomplete_min_length=0)

    direction = ModelSelect(
        Direction,
        verbose_name=_('direction'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
        autocomplete_min_length=0,
    )
    sub_direction = ModelSelect(SubDirection, verbose_name=_('sous-direction'), blank=True, null=True, on_delete=models.SET_NULL, default=None, autocomplete_min_length=0)
    service = ModelSelect(Service, verbose_name=_('service'), blank=True, null=True, on_delete=models.SET_NULL, default=None, autocomplete_min_length=0)

    first_name = models.CharField(_('prénom'), max_length=100, blank=True, null=True, default=None)
    middle_name = models.CharField(_('post-nom'), max_length=100, blank=True, null=True, default=None)
    last_name = models.CharField(_('nom'), max_length=100, blank=True, null=True, default=None)

    gender = models.CharField(
        _('genre'), max_length=10, choices=GENDERS, blank=True, null=True, default=None
    )
    date_of_birth = DateField(_('date de naissance'), blank=True, null=True, default=None)
    place_of_birth = models.CharField(_('lieu de naissance'), max_length=100, blank=True, null=True, default=None)

    citizenship = CountryChoiceField(
        _('nationalité'),
        blank=True,
        null=True,
        default=DEFAULT_COUNTRY,
    )
    home_country = CountryChoiceField(
        _('pays d\'origine'),
        blank=True,
        null=True,
        default=DEFAULT_COUNTRY,
    )
    home_province = ModelSelect(
        'employee.Province',
        verbose_name=_('province d\'origine'),
        autocomplete_min_length=0,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )
    home_territory = CascadeModelSelect(
        'employee.Territory',
        verbose_name=_('territoire d\'origine'),
        forward_fields=[('home_province', 'province')],
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )
    home_sector = CascadeModelSelect(
        'employee.Sector',
        verbose_name=_('secteur d\'origine'),
        forward_fields=[('home_territory', 'territory')],
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )
    home_groupement = CascadeModelSelect(
        'employee.Groupement',
        verbose_name=_('groupement d\'origine'),
        forward_fields=[('home_sector', 'sector')],
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )
    home_village = CascadeModelSelect(
        'employee.Village',
        verbose_name=_('village d\'origine'),
        forward_fields=[
            ('home_groupement', 'groupement'),
            ('home_sector', 'sector'),
            ('home_territory', 'territory'),
            ('home_province', 'province'),
        ],
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )

    type_of_identity = models.CharField(
        _('type de pièce d\'identité'),
        max_length=100,
        choices=IdCardType.choices,
        blank=True,
        null=True,
        default=None,
    )
    identity_number = models.CharField(_('numéro de pièce d\'identité'), max_length=100, blank=True, null=True, default=None)

    date_of_issue = DateField(_('date de délivrance'), blank=True, null=True, default=None)
    date_of_expiry = DateField(_('date d\'expiration'), blank=True, null=True, default=None)
    place_of_issue = models.CharField(_('lieu de délivrance'), max_length=100, blank=True, null=True, default=None)

    marital_status = models.CharField(
        _('état civil'), max_length=12, choices=MARITAl_STATUS, blank=True, null=True, default=None
    )
    spouse = models.CharField(_('conjoint'), max_length=100, blank=True, null=True, default=None)

    telephone_number = PhoneNumberField(
        _('numéro de téléphone professional'), blank=True, null=True, default=None
    )
    mobile_number = PhoneNumberField(
        _('numéro de téléphone mobile'), blank=True, null=True, default=None
    )
    
    email_professional = models.EmailField(_('email professional'), blank=True, null=True, default=None)
    email = models.EmailField(_('email'), blank=True, null=True, default=None)

    appointment_letter = models.FileField(_('lettre de nomination'), upload_to='employee/appointment_letter', blank=True, null=True, default=None)
    appointment_number = models.CharField(_('numéro de nomination'), max_length=50, blank=True, null=True, default=None)

    physical_address = models.TextField(_('adresse physique'), blank=True, null=True, default=None)
    emergency_information = models.TextField(
        _('informations d\'urgence'), blank=True, null=True, default=None
    )

    emergency_contact = models.CharField(_('contact d\'urgence'), max_length=50, blank=True, null=True, default=None)
    emergency_phone = PhoneNumberField(
        _('numéro de téléphone d\'urgence'), blank=True, null=True, default=None
    )
    relationship = models.CharField(_('relation'), max_length=50, blank=True, null=True, default=None)

    refering_doctor = models.CharField(_('médecin référent'), max_length=50, blank=True, null=True, default=None)
    refering_doctor_phone = PhoneNumberField(
        _('numéro de téléphone du médecin référent'), blank=True, null=True, default=None
    )
    refering_doctor_email = models.EmailField(_('email du médecin référent'), blank=True, null=True, default=None)

    payment_account = models.CharField(_('numéro de compte'), max_length=50, blank=True, null=True, default=None)
    payment_method = models.CharField(
        _('mode de paiement'), max_length=20, choices=PAYMENT_METHODS, blank=True, null=True, default=None
    )
    payer_name = models.CharField(
        _('nom du payeur'), max_length=50, blank=True, null=True, default=None
    )

    comment = models.TextField(_('commentaire'), blank=True, null=True, default=None)
    agent_situation = models.CharField(
        _('situation de l\'agent'),
        max_length=10,
        choices=AGENT_SITUATION,
        default='inactive',
    )

    list_filter = (
        'agreement', 'date_of_join', 'direction', 'branch', 'designation', 'gender',
        'marital_status', 'branch', 'agent_situation',
    )
    list_display = ('id', 'last_name', 'middle_name', 'designation', 'service', 'agent_situation')
    search_fields = (
        'registration_number',
        'first_name',
        'middle_name',
        'last_name',
        'email',
        'email_professional',
        'telephone_number',
        'mobile_number',
    )

    inlines = ['employee.child', 'employee.education', 'employee.experience', 'employee.document']

    layout = Layout(
        Fieldset(
            _('Identité personnelle'),
            Div('photo', css_class='onip-form-section-photo'),
            Row(
                Column('registration_number', css_class='col-md-6'),
                Column('social_security_number', css_class='col-md-6'),
            ),
            Row(
                Column('branch', css_class='col-md-3'),
                Column('agreement', css_class='col-md-3'),
                Column('date_of_join', css_class='col-md-3'),
                Column('onip_start_date', css_class='col-md-3'),
            ),
            Row(
                Column('direction', css_class='col-md-4'),
                Column('sub_direction', css_class='col-md-4'),
                Column('service', css_class='col-md-4'),
            ),
            Row(
                Column('grade', css_class='col-md-6'),
                Column('designation', css_class='col-md-6'),
            ),
            Row(
                Column('first_name', css_class='col-md-4'),
                Column('middle_name', css_class='col-md-4'),
                Column('last_name', css_class='col-md-4'),
            ),
            Row(
                Column('gender', css_class='col-md-4'),
                Column('date_of_birth', css_class='col-md-4'),
                Column('place_of_birth', css_class='col-md-4'),
            ),
            Row(
                Column('citizenship', css_class='col-md-6'),
                Column('home_country', css_class='col-md-6'),
            ),
            Div(
                Row(
                    Column('home_province', css_class='col-md-4'),
                ),
                Row(
                    Column('home_territory', css_class='col-md-3'),
                    Column('home_sector', css_class='col-md-3'),
                    Column('home_groupement', css_class='col-md-3'),
                    Column('home_village', css_class='col-md-3'),
                ),
                css_id='employee-geography-section',
                css_class='employee-geography-section',
            ),
            Row(
                Column('type_of_identity', css_class='col-md-6'),
                Column('identity_number', css_class='col-md-6'),
            ),
            Row(
                Column('date_of_issue', css_class='col-md-4'),
                Column('date_of_expiry', css_class='col-md-4'),
                Column('place_of_issue', css_class='col-md-4'),
            ),
            Row(
                Column('appointment_letter', css_class='col-md-6'),
                Column('appointment_number', css_class='col-md-6'),
            ),
            Row(
                Column('marital_status', css_class='col-md-6'),
                Column('spouse', css_class='col-md-6'),
            ),
            css_class='onip-form-section',
        ),
        Fieldset(
            _('Coordonnées & contacts d\'urgence'),
            HTML('<div class="onip-form-subsection-label">Communication</div>'),
            Row(
                Div(PrependedText('telephone_number', '+', active=True), css_class='col-md-6'),
                Div(PrependedText('mobile_number', '+', active=True), css_class='col-md-6'),
            ),
            Row(
                Div(PrependedText('email_professional', '@', active=True), css_class='col-md-6'),
                Div(PrependedText('email', '@', active=True), css_class='col-md-6'),
            ),
            'physical_address',
            HTML('<div class="onip-form-subsection-label">Urgence & médical</div>'),
            'emergency_information',
            Row(
                Column('emergency_contact', css_class='col-md-4'),
                Column('emergency_phone', css_class='col-md-4'),
                Column('relationship', css_class='col-md-4'),
            ),
            Row(
                Column('refering_doctor', css_class='col-md-4'),
                Column('refering_doctor_phone', css_class='col-md-4'),
                Column('refering_doctor_email', css_class='col-md-4'),
            ),
            css_class='onip-form-section',
        ),
        Fieldset(
            _('Paiement & bancaire'),
            Row(
                Column('payment_method', css_class='col-md-4'),
                Column('payer_name', css_class='col-md-4'),
                Column('payment_account', css_class='col-md-4'),
            ),
            css_class='onip-form-section',
        ),
        Fieldset(
            _('Notes & commentaires'),
            'comment',
            Row(
                Column('agent_situation', css_class='col-md-6'),
            ),
            css_class='onip-form-section',
        ),
    )

    def save(self, *args, **kwargs):
        if not self.registration_number:
            import uuid

            self.registration_number = f'ONIP-{uuid.uuid4().hex[:12].upper()}'
        super().save(*args, **kwargs)

    def full_name(self):
        return f"{self.last_name} {self.middle_name}, {self.first_name}"
    
    def short_name(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def name(self):
        return self.short_name()
    
    def get_absolute_url(self):
        return reverse_lazy("employee:change", kwargs={"pk": self.pk})
    
    # To Do : Improve this method to filter according to range of period
    def attendances(self, period=None):
        period = period if period else date.today()
        Attendance = apps.get_model('employee', model_name='attendance')
        attendances = Attendance.objects.filter(employee=self)
        attendances = attendances.filter(employee=self, date__year=period.year)
        attendances = attendances.filter(direction='OUT').values('employee', 'date')
        attendances = attendances.values('date').annotate(count=models.Count('employee'))
        return list(attendances)
    
    def create_user(self, password=None):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        email = (self.email_professional or self.email or '').strip()
        matricule = (self.registration_number or '').strip()
        if not email or not matricule:
            return None

        user = User.objects.filter(employee=self).first()
        if user is None:
            user = User.objects.filter(email__iexact=email).first()
        if user:
            if not user.employee_id:
                user.employee = self
                user.save(update_fields=['employee'])
            return user

        return User.objects.create_user(
            email=email,
            password=password or matricule,
            employee=self,
            is_active=True,
        )

    class Meta:
        verbose_name = _('employé')
        verbose_name_plural = _('employés')