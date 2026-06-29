"""
Segmentation et détection de l'iris
Algorithmes de traitement d'image pour isoler l'iris
"""

import cv2
import numpy as np
from scipy import ndimage


class IrisSegmentation:
    """
    Classe pour segmenter et isoler l'iris dans une image d'œil
    """
    
    def __init__(self, min_radius=30, max_radius=120):
        """
        Initialise le segmenteur
        
        Args:
            min_radius: Rayon minimum de l'iris en pixels
            max_radius: Rayon maximum de l'iris en pixels
        """
        self.min_radius = min_radius
        self.max_radius = max_radius
    
    def preprocess(self, eye_image):
        """
        Prétraite l'image de l'œil
        
        Args:
            eye_image: Image de l'œil (BGR ou grayscale)
            
        Returns:
            numpy.ndarray: Image prétraitée en niveaux de gris
        """
        # Convertir en niveaux de gris si nécessaire
        if len(eye_image.shape) == 3:
            gray = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = eye_image.copy()
        
        # Égalisation d'histogramme pour améliorer le contraste
        gray = cv2.equalizeHist(gray)
        
        # Réduction du bruit
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return gray
    
    def detect_pupil(self, gray_image):
        """
        Détecte la pupille (cercle sombre au centre)
        
        Args:
            gray_image: Image en niveaux de gris
            
        Returns:
            tuple: (x, y, radius) de la pupille ou None
        """
        # Inverser l'image (pupille devient claire)
        inverted = cv2.bitwise_not(gray_image)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            inverted, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Détection de cercles avec Hough Transform
        circles = cv2.HoughCircles(
            binary,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=15,
            minRadius=int(self.min_radius * 0.3),
            maxRadius=int(self.max_radius * 0.5)
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype(int)
            # Retourner le cercle le plus centré
            h, w = gray_image.shape
            center = (w // 2, h // 2)
            
            best_circle = min(circles, key=lambda c: 
                             np.sqrt((c[0] - center[0])**2 + (c[1] - center[1])**2))
            
            return tuple(best_circle)
        
        return None
    
    def detect_iris(self, gray_image, pupil=None):
        """
        Détecte l'iris (cercle autour de la pupille)
        
        Args:
            gray_image: Image en niveaux de gris
            pupil: (x, y, radius) de la pupille (optionnel)
            
        Returns:
            tuple: (x, y, radius) de l'iris ou None
        """
        # Détection de cercles
        circles = cv2.HoughCircles(
            gray_image,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype(int)
            
            # Si pupille connue, chercher le cercle concentrique
            if pupil is not None:
                px, py, pr = pupil
                
                # Trouver le cercle le plus proche de la pupille
                candidates = []
                for (x, y, r) in circles:
                    # Distance entre centres
                    dist = np.sqrt((x - px)**2 + (y - py)**2)
                    # L'iris doit englober la pupille
                    if r > pr and dist < 20:
                        candidates.append((x, y, r))
                
                if candidates:
                    # Prendre le cercle avec le rayon le plus approprié
                    best = min(candidates, key=lambda c: abs(c[2] - pr * 2.5))
                    return best
            else:
                # Retourner le cercle le plus centré
                h, w = gray_image.shape
                center = (w // 2, h // 2)
                
                best_circle = min(circles, key=lambda c: 
                                 np.sqrt((c[0] - center[0])**2 + (c[1] - center[1])**2))
                
                return tuple(best_circle)
        
        return None
    
    def segment_iris(self, eye_image):
        """
        Segmente l'iris complet (détection pupille + iris)
        
        Args:
            eye_image: Image de l'œil
            
        Returns:
            dict: Informations de segmentation
        """
        # Prétraitement
        gray = self.preprocess(eye_image)
        
        # Détecter la pupille
        pupil = self.detect_pupil(gray)
        
        # Détecter l'iris
        iris = self.detect_iris(gray, pupil)
        
        if iris is None:
            print("⚠ Iris non détecté")
            return None
        
        result = {
            'pupil': pupil,
            'iris': iris,
            'image_gray': gray,
            'image_original': eye_image
        }
        
        return result
    
    def create_iris_mask(self, image_shape, iris, pupil=None):
        """
        Crée un masque pour isoler l'iris
        
        Args:
            image_shape: (height, width) de l'image
            iris: (x, y, radius) de l'iris
            pupil: (x, y, radius) de la pupille (optionnel)
            
        Returns:
            numpy.ndarray: Masque binaire
        """
        mask = np.zeros(image_shape, dtype=np.uint8)
        
        ix, iy, ir = iris
        
        # Dessiner le cercle de l'iris
        cv2.circle(mask, (ix, iy), ir, 255, -1)
        
        # Retirer la pupille si fournie
        if pupil is not None:
            px, py, pr = pupil
            cv2.circle(mask, (px, py), pr, 0, -1)
        
        return mask
    
    def extract_iris_region(self, eye_image, segmentation):
        """
        Extrait la région de l'iris isolée
        
        Args:
            eye_image: Image de l'œil
            segmentation: Résultat de segment_iris()
            
        Returns:
            numpy.ndarray: Image de l'iris isolé
        """
        if segmentation is None:
            return None
        
        # Créer le masque
        mask = self.create_iris_mask(
            eye_image.shape[:2],
            segmentation['iris'],
            segmentation['pupil']
        )
        
        # Appliquer le masque
        if len(eye_image.shape) == 3:
            iris_only = cv2.bitwise_and(eye_image, eye_image, mask=mask)
        else:
            iris_only = cv2.bitwise_and(eye_image, eye_image, mask=mask)
        
        return iris_only
    
    def normalize_iris(self, eye_image, segmentation, output_size=(256, 64)):
        """
        Normalise l'iris en coordonnées polaires (Daugman's rubber sheet model)
        
        Args:
            eye_image: Image de l'œil
            segmentation: Résultat de segment_iris()
            output_size: (width, height) de l'image normalisée
            
        Returns:
            numpy.ndarray: Iris normalisé
        """
        if segmentation is None:
            return None
        
        iris = segmentation['iris']
        pupil = segmentation['pupil']
        
        if iris is None:
            return None
        
        # Convertir en niveaux de gris si nécessaire
        if len(eye_image.shape) == 3:
            gray = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = eye_image
        
        ix, iy, ir = iris
        
        if pupil is not None:
            px, py, pr = pupil
        else:
            px, py, pr = ix, iy, 0
        
        width, height = output_size
        normalized = np.zeros((height, width), dtype=np.uint8)
        
        # Transformation polaire
        for theta_idx in range(width):
            theta = 2 * np.pi * theta_idx / width
            
            for r_idx in range(height):
                # Interpolation radiale entre pupille et iris
                r = pr + (ir - pr) * r_idx / height
                
                # Coordonnées cartésiennes
                x = int(px + r * np.cos(theta))
                y = int(py + r * np.sin(theta))
                
                # Vérifier les limites
                if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:
                    normalized[r_idx, theta_idx] = gray[y, x]
        
        return normalized
    
    def visualize_segmentation(self, eye_image, segmentation):
        """
        Visualise la segmentation
        
        Args:
            eye_image: Image de l'œil
            segmentation: Résultat de segment_iris()
            
        Returns:
            numpy.ndarray: Image avec cercles dessinés
        """
        if segmentation is None:
            return eye_image
        
        vis = eye_image.copy()
        
        # Dessiner l'iris
        if segmentation['iris'] is not None:
            ix, iy, ir = segmentation['iris']
            cv2.circle(vis, (ix, iy), ir, (0, 255, 0), 2)
            cv2.circle(vis, (ix, iy), 2, (0, 255, 0), 3)
        
        # Dessiner la pupille
        if segmentation['pupil'] is not None:
            px, py, pr = segmentation['pupil']
            cv2.circle(vis, (px, py), pr, (255, 0, 0), 2)
            cv2.circle(vis, (px, py), 2, (255, 0, 0), 3)
        
        return vis
    
    def check_quality(self, segmentation, eye_image):
        """
        Évalue la qualité de la segmentation
        
        Args:
            segmentation: Résultat de segment_iris()
            eye_image: Image de l'œil
            
        Returns:
            dict: Scores de qualité
        """
        if segmentation is None:
            return {'overall': 0, 'valid': False}
        
        scores = {}
        
        # Vérifier la présence de l'iris
        if segmentation['iris'] is None:
            return {'overall': 0, 'valid': False}
        
        ix, iy, ir = segmentation['iris']
        
        # Score de taille (rayon approprié)
        size_score = 1.0 if self.min_radius <= ir <= self.max_radius else 0.5
        scores['size'] = size_score
        
        # Score de centrage
        h, w = eye_image.shape[:2]
        center_x, center_y = w / 2, h / 2
        center_dist = np.sqrt((ix - center_x)**2 + (iy - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        center_score = 1.0 - (center_dist / max_dist)
        scores['centering'] = center_score
        
        # Score de contraste
        if segmentation['pupil'] is not None:
            mask = self.create_iris_mask(
                eye_image.shape[:2],
                segmentation['iris'],
                segmentation['pupil']
            )
            
            if len(eye_image.shape) == 3:
                gray = cv2.cvtColor(eye_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = eye_image
            
            iris_pixels = gray[mask > 0]
            
            if len(iris_pixels) > 0:
                contrast = iris_pixels.std()
                contrast_score = min(contrast / 50.0, 1.0)  # Normaliser
                scores['contrast'] = contrast_score
            else:
                scores['contrast'] = 0.0
        else:
            scores['contrast'] = 0.5
        
        # Score global
        overall = np.mean(list(scores.values()))
        scores['overall'] = overall
        scores['valid'] = overall > 0.5
        
        return scores

