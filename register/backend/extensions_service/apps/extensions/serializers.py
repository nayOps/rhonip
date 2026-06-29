"""
Sérialiseurs pour les extensions par strate du système FGP
"""

from rest_framework import serializers
from .models import (
    ExtensionEducation, ExtensionElectoral, ExtensionPNC, ExtensionFARDC,
    ExtensionPrison, ExtensionRefugie, ExtensionEnfant, ExtensionFonctionnaire
)


class ExtensionEducationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension éducation"""
    
    class Meta:
        model = ExtensionEducation
        fields = [
            'nin', 'matricule_scolaire', 'etablissement', 'code_etablissement',
            'niveau', 'cycle', 'annee_scolaire', 'statut_scolaire', 'section',
            'responsable_tuteur', 'contact_tuteur', 'lien_tuteur',
            'type_etablissement', 'province_etablissement',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_nin(self, value):
        """Validation du format NIN"""
        if not value.startswith('CD-'):
            raise serializers.ValidationError("Le NIN doit commencer par 'CD-'")
        return value

    def validate_annee_scolaire(self, value):
        """Validation de l'année scolaire"""
        if not value or len(value) != 9 or '-' not in value:
            raise serializers.ValidationError("Format d'année scolaire invalide (ex: 2024-2025)")
        return value


class ExtensionElectoralSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension électorale"""
    
    class Meta:
        model = ExtensionElectoral
        fields = [
            'nin', 'centre_vote', 'code_centre_vote', 'circonscription',
            'secteur_vote', 'statut_inscription', 'date_inscription_ceni',
            'bureau_vote', 'province_vote', 'territoire_vote', 'commune_vote',
            'derniere_election', 'participation_historique',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_code_centre_vote(self, value):
        """Validation du code centre de vote"""
        if not value.startswith('CENI-'):
            raise serializers.ValidationError("Le code centre de vote doit commencer par 'CENI-'")
        return value


class ExtensionPNCSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension PNC"""
    
    class Meta:
        model = ExtensionPNC
        fields = [
            'nin', 'matricule_pnc', 'grade', 'unite', 'fonction',
            'date_integration', 'statut_service', 'zone_affectation',
            'type_arme', 'numero_arme', 'specialite',
            'historique_affectations', 'sanctions',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_matricule_pnc(self, value):
        """Validation du matricule PNC"""
        if not value.startswith('PNC-'):
            raise serializers.ValidationError("Le matricule PNC doit commencer par 'PNC-'")
        return value


class ExtensionFARDCSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension FARDC"""
    
    class Meta:
        model = ExtensionFARDC
        fields = [
            'nin', 'matricule_fardc', 'grade', 'unite_affectation',
            'zone_operation', 'fonction', 'date_integration', 'statut_militaire',
            'type_mission', 'arme_service', 'specialite',
            'historique_affectations', 'missions', 'decorations',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_matricule_fardc(self, value):
        """Validation du matricule FARDC"""
        if not value.startswith('FARDC-'):
            raise serializers.ValidationError("Le matricule FARDC doit commencer par 'FARDC-'")
        return value


class ExtensionPrisonSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension prison"""
    
    class Meta:
        model = ExtensionPrison
        fields = [
            'nin', 'numero_dossier_judiciaire', 'centre_detention',
            'statut_detention', 'date_incarceration', 'date_liberation_prevue',
            'infraction', 'autorite_judiciaire', 'duree_peine', 'type_peine',
            'pavillon', 'cellule', 'historique_detention', 'sanctions_disciplinaires',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_date_liberation_prevue(self, value):
        """Validation de la date de libération"""
        if value and hasattr(self, 'initial_data'):
            date_incarceration = self.initial_data.get('date_incarceration')
            if date_incarceration and value < date_incarceration:
                raise serializers.ValidationError("La date de libération ne peut pas être antérieure à la date d'incarcération")
        return value


class ExtensionRefugieSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension réfugié"""
    
    class Meta:
        model = ExtensionRefugie
        fields = [
            'nin', 'numero_hcr', 'pays_origine', 'statut_juridique',
            'document_sejour', 'date_entree_territoire', 'camp_refugie',
            'organisme_encadrement', 'motif_fuite', 'situation_familiale',
            'nombre_enfants', 'historique_demande',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_numero_hcr(self, value):
        """Validation du numéro HCR"""
        if not value.startswith('HCR-'):
            raise serializers.ValidationError("Le numéro HCR doit commencer par 'HCR-'")
        return value


class ExtensionEnfantSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension enfant"""
    
    class Meta:
        model = ExtensionEnfant
        fields = [
            'nin', 'tuteur_nom', 'tuteur_nin', 'lien_tuteur',
            'adresse_tuteur', 'document_parentalite', 'autorisation_parentale',
            'structure_accueil', 'contact_tuteur', 'situation_familiale',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_tuteur_nin(self, value):
        """Validation du NIN du tuteur"""
        if not value.startswith('CD-'):
            raise serializers.ValidationError("Le NIN du tuteur doit commencer par 'CD-'")
        return value


class ExtensionFonctionnaireSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'extension fonctionnaire"""
    
    class Meta:
        model = ExtensionFonctionnaire
        fields = [
            'nin', 'matricule', 'ministere', 'grade',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_matricule(self, value):
        """Validation du matricule fonctionnaire"""
        if value and not value.startswith('FP-'):
            raise serializers.ValidationError("Le matricule fonctionnaire doit commencer par 'FP-'")
        return value


# Sérialiseurs pour les opérations groupées
class ExtensionCreateSerializer(serializers.Serializer):
    """Sérialiseur pour créer plusieurs extensions en une fois"""
    
    education = ExtensionEducationSerializer(required=False)
    electoral = ExtensionElectoralSerializer(required=False)
    pnc = ExtensionPNCSerializer(required=False)
    fardc = ExtensionFARDCSerializer(required=False)
    prison = ExtensionPrisonSerializer(required=False)
    refugee = ExtensionRefugieSerializer(required=False)
    enfant = ExtensionEnfantSerializer(required=False)
    fonctionnaire = ExtensionFonctionnaireSerializer(required=False)

    def validate(self, data):
        """Validation globale"""
        if not any(data.values()):
            raise serializers.ValidationError("Au moins une extension doit être fournie")
        return data


class ExtensionUpdateSerializer(serializers.Serializer):
    """Sérialiseur pour mettre à jour les extensions"""
    
    strata = serializers.CharField(max_length=20)
    data = serializers.DictField()

    def validate_strata(self, value):
        """Validation du type de strate"""
        valid_strata = [
            'education', 'electoral', 'pnc', 'fardc',
            'prison', 'refugee', 'enfant', 'fonctionnaire'
        ]
        if value not in valid_strata:
            raise serializers.ValidationError(f"Strate invalide. Valeurs acceptées: {valid_strata}")
        return value


class ExtensionSearchSerializer(serializers.Serializer):
    """Sérialiseur pour la recherche dans les extensions"""
    
    strata = serializers.CharField(max_length=20, required=False)
    nin = serializers.CharField(max_length=20, required=False)
    search_term = serializers.CharField(max_length=100, required=False)
    province = serializers.CharField(max_length=50, required=False)
    status = serializers.CharField(max_length=20, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)
