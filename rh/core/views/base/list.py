from core.filters import filter_set_factory
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.shortcuts import render
from django.apps import apps
from django.db.models import Count, Q
from datetime import date, timedelta
from .base import BaseView


class List(BaseView):
    qs = None
    action = ["view"]
    template_name = "list.html"

    AGE_RANGES = (
        ('18-25', 18, 25, '18 - 25 ans'),
        ('26-35', 26, 35, '26 - 35 ans'),
        ('36-45', 36, 45, '36 - 45 ans'),
        ('46-60', 46, 60, '46 - 60 ans'),
        ('60+', 60, None, '60+ ans'),
    )

    @staticmethod
    def _years_ago(years):
        today = date.today()
        target_year = today.year - years
        try:
            return today.replace(year=target_year)
        except ValueError:
            # 29 février -> 28 février si l'année cible n'est pas bissextile
            return today.replace(year=target_year, day=28)

    @classmethod
    def _age_range_dates(cls, key):
        for range_key, min_age, max_age, _ in cls.AGE_RANGES:
            if range_key != key:
                continue
            latest_birth = cls._years_ago(min_age)
            if max_age is None:
                return None, latest_birth
            # N ans <= age <= M ans => dob in [today-(M+1y)+1d, today-Ny]
            lower = cls._years_ago(max_age + 1) + timedelta(days=1)
            return lower, latest_birth
        return None, None

    def get(self, request, app, model):
        try:
            model = apps.get_model(app, model_name=model)
        except LookupError:
            from django.http import Http404
            raise Http404(f"Le modèle {app}.{model} n'existe pas.")

        if hasattr(model, 'list_url'):
            return redirect(getattr(model, 'list_url'))

        list_filter = getattr(model, 'list_filter', [])
        list_display = [field for field in model._meta.fields if field.name in getattr(model, 'list_display', [])]
        
        self.qs = model.objects.select_related().prefetch_related()#.order_by('-created_at')
        try:
            # Cas spécial pour Employee: si l'utilisateur est un employé normal, filtrer pour son employé
            if model._meta.label == 'employee.Employee' and not request.user.is_superuser and not request.user.is_staff:
                if request.user.employee:
                    self.qs = self.qs.filter(id=request.user.employee.id)
                else:
                    self.qs = self.qs.none()
            else:
                self.qs = self.qs.all(user=request.user)
        except Exception:
            self.qs = self.qs.all()
        
        # Hard filter
        query = {k:v for k, v in request.GET.dict().items() if v}
        fields = [field.name for field in model._meta.fields if field.name]
        self.qs = self.qs.filter(**{k:v for k, v in query.items() if k.split("__")[0] in fields})

        # Soft filter
        qs_filter = filter_set_factory(model, fields=list_filter)
        qs_filter = qs_filter(request.GET, queryset=self.qs)
        self.qs = qs_filter.qs.order_by('-id')

        if model._meta.label == 'employee.Employee':
            self.qs = self.qs.select_related(
                'designation', 'direction', 'service', 'agreement', 'branch'
            )

            age_filter = (request.GET.get('age_range') or '').strip()
            if age_filter:
                start_birth, end_birth = self._age_range_dates(age_filter)
                if start_birth and end_birth:
                    self.qs = self.qs.filter(date_of_birth__range=(start_birth, end_birth))
                elif end_birth:
                    self.qs = self.qs.filter(date_of_birth__lte=end_birth)

            gender_filter = (request.GET.get('gender') or '').strip()
            if gender_filter:
                self.qs = self.qs.filter(gender=gender_filter)

            study_level_filter = (request.GET.get('study_level') or '').strip()
            if study_level_filter:
                self.qs = self.qs.filter(education__study_level_id=study_level_filter)

            field_of_study_filter = (request.GET.get('field_of_study') or '').strip()
            if field_of_study_filter:
                self.qs = self.qs.filter(education__field_of_study_id=field_of_study_filter)

            province_filter = (request.GET.get('home_province') or '').strip()
            if province_filter:
                self.qs = self.qs.filter(home_province_id=province_filter)

            situation_filter = (request.GET.get('agent_situation') or '').strip()
            if situation_filter:
                self.qs = self.qs.filter(agent_situation=situation_filter)

            self.qs = self.qs.distinct()

            StudyLevel = apps.get_model('employee', 'StudyLevel')
            FieldOfStudy = apps.get_model('employee', 'FieldOfStudy')
            study_levels = list(
                StudyLevel.objects.order_by('sort_order', 'name').values('id', 'name')
            )
            field_of_studies = list(
                FieldOfStudy.objects.order_by('sort_order', 'name').values('id', 'name')
            )
            Province = apps.get_model('employee', 'Province')
            provinces = Province.objects.order_by('name').values('id', 'name')
            age_ranges = [
                {'key': key, 'label': label}
                for key, _min_age, _max_age, label in self.AGE_RANGES
            ]
            age_labels = {key: label for key, _min_age, _max_age, label in self.AGE_RANGES}
            province_label_map = {str(p['id']): p['name'] for p in provinces}
            study_level_label_map = {str(item['id']): item['name'] for item in study_levels}
            field_of_study_label_map = {str(item['id']): item['name'] for item in field_of_studies}
            gender_labels = {'male': 'Masculin', 'female': 'Féminin'}
            situation_labels = {'active': 'Actif', 'inactive': 'Inactif'}

            dashboard_counts = self.qs.aggregate(
                total=Count('id', distinct=True),
                active=Count('id', filter=Q(agent_situation='active'), distinct=True),
                inactive=Count('id', filter=Q(agent_situation='inactive'), distinct=True),
                male=Count('id', filter=Q(gender='male'), distinct=True),
                female=Count('id', filter=Q(gender='female'), distinct=True),
            )
            if age_filter:
                dashboard_counts['age_range_label'] = age_labels.get(age_filter, age_filter)
                dashboard_counts['age_range_total'] = dashboard_counts['total']

            active_filter_labels = []
            if (request.GET.get('q') or '').strip():
                active_filter_labels.append(('Q', request.GET.get('q').strip()))
            if age_filter:
                active_filter_labels.append(('Âge', age_labels.get(age_filter, age_filter)))
            if gender_filter:
                active_filter_labels.append(('Sexe', gender_labels.get(gender_filter, gender_filter)))
            if study_level_filter:
                active_filter_labels.append((
                    'Niveau',
                    study_level_label_map.get(study_level_filter, study_level_filter).upper(),
                ))
            if field_of_study_filter:
                active_filter_labels.append((
                    'Domaine',
                    field_of_study_label_map.get(field_of_study_filter, field_of_study_filter).upper(),
                ))
            if province_filter:
                active_filter_labels.append(('Province', province_label_map.get(province_filter, province_filter)))
            if situation_filter:
                active_filter_labels.append(('Statut', situation_labels.get(situation_filter, situation_filter)))

        paginator = Paginator(self.qs, 25)
        page_num = request.GET.get('page', 1)
        try:
            page_num = max(1, int(page_num))
        except (TypeError, ValueError):
            page_num = 1
        page_obj = paginator.get_page(page_num)

        app_label = model._meta.app_label
        model_name = model._meta.model_name
        add_perm = f'{app_label}.add_{model_name}'
        show_create_button = (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.has_perm(add_perm)
        )
        if not request.user.is_superuser and not request.user.is_staff:
            if model._meta.label == 'mission.Mission':
                show_create_button = False

        page_title = getattr(model, 'agent_list_title', None)

        return render(
            request,
            getattr(model, 'change_list_template', self.template_name),
            locals(),
        )