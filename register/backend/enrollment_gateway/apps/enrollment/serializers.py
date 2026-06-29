"""
Sérialiseurs pour l'application Enrollment
"""
from rest_framework import serializers
from .models import EnrollmentSession, EnrollmentValidation, EnrollmentEvent, EnrollmentReceipt


class EnrollmentPayloadSerializer(serializers.Serializer):
    """
    Sérialiseur pour le payload d'enrôlement complet.
    Schéma 1.0 (FGP legacy) : core + strata.
    Schéma 2.0 (guichet ONIP) : employee + biometrics.
    """

    session_id = serializers.CharField(max_length=100, help_text="ID de session unique")
    channel = serializers.ChoiceField(
        choices=EnrollmentSession.CHANNEL_CHOICES,
        help_text="Canal d'enrôlement",
    )
    device_id = serializers.CharField(max_length=100, help_text="ID du dispositif")
    operator_id = serializers.CharField(max_length=100, help_text="ID de l'opérateur")
    location = serializers.JSONField(help_text="Localisation")
    schema_version = serializers.CharField(max_length=10, help_text="Version du schéma")

    core = serializers.JSONField(required=False, help_text="Données FGP Core (27 variables)")
    employee = serializers.JSONField(required=False, help_text="Fiche employé ONIP (guichet)")
    biometrics = serializers.JSONField(help_text="Données biométriques")
    strata = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Liste des strates (schéma 1.0)",
    )
    extensions = serializers.JSONField(
        required=False,
        help_text="Extensions spécifiques par strate",
    )
    attachments = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        help_text="Documents attachés",
    )
    auto_process = serializers.BooleanField(
        required=False,
        default=True,
        help_text="False = session guichet par étapes (empreintes/iris avant traitement)",
    )

    def validate_channel(self, value):
        from django.conf import settings

        allowed_channels = settings.ENROLLMENT_SETTINGS.get('ALLOWED_CHANNELS', [])
        if value not in allowed_channels:
            raise serializers.ValidationError(f"Canal non autorisé: {value}")
        return value

    def validate_schema_version(self, value):
        from django.conf import settings

        supported_versions = settings.ENROLLMENT_SETTINGS.get('SUPPORTED_SCHEMA_VERSIONS', [])
        if value not in supported_versions:
            raise serializers.ValidationError(f"Version de schéma non supportée: {value}")
        return value

    def validate_core(self, value):
        if value is None:
            return value
        if not isinstance(value, dict):
            raise serializers.ValidationError("Les données core doivent être un objet JSON")

        required_fields = [
            'nom', 'prenom', 'sexe', 'date_naissance', 'lieu_naissance',
            'province_naissance', 'nationalite', 'province_residence',
        ]
        for field in required_fields:
            if field not in value or value.get(field) in (None, ''):
                raise serializers.ValidationError(f"Champ obligatoire manquant ou vide: {field}")
        return value

    def validate_employee(self, value):
        if value is None:
            return value
        if not isinstance(value, dict):
            raise serializers.ValidationError("Les données employee doivent être un objet JSON")

        required_fields = ['registration_number', 'first_name', 'last_name']
        for field in required_fields:
            raw = value.get(field)
            if raw in (None, '') or (isinstance(raw, str) and not raw.strip()):
                raise serializers.ValidationError(f"Champ employé obligatoire manquant ou vide: {field}")
        return value

    def validate_biometrics(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Les données biométriques doivent être un objet JSON")

        biometric_types = ['face', 'fingerprints', 'iris']
        has_biometric = any(
            biometric_type in value and value[biometric_type]
            for biometric_type in biometric_types
        )
        if not has_biometric:
            raise serializers.ValidationError("Au moins une donnée biométrique est requise")
        return value

    def validate(self, attrs):
        schema_version = attrs.get('schema_version', '1.0')
        if schema_version == '2.0':
            if not attrs.get('employee'):
                raise serializers.ValidationError({'employee': 'Fiche employé requise pour le schéma 2.0'})
            self.validate_employee(attrs['employee'])
        else:
            if not attrs.get('core'):
                raise serializers.ValidationError({'core': 'Données core requises pour le schéma 1.0'})
            if not attrs.get('strata'):
                raise serializers.ValidationError({'strata': 'Liste des strates requise pour le schéma 1.0'})
        return attrs


class EnrollmentResponseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la réponse d'enrôlement (liste / statut)."""

    agent_name = serializers.SerializerMethodField()

    class Meta:
        model = EnrollmentSession
        fields = [
            'id', 'session_id', 'status', 'progress_percentage',
            'registration_number', 'agent_name', 'employee_status',
            'abis_result', 'modality_status', 'error_message', 'validation_errors',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_agent_name(self, obj):
        return EnrollmentSession.agent_display_name(obj.payload)


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur détaillé pour une session d'enrôlement."""

    validations = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    receipt = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()

    class Meta:
        model = EnrollmentSession
        fields = [
            'id', 'session_id', 'channel', 'device_id', 'operator_id',
            'location', 'status', 'progress_percentage', 'registration_number',
            'agent_name', 'employee_status', 'abis_result', 'modality_status',
            'error_message', 'validation_errors', 'payload', 'validations',
            'events', 'receipt', 'created_at', 'updated_at', 'completed_at',
            'processing_time_ms',
        ]

    def get_agent_name(self, obj):
        return EnrollmentSession.agent_display_name(obj.payload)

    def get_validations(self, obj):
        return EnrollmentValidationSerializer(obj.validations.all(), many=True).data

    def get_events(self, obj):
        return EnrollmentEventSerializer(obj.events.all()[:10], many=True).data

    def get_receipt(self, obj):
        if hasattr(obj, 'receipt'):
            return EnrollmentReceiptSerializer(obj.receipt).data
        return None


class EnrollmentValidationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les validations d'enrôlement."""

    class Meta:
        model = EnrollmentValidation
        fields = [
            'id', 'validation_type', 'status', 'validation_rules',
            'validation_result', 'error_details', 'created_at',
            'completed_at', 'processing_time_ms',
        ]
        read_only_fields = ['id', 'created_at']


class EnrollmentEventSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les événements d'enrôlement."""

    class Meta:
        model = EnrollmentEvent
        fields = [
            'id', 'event_type', 'event_data', 'message',
            'created_at', 'created_by',
        ]
        read_only_fields = ['id', 'created_at']


class EnrollmentReceiptSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les récépissés d'enrôlement."""

    class Meta:
        model = EnrollmentReceipt
        fields = [
            'id', 'registration_number', 'receipt_number', 'receipt_content',
            'receipt_pdf_url', 'qr_code_data', 'qr_code_url',
            'created_at', 'expires_at',
        ]
        read_only_fields = ['id', 'created_at']


class EnrollmentStatsSerializer(serializers.Serializer):
    """Sérialiseur pour les statistiques d'enrôlement."""

    date = serializers.DateField()
    channel = serializers.CharField()
    total_sessions = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    failed_sessions = serializers.IntegerField()
    abis_hits = serializers.IntegerField()
    abis_reviews = serializers.IntegerField()
    avg_processing_time_ms = serializers.IntegerField()
    success_rate = serializers.FloatField()
    abis_hit_rate = serializers.FloatField()


class EnrollmentSearchSerializer(serializers.Serializer):
    """Sérialiseur pour la recherche d'enrôlements."""

    session_id = serializers.CharField(required=False)
    registration_number = serializers.CharField(required=False)
    channel = serializers.ChoiceField(
        choices=EnrollmentSession.CHANNEL_CHOICES,
        required=False,
    )
    status = serializers.ChoiceField(
        choices=EnrollmentSession.STATUS_CHOICES,
        required=False,
    )
    operator_id = serializers.CharField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
