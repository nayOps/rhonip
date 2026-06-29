"""
Tâches Celery pour l'application Enrollment
"""
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_enrollment_async(self, session_id):
    """
    Tâche asynchrone pour traiter une session d'enrôlement
    """
    try:
        from .services import EnrollmentOrchestrator
        
        logger.info(f"Début du traitement de la session {session_id}")
        
        # Créer l'orchestrateur et traiter la session
        orchestrator = EnrollmentOrchestrator()
        success = orchestrator.process_enrollment(session_id)
        
        if success:
            logger.info(f"Session {session_id} traitée avec succès")
            return {'status': 'success', 'session_id': session_id}
        else:
            logger.error(f"Échec du traitement de la session {session_id}")
            return {'status': 'failed', 'session_id': session_id}
            
    except Exception as exc:
        logger.error(f"Erreur lors du traitement de la session {session_id}: {str(exc)}")
        
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_expired_sessions():
    """
    Tâche de nettoyage des sessions expirées
    """
    from datetime import timedelta
    from django.utils import timezone
    from .models import EnrollmentSession
    
    try:
        # Supprimer les sessions en attente depuis plus de 24h
        cutoff_time = timezone.now() - timedelta(hours=24)
        expired_sessions = EnrollmentSession.objects.filter(
            status='PENDING',
            created_at__lt=cutoff_time
        )
        
        count = expired_sessions.count()
        expired_sessions.delete()
        
        logger.info(f"Nettoyage terminé: {count} sessions expirées supprimées")
        return {'cleaned_sessions': count}
        
    except Exception as exc:
        logger.error(f"Erreur lors du nettoyage: {str(exc)}")
        raise exc


@shared_task
def generate_daily_statistics():
    """
    Tâche de génération des statistiques quotidiennes
    """
    from datetime import date, timedelta
    from django.db.models import Count, Avg, Min, Max
    from .models import EnrollmentSession, EnrollmentStatistics
    
    try:
        yesterday = date.today() - timedelta(days=1)
        
        # Calculer les statistiques par canal
        channels = ['fixed', 'mobile', 'itinerant', 'school', 'pnc', 'fardc', 'prison', 'refugee', 'ceni']
        
        for channel in channels:
            sessions = EnrollmentSession.objects.filter(
                channel=channel,
                created_at__date=yesterday
            )
            
            total_sessions = sessions.count()
            completed_sessions = sessions.filter(status='COMPLETED').count()
            failed_sessions = sessions.filter(status='FAILED').count()
            
            # Statistiques ABIS
            abis_hits = sessions.filter(abis_result__decision='HIT').count()
            abis_reviews = sessions.filter(abis_result__decision='REVIEW').count()
            
            # Temps de traitement
            completed_with_time = sessions.filter(
                status='COMPLETED',
                processing_time_ms__isnull=False
            )
            
            if completed_with_time.exists():
                avg_time = completed_with_time.aggregate(avg=Avg('processing_time_ms'))['avg'] or 0
                min_time = completed_with_time.aggregate(min=Min('processing_time_ms'))['min'] or 0
                max_time = completed_with_time.aggregate(max=Max('processing_time_ms'))['max'] or 0
            else:
                avg_time = min_time = max_time = 0
            
            # Créer ou mettre à jour les statistiques
            stats, created = EnrollmentStatistics.objects.get_or_create(
                date=yesterday,
                channel=channel,
                defaults={
                    'total_sessions': total_sessions,
                    'completed_sessions': completed_sessions,
                    'failed_sessions': failed_sessions,
                    'abis_hits': abis_hits,
                    'abis_reviews': abis_reviews,
                    'avg_processing_time_ms': int(avg_time),
                    'min_processing_time_ms': int(min_time),
                    'max_processing_time_ms': int(max_time),
                }
            )
            
            if not created:
                # Mettre à jour les statistiques existantes
                stats.total_sessions = total_sessions
                stats.completed_sessions = completed_sessions
                stats.failed_sessions = failed_sessions
                stats.abis_hits = abis_hits
                stats.abis_reviews = abis_reviews
                stats.avg_processing_time_ms = int(avg_time)
                stats.min_processing_time_ms = int(min_time)
                stats.max_processing_time_ms = int(max_time)
                stats.save()
        
        logger.info(f"Statistiques générées pour {yesterday}")
        return {'date': yesterday.isoformat(), 'channels_processed': len(channels)}
        
    except Exception as exc:
        logger.error(f"Erreur lors de la génération des statistiques: {str(exc)}")
        raise exc


@shared_task
def send_enrollment_notifications():
    """
    Tâche d'envoi des notifications d'enrôlement
    """
    from .models import EnrollmentSession
    from .services import NotificationService
    
    try:
        # Trouver les sessions terminées récemment sans notification
        recent_sessions = EnrollmentSession.objects.filter(
            status='COMPLETED',
            completed_at__isnull=False,
            notification_sent=False
        )[:100]  # Traiter par lots de 100
        
        notification_service = NotificationService()
        sent_count = 0
        
        for session in recent_sessions:
            try:
                # Envoyer la notification
                notification_service.send_enrollment_notification(session)
                session.notification_sent = True
                session.save()
                sent_count += 1
                
            except Exception as exc:
                logger.error(f"Erreur notification session {session.id}: {str(exc)}")
        
        logger.info(f"Notifications envoyées: {sent_count}")
        return {'notifications_sent': sent_count}
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi des notifications: {str(exc)}")
        raise exc


@shared_task
def validate_enrollment_data_async(session_id, validation_type):
    """
    Tâche asynchrone pour valider les données d'enrôlement
    """
    try:
        from .models import EnrollmentSession, EnrollmentValidation
        from .services import ValidationService
        
        session = EnrollmentSession.objects.get(id=session_id)
        validator = ValidationService()
        
        # Créer l'enregistrement de validation
        validation = EnrollmentValidation.objects.create(
            session=session,
            validation_type=validation_type,
            status='PENDING'
        )
        
        # Effectuer la validation selon le type
        if validation_type == 'schema':
            result = validator.validate_schema(session.payload)
        elif validation_type == 'business':
            result = validator.validate_business_rules(session.payload)
        elif validation_type == 'biometric':
            fp_status = session.get_modality_status('fingerprint')
            face_status = session.get_modality_status('face')
            result = validator.validate_biometrics(
                session.payload.get('biometrics', {}),
                fingerprint_skipped=fp_status in ('skipped', 'pending'),
                face_skipped=face_status in ('skipped', 'pending')
                or settings.ENROLLMENT_SETTINGS.get('BIOMETRIC_FACE_QUALITY_OPTIONAL', True),
            )
        else:
            raise ValueError(f"Type de validation inconnu: {validation_type}")
        
        # Mettre à jour le résultat
        validation.status = 'PASSED' if result['valid'] else 'FAILED'
        validation.validation_result = result
        validation.error_details = result.get('errors', [])
        validation.save()
        
        logger.info(f"Validation {validation_type} terminée pour session {session_id}")
        return {'validation_type': validation_type, 'valid': result['valid']}
        
    except Exception as exc:
        logger.error(f"Erreur validation {validation_type} session {session_id}: {str(exc)}")
        raise exc


@shared_task
def backup_enrollment_data():
    """
    Tâche de sauvegarde des données d'enrôlement
    """
    from datetime import datetime
    from django.core.management import call_command
    import os
    
    try:
        # Créer le nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"/backups/enrollment_data_{timestamp}.json"
        
        # Créer le répertoire de sauvegarde si nécessaire
        os.makedirs(os.path.dirname(backup_file), exist_ok=True)
        
        # Exporter les données d'enrôlement
        call_command('dumpdata', 'enrollment', output=backup_file, indent=2)
        
        logger.info(f"Sauvegarde créée: {backup_file}")
        return {'backup_file': backup_file}
        
    except Exception as exc:
        logger.error(f"Erreur lors de la sauvegarde: {str(exc)}")
        raise exc


@shared_task
def monitor_system_health():
    """
    Tâche de monitoring de la santé du système
    """
    from .models import EnrollmentSession
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        # Vérifier les sessions en cours depuis trop longtemps
        cutoff_time = timezone.now() - timedelta(minutes=30)
        stuck_sessions = EnrollmentSession.objects.filter(
            status__in=['PENDING', 'VALIDATING', 'PROCESSING', 'ABIS_CHECK'],
            created_at__lt=cutoff_time
        )
        
        stuck_count = stuck_sessions.count()
        
        if stuck_count > 0:
            logger.warning(f"{stuck_count} sessions bloquées détectées")
            
            # Marquer les sessions bloquées comme échouées
            for session in stuck_sessions:
                session.mark_failed("Session bloquée - timeout")
        
        # Vérifier le taux d'erreur
        last_hour = timezone.now() - timedelta(hours=1)
        recent_sessions = EnrollmentSession.objects.filter(created_at__gte=last_hour)
        
        if recent_sessions.exists():
            total = recent_sessions.count()
            failed = recent_sessions.filter(status='FAILED').count()
            error_rate = (failed / total) * 100
            
            if error_rate > 50:  # Seuil d'alerte
                logger.error(f"Taux d'erreur élevé: {error_rate:.1f}%")
        
        return {
            'stuck_sessions': stuck_count,
            'error_rate': error_rate if recent_sessions.exists() else 0
        }
        
    except Exception as exc:
        logger.error(f"Erreur lors du monitoring: {str(exc)}")
        raise exc
