from core.utils import upload_directory_file
from .employee import Employee
from .education_references import Degree, FieldOfStudy, Institution, StudyLevel
from core.models import Base

from django.utils.translation import gettext as _
from core.models.fields import ModelSelect
from core.models.fields import DateField
from django.db import models


class Education(Base):
    employee = ModelSelect(Employee, verbose_name=_('employé'), null=True, on_delete=models.SET_NULL)

    institution = ModelSelect(Institution, verbose_name=_('établissement'), null=True, blank=True, on_delete=models.SET_NULL)
    degree = ModelSelect(Degree, verbose_name=_('diplôme'), null=True, blank=True, on_delete=models.SET_NULL)
    study_level = ModelSelect(StudyLevel, verbose_name=_('niveau d\'étude'), null=True, blank=True, on_delete=models.SET_NULL)
    field_of_study = ModelSelect(FieldOfStudy, verbose_name=_('domaine'), null=True, blank=True, on_delete=models.SET_NULL)
    diploma_year = models.PositiveSmallIntegerField(
        _('année d\'obtention du diplôme'),
        blank=True,
        null=True,
        default=None,
    )

    start_date = DateField(_('date de début'), blank=True, null=True, default=None)
    end_date = DateField(_('date de fin'), blank=True, null=True, default=None)

    photo = models.ImageField(_('photo'), upload_to=upload_directory_file, blank=True, null=True, default=None)

    list_display = [
        'employee',
        'institution',
        'study_level',
        'field_of_study',
        'diploma_year',
        'degree',
        'start_date',
        'end_date',
    ]
    inline_form_fields = [
        'institution',
        'study_level',
        'field_of_study',
        'diploma_year',
        'degree',
        'start_date',
        'end_date',
    ]

    @property
    def name(self):
        parts = [self.study_level, self.field_of_study, self.degree]
        label = ' — '.join(str(part) for part in parts if part)
        return label or str(self.institution or self.pk)

    class Meta:
        verbose_name = _('education')
        verbose_name_plural = _('educations')
