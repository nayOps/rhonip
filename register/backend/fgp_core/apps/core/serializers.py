"""
Sérialiseurs pour l'application Core
"""
from rest_framework import serializers
from .models import PersonCore, StrataMembership, Document
from apps.biometric.models import BiometricData, FingerprintCapture


class PersonCoreSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de base pour PersonCore
    """
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonCore
        fields = [
            'nin', 'nom', 'postnom', 'prenom', 'sexe',
            'date_naissance', 'lieu_naissance', 'province_naissance', 'nationalite',
            'statut_matrimonial', 'nom_pere', 'nom_mere',
            'province_residence', 'territoire_residence', 'commune_residence',
            'quartier_residence', 'avenue_residence', 'numero_residence',
            'telephone', 'email', 'profession', 'niveau_etude',
            'type_piece_identite', 'numero_piece_identite',
            'date_emission_piece', 'lieu_emission_piece',
            'created_at', 'updated_at', 'version',
            'full_name', 'age', 'address'
        ]
        read_only_fields = ['nin', 'created_at', 'updated_at', 'version']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_age(self, obj):
        return obj.get_age()
    
    def get_address(self, obj):
        return obj.get_address()


class PersonCoreDetailSerializer(PersonCoreSerializer):
    """
    Sérialiseur détaillé pour PersonCore avec relations
    """
    strata_memberships = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    
    class Meta(PersonCoreSerializer.Meta):
        fields = PersonCoreSerializer.Meta.fields + ['strata_memberships', 'documents']
    
    def get_strata_memberships(self, obj):
        memberships = obj.strata_memberships.filter(status='ACTIVE')
        return StrataMembershipSerializer(memberships, many=True).data
    
    def get_documents(self, obj):
        return DocumentSerializer(obj.documents.all(), many=True).data


class PersonCoreCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création de PersonCore
    """
    class Meta:
        model = PersonCore
        fields = [
            'nom', 'postnom', 'prenom', 'sexe',
            'date_naissance', 'lieu_naissance', 'province_naissance', 'nationalite',
            'statut_matrimonial', 'nom_pere', 'nom_mere',
            'province_residence', 'territoire_residence', 'commune_residence',
            'quartier_residence', 'avenue_residence', 'numero_residence',
            'telephone', 'email', 'profession', 'niveau_etude',
            'type_piece_identite', 'numero_piece_identite',
            'date_emission_piece', 'lieu_emission_piece'
        ]
    
    def validate_telephone(self, value):
        """Validation du numéro de téléphone"""
        if value and not value.startswith('+243'):
            raise serializers.ValidationError("Le numéro doit commencer par +243")
        return value
    
    def validate_nin(self, value):
        """Validation du format NIN"""
        import re
        pattern = r'^CD-\d{4}-\d{4}-\d{7}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Format NIN invalide")
        return value


class StrataMembershipSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour StrataMembership
    """
    nin_display = serializers.CharField(source='nin.nin', read_only=True)
    strate_display = serializers.CharField(source='get_strate_code_display', read_only=True)
    
    class Meta:
        model = StrataMembership
        fields = [
            'id', 'nin', 'nin_display', 'strate_code', 'strate_display',
            'valid_from', 'valid_to', 'status', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at']


class StrataMembershipCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création de StrataMembership
    """
    class Meta:
        model = StrataMembership
        fields = ['nin', 'strate_code', 'valid_from', 'valid_to', 'status']
    
    def validate(self, data):
        """Validation des données"""
        if data.get('valid_to') and data['valid_to'] <= data['valid_from']:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début"
            )
        return data


class DocumentSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour Document
    """
    nin_display = serializers.CharField(source='nin.nin', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'nin', 'nin_display', 'document_type', 'document_type_display',
            'document_uri', 'document_hash', 'file_size', 'mime_type',
            'is_verified', 'verified_by', 'verified_at',
            'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'document_hash']

    def validate_document_uri(self, value):
        """Autorise aussi les URI file:// pour les médias locaux de dev."""
        if not value.startswith(('http://', 'https://', 's3://', 'file://')):
            raise serializers.ValidationError("URI de document invalide")
        return value


class BiometricDataSerializer(serializers.ModelSerializer):
    """Sérialiseur biométrie — clé matricule RH."""

    photo_uri = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    fingerprints_uri = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    iris_uri = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    signature_uri = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = BiometricData
        fields = [
            'registration_number',
            'photo_uri', 'photo_hash', 'photo_quality',
            'fingerprints_uri', 'fingerprints_hash', 'fingerprints_quality',
            'iris_uri', 'iris_hash', 'iris_quality',
            'signature_uri', 'signature_hash',
            'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def _validate_uri(self, value):
        if value in (None, ''):
            return value
        if not value.startswith(('http://', 'https://', 's3://', 'file://')):
            raise serializers.ValidationError("URI biométrique invalide")
        return value

    def validate_photo_uri(self, value):
        return self._validate_uri(value)

    def validate_fingerprints_uri(self, value):
        return self._validate_uri(value)

    def validate_iris_uri(self, value):
        return self._validate_uri(value)

    def validate_signature_uri(self, value):
        return self._validate_uri(value)


class FingerprintCaptureSerializer(serializers.ModelSerializer):
    """Sérialiseur empreintes — clé matricule RH."""

    image_uri = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    template_uri = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = FingerprintCapture
        fields = [
            'id',
            'registration_number',
            'finger_position',
            'capture_status',
            'image_uri',
            'image_hash',
            'template_uri',
            'template_hash',
            'template_format',
            'quality_score',
            'nfiq_score',
            'device',
            'captured_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_image_uri(self, value):
        if value in (None, ''):
            return value
        if not value.startswith(('http://', 'https://', 's3://', 'file://')):
            raise serializers.ValidationError("URI image empreinte invalide")
        return value

    def validate_template_uri(self, value):
        if value in (None, ''):
            return value
        if not value.startswith(('http://', 'https://', 's3://', 'file://')):
            raise serializers.ValidationError("URI template empreinte invalide")
        return value


class DocumentCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création de Document
    """
    class Meta:
        model = Document
        fields = [
            'nin', 'document_type', 'document_uri', 'file_size', 'mime_type'
        ]
    
    def validate_document_uri(self, value):
        """Validation de l'URI du document"""
        if not value.startswith(('http://', 'https://', 's3://', 'file://')):
            raise serializers.ValidationError("URI de document invalide")
        return value


class EnrollmentPayloadSerializer(serializers.Serializer):
    """
    Sérialiseur pour le payload d'enrôlement complet
    """
    core = PersonCoreCreateSerializer()
    strata = serializers.ListField(
        child=serializers.CharField(),
        help_text="Liste des codes de strates"
    )
    extensions = serializers.DictField(
        required=False,
        help_text="Extensions spécifiques par strate"
    )
    documents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Liste des documents"
    )
    
    def validate_strata(self, value):
        """Validation des strates"""
        valid_strata = [
            'ELEVES', 'ETUDIANTS', 'ELECTEURS', 'PNC', 'FARDC',
            'PRISON', 'REFUGIE', 'ENFANT', 'FONCTIONNAIRE'
        ]
        for strate in value:
            if strate not in valid_strata:
                raise serializers.ValidationError(f"Strate invalide: {strate}")
        return value


class EnrollmentResponseSerializer(serializers.Serializer):
    """
    Sérialiseur pour la réponse d'enrôlement
    """
    nin = serializers.CharField()
    status = serializers.CharField()
    core_persisted = serializers.BooleanField()
    extensions_persisted = serializers.ListField(child=serializers.CharField())
    abis = serializers.DictField()
    events = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField()
