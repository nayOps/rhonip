"""
Services pour l'Enrollment Gateway
"""
import requests
import time
import base64
import hashlib
import json
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from .models import EnrollmentSession, EnrollmentEvent, EnrollmentValidation


class EnrollmentOrchestrator:
    """
    Orchestrateur principal pour le processus d'enrôlement
    """
    
    def __init__(self):
        self.fgp_core_url = settings.ENROLLMENT_SETTINGS['FGP_CORE_URL']
        self.rh_service_url = settings.ENROLLMENT_SETTINGS.get(
            'RH_SERVICE_URL', 'http://server:8000'
        )
        self.abis_service_url = settings.ENROLLMENT_SETTINGS['ABIS_SERVICE_URL']
    
    def process_enrollment(self, session_id):
        """
        Traite une session d'enrôlement complète
        """
        try:
            session = EnrollmentSession.objects.get(id=session_id)
            
            # Mise à jour du statut
            session.update_progress(10, 'VALIDATING')
            self._create_event(session, 'validation_started', 'Début de la validation')
            
            # Étape 1: Validation des données
            validation_result = self._validate_enrollment_data(session)
            if not validation_result['success']:
                session.mark_failed(f"Échec de validation: {validation_result['errors']}")
                return False
            
            session.update_progress(30, 'ABIS_CHECK')
            self._create_event(session, 'abis_check_started', 'Début de la vérification ABIS')
            
            # Étape 2: Vérification ABIS (déduplication)
            abis_result = self._check_abis_duplicates(session)
            fp_local_result = self._check_local_fingerprint_duplicates(session)
            if fp_local_result.get('decision') == 'HIT':
                # Priorité au matching empreintes local (avant enrôlement final)
                abis_result = fp_local_result
            if abis_result.get('decision') == 'ERROR':
                # ABIS indisponible en dev : ne pas bloquer l'enrôlement guichet
                abis_result = {'decision': 'NO_HIT', 'matches': [], 'max_score': 0.0}
            if abis_result['decision'] == 'HIT':
                session.mark_failed("Doublon biométrique détecté")
                session.abis_result = abis_result
                session.save()
                return False
            elif abis_result['decision'] == 'REVIEW':
                session.update_progress(50, 'REVIEW')
                session.abis_result = abis_result
                session.save()
                self._create_event(session, 'abis_review_required', 'Révision manuelle requise')
                return True  # En attente de révision
            
            session.update_progress(60, 'PROCESSING')
            
            # Étape 3: Fiche employé RH (matricule)
            employee_result = self._upsert_employee(session)
            if not employee_result['success']:
                session.mark_failed(f"Échec enregistrement employé: {employee_result['error']}")
                return False
            
            matricule = employee_result['registration_number']
            session.registration_number = matricule
            session.employee_status = employee_result.get('status', 'created')
            session.update_progress(75, 'PROCESSING')
            self._create_event(session, 'employee_upserted', f'Matricule: {matricule}')

            # Étape 4: Médias biométriques → FGP Core (best-effort)
            media_result = self._persist_enrollment_media(session)
            if media_result.get('errors'):
                self._create_event(
                    session,
                    'media_persist_partial',
                    f"Médias partiels: {'; '.join(media_result['errors'][:5])}",
                )
            else:
                self._create_event(session, 'media_persisted', 'Biométrie enregistrée')

            photo_sync = self._sync_employee_photo_to_rh(session)
            if photo_sync.get('success'):
                self._create_event(session, 'employee_photo_synced', 'Photo RH synchronisée')
            elif photo_sync.get('skipped'):
                pass
            else:
                self._create_event(
                    session,
                    'employee_photo_sync_failed',
                    photo_sync.get('error', 'Photo RH non synchronisée'),
                )
            
            # Étape 5: Finalisation
            session.mark_completed(matricule)
            session.abis_result = abis_result
            processing_time = int((time.time() - session.created_at.timestamp()) * 1000)
            session.processing_time_ms = processing_time
            session.save()
            
            self._create_event(
                session,
                'session_completed',
                f'Session terminée — matricule: {matricule}',
            )
            
            self._generate_receipt(session)
            
            return True
            
        except Exception as e:
            session.mark_failed(f"Erreur lors du traitement: {str(e)}")
            self._create_event(session, 'session_failed', f'Erreur: {str(e)}')
            return False
    
    def _validate_enrollment_data(self, session):
        """
        Valide les données d'enrôlement
        """
        try:
            validator = ValidationService()
            
            fp_status = session.get_modality_status('fingerprint')
            fp_optional = fp_status in ('skipped', 'pending')

            face_status = session.get_modality_status('face')
            biometrics = (session.payload or {}).get('biometrics') or {}
            face_data = biometrics.get('face') or {}
            face_ref = str(face_data.get('ref') or '')
            face_optional = (
                settings.ENROLLMENT_SETTINGS.get('BIOMETRIC_FACE_QUALITY_OPTIONAL', True)
                or face_status in ('skipped', 'pending')
                or face_ref.startswith('pending://')
                or not face_data.get('image_base64')
            )

            # Validation du schéma
            schema_validation = validator.validate_schema(
                session.payload,
                fingerprint_skipped=fp_optional,
                face_skipped=face_optional,
            )
            if not schema_validation['valid']:
                return {'success': False, 'errors': schema_validation['errors']}
            
            # Validation métier
            business_validation = validator.validate_business_rules(session.payload)
            if not business_validation['valid']:
                return {'success': False, 'errors': business_validation['errors']}
            
            # Validation biométrique (empreintes / photo optionnelles en guichet)
            biometric_validation = validator.validate_biometrics(
                session.payload.get('biometrics', {}),
                fingerprint_skipped=fp_optional,
                face_skipped=face_optional,
            )
            if not biometric_validation['valid']:
                return {'success': False, 'errors': biometric_validation['errors']}
            
            return {'success': True, 'errors': []}
            
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def _check_abis_duplicates(self, session):
        """
        Vérifie les doublons biométriques via ABIS
        """
        try:
            from .abis_service import ABISService
            abis_service = ABISService()
            
            # Préparer les données biométriques pour ABIS
            biometric_data = session.payload.get('biometrics', {})
            
            # Recherche 1:N
            search_result = abis_service.search_duplicates(biometric_data)
            
            return search_result
            
        except Exception as e:
            return {
                'decision': 'ERROR',
                'error': str(e),
                'matches': []
            }

    def _check_local_fingerprint_duplicates(self, session):
        """
        Matching 1:N local basé sur le hash de template empreinte.
        Exécuté avant création FGP Core pour bloquer un doublon évident.
        """
        try:
            biometrics = (session.payload or {}).get('biometrics') or {}
            fp = biometrics.get('fingerprints') or {}
            fingers = fp.get('fingers') or []
            if not isinstance(fingers, list):
                return {'decision': 'NO_HIT', 'matches': [], 'max_score': 0.0}

            template_hashes = []
            for finger in fingers:
                if str(finger.get('status', '')).upper() != 'CAPTURED':
                    continue
                tpl_b64 = finger.get('template_base64')
                if not tpl_b64 or not isinstance(tpl_b64, str):
                    continue
                try:
                    raw = base64.b64decode(tpl_b64)
                except Exception:
                    continue
                template_hashes.append(hashlib.sha256(raw).hexdigest())

            if not template_hashes:
                return {'decision': 'NO_HIT', 'matches': [], 'max_score': 0.0}

            matricule = session.resolve_registration_number()
            if not matricule:
                employee = (session.payload or {}).get('employee') or {}
                matricule = (employee.get('registration_number') or '').strip() or None

            placeholders = ','.join(['%s'] * len(template_hashes))
            sql = (
                "SELECT registration_number, finger_position, template_hash "
                "FROM fgp_fingerprints "
                f"WHERE template_hash IN ({placeholders}) "
            )
            params = list(template_hashes)
            if matricule:
                # Empreintes déjà persistées pour CE matricule (étape guichet) ≠ doublon inter-personnes.
                sql += "AND registration_number <> %s "
                params.append(str(matricule))
            sql += "ORDER BY registration_number, finger_position"

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()

            if not rows:
                return {'decision': 'NO_HIT', 'matches': [], 'max_score': 0.0}

            matches = [
                {
                    'registration_number': r[0],
                    'finger_position': r[1],
                    'template_hash': r[2],
                    'similarity_score': 1.0,
                    'source': 'local_fingerprint_hash',
                }
                for r in rows
            ]
            return {
                'decision': 'HIT',
                'matches': matches,
                'max_score': 1.0,
                'reason': 'Empreintes déjà enregistrées (matching local template_hash)',
            }
        except Exception as exc:
            # Ne pas casser l'enrôlement en cas d'erreur technique de matching local.
            return {'decision': 'ERROR', 'error': str(exc), 'matches': []}
    
    def _normalize_rh_gender(self, value):
        if value is None:
            return value
        raw = str(value).strip()
        if not raw:
            return raw
        upper = raw.upper()
        if upper in ('M', 'MALE', 'MASCULIN', 'H'):
            return 'male'
        if upper in ('F', 'FEMALE', 'FEMININ', 'FÉMININ'):
            return 'female'
        return raw.lower()

    def _upsert_employee(self, session):
        """Crée ou met à jour la fiche employé RH via l'API guichet interne."""
        try:
            employee_data = dict(session.payload.get('employee') or {})
            matricule = employee_data.get('registration_number')
            if not matricule:
                return {'success': False, 'error': 'Matricule manquant dans le payload'}

            if employee_data.get('gender') is not None:
                employee_data['gender'] = self._normalize_rh_gender(employee_data.get('gender'))

            headers = {'Content-Type': 'application/json'}
            internal_key = getattr(settings, 'GUICHET_INTERNAL_API_KEY', None)
            if internal_key:
                headers['X-Guichet-Internal-Key'] = internal_key

            response = requests.post(
                f"{self.rh_service_url}/api/guichet/employee/upsert/",
                json=employee_data,
                headers=headers,
                timeout=30,
            )

            if response.status_code in (200, 201):
                data = response.json().get('data') or response.json()
                return {
                    'success': True,
                    'registration_number': data.get('registration_number', matricule),
                    'status': response.json().get('status', 'created'),
                    'data': data,
                }
            return {
                'success': False,
                'error': f"Erreur RH: {response.status_code} - {response.text}",
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _sync_employee_photo_to_rh(self, session):
        """Envoie la photo biométrique vers employee.photo (RH) après capture."""
        from .enrollment_storage import load_session_face_photo_base64

        matricule = session.registration_number or session.resolve_registration_number()
        if not matricule:
            return {'skipped': True}

        photo_b64 = load_session_face_photo_base64(session)
        if not photo_b64:
            return {'skipped': True}

        headers = {'Content-Type': 'application/json'}
        internal_key = getattr(settings, 'GUICHET_INTERNAL_API_KEY', None)
        if internal_key:
            headers['X-Guichet-Internal-Key'] = internal_key

        try:
            response = requests.post(
                f"{self.rh_service_url}/api/guichet/employee/upsert/",
                json={
                    'registration_number': matricule,
                    'photo_base64': photo_b64,
                },
                headers=headers,
                timeout=60,
            )
            if response.status_code in (200, 201):
                return {'success': True}
            return {
                'success': False,
                'error': f"Photo RH: {response.status_code} - {response.text[:200]}",
            }
        except Exception as exc:
            return {'success': False, 'error': str(exc)}

    def finalize_session_with_photo(self, session, *, dry_run=False):
        """
        Finalise une session ayant une photo : sync RH + statut COMPLETED.
        Utilisé pour rattraper les sessions FAILED / PENDING avec photo capturée.
        """
        from .enrollment_storage import session_has_face_photo

        session.sync_registration_number_from_payload(save=True)
        matricule = session.registration_number
        if not matricule:
            return {
                'session_id': session.session_id,
                'ok': False,
                'error': 'matricule manquant',
            }
        if not session_has_face_photo(session):
            return {
                'session_id': session.session_id,
                'ok': False,
                'error': 'photo introuvable',
            }
        if dry_run:
            return {
                'session_id': session.session_id,
                'ok': True,
                'dry_run': True,
                'matricule': matricule,
                'status': session.status,
            }

        self._persist_enrollment_media(session)
        photo_sync = self._sync_employee_photo_to_rh(session)
        if not photo_sync.get('success'):
            err = photo_sync.get('error') or 'photo non synchronisée'
            if photo_sync.get('skipped'):
                err = 'photo non synchronisée (données absentes)'
            return {
                'session_id': session.session_id,
                'matricule': matricule,
                'ok': False,
                'error': err,
            }

        session.set_modality_status('face', 'completed')
        session.error_message = None
        session.validation_errors = []
        session.mark_completed(matricule)
        self._create_event(
            session,
            'backfill_photo_completed',
            f'Rattrapage photo — matricule {matricule}',
        )
        return {
            'session_id': session.session_id,
            'matricule': matricule,
            'ok': True,
        }

    def resync_completed_session_photo(self, session, *, dry_run=False):
        """Re-synchronise la photo RH pour une session déjà COMPLETED."""
        from .enrollment_storage import session_has_face_photo

        if session.status != 'COMPLETED':
            return {
                'session_id': session.session_id,
                'ok': False,
                'error': 'session non terminée',
            }
        session.sync_registration_number_from_payload(save=True)
        matricule = session.registration_number
        if not matricule or not session_has_face_photo(session):
            return {
                'session_id': session.session_id,
                'ok': False,
                'error': 'matricule ou photo manquant',
            }
        if dry_run:
            return {
                'session_id': session.session_id,
                'ok': True,
                'dry_run': True,
                'matricule': matricule,
            }

        photo_sync = self._sync_employee_photo_to_rh(session)
        if not photo_sync.get('success'):
            err = photo_sync.get('error') or 'sync échouée'
            return {
                'session_id': session.session_id,
                'matricule': matricule,
                'ok': False,
                'error': err,
            }
        self._create_event(
            session,
            'employee_photo_synced',
            f'Photo RH re-synchronisée — {matricule}',
        )
        return {
            'session_id': session.session_id,
            'matricule': matricule,
            'ok': True,
        }

    def backfill_sessions_with_photos(
        self,
        *,
        dry_run=False,
        statuses=None,
        resync_completed=False,
    ):
        """Finalise ou re-synchronise toutes les sessions éligibles avec photo."""
        from .enrollment_storage import session_has_face_photo

        if statuses is None:
            statuses = [
                'PENDING', 'FAILED', 'REVIEW',
                'VALIDATING', 'PROCESSING', 'ABIS_CHECK',
            ]

        results = []
        for session in EnrollmentSession.objects.filter(status__in=statuses).order_by('updated_at'):
            if not session_has_face_photo(session):
                continue
            results.append(self.finalize_session_with_photo(session, dry_run=dry_run))

        if resync_completed:
            for session in EnrollmentSession.objects.filter(status='COMPLETED').order_by('-updated_at'):
                if not session_has_face_photo(session):
                    continue
                matricule = session.registration_number or session.resolve_registration_number()
                if matricule and self._rh_employee_has_photo(matricule):
                    continue
                results.append(self.resync_completed_session_photo(session, dry_run=dry_run))

        return results

    def _rh_employee_has_photo(self, matricule: str) -> bool:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT photo FROM employee_employee WHERE registration_number = %s LIMIT 1",
                [matricule],
            )
            row = cursor.fetchone()
        if not row or not row[0]:
            return False
        return bool(str(row[0]).strip())

    def _persist_enrollment_media(self, session):
        """Écrit les fichiers biométriques et les promeut vers le service biométrique."""
        from .enrollment_storage import (
            persist_session_biometric_files,
            persist_session_biometrics,
            persist_session_fingerprints,
        )

        errors = []
        payload = dict(session.payload or {})
        try:
            payload['persisted_media'] = persist_session_biometric_files(session)
        except Exception as exc:
            errors.append(f'biometrics: {exc}')
            payload['persisted_media'] = {}

        session.payload = payload
        session.save(update_fields=['payload', 'updated_at'])

        matricule = session.registration_number
        if matricule:
            try:
                bio_result = persist_session_biometrics(
                    session,
                    matricule,
                    self.fgp_core_url,
                    payload.get('persisted_media') or {},
                )
                if bio_result.get('saved') is False and bio_result.get('status') not in (None, 'no_data'):
                    errors.append(f"biometric: HTTP {bio_result.get('status')}")
                fp_result = persist_session_fingerprints(
                    session,
                    matricule,
                    self.fgp_core_url,
                    payload.get('persisted_media') or {},
                )
                if fp_result.get('errors'):
                    errors.extend([f"fingerprints: {e}" for e in fp_result['errors'][:10]])
            except Exception as exc:
                errors.append(f'biometric persist: {exc}')

        return {'errors': errors}

    def _generate_receipt(self, session):
        """
        Génère le récépissé d'enrôlement
        """
        try:
            from .receipt_service import ReceiptService
            receipt_service = ReceiptService()
            
            receipt = receipt_service.generate_receipt(session)
            
            self._create_event(
                session,
                'receipt_generated',
                f'Récépissé généré: {receipt.receipt_number}'
            )
            
        except Exception as e:
            self._create_event(
                session,
                'receipt_error',
                f'Erreur génération récépissé: {str(e)}'
            )
    
    def _create_event(self, session, event_type, message, event_data=None):
        """
        Crée un événement d'enrôlement
        """
        EnrollmentEvent.objects.create(
            session=session,
            event_type=event_type,
            event_data=event_data or {},
            message=message
        )


class ValidationService:
    """
    Service de validation des données d'enrôlement
    """
    
    def __init__(self):
        self.required_employee_fields = [
            'registration_number', 'first_name', 'last_name', 'gender', 'payment_method'
        ]
        self.required_biometric_fields = ['face', 'fingerprints']

    @staticmethod
    def _normalize_strata(strata):
        alias = {
            'ELECTEUR': 'ELECTEURS',
            'ETUDIANT': 'ETUDIANTS',
        }
        return [alias.get(str(s), str(s)) for s in (strata or [])]

    @staticmethod
    def _normalize_phone_for_rcd(phone):
        """
        Normalise un numéro RDC vers +243XXXXXXXXX quand possible,
        sans bloquer le flux de soumission guichet.
        """
        if phone is None:
            return phone
        raw = str(phone).strip()
        if not raw:
            return raw

        # Garder uniquement les chiffres (on traite le '+' séparément).
        digits = ''.join(ch for ch in raw if ch.isdigit())
        if not digits:
            return raw

        if digits.startswith('243') and len(digits) >= 12:
            return f"+{digits}"
        if digits.startswith('0') and len(digits) >= 10:
            return f"+243{digits[1:]}"
        if len(digits) == 9:
            return f"+243{digits}"
        if raw.startswith('+') and digits.startswith('243'):
            return raw
        return raw
    
    def validate_schema(self, payload, fingerprint_skipped=False, face_skipped=False):
        """
        Valide le schéma JSON du payload
        """
        errors = []
        
        required_fields = ['employee', 'biometrics']
        for field in required_fields:
            if field not in payload:
                errors.append(f"Champ obligatoire manquant: {field}")
        
        if 'employee' in payload:
            employee_data = payload['employee']
            for field in self.required_employee_fields:
                if field not in employee_data or not employee_data[field]:
                    errors.append(f"Champ employé obligatoire manquant: {field}")
        
        # Vérifier les données biométriques
        if 'biometrics' in payload:
            biometric_data = payload['biometrics']
            skip_fp = fingerprint_skipped
            skip_face = face_skipped or settings.ENROLLMENT_SETTINGS.get(
                'BIOMETRIC_FACE_QUALITY_OPTIONAL', True
            )
            for field in self.required_biometric_fields:
                if field == 'fingerprints' and skip_fp:
                    continue
                if field == 'face' and skip_face:
                    continue
                if field not in biometric_data or not biometric_data[field]:
                    errors.append(f"Donnée biométrique obligatoire manquante: {field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_business_rules(self, payload):
        """Valide les règles métier employé RH."""
        errors = []
        employee = payload.get('employee') or {}
        gender = employee.get('gender')
        if gender and gender not in ('male', 'female', 'M', 'F'):
            errors.append(f"Genre invalide: {gender}")
        payment = employee.get('payment_method')
        if payment and payment not in ('cash', 'bank', 'mobile money'):
            errors.append(f"Mode de paiement invalide: {payment}")
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def validate_biometrics(self, biometric_data, fingerprint_skipped=False, face_skipped=False):
        """
        Valide les données biométriques
        """
        errors = []

        if fingerprint_skipped and face_skipped:
            return {'valid': True, 'errors': []}

        skip_face = face_skipped or settings.ENROLLMENT_SETTINGS.get(
            'BIOMETRIC_FACE_QUALITY_OPTIONAL', True
        )
        
        quality_threshold = settings.ENROLLMENT_SETTINGS.get('BIOMETRIC_QUALITY_THRESHOLD', 0.7)
        
        for biometric_type, data in biometric_data.items():
            if fingerprint_skipped and biometric_type == 'fingerprints':
                continue
            if skip_face and biometric_type == 'face':
                continue
            if not isinstance(data, dict):
                continue
            if biometric_type == 'face':
                ref = str(data.get('ref') or '')
                if ref.startswith('pending://') or not data.get('image_base64'):
                    continue
                try:
                    quality = float(data.get('quality', 0))
                except (TypeError, ValueError):
                    quality = 0.0
                if quality <= 0:
                    continue
            if 'quality' in data:
                quality = data['quality']
                try:
                    quality = float(quality)
                except (TypeError, ValueError):
                    quality = 0.0
                if quality > 1:
                    quality = round(quality / 100.0, 4)
                if quality < quality_threshold:
                    errors.append(
                        f"Qualité biométrique insuffisante pour {biometric_type}: {quality} < {quality_threshold}"
                    )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


class ABISService:
    """
    Service ABIS pour la déduplication biométrique
    """
    
    def __init__(self):
        self.abis_url = settings.ENROLLMENT_SETTINGS['ABIS_SERVICE_URL']
        self.face_threshold = settings.ENROLLMENT_SETTINGS.get('ABIS_FACE_THRESHOLD', 0.8)
        self.fingerprint_threshold = settings.ENROLLMENT_SETTINGS.get('ABIS_FINGERPRINT_THRESHOLD', 0.9)
    
    def search_duplicates(self, biometric_data):
        """
        Recherche des doublons biométriques
        """
        try:
            # Préparer les données pour ABIS
            search_payload = {
                'templates': []
            }
            
            for biometric_type, data in biometric_data.items():
                if isinstance(data, dict) and 'ref' in data:
                    template_data = {
                        'type': biometric_type,
                        'data': data['ref'],
                        'quality': data.get('quality', 1.0)
                    }
                    search_payload['templates'].append(template_data)
            
            # Appel à ABIS
            response = requests.post(
                f"{self.abis_url}/api/v1/abis/search/",
                json=search_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                abis_result = response.json()
                
                # Analyser les résultats
                return self._analyze_abis_result(abis_result)
            else:
                return {
                    'decision': 'ERROR',
                    'error': f"Erreur ABIS: {response.status_code}",
                    'matches': []
                }
                
        except Exception as e:
            return {
                'decision': 'ERROR',
                'error': str(e),
                'matches': []
            }
    
    def _analyze_abis_result(self, abis_result):
        """
        Analyse les résultats ABIS et prend une décision
        """
        matches = abis_result.get('matches', [])
        
        if not matches:
            return {
                'decision': 'NO_HIT',
                'matches': [],
                'max_score': 0.0
            }
        
        # Trouver le meilleur match
        best_match = max(matches, key=lambda x: x.get('similarity_score', 0))
        max_score = best_match.get('similarity_score', 0)
        
        # Déterminer la décision basée sur le seuil
        if max_score >= self.face_threshold:
            decision = 'HIT'
        elif max_score >= 0.7:  # Zone grise
            decision = 'REVIEW'
        else:
            decision = 'NO_HIT'
        
        return {
            'decision': decision,
            'matches': matches,
            'max_score': max_score,
            'best_match': best_match
        }


class ReceiptService:
    """
    Service de génération de récépissés
    """
    
    def generate_receipt(self, session):
        """
        Génère un récépissé d'enrôlement
        """
        from .models import EnrollmentReceipt
        import qrcode
        import io
        import base64
        
        # Générer le numéro de récépissé
        receipt_number = f"REC-{session.registration_number}-{session.created_at.strftime('%Y%m%d%H%M%S')}"
        employee = session.payload.get('employee') or {}
        receipt_content = {
            'receipt_number': receipt_number,
            'registration_number': session.registration_number,
            'full_name': self._get_full_name(employee),
            'enrollment_date': session.completed_at.isoformat(),
            'channel': session.channel,
            'location': session.location,
            'operator_id': session.operator_id,
            'device_id': session.device_id,
        }
        qr_data = {
            'registration_number': session.registration_number,
            'receipt_number': receipt_number,
        }
        
        qr_code = qrcode.QRCode(version=1, box_size=10, border=5)
        qr_code.add_data(json.dumps(qr_data))
        qr_code.make(fit=True)
        
        # Convertir en base64
        img_buffer = io.BytesIO()
        qr_code.make_image().save(img_buffer, format='PNG')
        qr_code_b64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Créer le récépissé
        receipt = EnrollmentReceipt.objects.create(
            session=session,
            registration_number=session.registration_number,
            receipt_number=receipt_number,
            receipt_content=receipt_content,
            qr_code_data=qr_code_b64,
            expires_at=session.completed_at + timedelta(days=365)  # Valide 1 an
        )
        
        return receipt
    
    def _get_full_name(self, employee_data):
        parts = [
            employee_data.get('last_name', ''),
            employee_data.get('middle_name', ''),
            employee_data.get('first_name', ''),
        ]
        return ' '.join(filter(None, parts))
