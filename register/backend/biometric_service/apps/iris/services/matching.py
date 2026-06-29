"""
Service de matching d'iris
Gère la comparaison et recherche de correspondances
"""

import logging
import pickle
from django.conf import settings

from ..models import IrisTemplate, IrisMatch
from .modules import IrisMatcher

logger = logging.getLogger(__name__)


class IrisMatchingService:
    """
    Service pour comparer des templates d'iris
    """
    
    def __init__(self):
        self.config = settings.BIOMETRIC_SETTINGS['IRIS']
        self.matcher = IrisMatcher(
            threshold=self.config['MATCHING_THRESHOLD']
        )
    
    def compare_templates(self, template1, template2):
        """
        Compare deux templates d'iris
        
        Args:
            template1: IrisTemplate
            template2: IrisTemplate
            
        Returns:
            IrisMatch: Résultat de la comparaison
        """
        logger.info(f"Comparaison templates {template1.id} et {template2.id}")
        
        # Désérialiser les templates
        data1 = pickle.loads(template1.template_data)
        data2 = pickle.loads(template2.template_data)
        
        # Comparer
        is_match, score = self.matcher.compare_templates(data1, data2)
        
        # Calculer la distance de Hamming
        distance = 1.0 - score
        
        # Obtenir le décalage de rotation optimal
        _, shift = self.matcher.compare_with_rotation(data1, data2)
        
        # Créer l'objet IrisMatch
        match = IrisMatch.objects.create(
            template_1=template1,
            template_2=template2,
            is_match=is_match,
            similarity_score=score,
            hamming_distance=distance,
            rotation_shift=shift,
            matching_threshold=self.matcher.threshold
        )
        
        logger.info(f"Match créé: {match.id} - Score: {score:.2%} ({'✓' if is_match else '✗'})")
        
        return match
    
    def search_duplicates(self, template, limit=10):
        """
        Cherche des duplicatas potentiels dans la base
        
        Args:
            template: IrisTemplate à chercher
            limit: Nombre maximum de résultats
            
        Returns:
            list: Liste de (IrisTemplate, score) ordonnée par score
        """
        logger.info(f"Recherche duplicatas pour template {template.id}")
        
        # Désérialiser le template à chercher
        search_data = pickle.loads(template.template_data)
        
        # Récupérer tous les autres templates (même position d'œil)
        eye_position = template.capture.eye_position
        other_templates = IrisTemplate.objects.filter(
            capture__eye_position=eye_position
        ).exclude(
            id=template.id
        ).select_related('capture')
        
        results = []
        
        for other_template in other_templates:
            try:
                # Désérialiser
                other_data = pickle.loads(other_template.template_data)
                
                # Comparer
                is_match, score = self.matcher.compare_templates(search_data, other_data)
                
                if score > 0.3:  # Seuil minimal pour considérer
                    results.append((other_template, score, is_match))
                    
            except Exception as e:
                logger.warning(f"Erreur comparaison avec template {other_template.id}: {e}")
                continue
        
        # Trier par score décroissant
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Limiter les résultats
        results = results[:limit]
        
        logger.info(f"Trouvé {len(results)} correspondances potentielles")
        
        return results
    
    def verify_identity(self, template1, template2):
        """
        Vérifie si deux templates correspondent à la même personne (1:1)
        
        Args:
            template1: Premier template
            template2: Deuxième template
            
        Returns:
            bool: True si correspondance
        """
        logger.info(f"Vérification identité: {template1.id} vs {template2.id}")
        
        data1 = pickle.loads(template1.template_data)
        data2 = pickle.loads(template2.template_data)
        
        is_match = self.matcher.verify(data1, data2)
        
        logger.info(f"Résultat vérification: {'✓ Match' if is_match else '✗ Pas de match'}")
        
        return is_match
    
    def identify_person(self, template, database_templates, top_n=5):
        """
        Identifie une personne dans une base de templates (1:N)
        
        Args:
            template: Template à identifier
            database_templates: Liste de templates de la base
            top_n: Nombre de résultats à retourner
            
        Returns:
            list: Liste de (template, score) ordonnée par score
        """
        logger.info(f"Identification pour template {template.id} dans {len(database_templates)} templates")
        
        search_data = pickle.loads(template.template_data)
        
        # Préparer les données de la base
        db_data = []
        for db_template in database_templates:
            try:
                data = pickle.loads(db_template.template_data)
                db_data.append(data)
            except Exception as e:
                logger.warning(f"Erreur chargement template {db_template.id}: {e}")
                db_data.append(None)
        
        # Identifier
        results = self.matcher.identify(search_data, [d for d in db_data if d is not None], top_n=top_n)
        
        # Mapper les résultats aux templates
        mapped_results = []
        for idx, score in results:
            if idx < len(database_templates):
                mapped_results.append((database_templates[idx], score))
        
        logger.info(f"Identification terminée: {len(mapped_results)} résultats")
        
        return mapped_results

