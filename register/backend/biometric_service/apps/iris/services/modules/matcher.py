"""
Matcher pour comparer des iris
Basé sur les filtres de Gabor et distance de Hamming
"""

import numpy as np
import cv2
from scipy.signal import convolve2d


class IrisMatcher:
    """
    Classe pour comparer des templates d'iris
    """
    
    def __init__(self, threshold=0.35):
        """
        Initialise le matcher
        
        Args:
            threshold: Seuil de distance de Hamming (0-1, plus bas = plus strict)
        """
        self.threshold = threshold
    
    def create_gabor_filters(self, num_filters=8):
        """
        Crée une banque de filtres de Gabor
        
        Args:
            num_filters: Nombre de filtres
            
        Returns:
            list: Liste de filtres de Gabor
        """
        filters = []
        
        ksize = 21  # Taille du noyau
        sigma = 3.0  # Écart-type
        lambd = 10.0  # Longueur d'onde
        gamma = 0.5  # Rapport d'aspect
        psi = 0  # Décalage de phase
        
        for i in range(num_filters):
            theta = np.pi * i / num_filters  # Orientation
            
            kernel = cv2.getGaborKernel(
                (ksize, ksize),
                sigma,
                theta,
                lambd,
                gamma,
                psi,
                ktype=cv2.CV_32F
            )
            
            filters.append(kernel)
        
        return filters
    
    def encode_iris(self, normalized_iris):
        """
        Encode l'iris normalisé en code binaire
        
        Args:
            normalized_iris: Image normalisée de l'iris
            
        Returns:
            dict: Template avec code et masque
        """
        if normalized_iris is None:
            return None
        
        # S'assurer que c'est en niveaux de gris
        if len(normalized_iris.shape) == 3:
            gray = cv2.cvtColor(normalized_iris, cv2.COLOR_BGR2GRAY)
        else:
            gray = normalized_iris
        
        # Normaliser les valeurs
        gray = gray.astype(float) / 255.0
        
        # Créer les filtres de Gabor
        gabor_filters = self.create_gabor_filters(num_filters=8)
        
        # Appliquer les filtres
        responses = []
        
        for gabor_filter in gabor_filters:
            # Convoluer avec le filtre
            filtered = cv2.filter2D(gray, cv2.CV_32F, gabor_filter)
            responses.append(filtered)
        
        # Empiler les réponses
        response_stack = np.array(responses)
        
        # Encodage binaire (phase quantization)
        # Partie réelle > 0 => 1, sinon 0
        code = (response_stack > 0).astype(np.uint8)
        
        # Créer un masque pour les régions valides
        # (exclure les paupières, reflets, etc.)
        mask = self._create_quality_mask(gray)
        
        template = {
            'code': code,
            'mask': mask,
            'shape': code.shape,
            'method': 'gabor_phase'
        }
        
        return template
    
    def _create_quality_mask(self, iris_image):
        """
        Crée un masque de qualité pour ignorer les zones invalides
        
        Args:
            iris_image: Image normalisée de l'iris
            
        Returns:
            numpy.ndarray: Masque binaire
        """
        # Détecter les zones trop sombres ou trop claires (reflets, paupières)
        mask = np.ones(iris_image.shape, dtype=np.uint8)
        
        # Exclure les pixels très sombres (< 0.1)
        mask[iris_image < 0.1] = 0
        
        # Exclure les pixels très clairs (> 0.9) - reflets
        mask[iris_image > 0.9] = 0
        
        return mask
    
    def hamming_distance(self, code1, code2, mask1=None, mask2=None):
        """
        Calcule la distance de Hamming entre deux codes
        
        Args:
            code1: Premier code binaire
            code2: Deuxième code binaire
            mask1: Masque du premier code (optionnel)
            mask2: Masque du deuxième code (optionnel)
            
        Returns:
            float: Distance de Hamming normalisée (0-1)
        """
        # XOR pour trouver les bits différents
        xor = np.bitwise_xor(code1, code2)
        
        # Appliquer les masques si fournis
        if mask1 is not None and mask2 is not None:
            # Masque combiné (AND)
            combined_mask = np.bitwise_and(mask1, mask2)
            
            # Compter seulement les bits masqués
            xor_masked = xor * combined_mask
            
            num_different = np.sum(xor_masked)
            num_total = np.sum(combined_mask)
        else:
            num_different = np.sum(xor)
            num_total = xor.size
        
        if num_total == 0:
            return 1.0  # Distance maximale si aucun bit valide
        
        distance = num_different / num_total
        
        return distance
    
    def compare_with_rotation(self, template1, template2, max_shift=15):
        """
        Compare deux templates avec compensation de rotation
        
        Args:
            template1: Premier template
            template2: Deuxième template
            max_shift: Décalage maximum en pixels pour compenser la rotation
            
        Returns:
            tuple: (best_distance, best_shift)
        """
        code1 = template1['code']
        code2 = template2['code']
        mask1 = template1.get('mask')
        mask2 = template2.get('mask')
        
        best_distance = 1.0
        best_shift = 0
        
        # Tester différents décalages circulaires (rotation)
        for shift in range(-max_shift, max_shift + 1):
            # Décaler code2 circulairement
            code2_shifted = np.roll(code2, shift, axis=2)
            
            if mask2 is not None:
                mask2_shifted = np.roll(mask2, shift, axis=1)
            else:
                mask2_shifted = None
            
            # Calculer la distance
            distance = self.hamming_distance(code1, code2_shifted, mask1, mask2_shifted)
            
            if distance < best_distance:
                best_distance = distance
                best_shift = shift
        
        return (best_distance, best_shift)
    
    def compare_templates(self, template1, template2):
        """
        Compare deux templates d'iris
        
        Args:
            template1: Premier template
            template2: Deuxième template
            
        Returns:
            tuple: (match, score)
        """
        if template1 is None or template2 is None:
            return (False, 0.0)
        
        # Vérifier la compatibilité
        if template1['code'].shape != template2['code'].shape:
            print("⚠ Templates de tailles différentes")
            return (False, 0.0)
        
        # Comparer avec compensation de rotation
        distance, shift = self.compare_with_rotation(template1, template2)
        
        # Convertir distance en score de similarité
        score = 1.0 - distance
        
        # Vérifier le seuil
        is_match = distance <= self.threshold
        
        return (is_match, score)
    
    def match(self, template, database):
        """
        Cherche une correspondance dans une base de données
        
        Args:
            template: Template à chercher
            database: Liste de templates
            
        Returns:
            tuple: (best_match_index, score) ou (None, 0.0)
        """
        best_match = None
        best_score = 0.0
        
        for i, db_template in enumerate(database):
            is_match, score = self.compare_templates(template, db_template)
            
            if score > best_score:
                best_score = score
                if is_match:
                    best_match = i
        
        return (best_match, best_score)
    
    def verify(self, template1, template2):
        """
        Vérifie si deux templates correspondent (1:1)
        
        Args:
            template1: Premier template
            template2: Deuxième template
            
        Returns:
            bool: True si correspondance
        """
        is_match, _ = self.compare_templates(template1, template2)
        return is_match
    
    def identify(self, template, database, top_n=5):
        """
        Identifie les meilleures correspondances
        
        Args:
            template: Template à identifier
            database: Liste de templates
            top_n: Nombre de résultats à retourner
            
        Returns:
            list: Liste de tuples (index, score) triés par score
        """
        results = []
        
        for i, db_template in enumerate(database):
            _, score = self.compare_templates(template, db_template)
            results.append((i, score))
        
        # Trier par score décroissant
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_n]
    
    def calculate_similarity(self, template1, template2):
        """
        Calcule le score de similarité entre deux templates
        
        Args:
            template1: Premier template
            template2: Deuxième template
            
        Returns:
            float: Score de similarité (0-1)
        """
        _, score = self.compare_templates(template1, template2)
        return score

