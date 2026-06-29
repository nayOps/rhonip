"""
Serializers pour l'API Iris
"""

from rest_framework import serializers
from .models import (
    IrisCaptureSession,
    IrisCapture,
    IrisTemplate,
    IrisMatch,
    IrisQualityLog
)


class IrisCaptureSerializer(serializers.ModelSerializer):
    """Serializer pour les captures d'iris"""
    
    quality_percentage = serializers.SerializerMethodField()
    eye_label = serializers.SerializerMethodField()
    
    class Meta:
        model = IrisCapture
        fields = [
            'id',
            'session',
            'eye_position',
            'eye_label',
            'status',
            'full_frame',
            'eye_region',
            'normalized_iris',
            'segmented_iris',
            'iris_center_x',
            'iris_center_y',
            'iris_radius',
            'pupil_center_x',
            'pupil_center_y',
            'pupil_radius',
            'quality_score',
            'quality_percentage',
            'size_score',
            'centering_score',
            'contrast_score',
            'is_valid',
            'captured_at',
            'processed_at',
            'reason',
        ]
        read_only_fields = [
            'id',
            'captured_at',
            'processed_at',
            'quality_percentage',
            'eye_label',
        ]
    
    def get_quality_percentage(self, obj):
        """Retourne la qualité en pourcentage"""
        if obj.quality_score is not None:
            return int(obj.quality_score * 100)
        return None
    
    def get_eye_label(self, obj):
        """Retourne le label de l'œil en français"""
        labels = {
            'LEFT': 'Œil gauche',
            'RIGHT': 'Œil droit'
        }
        return labels.get(obj.eye_position, obj.eye_position)


class IrisQualityLogSerializer(serializers.ModelSerializer):
    """Serializer pour les logs de qualité"""
    
    class Meta:
        model = IrisQualityLog
        fields = [
            'id',
            'capture',
            'overall_score',
            'size_score',
            'centering_score',
            'contrast_score',
            'sharpness_score',
            'occlusion_score',
            'capture_duration',
            'processing_duration',
            'pupil_detected',
            'iris_detected',
            'issues',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class IrisCaptureSessionSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions de capture"""
    
    captures = IrisCaptureSerializer(many=True, read_only=True)
    captures_count = serializers.SerializerMethodField()
    valid_captures_count = serializers.SerializerMethodField()
    
    class Meta:
        model = IrisCaptureSession
        fields = [
            'id',
            'enrollment_session_id',
            'status',
            'started_at',
            'completed_at',
            'operator_id',
            'station_id',
            'notes',
            'error_message',
            'captures',
            'captures_count',
            'valid_captures_count',
        ]
        read_only_fields = [
            'id',
            'started_at',
            'completed_at',
            'captures_count',
            'valid_captures_count',
        ]
    
    def get_captures_count(self, obj):
        """Nombre total de captures"""
        return obj.captures.count()
    
    def get_valid_captures_count(self, obj):
        """Nombre de captures valides"""
        return obj.captures.filter(is_valid=True).count()


class IrisTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les templates d'iris"""
    
    capture_info = IrisCaptureSerializer(source='capture', read_only=True)
    
    class Meta:
        model = IrisTemplate
        fields = [
            'id',
            'capture',
            'capture_info',
            'encoding_method',
            'template_size',
            'code_shape_filters',
            'code_shape_height',
            'code_shape_width',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'template_size']


class IrisMatchSerializer(serializers.ModelSerializer):
    """Serializer pour les résultats de matching"""
    
    template1_info = IrisTemplateSerializer(source='template_1', read_only=True)
    template2_info = IrisTemplateSerializer(source='template_2', read_only=True)
    similarity_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = IrisMatch
        fields = [
            'id',
            'template_1',
            'template_2',
            'template1_info',
            'template2_info',
            'is_match',
            'similarity_score',
            'similarity_percentage',
            'hamming_distance',
            'rotation_shift',
            'matched_at',
            'matching_threshold',
        ]
        read_only_fields = [
            'id',
            'matched_at',
            'similarity_percentage',
        ]
    
    def get_similarity_percentage(self, obj):
        """Retourne la similarité en pourcentage"""
        return int(obj.similarity_score * 100)


# Serializers pour les requêtes

class StartSessionRequestSerializer(serializers.Serializer):
    """Requête pour démarrer une session"""
    enrollment_session_id = serializers.UUIDField()
    operator_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    station_id = serializers.CharField(max_length=50, required=False, allow_blank=True)


class CaptureEyeRequestSerializer(serializers.Serializer):
    """Requête pour capturer un œil"""
    eye_position = serializers.ChoiceField(choices=['LEFT', 'RIGHT'])
    timeout = serializers.IntegerField(required=False, min_value=5, max_value=120, default=30)


class MarkHandicapRequestSerializer(serializers.Serializer):
    """Requête pour marquer un handicap"""
    eye_position = serializers.ChoiceField(choices=['LEFT', 'RIGHT'])
    handicap_type = serializers.ChoiceField(choices=['BLIND', 'MISSING', 'DAMAGED'])
    reason = serializers.CharField(max_length=500)


class ProcessCaptureRequestSerializer(serializers.Serializer):
    """Requête pour traiter une capture"""
    capture_id = serializers.UUIDField()


class CompareTemplatesRequestSerializer(serializers.Serializer):
    """Requête pour comparer deux templates"""
    template1_id = serializers.UUIDField()
    template2_id = serializers.UUIDField()


class SearchDuplicatesRequestSerializer(serializers.Serializer):
    """Requête pour chercher des duplicatas"""
    template_id = serializers.UUIDField()
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)

