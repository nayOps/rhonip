"""
Matcher pour comparer des empreintes digitales
Basé sur la comparaison de minuties
"""

import numpy as np
from scipy.spatial.distance import cdist


class FingerprintMatcher:
    """
    Classe pour comparer des empreintes digitales
    """
    
    def __init__(self, threshold=0.4):
        """
        Initialise le matcher
        
        Args:
            threshold: Seuil de similarité (0-1, plus bas = plus strict)
        """
        self.threshold = threshold
    
    def compare_templates(self, template1, template2):
        """
        Compare deux templates d'empreintes
        
        Args:
            template1: Premier template
            template2: Deuxième template
            
        Returns:
            tuple: (match, score)
        """
        # Vérifier si ce sont des templates avec minuties
        if 'minutiae' in template1 and 'minutiae' in template2:
            return self._compare_minutiae(template1, template2)
        
        # Sinon, comparaison d'images brutes
        elif 'image_raw' in template1 and 'image_raw' in template2:
            return self._compare_raw_images(template1, template2)
        
        print("❌ Format de template incompatible")
        return (False, 0.0)
    
    def _compare_minutiae(self, template1, template2):
        """
        Compare des templates basés sur les minuties
        
        Args:
            template1: Template avec minuties
            template2: Template avec minuties
            
        Returns:
            tuple: (match, score)
        """
        minutiae1 = template1['minutiae']
        minutiae2 = template2['minutiae']
        
        if len(minutiae1) == 0 or len(minutiae2) == 0:
            return (False, 0.0)
        
        # Extraire les positions
        points1 = np.array([[m['x'], m['y']] for m in minutiae1])
        points2 = np.array([[m['x'], m['y']] for m in minutiae2])
        
        # Calculer la matrice de distances
        distances = cdist(points1, points2, metric='euclidean')
        
        # Trouver les correspondances (distance minimale)
        matches = 0
        max_distance = 20  # Distance maximale pour considérer une correspondance
        
        for i in range(len(points1)):
            min_dist = distances[i].min()
            if min_dist < max_distance:
                matches += 1
        
        # Calculer le score
        max_matches = max(len(minutiae1), len(minutiae2))
        score = matches / max_matches if max_matches > 0 else 0.0
        
        # Vérifier le seuil
        is_match = score >= (1 - self.threshold)
        
        return (is_match, score)
    
    def _compare_raw_images(self, template1, template2):
        """
        Compare des images brutes
        
        Args:
            template1: Template avec image brute
            template2: Template avec image brute
            
        Returns:
            tuple: (match, score)
        """
        try:
            # Convertir en arrays numpy
            img1 = np.frombuffer(template1['image_raw'], dtype=np.uint8)
            img1 = img1.reshape(template1['image_shape'])
            
            img2 = np.frombuffer(template2['image_raw'], dtype=np.uint8)
            img2 = img2.reshape(template2['image_shape'])
            
            # Normaliser
            img1 = img1.astype(float) / 255.0
            img2 = img2.astype(float) / 255.0
            
            # Calculer la corrélation
            correlation = np.corrcoef(img1.flatten(), img2.flatten())[0, 1]
            
            # Score = corrélation (0-1)
            score = (correlation + 1) / 2  # Normaliser à [0, 1]
            
            is_match = score >= (1 - self.threshold)
            
            return (is_match, score)
            
        except Exception as e:
            print(f"❌ Erreur comparaison: {e}")
            return (False, 0.0)
    
    def calculate_similarity(self, template1, template2):
        """
        Calcule seulement le score de similarité
        
        Args:
            template1: Premier template
            template2: Deuxième template
            
        Returns:
            float: Score de similarité (0-1)
        """
        _, score = self.compare_templates(template1, template2)
        return score
    
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

