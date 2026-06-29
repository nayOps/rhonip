"""
Models for Iris biometric capture and storage
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class IrisCaptureSession(models.Model):
    """
    Session de capture d'iris (pour un enrôlement)
    """
    
    STATUS_CHOICES = [
        ('INITIATED', 'Initiée'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Complétée'),
        ('FAILED', 'Échouée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment_session_id = models.UUIDField(
        help_text="ID de la session d'enrôlement parente"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='INITIATED'
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    operator_id = models.CharField(max_length=50, null=True, blank=True)
    station_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'iris_capture_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['enrollment_session_id']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"IrisSession {self.id} - {self.status}"


class IrisCapture(models.Model):
    """
    Capture d'un iris individuel (gauche ou droit)
    """
    
    EYE_CHOICES = [
        ('LEFT', 'Œil gauche'),
        ('RIGHT', 'Œil droit'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CAPTURED', 'Capturé'),
        ('BLIND', 'Œil aveugle'),
        ('MISSING', 'Œil manquant'),
        ('DAMAGED', 'Œil endommagé'),
        ('FAILED', 'Échec capture'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        IrisCaptureSession,
        on_delete=models.CASCADE,
        related_name='captures'
    )
    
    eye_position = models.CharField(
        max_length=10,
        choices=EYE_CHOICES
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Images
    full_frame = models.ImageField(
        upload_to='iris/images/full_frames/',
        null=True,
        blank=True,
        help_text="Image complète capturée"
    )
    eye_region = models.ImageField(
        upload_to='iris/images/eye_regions/',
        null=True,
        blank=True,
        help_text="Région de l'œil extraite"
    )
    normalized_iris = models.ImageField(
        upload_to='iris/images/normalized/',
        null=True,
        blank=True,
        help_text="Iris normalisé (coordonnées polaires)"
    )
    segmented_iris = models.ImageField(
        upload_to='iris/images/segmented/',
        null=True,
        blank=True,
        help_text="Iris segmenté avec visualisation"
    )
    
    # Segmentation data
    iris_center_x = models.IntegerField(null=True, blank=True)
    iris_center_y = models.IntegerField(null=True, blank=True)
    iris_radius = models.IntegerField(null=True, blank=True)
    
    pupil_center_x = models.IntegerField(null=True, blank=True)
    pupil_center_y = models.IntegerField(null=True, blank=True)
    pupil_radius = models.IntegerField(null=True, blank=True)
    
    # Quality scores
    quality_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Score de qualité global (0-1)"
    )
    size_score = models.FloatField(null=True, blank=True)
    centering_score = models.FloatField(null=True, blank=True)
    contrast_score = models.FloatField(null=True, blank=True)
    
    is_valid = models.BooleanField(
        default=False,
        help_text="True si qualité suffisante pour enrollment"
    )
    
    # Timestamps
    captured_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Reason (for handicaps)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'iris_captures'
        ordering = ['-captured_at']
        unique_together = [['session', 'eye_position']]
        indexes = [
            models.Index(fields=['session', 'eye_position']),
            models.Index(fields=['status']),
            models.Index(fields=['is_valid']),
        ]
    
    def __str__(self):
        return f"Iris {self.eye_position} - {self.status} (Q:{self.quality_score})"


class IrisTemplate(models.Model):
    """
    Template encodé d'un iris (pour matching)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capture = models.OneToOneField(
        IrisCapture,
        on_delete=models.CASCADE,
        related_name='template'
    )
    
    # Template data (stored as binary)
    template_data = models.BinaryField(
        help_text="Template binaire encodé (code + mask)"
    )
    
    # Template metadata
    encoding_method = models.CharField(
        max_length=50,
        default='gabor_phase',
        help_text="Méthode d'encodage utilisée"
    )
    template_size = models.IntegerField(
        help_text="Taille du template en bytes"
    )
    
    # Shape information
    code_shape_filters = models.IntegerField(default=8)
    code_shape_height = models.IntegerField(default=64)
    code_shape_width = models.IntegerField(default=256)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'iris_templates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Template for {self.capture}"


class IrisMatch(models.Model):
    """
    Résultat de matching entre deux iris
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    template_1 = models.ForeignKey(
        IrisTemplate,
        on_delete=models.CASCADE,
        related_name='matches_as_template1'
    )
    template_2 = models.ForeignKey(
        IrisTemplate,
        on_delete=models.CASCADE,
        related_name='matches_as_template2'
    )
    
    # Match results
    is_match = models.BooleanField(
        help_text="True si les iris correspondent"
    )
    similarity_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Score de similarité (0-1)"
    )
    hamming_distance = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Distance de Hamming normalisée (0-1)"
    )
    
    # Rotation info
    rotation_shift = models.IntegerField(
        help_text="Décalage de rotation optimal (pixels)"
    )
    
    # Metadata
    matched_at = models.DateTimeField(auto_now_add=True)
    matching_threshold = models.FloatField(
        help_text="Seuil utilisé pour la décision"
    )
    
    class Meta:
        db_table = 'iris_matches'
        ordering = ['-matched_at']
        indexes = [
            models.Index(fields=['is_match']),
            models.Index(fields=['similarity_score']),
        ]
    
    def __str__(self):
        return f"Match: {self.similarity_score:.2%} ({'✓' if self.is_match else '✗'})"


class IrisQualityLog(models.Model):
    """
    Log détaillé de la qualité d'une capture
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capture = models.OneToOneField(
        IrisCapture,
        on_delete=models.CASCADE,
        related_name='quality_log'
    )
    
    # Detailed quality metrics
    overall_score = models.FloatField()
    size_score = models.FloatField()
    centering_score = models.FloatField()
    contrast_score = models.FloatField()
    sharpness_score = models.FloatField(null=True, blank=True)
    occlusion_score = models.FloatField(null=True, blank=True)
    
    # Technical details
    capture_duration = models.FloatField(
        help_text="Durée de capture en secondes"
    )
    processing_duration = models.FloatField(
        help_text="Durée de traitement en secondes"
    )
    
    # Segmentation info
    pupil_detected = models.BooleanField(default=False)
    iris_detected = models.BooleanField(default=False)
    
    # Issues detected
    issues = models.JSONField(
        default=list,
        help_text="Liste des problèmes détectés"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'iris_quality_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"QualityLog for {self.capture} - {self.overall_score:.2%}"

