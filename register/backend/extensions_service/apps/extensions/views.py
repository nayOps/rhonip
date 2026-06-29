"""
Vues pour les extensions par strate du système FGP
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import (
    ExtensionEducation, ExtensionElectoral, ExtensionPNC, ExtensionFARDC,
    ExtensionPrison, ExtensionRefugie, ExtensionEnfant, ExtensionFonctionnaire
)
from .permissions import GuichetInternalOrAuthenticated
from .serializers import (
    ExtensionEducationSerializer, ExtensionElectoralSerializer, ExtensionPNCSerializer,
    ExtensionFARDCSerializer, ExtensionPrisonSerializer, ExtensionRefugieSerializer,
    ExtensionEnfantSerializer, ExtensionFonctionnaireSerializer,
    ExtensionCreateSerializer, ExtensionUpdateSerializer, ExtensionSearchSerializer
)


class ExtensionViewSetMixin:
    permission_classes = [GuichetInternalOrAuthenticated]


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination standard pour les extensions"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ExtensionEducationViewSet(ExtensionViewSetMixin, viewsets.ModelViewSet):
    """ViewSet pour l'extension éducation"""
    queryset = ExtensionEducation.objects.all()
    serializer_class = ExtensionEducationSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['niveau', 'cycle', 'statut_scolaire', 'province_etablissement']
    search_fields = ['nin', 'matricule_scolaire', 'etablissement', 'responsable_tuteur']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        # Filtres personnalisés
        nin = self.request.query_params.get('nin')
        if nin:
            queryset = queryset.filter(nin__icontains=nin)
        
        etablissement = self.request.query_params.get('etablissement')
        if etablissement:
            queryset = queryset.filter(etablissement__icontains=etablissement)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension éducation"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_cycle': dict(
                self.get_queryset().values('cycle').annotate(count=Count('id')).values_list('cycle', 'count')
            ),
            'by_statut': dict(
                self.get_queryset().values('statut_scolaire').annotate(count=Count('id')).values_list('statut_scolaire', 'count')
            ),
            'by_province': dict(
                self.get_queryset().values('province_etablissement').annotate(count=Count('id')).values_list('province_etablissement', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionElectoralViewSet(ExtensionViewSetMixin, viewsets.ModelViewSet):
    """ViewSet pour l'extension électorale"""
    queryset = ExtensionElectoral.objects.all()
    serializer_class = ExtensionElectoralSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['statut_inscription', 'province_vote', 'commune_vote']
    search_fields = ['nin', 'code_centre_vote', 'centre_vote', 'secteur_vote']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        circonscription = self.request.query_params.get('circonscription')
        if circonscription:
            queryset = queryset.filter(circonscription__icontains=circonscription)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension électorale"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_statut': dict(
                self.get_queryset().values('statut_inscription').annotate(count=Count('id')).values_list('statut_inscription', 'count')
            ),
            'by_province': dict(
                self.get_queryset().values('province_vote').annotate(count=Count('id')).values_list('province_vote', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionPNCViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'extension PNC"""
    queryset = ExtensionPNC.objects.all()
    serializer_class = ExtensionPNCSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['grade', 'statut_service', 'zone_affectation']
    search_fields = ['nin', 'matricule_pnc', 'unite', 'fonction']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        unite = self.request.query_params.get('unite')
        if unite:
            queryset = queryset.filter(unite__icontains=unite)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension PNC"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_grade': dict(
                self.get_queryset().values('grade').annotate(count=Count('id')).values_list('grade', 'count')
            ),
            'by_statut': dict(
                self.get_queryset().values('statut_service').annotate(count=Count('id')).values_list('statut_service', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionFARDCViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'extension FARDC"""
    queryset = ExtensionFARDC.objects.all()
    serializer_class = ExtensionFARDCSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['grade', 'statut_militaire', 'type_mission', 'zone_operation']
    search_fields = ['nin', 'matricule_fardc', 'unite_affectation', 'fonction']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        zone = self.request.query_params.get('zone_operation')
        if zone:
            queryset = queryset.filter(zone_operation__icontains=zone)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension FARDC"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_grade': dict(
                self.get_queryset().values('grade').annotate(count=Count('id')).values_list('grade', 'count')
            ),
            'by_statut': dict(
                self.get_queryset().values('statut_militaire').annotate(count=Count('id')).values_list('statut_militaire', 'count')
            ),
            'by_mission': dict(
                self.get_queryset().values('type_mission').annotate(count=Count('id')).values_list('type_mission', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionPrisonViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'extension prison"""
    queryset = ExtensionPrison.objects.all()
    serializer_class = ExtensionPrisonSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['statut_detention', 'centre_detention']
    search_fields = ['nin', 'numero_dossier_judiciaire', 'infraction']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        autorite = self.request.query_params.get('autorite_judiciaire')
        if autorite:
            queryset = queryset.filter(autorite_judiciaire__icontains=autorite)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension prison"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_statut': dict(
                self.get_queryset().values('statut_detention').annotate(count=Count('id')).values_list('statut_detention', 'count')
            ),
            'by_centre': dict(
                self.get_queryset().values('centre_detention').annotate(count=Count('id')).values_list('centre_detention', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionRefugieViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'extension réfugié"""
    queryset = ExtensionRefugie.objects.all()
    serializer_class = ExtensionRefugieSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['statut_juridique', 'pays_origine', 'organisme_encadrement']
    search_fields = ['nin', 'numero_hcr', 'camp_refugie']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        camp = self.request.query_params.get('camp_refugie')
        if camp:
            queryset = queryset.filter(camp_refugie__icontains=camp)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension réfugié"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_statut': dict(
                self.get_queryset().values('statut_juridique').annotate(count=Count('id')).values_list('statut_juridique', 'count')
            ),
            'by_pays': dict(
                self.get_queryset().values('pays_origine').annotate(count=Count('id')).values_list('pays_origine', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionEnfantViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'extension enfant"""
    queryset = ExtensionEnfant.objects.all()
    serializer_class = ExtensionEnfantSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['lien_tuteur', 'situation_familiale']
    search_fields = ['nin', 'tuteur_nin', 'tuteur_nom', 'structure_accueil']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        tuteur = self.request.query_params.get('tuteur_nin')
        if tuteur:
            queryset = queryset.filter(tuteur_nin__icontains=tuteur)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension enfant"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_lien': dict(
                self.get_queryset().values('lien_tuteur').annotate(count=Count('id')).values_list('lien_tuteur', 'count')
            ),
            'by_situation': dict(
                self.get_queryset().values('situation_familiale').annotate(count=Count('id')).values_list('situation_familiale', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionFonctionnaireViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'extension fonctionnaire"""
    queryset = ExtensionFonctionnaire.objects.all()
    serializer_class = ExtensionFonctionnaireSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['ministere_affectation', 'statut_service', 'type_contrat']
    search_fields = ['nin', 'matricule_fonctionnaire', 'service_affectation', 'poste']

    def get_queryset(self):
        """Filtrage du queryset"""
        queryset = super().get_queryset()
        
        ministere = self.request.query_params.get('ministere')
        if ministere:
            queryset = queryset.filter(ministere_affectation__icontains=ministere)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques pour l'extension fonctionnaire"""
        from django.db.models import Count
        
        stats = {
            'total': self.get_queryset().count(),
            'by_ministere': dict(
                self.get_queryset().values('ministere_affectation').annotate(count=Count('id')).values_list('ministere_affectation', 'count')
            ),
            'by_statut': dict(
                self.get_queryset().values('statut_service').annotate(count=Count('id')).values_list('statut_service', 'count')
            ),
            'by_contrat': dict(
                self.get_queryset().values('type_contrat').annotate(count=Count('id')).values_list('type_contrat', 'count')
            ),
        }
        
        return Response(stats)


class ExtensionManagerViewSet(viewsets.ViewSet):
    """ViewSet pour la gestion globale des extensions"""
    
    @action(detail=False, methods=['post'])
    def create_multiple(self, request):
        """Créer plusieurs extensions pour un NIN"""
        serializer = ExtensionCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    results = {}
                    
                    # Créer chaque extension si fournie
                    if 'education' in serializer.validated_data:
                        edu_serializer = ExtensionEducationSerializer(data=serializer.validated_data['education'])
                        if edu_serializer.is_valid():
                            results['education'] = edu_serializer.save()
                    
                    if 'electoral' in serializer.validated_data:
                        elec_serializer = ExtensionElectoralSerializer(data=serializer.validated_data['electoral'])
                        if elec_serializer.is_valid():
                            results['electoral'] = elec_serializer.save()
                    
                    if 'pnc' in serializer.validated_data:
                        pnc_serializer = ExtensionPNCSerializer(data=serializer.validated_data['pnc'])
                        if pnc_serializer.is_valid():
                            results['pnc'] = pnc_serializer.save()
                    
                    if 'fardc' in serializer.validated_data:
                        fardc_serializer = ExtensionFARDCSerializer(data=serializer.validated_data['fardc'])
                        if fardc_serializer.is_valid():
                            results['fardc'] = fardc_serializer.save()
                    
                    if 'prison' in serializer.validated_data:
                        prison_serializer = ExtensionPrisonSerializer(data=serializer.validated_data['prison'])
                        if prison_serializer.is_valid():
                            results['prison'] = prison_serializer.save()
                    
                    if 'refugee' in serializer.validated_data:
                        ref_serializer = ExtensionRefugieSerializer(data=serializer.validated_data['refugee'])
                        if ref_serializer.is_valid():
                            results['refugee'] = ref_serializer.save()
                    
                    if 'enfant' in serializer.validated_data:
                        enfant_serializer = ExtensionEnfantSerializer(data=serializer.validated_data['enfant'])
                        if enfant_serializer.is_valid():
                            results['enfant'] = enfant_serializer.save()
                    
                    if 'fonctionnaire' in serializer.validated_data:
                        fonc_serializer = ExtensionFonctionnaireSerializer(data=serializer.validated_data['fonctionnaire'])
                        if fonc_serializer.is_valid():
                            results['fonctionnaire'] = fonc_serializer.save()
                    
                    return Response({
                        'success': True,
                        'message': f'{len(results)} extensions créées avec succès',
                        'results': results
                    }, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche globale dans toutes les extensions"""
        serializer = ExtensionSearchSerializer(data=request.query_params)
        
        if serializer.is_valid():
            results = {}
            params = serializer.validated_data
            
            # Recherche dans chaque extension si spécifiée
            if not params.get('strata') or params['strata'] == 'education':
                results['education'] = self._search_education(params)
            
            if not params.get('strata') or params['strata'] == 'electoral':
                results['electoral'] = self._search_electoral(params)
            
            if not params.get('strata') or params['strata'] == 'pnc':
                results['pnc'] = self._search_pnc(params)
            
            if not params.get('strata') or params['strata'] == 'fardc':
                results['fardc'] = self._search_fardc(params)
            
            if not params.get('strata') or params['strata'] == 'prison':
                results['prison'] = self._search_prison(params)
            
            if not params.get('strata') or params['strata'] == 'refugee':
                results['refugee'] = self._search_refugee(params)
            
            if not params.get('strata') or params['strata'] == 'enfant':
                results['enfant'] = self._search_enfant(params)
            
            if not params.get('strata') or params['strata'] == 'fonctionnaire':
                results['fonctionnaire'] = self._search_fonctionnaire(params)
            
            return Response(results)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _search_education(self, params):
        """Recherche dans l'extension éducation"""
        queryset = ExtensionEducation.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(etablissement__icontains=params['search_term']) |
                Q(matricule_scolaire__icontains=params['search_term'])
            )
        
        return queryset.count()

    def _search_electoral(self, params):
        """Recherche dans l'extension électorale"""
        queryset = ExtensionElectoral.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(centre_vote__icontains=params['search_term']) |
                Q(secteur_vote__icontains=params['search_term'])
            )
        
        return queryset.count()

    def _search_pnc(self, params):
        """Recherche dans l'extension PNC"""
        queryset = ExtensionPNC.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(unite__icontains=params['search_term']) |
                Q(matricule_pnc__icontains=params['search_term'])
            )
        
        return queryset.count()

    def _search_fardc(self, params):
        """Recherche dans l'extension FARDC"""
        queryset = ExtensionFARDC.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(unite_affectation__icontains=params['search_term']) |
                Q(matricule_fardc__icontains=params['search_term'])
            )
        
        return queryset.count()

    def _search_prison(self, params):
        """Recherche dans l'extension prison"""
        queryset = ExtensionPrison.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(centre_detention__icontains=params['search_term']) |
                Q(numero_dossier_judiciaire__icontains=params['search_term'])
            )
        
        return queryset.count()

    def _search_refugee(self, params):
        """Recherche dans l'extension réfugié"""
        queryset = ExtensionRefugie.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(numero_hcr__icontains=params['search_term']) |
                Q(camp_refugie__icontains=params['search_term'])
            )
        
        return queryset.count()

    def _search_enfant(self, params):
        """Recherche dans l'extension enfant"""
        queryset = ExtensionEnfant.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(tuteur_nom__icontains=params['search_term']) |
                Q(structure_accueil__icontains=params['search_term'])
            )
        
        return queryset.count()

    def _search_fonctionnaire(self, params):
        """Recherche dans l'extension fonctionnaire"""
        queryset = ExtensionFonctionnaire.objects.all()
        
        if params.get('nin'):
            queryset = queryset.filter(nin__icontains=params['nin'])
        
        if params.get('search_term'):
            queryset = queryset.filter(
                Q(ministere_affectation__icontains=params['search_term']) |
                Q(matricule_fonctionnaire__icontains=params['search_term'])
            )
        
        return queryset.count()

    @action(detail=False, methods=['get'])
    def global_stats(self, request):
        """Statistiques globales de toutes les extensions"""
        stats = {
            'education': ExtensionEducation.objects.count(),
            'electoral': ExtensionElectoral.objects.count(),
            'pnc': ExtensionPNC.objects.count(),
            'fardc': ExtensionFARDC.objects.count(),
            'prison': ExtensionPrison.objects.count(),
            'refugee': ExtensionRefugie.objects.count(),
            'enfant': ExtensionEnfant.objects.count(),
            'fonctionnaire': ExtensionFonctionnaire.objects.count(),
            'total': 0
        }
        
        stats['total'] = sum(stats.values()) - stats['total']  # Remove the total from the sum
        
        return Response(stats)
