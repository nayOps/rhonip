"""
Vues pour l'application Enrollment
"""
import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import connection
from django.conf import settings
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view, permission_classes

from .models import (
    EnrollmentSession, EnrollmentValidation, EnrollmentEvent, 
    EnrollmentReceipt, EnrollmentStatistics
)
from .serializers import (
    EnrollmentPayloadSerializer, EnrollmentResponseSerializer,
    EnrollmentDetailSerializer, EnrollmentValidationSerializer,
    EnrollmentEventSerializer, EnrollmentReceiptSerializer,
    EnrollmentStatsSerializer, EnrollmentSearchSerializer
)
from .services import EnrollmentOrchestrator, ValidationService, ABISService
from .tasks import process_enrollment_async


class EnrollmentSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des sessions d'enrôlement
    """
    queryset = EnrollmentSession.objects.all()
    serializer_class = EnrollmentDetailSerializer
    # Dev-only: ouvrir certains endpoints sans auth pour tests frontend
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'channel', 'operator_id']
    search_fields = ['session_id', 'registration_number', 'device_id']
    ordering_fields = ['created_at', 'updated_at', 'processing_time_ms']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Masquer les sessions de smoke test du tableau de bord admin.
        return queryset.exclude(session_id__startswith='FGP-SMOKE-')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EnrollmentResponseSerializer
        return EnrollmentDetailSerializer

    def get_permissions(self):
        # Autoriser sans auth pour création et lecture de statut pendant les tests
        if self.action in [
            'list',
            'retrieve',
            'get_detail',
            'get_db_snapshot',
            'get_db_overview',
            'completed_report',
            'media_proxy',
            'create',
            'get_status',
            'search',
            'update_fingerprint_modality',
            'update_iris_modality',
            'update_face_modality',
            'update_document_modality',
            'update_employee',
            'prepare_edit',
            'submit_session',
            'cancel_session',
        ]:
            return [AllowAny()]
        return super().get_permissions()
    
    @extend_schema(
        summary="Créer une nouvelle session d'enrôlement",
        request=EnrollmentPayloadSerializer,
        responses={201: EnrollmentResponseSerializer}
    )
    def create(self, request):
        """
        Créer une nouvelle session d'enrôlement
        """
        start_time = time.time()
        
        # Validation du payload
        payload_serializer = EnrollmentPayloadSerializer(data=request.data)
        if not payload_serializer.is_valid():
            return Response(
                {'error': 'Payload invalide', 'details': payload_serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        validated_data = payload_serializer.validated_data
        
        try:
            matricule = None
            employee = validated_data.get('employee') or request.data.get('employee') or {}
            if isinstance(employee, dict):
                matricule = (employee.get('registration_number') or '').strip() or None

            # Créer la session d'enrôlement
            session = EnrollmentSession.objects.create(
                session_id=validated_data['session_id'],
                channel=validated_data['channel'],
                device_id=validated_data['device_id'],
                operator_id=validated_data['operator_id'],
                location=validated_data['location'],
                payload=request.data,
                payload_hash=self._calculate_payload_hash(request.data),
                payload_signature=request.META.get('HTTP_X_PAYLOAD_SIGNATURE', ''),
                status='PENDING',
                registration_number=matricule,
            )
            
            # Créer l'événement de début
            EnrollmentEvent.objects.create(
                session=session,
                event_type='session_started',
                event_data={'channel': session.channel, 'device_id': session.device_id},
                message=f"Session d'enrôlement démarrée via {session.channel}"
            )
            
            # Traitement asynchrone (désactivable pour enrôlement guichet par étapes)
            if request.data.get('auto_process', True):
                process_enrollment_async.delay(session.id)
            
            # Réponse immédiate
            response_serializer = EnrollmentResponseSerializer(session)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': 'Erreur lors de la création de la session', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Obtenir le statut d'une session d'enrôlement",
        parameters=[
            OpenApiParameter(name='session_id', description='ID de la session', required=True, type=str)
        ]
    )
    @action(detail=False, methods=['get'], url_path='status/(?P<session_id>[^/.]+)')
    def get_status(self, request, session_id=None):
        """Obtenir le statut d'une session d'enrôlement"""
        try:
            session = get_object_or_404(EnrollmentSession, session_id=session_id)
            serializer = EnrollmentResponseSerializer(session)
            return Response(serializer.data)
        except EnrollmentSession.DoesNotExist:
            return Response(
                {'error': 'Session non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Obtenir le détail complet d'une session d'enrôlement",
        parameters=[
            OpenApiParameter(name='session_id', description='ID de la session', required=True, type=str)
        ]
    )
    @action(detail=False, methods=['get'], url_path='detail/(?P<session_id>[^/.]+)')
    def get_detail(self, request, session_id=None):
        """Obtenir le détail complet d'une session d'enrôlement par session_id métier."""
        try:
            session = get_object_or_404(EnrollmentSession, session_id=session_id)
            serializer = EnrollmentDetailSerializer(session)
            return Response(serializer.data)
        except EnrollmentSession.DoesNotExist:
            return Response(
                {'error': 'Session non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Obtenir un snapshot BD (personne, biométrie, documents, extensions) par session_id",
        parameters=[
            OpenApiParameter(name='session_id', description='ID de la session', required=True, type=str)
        ]
    )
    @action(detail=False, methods=['get'], url_path='db-snapshot/(?P<session_id>[^/.]+)')
    def get_db_snapshot(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        matricule = session.sync_registration_number_from_payload(save=True)
        payload = session.payload or {}
        employee = payload.get('employee') or {}

        if not matricule:
            return Response(
                {
                    'session_id': session.session_id,
                    'registration_number': None,
                    'agent_name': EnrollmentSession.agent_display_name(payload),
                    'employee': employee or None,
                    'db': {},
                },
                status=status.HTTP_200_OK,
            )

        def fetch_one(sql, params):
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [c[0] for c in cursor.description]
                return dict(zip(cols, row))

        def fetch_all(sql, params):
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                cols = [c[0] for c in cursor.description]
                return [dict(zip(cols, r)) for r in rows]

        biometric = fetch_one(
            "SELECT * FROM fgp_biometric WHERE registration_number=%s",
            [matricule],
        )
        try:
            fingerprints = fetch_all(
                "SELECT id, registration_number, finger_position, capture_status, image_uri, image_hash, "
                "template_uri, template_hash, template_format, quality_score, nfiq_score, device, "
                "captured_at, created_at, updated_at "
                "FROM fgp_fingerprints WHERE registration_number=%s ORDER BY finger_position ASC",
                [matricule],
            )
        except Exception:
            fingerprints = []

        documents = []
        try:
            documents = fetch_all(
                "SELECT id, registration_number, document_type, document_uri, document_hash, file_size, "
                "mime_type, is_verified, created_at "
                "FROM fgp_documents WHERE registration_number=%s ORDER BY created_at DESC",
                [matricule],
            )
        except Exception:
            try:
                documents = fetch_all(
                    "SELECT id, nin, document_type, document_uri, document_hash, file_size, mime_type, "
                    "is_verified, created_at "
                    "FROM fgp_documents WHERE nin=%s ORDER BY created_at DESC",
                    [matricule],
                )
            except Exception:
                documents = []

        person = None
        try:
            person = fetch_one("SELECT * FROM fgp_person_core WHERE nin=%s", [matricule])
        except Exception:
            person = None

        should_repair = str(request.query_params.get('repair', '')).lower() in ('1', 'true', 'yes')
        repaired = False
        repair_error = None
        if should_repair and (biometric is None or len(fingerprints) == 0):
            try:
                media_result = EnrollmentOrchestrator()._persist_enrollment_media(session)
                repaired = True
                if isinstance(media_result, dict) and media_result.get('errors'):
                    repair_error = '; '.join(str(e) for e in media_result['errors'][:10])
                biometric = fetch_one(
                    "SELECT * FROM fgp_biometric WHERE registration_number=%s",
                    [matricule],
                )
                try:
                    fingerprints = fetch_all(
                        "SELECT id, registration_number, finger_position, capture_status, image_uri, image_hash, "
                        "template_uri, template_hash, template_format, quality_score, nfiq_score, device, "
                        "captured_at, created_at, updated_at "
                        "FROM fgp_fingerprints WHERE registration_number=%s ORDER BY finger_position ASC",
                        [matricule],
                    )
                except Exception:
                    fingerprints = []
            except Exception as exc:
                repair_error = str(exc)

        return Response(
            {
                'session_id': session.session_id,
                'registration_number': matricule,
                'agent_name': EnrollmentSession.agent_display_name(payload),
                'employee': employee or None,
                'db': {
                    'employee': employee or None,
                    'person_core': person,
                    'biometric': biometric,
                    'fingerprints': fingerprints,
                    'documents': documents,
                    'extensions': {},
                },
                'repair': {
                    'requested': should_repair,
                    'performed': repaired,
                    'error': repair_error,
                },
            }
        )

    @action(detail=False, methods=['get'], url_path='media-proxy')
    def media_proxy(self, request):
        """
        Sert un fichier média local à partir d'une URI file:// ou chemin /media/...
        """
        raw = request.query_params.get('uri') or request.query_params.get('path')
        if not raw:
            return Response({'error': 'uri requis'}, status=status.HTTP_400_BAD_REQUEST)

        media_root = Path(getattr(settings, 'MEDIA_ROOT', '/app/media')).resolve()
        target: Path

        if raw.startswith('file://'):
            file_path = raw[len('file://'):]
            target = Path(file_path)
            if not target.is_absolute():
                target = media_root / target
        elif raw.startswith('/media/'):
            target = media_root / raw[len('/media/'):]
        elif raw.startswith('media/'):
            target = media_root / raw[len('media/'):]
        else:
            return Response({'error': 'uri non supportée'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_resolved = target.resolve()
        except Exception:
            return Response({'error': 'chemin invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if not str(target_resolved).startswith(str(media_root)):
            return Response({'error': 'accès refusé'}, status=status.HTTP_403_FORBIDDEN)
        if not target_resolved.exists() or not target_resolved.is_file():
            return Response({'error': 'fichier introuvable'}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(open(target_resolved, 'rb'))

    @extend_schema(summary="Liste des enrôlements COMPLETED pour rapport PDF (nom, postnom, NIN, photo)")
    @action(detail=False, methods=['get'], url_path='completed-report')
    def completed_report(self, request):
        def fetch_one(sql, params):
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [c[0] for c in cursor.description]
                return dict(zip(cols, row))

        sessions = (
            self.get_queryset()
            .filter(status='COMPLETED')
            .order_by('-created_at')
        )
        rows = []
        for session in sessions:
            payload = session.payload or {}
            employee = payload.get('employee') or {}
            core = payload.get('core') or {}
            nom = str(employee.get('last_name') or core.get('nom') or '').strip()
            postnom = str(employee.get('middle_name') or core.get('postnom') or '').strip()
            prenom = str(employee.get('first_name') or core.get('prenom') or '').strip()
            photo_uri = None
            matricule = session.resolve_registration_number()

            if matricule:
                bio = fetch_one(
                    "SELECT photo_uri FROM fgp_biometric WHERE registration_number=%s",
                    [matricule],
                )
                if bio and bio.get('photo_uri'):
                    photo_uri = bio['photo_uri']

            persisted = payload.get('persisted_media') or {}
            if not photo_uri and isinstance(persisted, dict):
                photo_uri = persisted.get('photo_uri')

            rows.append(
                {
                    'session_id': session.session_id,
                    'nom': nom,
                    'postnom': postnom,
                    'prenom': prenom,
                    'agent_name': EnrollmentSession.agent_display_name(payload),
                    'statut': session.status,
                    'registration_number': matricule,
                    'created_at': session.created_at.isoformat() if session.created_at else None,
                    'photo_uri': photo_uri,
                }
            )

        return Response(
            {
                'count': len(rows),
                'generated_at': datetime.now().isoformat(),
                'rows': rows,
            }
        )

    @extend_schema(summary="Obtenir un résumé global des données BD (sessions/core/biométrie/documents)")
    @action(detail=False, methods=['get'], url_path='db-overview')
    def get_db_overview(self, request):
        def safe_scalar(sql):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    return int(row[0]) if row and row[0] is not None else 0
            except Exception:
                return 0

        return Response(
            {
                'sessions_total': safe_scalar("SELECT COUNT(*) FROM enrollment_sessions"),
                'sessions_with_matricule': safe_scalar(
                    "SELECT COUNT(*) FROM enrollment_sessions "
                    "WHERE registration_number IS NOT NULL AND registration_number <> ''"
                ),
                'biometric_total': safe_scalar("SELECT COUNT(*) FROM fgp_biometric"),
                'fingerprints_total': safe_scalar("SELECT COUNT(*) FROM fgp_fingerprints"),
                'documents_total': safe_scalar("SELECT COUNT(*) FROM fgp_documents"),
            }
        )

    @extend_schema(summary="Mettre à jour le statut modalité empreintes")
    @action(detail=False, methods=['patch'], url_path='modality/fingerprint/(?P<session_id>[^/.]+)')
    def update_fingerprint_modality(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        session.sync_registration_number_from_payload(save=True)
        status_value = request.data.get('status')
        allowed = {'pending', 'completed', 'skipped', 'failed'}
        if status_value not in allowed:
            return Response(
                {'error': f'status invalide — valeurs: {", ".join(sorted(allowed))}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.set_modality_status('fingerprint', status_value, request.data.get('message'))

        fingerprints_payload = request.data.get('fingerprints')
        update_fields = ['modality_status', 'updated_at', 'registration_number']
        if fingerprints_payload is not None:
            payload = dict(session.payload or {})
            biometrics = dict(payload.get('biometrics') or {})
            fingers = fingerprints_payload.get('fingers') or []
            if not isinstance(fingers, list):
                return Response(
                    {'error': 'fingerprints.fingers doit être une liste'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            captured = [f for f in fingers if f.get('status') == 'CAPTURED']
            qualities = []
            for finger in captured:
                q = finger.get('quality')
                if q is None:
                    continue
                try:
                    qf = float(q)
                except (TypeError, ValueError):
                    continue
                qualities.append(qf / 100.0 if qf > 1 else qf)

            aggregate_quality = fingerprints_payload.get('quality')
            if aggregate_quality is None and qualities:
                aggregate_quality = round(sum(qualities) / len(qualities), 4)
            elif aggregate_quality is not None:
                try:
                    aggregate_quality = float(aggregate_quality)
                    if aggregate_quality > 1:
                        aggregate_quality = round(aggregate_quality / 100.0, 4)
                except (TypeError, ValueError):
                    aggregate_quality = None

            biometrics['fingerprints'] = {
                'ref': f'inline://{session.session_id}/fingerprints',
                'quality': aggregate_quality if aggregate_quality is not None else 0.0,
                'device': fingerprints_payload.get('device', 'fap60'),
                'source': fingerprints_payload.get('source', 'live'),
                'fingers': fingers,
                'summary': fingerprints_payload.get('summary', {}),
            }
            payload['biometrics'] = biometrics
            session.payload = payload
            update_fields.append('payload')

        session.save(update_fields=update_fields)
        if status_value == 'completed' and session.registration_number:
            try:
                EnrollmentOrchestrator()._persist_enrollment_media(session)
            except Exception:
                pass
        EnrollmentEvent.objects.create(
            session=session,
            event_type='payload_received',
            event_data={
                'modality': 'fingerprint',
                'status': status_value,
                'finger_count': len((fingerprints_payload or {}).get('fingers') or []),
            },
            message=f"Empreintes: {status_value}",
        )
        return Response({'session_id': session.session_id, 'modality_status': session.modality_status})

    @extend_schema(summary="Mettre à jour le statut modalité iris")
    @action(detail=False, methods=['patch'], url_path='modality/iris/(?P<session_id>[^/.]+)')
    def update_iris_modality(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        session.sync_registration_number_from_payload(save=True)
        status_value = request.data.get('status')
        allowed = {'pending', 'completed', 'skipped', 'failed'}
        if status_value not in allowed:
            return Response(
                {'error': f'status invalide — valeurs: {", ".join(sorted(allowed))}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.set_modality_status('iris', status_value, request.data.get('message'))

        iris_payload = request.data.get('iris')
        update_fields = ['modality_status', 'updated_at', 'registration_number']
        if iris_payload is not None:
            payload = dict(session.payload or {})
            biometrics = dict(payload.get('biometrics') or {})
            eyes = iris_payload.get('eyes') or []
            if not isinstance(eyes, list):
                return Response(
                    {'error': 'iris.eyes doit être une liste'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            captured = [e for e in eyes if e.get('status') == 'CAPTURED']
            qualities = []
            for eye in captured:
                q = eye.get('quality')
                if q is None:
                    continue
                try:
                    qf = float(q)
                except (TypeError, ValueError):
                    continue
                qualities.append(qf / 100.0 if qf > 1 else qf)

            aggregate_quality = iris_payload.get('quality')
            if aggregate_quality is None and qualities:
                aggregate_quality = round(sum(qualities) / len(qualities), 4)
            elif aggregate_quality is not None:
                try:
                    aggregate_quality = float(aggregate_quality)
                    if aggregate_quality > 1:
                        aggregate_quality = round(aggregate_quality / 100.0, 4)
                except (TypeError, ValueError):
                    aggregate_quality = None

            biometrics['iris'] = {
                'ref': f'inline://{session.session_id}/iris',
                'quality': aggregate_quality if aggregate_quality is not None else 0.0,
                'device': iris_payload.get('device', 'iris-device-server'),
                'eyes': eyes,
                'summary': iris_payload.get('summary', {}),
            }
            payload['biometrics'] = biometrics
            session.payload = payload
            update_fields.append('payload')

        session.save(update_fields=update_fields)
        if status_value == 'completed' and session.registration_number:
            try:
                EnrollmentOrchestrator()._persist_enrollment_media(session)
            except Exception:
                pass
        EnrollmentEvent.objects.create(
            session=session,
            event_type='payload_received',
            event_data={
                'modality': 'iris',
                'status': status_value,
                'eye_count': len((iris_payload or {}).get('eyes') or []),
            },
            message=f"Iris: {status_value}",
        )
        return Response({'session_id': session.session_id, 'modality_status': session.modality_status})

    @extend_schema(summary="Mettre à jour le statut modalité photo (visage)")
    @action(detail=False, methods=['patch'], url_path='modality/face/(?P<session_id>[^/.]+)')
    def update_face_modality(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        session.sync_registration_number_from_payload(save=True)
        status_value = request.data.get('status')
        allowed = {'pending', 'completed', 'skipped', 'failed'}
        if status_value not in allowed:
            return Response(
                {'error': f'status invalide — valeurs: {", ".join(sorted(allowed))}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.set_modality_status('face', status_value, request.data.get('message'))

        face_payload = request.data.get('face')
        update_fields = ['modality_status', 'updated_at', 'registration_number']
        if face_payload is not None:
            payload = dict(session.payload or {})
            biometrics = dict(payload.get('biometrics') or {})
            quality = face_payload.get('quality')
            if quality is not None:
                try:
                    qf = float(quality)
                    if qf > 1:
                        qf = round(qf / 100.0, 4)
                    quality = qf
                except (TypeError, ValueError):
                    quality = None

            biometrics['face'] = {
                'ref': f'inline://{session.session_id}/face',
                'quality': quality if quality is not None else 0.0,
                'device': face_payload.get('device', 'gpy-com'),
                'icao_compliant': face_payload.get('icao_compliant', True),
                'source': face_payload.get('source', 'gpy'),
                'checks': face_payload.get('checks', {}),
            }
            for field in (
                'image_base64',
                'raw_image_base64',
                'icao_image_base64',
                'raw_sha256',
                'icao_sha256',
                'capture_metadata',
                'crop',
                'capture_timestamp',
                'camera',
            ):
                val = face_payload.get(field)
                if val is not None:
                    biometrics['face'][field] = val
            payload['biometrics'] = biometrics
            session.payload = payload
            update_fields.append('payload')

        session.save(update_fields=update_fields)
        if status_value == 'completed':
            session.sync_registration_number_from_payload(save=True)
            if session.registration_number:
                try:
                    orchestrator = EnrollmentOrchestrator()
                    orchestrator._persist_enrollment_media(session)
                    photo_sync = orchestrator._sync_employee_photo_to_rh(session)
                    if photo_sync.get('success'):
                        EnrollmentEvent.objects.create(
                            session=session,
                            event_type='employee_photo_synced',
                            event_data={'trigger': 'face_modality'},
                            message='Photo RH synchronisée (capture)',
                        )
                    elif not photo_sync.get('skipped'):
                        EnrollmentEvent.objects.create(
                            session=session,
                            event_type='employee_photo_sync_failed',
                            event_data={'trigger': 'face_modality'},
                            message=photo_sync.get('error', 'Photo RH non synchronisée'),
                        )
                except Exception:
                    pass
        EnrollmentEvent.objects.create(
            session=session,
            event_type='payload_received',
            event_data={'modality': 'face', 'status': status_value},
            message=f"Photo: {status_value}",
        )
        return Response({'session_id': session.session_id, 'modality_status': session.modality_status})

    @extend_schema(summary="Mettre à jour les documents scannés (guichet)")
    @action(detail=False, methods=['patch'], url_path='modality/document/(?P<session_id>[^/.]+)')
    def update_document_modality(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        session.sync_registration_number_from_payload(save=True)
        status_value = request.data.get('status')
        allowed = {'pending', 'completed', 'skipped', 'failed'}
        if status_value not in allowed:
            return Response(
                {'error': f'status invalide — valeurs: {", ".join(sorted(allowed))}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session.set_modality_status('document', status_value, request.data.get('message'))

        documents_payload = request.data.get('documents')
        update_fields = ['modality_status', 'updated_at', 'registration_number']
        if documents_payload is not None:
            payload = dict(session.payload or {})
            docs = documents_payload.get('documents') or []
            if not isinstance(docs, list):
                return Response(
                    {'error': 'documents.documents doit être une liste'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payload['attachments'] = docs
            payload['documents_meta'] = documents_payload.get('summary', {})
            payload['guichet_documents_saved_at'] = datetime.utcnow().isoformat() + 'Z'
            session.payload = payload
            update_fields.append('payload')

        session.save(update_fields=update_fields)
        EnrollmentEvent.objects.create(
            session=session,
            event_type='payload_received',
            event_data={
                'modality': 'document',
                'status': status_value,
                'document_count': len((documents_payload or {}).get('documents') or []),
            },
            message=f"Documents: {status_value}",
        )
        return Response({'session_id': session.session_id, 'modality_status': session.modality_status})

    @extend_schema(summary="Lancer le traitement asynchrone d'une session guichet")
    @action(detail=False, methods=['post'], url_path='submit/(?P<session_id>[^/.]+)')
    def submit_session(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        if session.status not in ('PENDING', 'FAILED'):
            return Response(
                {'session_id': session.session_id, 'status': session.status},
                status=status.HTTP_200_OK,
            )
        session.status = 'VALIDATING'
        session.save(update_fields=['status', 'updated_at'])
        process_enrollment_async.delay(session.id)
        EnrollmentEvent.objects.create(
            session=session,
            event_type='validation_started',
            event_data={'trigger': 'guichet_submit'},
            message='Traitement enrôlement démarré (guichet)',
        )
        return Response(
            {'session_id': session.session_id, 'status': session.status},
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(summary="Préparer une session pour modification biographique ou biométrique")
    @action(detail=False, methods=['post'], url_path='prepare-edit/(?P<session_id>[^/.]+)')
    def prepare_edit(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        if session.status == 'CANCELLED':
            return Response(
                {'error': 'Session annulée — créez une nouvelle identification'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mode = (request.data.get('mode') or 'full').strip().lower()
        if mode not in ('biographic', 'biometric', 'full'):
            return Response(
                {'error': 'mode invalide — biographic | biometric | full'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.status = 'PENDING'
        session.error_message = None
        session.progress_percentage = 0
        session.completed_at = None
        session.validation_errors = []

        if mode in ('biometric', 'full'):
            session.ensure_modality_status()
            for modality in ('face', 'fingerprint', 'iris', 'document', 'signature'):
                session.set_modality_status(modality, 'pending')

        session.save(
            update_fields=[
                'status',
                'error_message',
                'progress_percentage',
                'completed_at',
                'validation_errors',
                'modality_status',
                'updated_at',
            ]
        )

        EnrollmentEvent.objects.create(
            session=session,
            event_type='session_reopened',
            event_data={'mode': mode},
            message=f'Session rouverte pour modification ({mode})',
            created_by=request.user.username if request.user.is_authenticated else 'system',
        )

        serializer = EnrollmentResponseSerializer(session)
        return Response(serializer.data)

    @extend_schema(summary="Mettre à jour les données employé d'une session guichet")
    @action(detail=False, methods=['patch'], url_path='employee/(?P<session_id>[^/.]+)')
    def update_employee(self, request, session_id=None):
        session = get_object_or_404(EnrollmentSession, session_id=session_id)
        if session.status == 'CANCELLED':
            return Response({'error': 'Session annulée'}, status=status.HTTP_400_BAD_REQUEST)

        employee = request.data.get('employee')
        if not isinstance(employee, dict):
            return Response(
                {'error': 'employee (objet) requis'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = dict(session.payload or {})
        payload['employee'] = employee
        session.payload = payload
        session.payload_hash = self._calculate_payload_hash(payload)

        matricule = (employee.get('registration_number') or '').strip()
        if matricule:
            session.registration_number = matricule

        session.save(
            update_fields=['payload', 'payload_hash', 'registration_number', 'updated_at']
        )

        EnrollmentEvent.objects.create(
            session=session,
            event_type='employee_updated',
            event_data={'registration_number': matricule or None},
            message='Données biographiques mises à jour',
            created_by=request.user.username if request.user.is_authenticated else 'system',
        )

        serializer = EnrollmentResponseSerializer(session)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Rechercher des sessions d'enrôlement",
        request=EnrollmentSearchSerializer
    )
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Recherche avancée de sessions d'enrôlement"""
        search_serializer = EnrollmentSearchSerializer(data=request.data)
        if not search_serializer.is_valid():
            return Response(
                {'error': 'Critères de recherche invalides', 'details': search_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        filters = search_serializer.validated_data
        queryset = self.get_queryset()
        
        # Appliquer les filtres
        if filters.get('session_id'):
            queryset = queryset.filter(session_id__icontains=filters['session_id'])
        
        if filters.get('registration_number'):
            queryset = queryset.filter(
                registration_number__icontains=filters['registration_number']
            )
        
        if filters.get('channel'):
            queryset = queryset.filter(channel=filters['channel'])
        
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        if filters.get('operator_id'):
            queryset = queryset.filter(operator_id__icontains=filters['operator_id'])
        
        if filters.get('date_from'):
            queryset = queryset.filter(created_at__date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(created_at__date__lte=filters['date_to'])
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EnrollmentResponseSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EnrollmentResponseSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Annuler une session d'enrôlement",
        parameters=[
            OpenApiParameter(name='session_id', description='ID de la session', required=True, type=str)
        ]
    )
    @action(detail=False, methods=['post'], url_path='cancel/(?P<session_id>[^/.]+)')
    def cancel_session(self, request, session_id=None):
        """Annuler une session d'enrôlement"""
        try:
            session = get_object_or_404(EnrollmentSession, session_id=session_id)
            
            if session.status in ['COMPLETED', 'FAILED', 'CANCELLED']:
                return Response(
                    {'error': 'La session ne peut pas être annulée dans son état actuel'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            session.status = 'CANCELLED'
            session.save()
            
            # Créer l'événement d'annulation
            EnrollmentEvent.objects.create(
                session=session,
                event_type='session_cancelled',
                event_data={'reason': request.data.get('reason', 'Annulation manuelle')},
                message=f"Session annulée: {request.data.get('reason', 'Annulation manuelle')}",
                created_by=request.user.username if request.user.is_authenticated else 'system'
            )
            
            serializer = EnrollmentResponseSerializer(session)
            return Response(serializer.data)
            
        except EnrollmentSession.DoesNotExist:
            return Response(
                {'error': 'Session non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _calculate_payload_hash(self, payload):
        """Calcule le hash SHA-256 du payload"""
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()


class EnrollmentValidationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les validations d'enrôlement
    """
    queryset = EnrollmentValidation.objects.all()
    serializer_class = EnrollmentValidationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['validation_type', 'status', 'session']
    ordering_fields = ['created_at', 'completed_at']
    ordering = ['-created_at']


class EnrollmentEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les événements d'enrôlement
    """
    queryset = EnrollmentEvent.objects.all()
    serializer_class = EnrollmentEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['event_type', 'session', 'created_by']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class EnrollmentReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les récépissés d'enrôlement
    """
    queryset = EnrollmentReceipt.objects.all()
    serializer_class = EnrollmentReceiptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['registration_number', 'session']
    search_fields = ['registration_number', 'receipt_number']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @extend_schema(
        summary="Obtenir un récépissé par matricule",
        parameters=[
            OpenApiParameter(name='registration_number', description='Matricule RH', required=True, type=str)
        ]
    )
    @action(detail=False, methods=['get'], url_path='by-matricule/(?P<registration_number>[^/.]+)')
    def get_by_matricule(self, request, registration_number=None):
        """Obtenir un récépissé par matricule RH."""
        try:
            receipt = get_object_or_404(EnrollmentReceipt, registration_number=registration_number)
            serializer = EnrollmentReceiptSerializer(receipt)
            return Response(serializer.data)
        except EnrollmentReceipt.DoesNotExist:
            return Response(
                {'error': 'Récépissé non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )


class EnrollmentStatsViewSet(viewsets.ViewSet):
    """
    ViewSet pour les statistiques d'enrôlement
    """
    # Dev-only: ouvrir pour tableau de bord
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Obtenir les statistiques d'enrôlement",
        parameters=[
            OpenApiParameter(name='date_from', description='Date de début', required=False, type=str),
            OpenApiParameter(name='date_to', description='Date de fin', required=False, type=str),
            OpenApiParameter(name='channel', description='Canal', required=False, type=str),
        ]
    )
    @action(detail=False, methods=['get'])
    def get_stats(self, request):
        """Obtenir les statistiques d'enrôlement"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        channel = request.query_params.get('channel')
        
        # Construire la requête
        queryset = EnrollmentStatistics.objects.all()
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        if channel:
            queryset = queryset.filter(channel=channel)
        
        # Calculer les statistiques
        stats = []
        for stat in queryset:
            success_rate = (stat.completed_sessions / stat.total_sessions * 100) if stat.total_sessions > 0 else 0
            abis_hit_rate = (stat.abis_hits / stat.total_sessions * 100) if stat.total_sessions > 0 else 0
            
            stats.append({
                'date': stat.date,
                'channel': stat.channel,
                'total_sessions': stat.total_sessions,
                'completed_sessions': stat.completed_sessions,
                'failed_sessions': stat.failed_sessions,
                'abis_hits': stat.abis_hits,
                'abis_reviews': stat.abis_reviews,
                'avg_processing_time_ms': stat.avg_processing_time_ms,
                'success_rate': round(success_rate, 2),
                'abis_hit_rate': round(abis_hit_rate, 2)
            })
        
        return Response(stats)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de vérification de santé du service
    """
    return Response({
        'status': 'healthy',
        'service': 'Enrollment Gateway',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats(request):
    """Statistiques agrégées pour le tableau de bord guichet agents ONIP."""
    try:
        from django.db.models import Count
        from django.utils import timezone

        from .models import EnrollmentSession

        def safe_scalar(sql):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    row = cursor.fetchone()
                    return int(row[0]) if row and row[0] is not None else 0
            except Exception:
                return 0

        now = timezone.now()
        start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_enrolled = EnrollmentSession.objects.filter(status='COMPLETED').count()
        enrollments_today = EnrollmentSession.objects.filter(
            status='COMPLETED', created_at__gte=start_today
        ).count()
        enrollments_this_month = EnrollmentSession.objects.filter(
            status='COMPLETED', created_at__gte=start_month
        ).count()

        sessions_total = EnrollmentSession.objects.count()
        sessions_failed = EnrollmentSession.objects.filter(status='FAILED').count()
        sessions_with_matricule = EnrollmentSession.objects.exclude(
            registration_number__isnull=True
        ).exclude(registration_number='').count()

        by_status = {
            row['status']: row['count']
            for row in EnrollmentSession.objects.values('status').annotate(count=Count('id'))
        }

        by_province = {}
        try:
            province_counts = (
                EnrollmentSession.objects
                .filter(status='COMPLETED')
                .values('location__province')
                .annotate(count=Count('id'))
            )
            for row in province_counts:
                key = row.get('location__province') or 'Non renseignée'
                by_province[key] = row['count']
        except Exception:
            by_province = {}

        total_sessions = sessions_total or 1
        quality_score = total_enrolled / total_sessions

        recent_sessions = []
        for session in EnrollmentSession.objects.order_by('-created_at')[:8]:
            payload = session.payload or {}
            recent_sessions.append({
                'session_id': session.session_id,
                'registration_number': session.registration_number or payload.get('registration_number') or '',
                'agent_name': EnrollmentSession.agent_display_name(payload) or '—',
                'status': session.status,
                'modality_status': session.modality_status or {},
                'created_at': session.created_at.isoformat() if session.created_at else None,
            })

        system_health = {
            'status': 'HEALTHY',
            'uptime': 3600 * 24,
            'response_time': 120,
        }

        return Response({
            'total_enrolled': total_enrolled,
            'enrollments_today': enrollments_today,
            'enrollments_this_month': enrollments_this_month,
            'sessions_total': sessions_total,
            'sessions_failed': sessions_failed,
            'sessions_with_matricule': sessions_with_matricule,
            'biometric_total': safe_scalar('SELECT COUNT(*) FROM fgp_biometric'),
            'fingerprints_total': safe_scalar('SELECT COUNT(*) FROM fgp_fingerprints'),
            'by_status': by_status,
            'by_province': by_province,
            'recent_sessions': recent_sessions,
            'quality_score': quality_score,
            'system_health': system_health,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)
