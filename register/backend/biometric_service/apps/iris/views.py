"""
API Views pour la capture et traitement d'iris
"""

import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import (
    IrisCaptureSession,
    IrisCapture,
    IrisTemplate,
    IrisMatch,
    IrisQualityLog
)
from .serializers import (
    IrisCaptureSessionSerializer,
    IrisCaptureSerializer,
    IrisTemplateSerializer,
    IrisMatchSerializer,
    IrisQualityLogSerializer,
    StartSessionRequestSerializer,
    CaptureEyeRequestSerializer,
    MarkHandicapRequestSerializer,
    ProcessCaptureRequestSerializer,
    CompareTemplatesRequestSerializer,
    SearchDuplicatesRequestSerializer,
)
from .services import (
    IrisCaptureService,
    IrisProcessingService,
    IrisMatchingService,
    session_manager
)

logger = logging.getLogger(__name__)


class IrisCaptureSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les sessions de capture d'iris
    """
    queryset = IrisCaptureSession.objects.all()
    serializer_class = IrisCaptureSessionSerializer
    permission_classes = [AllowAny]  # TODO: Ajouter authentification en production
    
    @action(detail=False, methods=['post'], url_path='start')
    def start_session(self, request):
        """
        POST /api/v1/biometrics/iris/session/start/
        Démarre une nouvelle session de capture
        """
        serializer = StartSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Créer la session d'abord
            capture_service = IrisCaptureService()
            session = capture_service.start_session(
                enrollment_session_id=serializer.validated_data['enrollment_session_id'],
                operator_id=serializer.validated_data.get('operator_id'),
                station_id=serializer.validated_data.get('station_id')
            )
            
            # Enregistrer le service dans le session_manager
            session_manager._sessions[str(session.id)] = capture_service
            
            response_serializer = IrisCaptureSessionSerializer(session)
            
            return Response(
                {
                    'success': True,
                    'message': 'Session de capture démarrée',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Erreur démarrage session: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='capture')
    def capture_eye(self, request, pk=None):
        """
        POST /api/v1/biometrics/iris/session/{id}/capture/
        Capture un œil
        """
        session = self.get_object()
        
        serializer = CaptureEyeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            capture_service = IrisCaptureService()
            capture = capture_service.capture_eye(
                session=session,
                eye_position=serializer.validated_data['eye_position'],
                timeout=serializer.validated_data.get('timeout')
            )
            
            response_serializer = IrisCaptureSerializer(capture)
            
            return Response(
                {
                    'success': True,
                    'message': f"Capture de l'œil {serializer.validated_data['eye_position']} réussie",
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Erreur capture œil: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='handicap')
    def mark_handicap(self, request, pk=None):
        """
        POST /api/v1/biometrics/iris/session/{id}/handicap/
        Marque un œil comme handicapé
        """
        session = self.get_object()
        
        serializer = MarkHandicapRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            capture_service = IrisCaptureService()
            capture = capture_service.mark_eye_handicap(
                session=session,
                eye_position=serializer.validated_data['eye_position'],
                handicap_type=serializer.validated_data['handicap_type'],
                reason=serializer.validated_data['reason']
            )
            
            response_serializer = IrisCaptureSerializer(capture)
            
            return Response(
                {
                    'success': True,
                    'message': 'Handicap enregistré',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Erreur marquage handicap: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete_session(self, request, pk=None):
        """
        POST /api/v1/biometrics/iris/session/{id}/complete/
        Termine une session de capture
        """
        session = self.get_object()
        
        try:
            capture_service = session_manager.get_or_create_service(str(session.id))
            session = capture_service.complete_session(session)
            
            # Libérer le service
            session_manager.release_service(str(session.id))
            
            response_serializer = IrisCaptureSessionSerializer(session)
            
            return Response(
                {
                    'success': True,
                    'message': 'Session terminée',
                    'data': response_serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Erreur finalisation session: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_session(self, request, pk=None):
        """
        POST /api/v1/biometrics/iris/session/{id}/cancel/
        Annule une session de capture
        """
        session = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            capture_service = session_manager.get_or_create_service(str(session.id))
            session = capture_service.cancel_session(session, reason)
            
            # Libérer le service
            session_manager.release_service(str(session.id))
            
            response_serializer = IrisCaptureSessionSerializer(session)
            
            return Response(
                {
                    'success': True,
                    'message': 'Session annulée',
                    'data': response_serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Erreur annulation session: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='stream')
    def video_stream(self, request, pk=None):
        """
        GET /api/v1/biometrics/iris/sessions/{id}/stream/
        Stream vidéo en temps réel avec détection des yeux
        """
        from django.http import StreamingHttpResponse
        
        session = self.get_object()
        
        if session.status != 'IN_PROGRESS':
            return Response(
                {
                    'success': False,
                    'message': 'Session non active'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Utiliser le service du session_manager
            capture_service = session_manager.get_or_create_service(str(session.id))
            
            return StreamingHttpResponse(
                capture_service.generate_preview_stream(session),
                content_type='multipart/x-mixed-replace; boundary=frame'
            )
            
        except Exception as e:
            logger.error(f"Erreur streaming: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='capture_both')
    def capture_both_eyes(self, request, pk=None):
        """
        POST /api/v1/biometrics/iris/sessions/{id}/capture_both/
        Capture les deux yeux simultanément
        """
        session = self.get_object()
        
        timeout = request.data.get('timeout', 10)
        
        try:
            # Utiliser le service du session_manager (même instance que le streaming)
            capture_service = session_manager.get_or_create_service(str(session.id))
            capture_left, capture_right = capture_service.capture_both_eyes(
                session=session,
                timeout=timeout
            )
            
            if not capture_left or not capture_right:
                return Response(
                    {
                        'success': False,
                        'message': 'Impossible de capturer les deux yeux'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {
                    'success': True,
                    'message': 'Capture des deux yeux réussie',
                    'data': {
                        'left': IrisCaptureSerializer(capture_left).data,
                        'right': IrisCaptureSerializer(capture_right).data
                    }
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Erreur capture simultanée: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IrisCaptureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les captures d'iris
    """
    queryset = IrisCapture.objects.all()
    serializer_class = IrisCaptureSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['post'], url_path='process')
    def process(self, request, pk=None):
        """
        POST /api/v1/biometrics/iris/captures/{id}/process/
        Traite une capture (segmentation + encodage)
        """
        capture = self.get_object()
        
        if capture.status not in ['CAPTURED']:
            return Response(
                {
                    'success': False,
                    'message': 'Cette capture ne peut pas être traitée'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            processing_service = IrisProcessingService()
            template, quality_log = processing_service.process_capture(capture)
            
            # Recharger la capture mise à jour
            capture.refresh_from_db()
            
            response_data = {
                'capture': IrisCaptureSerializer(capture).data,
            }
            
            if template:
                response_data['template'] = IrisTemplateSerializer(template).data
            
            if quality_log:
                response_data['quality_log'] = IrisQualityLogSerializer(quality_log).data
            
            return Response(
                {
                    'success': True,
                    'message': 'Capture traitée avec succès',
                    'data': response_data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Erreur traitement capture: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IrisTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les templates d'iris
    """
    queryset = IrisTemplate.objects.all()
    serializer_class = IrisTemplateSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='compare')
    def compare(self, request):
        """
        POST /api/v1/biometrics/iris/templates/compare/
        Compare deux templates
        """
        serializer = CompareTemplatesRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            template1 = get_object_or_404(IrisTemplate, id=serializer.validated_data['template1_id'])
            template2 = get_object_or_404(IrisTemplate, id=serializer.validated_data['template2_id'])
            
            matching_service = IrisMatchingService()
            match = matching_service.compare_templates(template1, template2)
            
            response_serializer = IrisMatchSerializer(match)
            
            return Response(
                {
                    'success': True,
                    'message': 'Comparaison effectuée',
                    'data': response_serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Erreur comparaison templates: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='search-duplicates')
    def search_duplicates(self, request, pk=None):
        """
        POST /api/v1/biometrics/iris/templates/{id}/search-duplicates/
        Cherche des duplicatas
        """
        template = self.get_object()
        limit = request.data.get('limit', 10)
        
        try:
            matching_service = IrisMatchingService()
            results = matching_service.search_duplicates(template, limit=limit)
            
            duplicates = []
            for other_template, score, is_match in results:
                duplicates.append({
                    'template': IrisTemplateSerializer(other_template).data,
                    'similarity_score': score,
                    'similarity_percentage': int(score * 100),
                    'is_match': is_match
                })
            
            return Response(
                {
                    'success': True,
                    'message': f'{len(duplicates)} correspondances trouvées',
                    'data': {
                        'template_id': str(template.id),
                        'duplicates': duplicates
                    }
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Erreur recherche duplicatas: {e}")
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IrisMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les résultats de matching
    """
    queryset = IrisMatch.objects.all()
    serializer_class = IrisMatchSerializer
    permission_classes = [AllowAny]

