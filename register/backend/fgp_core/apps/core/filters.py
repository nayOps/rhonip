"""
Filtres pour l'application Core
"""
import django_filters
from django.db.models import Q
from .models import PersonCore, StrataMembership, Document


class PersonCoreFilter(django_filters.FilterSet):
    """
    Filtres pour PersonCore
    """
    # Filtres de base
    nom = django_filters.CharFilter(lookup_expr='icontains')
    prenom = django_filters.CharFilter(lookup_expr='icontains')
    postnom = django_filters.CharFilter(lookup_expr='icontains')
    nin = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtres géographiques
    province_residence = django_filters.CharFilter(lookup_expr='icontains')
    territoire_residence = django_filters.CharFilter(lookup_expr='icontains')
    commune_residence = django_filters.CharFilter(lookup_expr='icontains')
    quartier_residence = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtres de naissance
    province_naissance = django_filters.CharFilter(lookup_expr='icontains')
    lieu_naissance = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtres de contact
    telephone = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    # Filtres de date
    date_naissance_after = django_filters.DateFilter(field_name='date_naissance', lookup_expr='gte')
    date_naissance_before = django_filters.DateFilter(field_name='date_naissance', lookup_expr='lte')
    
    # Filtres de création
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Filtres par strate
    strate = django_filters.CharFilter(method='filter_by_strate')
    
    # Recherche globale
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = PersonCore
        fields = {
            'sexe': ['exact'],
            'nationalite': ['exact'],
            'statut_matrimonial': ['exact'],
            'niveau_etude': ['exact'],
            'type_piece_identite': ['exact'],
        }
    
    def filter_by_strate(self, queryset, name, value):
        """Filtrer par strate active"""
        return queryset.filter(
            strata_memberships__strate_code=value,
            strata_memberships__status='ACTIVE'
        ).distinct()
    
    def filter_search(self, queryset, name, value):
        """Recherche globale"""
        return queryset.filter(
            Q(nom__icontains=value) |
            Q(prenom__icontains=value) |
            Q(postnom__icontains=value) |
            Q(nin__icontains=value) |
            Q(telephone__icontains=value) |
            Q(email__icontains=value)
        )


class StrataMembershipFilter(django_filters.FilterSet):
    """
    Filtres pour StrataMembership
    """
    nin = django_filters.CharFilter(field_name='nin__nin', lookup_expr='icontains')
    strate_code = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='exact')
    
    # Filtres de date
    valid_from_after = django_filters.DateFilter(field_name='valid_from', lookup_expr='gte')
    valid_from_before = django_filters.DateFilter(field_name='valid_from', lookup_expr='lte')
    valid_to_after = django_filters.DateFilter(field_name='valid_to', lookup_expr='gte')
    valid_to_before = django_filters.DateFilter(field_name='valid_to', lookup_expr='lte')
    
    # Filtres de création
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = StrataMembership
        fields = ['strate_code', 'status']


class DocumentFilter(django_filters.FilterSet):
    """
    Filtres pour Document
    """
    nin = django_filters.CharFilter(field_name='nin__nin', lookup_expr='icontains')
    document_type = django_filters.CharFilter(lookup_expr='icontains')
    is_verified = django_filters.BooleanFilter()
    
    # Filtres de date
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    verified_after = django_filters.DateTimeFilter(field_name='verified_at', lookup_expr='gte')
    verified_before = django_filters.DateTimeFilter(field_name='verified_at', lookup_expr='lte')
    
    class Meta:
        model = Document
        fields = ['document_type', 'is_verified']
