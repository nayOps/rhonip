"""
Service de traitement d'iris
Gère la segmentation, normalisation et encodage
"""

import logging
import time
import pickle
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
import cv2
import numpy as np

from ..models import IrisCapture, IrisTemplate, IrisQualityLog
from .modules import IrisSegmentation, IrisMatcher

logger = logging.getLogger(__name__)


class IrisProcessingService:
    """
    Service pour traiter les captures d'iris
    """
    
    def __init__(self):
        self.config = settings.BIOMETRIC_SETTINGS['IRIS']
        self.segmenter = IrisSegmentation(
            min_radius=self.config['MIN_RADIUS'],
            max_radius=self.config['MAX_RADIUS']
        )
        self.matcher = IrisMatcher(
            threshold=self.config['MATCHING_THRESHOLD']
        )
    
    def process_capture(self, capture):
        """
        Traite une capture d'iris complète
        (segmentation + normalisation + encodage + qualité)
        
        Args:
            capture: IrisCapture object
            
        Returns:
            tuple: (IrisTemplate, IrisQualityLog)
        """
        logger.info(f"Traitement de la capture {capture.id}")
        
        start_time = time.time()
        
        try:
            # Charger l'image de l'œil
            if not capture.eye_region:
                raise Exception("Aucune image eye_region disponible")
            
            eye_image = self._load_image(capture.eye_region.path)
            
            # Segmentation
            logger.debug("Segmentation de l'iris...")
            segmentation = self.segmenter.segment_iris(eye_image)
            
            if not segmentation or not segmentation.get('iris'):
                logger.warning("Segmentation échouée")
                capture.is_valid = False
                capture.save()
                return None, None
            
            # Sauvegarder les données de segmentation
            iris = segmentation['iris']
            pupil = segmentation.get('pupil')
            
            capture.iris_center_x = iris[0]
            capture.iris_center_y = iris[1]
            capture.iris_radius = iris[2]
            
            if pupil:
                capture.pupil_center_x = pupil[0]
                capture.pupil_center_y = pupil[1]
                capture.pupil_radius = pupil[2]
            
            # Visualisation de la segmentation
            if self.config['SAVE_IMAGES']:
                vis = self.segmenter.visualize_segmentation(eye_image, segmentation)
                vis_bytes = self._image_to_bytes(vis)
                capture.segmented_iris.save(
                    f"{capture.id}_segmented.jpg",
                    ContentFile(vis_bytes),
                    save=False
                )
            
            # Évaluation de la qualité
            logger.debug("Évaluation de la qualité...")
            quality = self.segmenter.check_quality(segmentation, eye_image)
            
            capture.quality_score = quality['overall']
            capture.size_score = quality.get('size', 0)
            capture.centering_score = quality.get('centering', 0)
            capture.contrast_score = quality.get('contrast', 0)
            capture.is_valid = quality['valid']
            
            # Normalisation
            logger.debug("Normalisation de l'iris...")
            normalized = self.segmenter.normalize_iris(eye_image, segmentation)
            
            if normalized is None:
                logger.warning("Normalisation échouée")
                capture.is_valid = False
                capture.save()
                return None, None
            
            # Sauvegarder l'iris normalisé
            if self.config['SAVE_IMAGES']:
                norm_bytes = self._image_to_bytes(normalized)
                capture.normalized_iris.save(
                    f"{capture.id}_normalized.jpg",
                    ContentFile(norm_bytes),
                    save=False
                )
            
            capture.processed_at = timezone.now()
            capture.save()
            
            # Encodage du template
            logger.debug("Encodage du template...")
            template = self._encode_template(capture, normalized)
            
            # Log de qualité
            processing_duration = time.time() - start_time
            quality_log = self._create_quality_log(
                capture,
                quality,
                segmentation,
                processing_duration
            )
            
            logger.info(f"Traitement terminé en {processing_duration:.2f}s - Qualité: {quality['overall']:.2%}")
            
            return template, quality_log
            
        except Exception as e:
            logger.error(f"Erreur traitement capture {capture.id}: {e}")
            capture.is_valid = False
            capture.save()
            raise
    
    def _encode_template(self, capture, normalized_iris):
        """
        Encode un iris normalisé en template
        
        Args:
            capture: IrisCapture
            normalized_iris: Image normalisée
            
        Returns:
            IrisTemplate: Template créé
        """
        logger.debug(f"Encodage template pour capture {capture.id}")
        
        # Encoder avec le matcher
        template_data = self.matcher.encode_iris(normalized_iris)
        
        if not template_data:
            raise Exception("Encodage du template échoué")
        
        # Sérialiser le template
        template_bytes = pickle.dumps(template_data)
        
        # Créer l'objet IrisTemplate
        template = IrisTemplate.objects.create(
            capture=capture,
            template_data=template_bytes,
            encoding_method=template_data['method'],
            template_size=len(template_bytes),
            code_shape_filters=template_data['shape'][0],
            code_shape_height=template_data['shape'][1],
            code_shape_width=template_data['shape'][2],
        )
        
        logger.info(f"Template créé: {template.id} ({template.template_size} bytes)")
        
        return template
    
    def _create_quality_log(self, capture, quality, segmentation, processing_duration):
        """
        Crée un log de qualité détaillé
        
        Args:
            capture: IrisCapture
            quality: Dict de scores de qualité
            segmentation: Résultat de la segmentation
            processing_duration: Durée du traitement
            
        Returns:
            IrisQualityLog
        """
        issues = []
        
        if quality['overall'] < self.config['MIN_QUALITY_SCORE']:
            issues.append("Qualité globale insuffisante")
        
        if quality.get('size', 1) < 0.7:
            issues.append("Taille de l'iris non optimale")
        
        if quality.get('centering', 1) < 0.7:
            issues.append("Iris mal centré")
        
        if quality.get('contrast', 1) < 0.5:
            issues.append("Contraste insuffisant")
        
        quality_log = IrisQualityLog.objects.create(
            capture=capture,
            overall_score=quality['overall'],
            size_score=quality.get('size', 0),
            centering_score=quality.get('centering', 0),
            contrast_score=quality.get('contrast', 0),
            capture_duration=0,  # Will be set by capture service
            processing_duration=processing_duration,
            pupil_detected=segmentation.get('pupil') is not None,
            iris_detected=segmentation.get('iris') is not None,
            issues=issues
        )
        
        return quality_log
    
    def _load_image(self, path):
        """
        Charge une image depuis un chemin
        
        Args:
            path: Chemin vers l'image
            
        Returns:
            numpy array
        """
        image = cv2.imread(str(path))
        if image is None:
            raise Exception(f"Impossible de charger l'image {path}")
        return image
    
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

