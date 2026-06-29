"""
Modèles biométriques ONIP — clé = matricule RH (registration_number).
"""
from django.db import models
import uuid


class BiometricData(models.Model):
    """Données biométriques rattachées au matricule employé."""

    MIN_QUALITY = 0.7

    registration_number = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Matricule RH (registration_number)",
    )

    photo_uri = models.URLField(blank=True, null=True)
    photo_hash = models.CharField(max_length=64, blank=True, null=True)
    photo_quality = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    fingerprints_uri = models.URLField(blank=True, null=True)
    fingerprints_hash = models.CharField(max_length=64, blank=True, null=True)
    fingerprints_quality = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    iris_uri = models.URLField(blank=True, null=True)
    iris_hash = models.CharField(max_length=64, blank=True, null=True)
    iris_quality = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    signature_uri = models.URLField(blank=True, null=True)
    signature_hash = models.CharField(max_length=64, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'fgp_biometric'
        verbose_name = 'Données biométriques'
        verbose_name_plural = 'Données biométriques'

    def __str__(self):
        return f"Biométrie — {self.registration_number}"


class FingerprintCapture(models.Model):
    """Capture détaillée des empreintes (une ligne par doigt)."""

    POSITION_CHOICES = [
        ('LEFT_THUMB', 'Pouce gauche'),
        ('LEFT_INDEX', 'Index gauche'),
        ('LEFT_MIDDLE', 'Majeur gauche'),
        ('LEFT_RING', 'Annulaire gauche'),
        ('LEFT_LITTLE', 'Auriculaire gauche'),
        ('RIGHT_THUMB', 'Pouce droit'),
        ('RIGHT_INDEX', 'Index droit'),
        ('RIGHT_MIDDLE', 'Majeur droit'),
        ('RIGHT_RING', 'Annulaire droit'),
        ('RIGHT_LITTLE', 'Auriculaire droit'),
        ('UNKNOWN', 'Inconnu'),
    ]

    STATUS_CHOICES = [
        ('CAPTURED', 'Capturée'),
        ('PENDING', 'En attente'),
        ('MISSING', 'Manquante'),
        ('AMPUTATED', 'Amputée'),
        ('DAMAGED', 'Endommagée'),
        ('FAILED', 'Échec'),
        ('SKIPPED', 'Ignorée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration_number = models.CharField(max_length=50, db_index=True)
    finger_position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='UNKNOWN')
    capture_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    image_uri = models.URLField(blank=True, null=True)
    image_hash = models.CharField(max_length=64, blank=True, null=True)
    template_uri = models.URLField(blank=True, null=True)
    template_hash = models.CharField(max_length=64, blank=True, null=True)
    template_format = models.CharField(max_length=30, blank=True, null=True)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nfiq_score = models.IntegerField(blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)
    captured_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fgp_fingerprints'
        verbose_name = 'Capture empreinte'
        verbose_name_plural = 'Captures empreintes'
        constraints = [
            models.UniqueConstraint(
                fields=['registration_number', 'finger_position'],
                name='uniq_fgp_fingerprints_matricule_position',
            )
        ]
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['finger_position']),
            models.Index(fields=['capture_status']),
        ]

    def __str__(self):
        return f"{self.registration_number} — {self.finger_position} ({self.capture_status})"


class BiometricMatch(models.Model):
    """Résultats de correspondance biométrique (déduplication locale / ABIS)."""

    MATCH_TYPES = [
        ('face', 'Face'),
        ('fingerprint', 'Empreinte digitale'),
        ('iris', 'Iris'),
        ('multimodal', 'Multimodal'),
    ]

    DECISION_CHOICES = [
        ('HIT', 'Correspondance trouvée'),
        ('NO_HIT', 'Aucune correspondance'),
        ('REVIEW', 'À réviser'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration_number_candidate = models.CharField(max_length=50, db_index=True)
    registration_number_existing = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    match_type = models.CharField(max_length=20, choices=MATCH_TYPES)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=4)
    threshold = models.DecimalField(max_digits=5, decimal_places=4)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    reviewed_by = models.CharField(max_length=100, blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    review_decision = models.CharField(max_length=20, blank=True, null=True)
    review_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'abis_matches'
        verbose_name = 'Correspondance biométrique'
        verbose_name_plural = 'Correspondances biométriques'

    def __str__(self):
        return f"{self.registration_number_candidate} vs {self.registration_number_existing or 'N/A'}"
