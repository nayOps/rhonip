"""
Service de capture d'iris
Gère la capture via caméra et la sauvegarde
"""

import logging
import time
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
import cv2
import numpy as np

from ..models import IrisCaptureSession, IrisCapture
from .modules import IrisCamera

logger = logging.getLogger(__name__)


class IrisCaptureService:
    """
    Service pour capturer des iris via caméra
    """
    
    def __init__(self):
        self.config = settings.BIOMETRIC_SETTINGS['IRIS']
        self.camera = None
    
    def start_session(self, enrollment_session_id, operator_id=None, station_id=None):
        """
        Démarre une nouvelle session de capture d'iris
        
        Args:
            enrollment_session_id: UUID de la session d'enrôlement
            operator_id: ID de l'opérateur
            station_id: ID de la station
            
        Returns:
            IrisCaptureSession: Session créée
        """
        logger.info(f"Démarrage session iris pour enrollment {enrollment_session_id}")
        
        session = IrisCaptureSession.objects.create(
            enrollment_session_id=enrollment_session_id,
            status='INITIATED',
            operator_id=operator_id,
            station_id=station_id
        )
        
        # Initialiser la caméra
        try:
            self.camera = IrisCamera(
                camera_index=self.config['CAMERA_INDEX']
            )
            self.camera.connect()
            
            session.status = 'IN_PROGRESS'
            session.save()
            
            logger.info(f"Session iris {session.id} démarrée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation caméra: {e}")
            session.status = 'FAILED'
            session.error_message = str(e)
            session.save()
            raise
        
        return session
    
    def capture_eye(self, session, eye_position, timeout=None):
        """
        Capture un œil spécifique
        
        Args:
            session: IrisCaptureSession
            eye_position: 'LEFT' ou 'RIGHT'
            timeout: Timeout en secondes (optionnel)
            
        Returns:
            IrisCapture: Capture créée
        """
        if timeout is None:
            timeout = self.config['CAPTURE_TIMEOUT']
        
        logger.info(f"Capture de l'œil {eye_position} pour session {session.id}")
        
        # Créer l'objet capture
        capture = IrisCapture.objects.create(
            session=session,
            eye_position=eye_position,
            status='PENDING'
        )
        
        start_time = time.time()
        
        try:
            # Vérifier que la caméra est connectée, sinon la reconnecter
            if not self.camera or not self.camera.connected:
                logger.info(f"Reconnexion de la caméra pour session {session.id}")
                self.camera = IrisCamera(
                    camera_index=self.config['CAMERA_INDEX']
                )
                self.camera.connect()
            
            # Capturer l'iris
            capture_result = self.camera.capture_iris(
                timeout=timeout,
                preview=False  # Pas de preview en mode serveur
            )
            
            if not capture_result:
                capture.status = 'FAILED'
                capture.reason = "Timeout ou capture annulée"
                capture.save()
                return capture
            
            # Sauvegarder les images
            if self.config['SAVE_IMAGES']:
                # Full frame
                full_frame_bytes = self._image_to_bytes(capture_result['full_frame'])
                capture.full_frame.save(
                    f"{session.id}_{eye_position}_full.jpg",
                    ContentFile(full_frame_bytes),
                    save=False
                )
                
                # Eye region
                eye_region_bytes = self._image_to_bytes(capture_result['eye_region'])
                capture.eye_region.save(
                    f"{session.id}_{eye_position}_eye.jpg",
                    ContentFile(eye_region_bytes),
                    save=False
                )
            
            # Mise à jour du statut
            capture.status = 'CAPTURED'
            capture_duration = time.time() - start_time
            
            capture.save()
            
            logger.info(f"Capture {eye_position} réussie en {capture_duration:.2f}s")
            
            return capture
            
        except Exception as e:
            logger.error(f"Erreur capture {eye_position}: {e}")
            capture.status = 'FAILED'
            capture.reason = str(e)
            capture.save()
            raise
    
    def mark_eye_handicap(self, session, eye_position, handicap_type, reason):
        """
        Marque un œil comme handicapé
        
        Args:
            session: IrisCaptureSession
            eye_position: 'LEFT' ou 'RIGHT'
            handicap_type: 'BLIND', 'MISSING', ou 'DAMAGED'
            reason: Raison détaillée
            
        Returns:
            IrisCapture: Capture créée
        """
        logger.info(f"Marquage handicap {handicap_type} pour œil {eye_position}")
        
        capture = IrisCapture.objects.create(
            session=session,
            eye_position=eye_position,
            status=handicap_type,
            reason=reason
        )
        
        return capture
    
    def complete_session(self, session):
        """
        Termine une session de capture
        
        Args:
            session: IrisCaptureSession
            
        Returns:
            IrisCaptureSession: Session mise à jour
        """
        logger.info(f"Finalisation session {session.id}")
        
        # Vérifier que les deux yeux sont traités
        captures = session.captures.all()
        
        if captures.count() < 2:
            logger.warning(f"Session {session.id} incomplète: {captures.count()}/2 yeux")
        
        session.status = 'COMPLETED'
        session.completed_at = timezone.now()
        session.save()
        
        # Fermer la caméra
        if self.camera:
            self.camera.disconnect()
            self.camera = None
        
        logger.info(f"Session {session.id} terminée avec succès")
        
        return session
    
    def cancel_session(self, session, reason=None):
        """
        Annule une session de capture
        
        Args:
            session: IrisCaptureSession
            reason: Raison de l'annulation
            
        Returns:
            IrisCaptureSession: Session mise à jour
        """
        logger.info(f"Annulation session {session.id}")
        
        session.status = 'CANCELLED'
        session.completed_at = timezone.now()
        
        if reason:
            session.notes = reason
        
        session.save()
        
        # Fermer la caméra
        if self.camera:
            self.camera.disconnect()
            self.camera = None
        
        return session
    
    def generate_preview_stream(self, session):
        """
        Génère un stream vidéo avec détection des yeux en temps réel
        
        Args:
            session: IrisCaptureSession
            
        Yields:
            bytes: Frames JPEG encodées
        """
        # Vérifier/reconnecter la caméra
        if not self.camera or not self.camera.connected:
            self.camera = IrisCamera(camera_index=self.config['CAMERA_INDEX'])
            self.camera.connect()
        
        while session.status == 'IN_PROGRESS':
            frame = self.camera.capture_frame()
            
            if frame is None:
                continue
            
            # Copie pour affichage
            display_frame = frame.copy()
            
            # Détecter le visage
            face = self.camera.detect_face(frame)
            
            if face is not None:
                fx, fy, fw, fh = face
                cv2.rectangle(display_frame, (fx, fy), (fx+fw, fy+fh), (0, 255, 0), 2)
                
                # Détecter les yeux
                eyes = self.camera.detect_eyes(frame, face)
                
                if len(eyes) > 0:
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(display_frame, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
                    
                    # Texte de statut
                    cv2.putText(display_frame, f"{len(eyes)} oeil(x) detecte(s) - Cliquez Capturer", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(display_frame, "Visage detecte, cherche les yeux...", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                cv2.putText(display_frame, "Aucun visage detecte", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Encoder en JPEG
            _, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_bytes = buffer.tobytes()
            
            # Format MJPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.033)  # ~30 FPS
    
    def capture_both_eyes(self, session, timeout=10):
        """
        Capture les deux yeux simultanément
        
        Args:
            session: IrisCaptureSession
            timeout: Timeout en secondes
            
        Returns:
            tuple: (capture_left, capture_right) ou (None, None) si échec
        """
        logger.info(f"Capture simultanée des deux yeux pour session {session.id}")
        
        # Vérifier/reconnecter la caméra
        if not self.camera or not self.camera.connected:
            self.camera = IrisCamera(camera_index=self.config['CAMERA_INDEX'])
            self.camera.connect()
        
        start_time = time.time()
        best_capture = None
        
        # Boucle pour trouver une bonne frame avec les deux yeux
        while time.time() - start_time < timeout:
            frame = self.camera.capture_frame()
            
            if frame is None:
                continue
            
            # Détecter le visage
            face = self.camera.detect_face(frame)
            
            if face is not None:
                # Détecter les yeux
                eyes = self.camera.detect_eyes(frame, face)
                
                # Si on détecte 2 yeux, on garde cette capture
                if len(eyes) >= 2:
                    best_capture = {
                        'frame': frame,
                        'eyes': eyes[:2],  # Garder seulement les 2 premiers
                        'face': face
                    }
                    break
                # Si on détecte au moins 1 œil, on garde quand même
                elif len(eyes) == 1:
                    best_capture = {
                        'frame': frame,
                        'eyes': eyes,
                        'face': face
                    }
                    # Ne pas break, continuer à chercher 2 yeux
            else:
                # Même sans détection de visage, capturer la frame après 3 secondes
                if time.time() - start_time > 3 and best_capture is None:
                    logger.info("Capture de la frame sans détection de visage/yeux")
                    best_capture = {
                        'frame': frame,
                        'eyes': [],
                        'face': None
                    }
                    break
        
        if not best_capture:
            logger.warning("Aucune capture possible dans le timeout")
            return (None, None)
        
        # Créer les captures pour chaque œil
        eyes = best_capture['eyes']
        frame = best_capture['frame']
        
        captures = []
        
        if len(eyes) >= 2:
            # Cas idéal: 2 yeux détectés
            # Déterminer LEFT et RIGHT (l'œil à gauche de l'image est l'œil droit de la personne)
            eyes_sorted = sorted(eyes, key=lambda e: e[0])  # Trier par position X
            eye_positions = ['RIGHT', 'LEFT']  # Inversé car miroir
            
            for i, (eye, position) in enumerate(zip(eyes_sorted, eye_positions)):
                capture = IrisCapture.objects.create(
                    session=session,
                    eye_position=position,
                    status='CAPTURED'
                )
                
                # Extraire la région de l'œil
                eye_region = self.camera.extract_eye_region(frame, eye)
                
                # Sauvegarder les images
                if self.config['SAVE_IMAGES']:
                    full_frame_bytes = self._image_to_bytes(frame)
                    capture.full_frame.save(
                        f"{session.id}_{position}_full.jpg",
                        ContentFile(full_frame_bytes),
                        save=False
                    )
                    
                    eye_region_bytes = self._image_to_bytes(eye_region)
                    capture.eye_region.save(
                        f"{session.id}_{position}_eye.jpg",
                        ContentFile(eye_region_bytes),
                        save=False
                    )
                
                capture.save()
                captures.append(capture)
                
                logger.info(f"Capture {position} créée avec succès")
        
        else:
            # Pas de détection automatique: capturer la frame entière pour chaque œil
            # L'utilisateur devra segmenter manuellement ou on traite l'image complète
            logger.info("Capture de la frame complète sans détection d'yeux individuels")
            
            height, width = frame.shape[:2]
            
            # Diviser l'image en deux: gauche = RIGHT eye, droite = LEFT eye (effet miroir)
            for i, position in enumerate(['RIGHT', 'LEFT']):
                capture = IrisCapture.objects.create(
                    session=session,
                    eye_position=position,
                    status='CAPTURED'
                )
                
                # Extraire la moitié de l'image
                if position == 'RIGHT':
                    eye_region = frame[:, :width//2]  # Moitié gauche
                else:
                    eye_region = frame[:, width//2:]  # Moitié droite
                
                # Sauvegarder les images
                if self.config['SAVE_IMAGES']:
                    full_frame_bytes = self._image_to_bytes(frame)
                    capture.full_frame.save(
                        f"{session.id}_{position}_full.jpg",
                        ContentFile(full_frame_bytes),
                        save=False
                    )
                    
                    eye_region_bytes = self._image_to_bytes(eye_region)
                    capture.eye_region.save(
                        f"{session.id}_{position}_eye.jpg",
                        ContentFile(eye_region_bytes),
                        save=False
                    )
                
                capture.save()
                captures.append(capture)
                
                logger.info(f"Capture {position} créée (moitié de frame)")
        
        return tuple(captures) if len(captures) == 2 else (captures[0] if captures else None, None)
    
    def _image_to_bytes(self, image):
        """
        Convertit une image numpy en bytes JPEG
        
        Args:
            image: numpy array
            
        Returns:
            bytes: Image encodée en JPEG
        """
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()
    
    def __del__(self):
        """Cleanup"""
        if self.camera:
            self.camera.disconnect()

