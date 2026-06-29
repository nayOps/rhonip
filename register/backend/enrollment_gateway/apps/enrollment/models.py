"""
Modèles pour l'Enrollment Gateway
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class EnrollmentSession(models.Model):
    """
    Session d'enrôlement - suivi du processus complet
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('VALIDATING', 'En validation'),
        ('PROCESSING', 'En traitement'),
        ('ABIS_CHECK', 'Vérification ABIS'),
        ('REVIEW', 'En révision'),
        ('COMPLETED', 'Terminé'),
        ('FAILED', 'Échoué'),
        ('CANCELLED', 'Annulé'),
    ]
    
    CHANNEL_CHOICES = [
        ('fixed', 'Poste fixe'),
        ('mobile', 'Mobile'),
        ('itinerant', 'Itinérant'),
        ('school', 'École'),
        ('pnc', 'PNC'),
        ('fardc', 'FARDC'),
        ('prison', 'Prison'),
        ('refugee', 'Réfugiés'),
        ('ceni', 'CENI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, unique=True, help_text="ID de session unique")
    
    # Métadonnées de session
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        help_text="Canal d'enrôlement"
    )
    device_id = models.CharField(max_length=100, help_text="ID du dispositif")
    operator_id = models.CharField(max_length=100, help_text="ID de l'opérateur")
    location = models.JSONField(help_text="Localisation (province, territoire, etc.)")
    
    # Données d'enrôlement
    payload = models.JSONField(help_text="Payload complet d'enrôlement")
    payload_hash = models.CharField(max_length=64, help_text="Hash du payload")
    payload_signature = models.TextField(blank=True, null=True, help_text="Signature JWS")
    
    # Statut et progression
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Statut de la session"
    )
    progress_percentage = models.IntegerField(default=0, help_text="Pourcentage de progression")
    
    # Résultats
    registration_number = models.CharField(
        max_length=50, blank=True, null=True, help_text="Matricule RH"
    )
    employee_status = models.CharField(max_length=50, blank=True, null=True)
    abis_result = models.JSONField(default=dict, help_text="Résultat ABIS")
    modality_status = models.JSONField(
        default=dict,
        help_text="Statut par modalité biométrique (fingerprint, iris, ...)",
    )
    
    # Erreurs et messages
    error_message = models.TextField(blank=True, null=True, help_text="Message d'erreur")
    validation_errors = models.JSONField(default=list, help_text="Erreurs de validation")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Temps de traitement
    processing_time_ms = models.IntegerField(blank=True, null=True, help_text="Temps de traitement en ms")
    
    class Meta:
        db_table = 'enrollment_sessions'
        verbose_name = 'Session d\'enrôlement'
        verbose_name_plural = 'Sessions d\'enrôlement'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['status']),
            models.Index(fields=['channel']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.session_id} - {self.get_status_display()}"
    
    DEFAULT_MODALITY_STATUS = {
        'fingerprint': 'pending',
        'iris': 'pending',
        'document': 'pending',
        'signature': 'pending',
    }

    def ensure_modality_status(self):
        if not self.modality_status:
            self.modality_status = dict(self.DEFAULT_MODALITY_STATUS)

    def set_modality_status(self, modality, status, message=None):
        """pending | completed | skipped | failed"""
        self.ensure_modality_status()
        entry = {'status': status}
        if message:
            entry['message'] = message
        self.modality_status[modality] = entry

    def get_modality_status(self, modality: str) -> str:
        self.ensure_modality_status()
        value = self.modality_status.get(modality, 'pending')
        if isinstance(value, dict):
            return value.get('status', 'pending')
        return value

    def resolve_registration_number(self):
        """Matricule RH : colonne session ou payload guichet ONIP."""
        if self.registration_number:
            return str(self.registration_number).strip() or None
        payload = self.payload or {}
        employee = payload.get('employee') or {}
        matricule = (employee.get('registration_number') or '').strip()
        return matricule or None

    def sync_registration_number_from_payload(self, save=False):
        matricule = self.resolve_registration_number()
        if matricule and matricule != self.registration_number:
            self.registration_number = matricule
            if save:
                self.save(update_fields=['registration_number', 'updated_at'])
        return matricule

    @staticmethod
    def agent_display_name(payload):
        data = payload or {}
        employee = data.get('employee') or {}
        parts = [
            str(employee.get('first_name') or '').strip(),
            str(employee.get('middle_name') or '').strip(),
            str(employee.get('last_name') or '').strip(),
        ]
        name = ' '.join(p for p in parts if p)
        if name:
            return name
        core = data.get('core') or {}
        legacy = ' '.join(
            str(core.get(k) or '').strip()
            for k in ('prenom', 'nom', 'postnom')
            if core.get(k)
        )
        return legacy.strip()

    def update_progress(self, percentage, status=None):
        """Met à jour la progression de la session"""
        self.progress_percentage = percentage
        if status:
            self.status = status
        self.save()
    
    def mark_completed(self, registration_number=None):
        """Marque la session comme terminée"""
        self.status = 'COMPLETED'
        self.progress_percentage = 100
        self.completed_at = timezone.now()
        if registration_number:
            self.registration_number = registration_number
        self.save()
    
    def mark_failed(self, error_message):
        """Marque la session comme échouée"""
        self.status = 'FAILED'
        self.error_message = error_message
        self.save()


class EnrollmentValidation(models.Model):
    """
    Validation des données d'enrôlement
    """
    
    VALIDATION_TYPE_CHOICES = [
        ('schema', 'Validation du schéma'),
        ('business', 'Validation métier'),
        ('biometric', 'Validation biométrique'),
        ('document', 'Validation des documents'),
        ('duplicate', 'Vérification des doublons'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PASSED', 'Validé'),
        ('FAILED', 'Échoué'),
        ('WARNING', 'Avertissement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        EnrollmentSession,
        on_delete=models.CASCADE,
        related_name='validations',
        help_text="Session d'enrôlement"
    )
    
    validation_type = models.CharField(
        max_length=20,
        choices=VALIDATION_TYPE_CHOICES,
        help_text="Type de validation"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Statut de validation"
    )
    
    # Détails de validation
    validation_rules = models.JSONField(help_text="Règles de validation appliquées")
    validation_result = models.JSONField(help_text="Résultat de validation")
    error_details = models.JSONField(default=list, help_text="Détails des erreurs")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    processing_time_ms = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'enrollment_validations'
        verbose_name = 'Validation d\'enrôlement'
        verbose_name_plural = 'Validations d\'enrôlement'
        unique_together = ['session', 'validation_type']
    
    def __str__(self):
        return f"{self.session.session_id} - {self.get_validation_type_display()}"


class EnrollmentEvent(models.Model):
    """
    Événements liés à l'enrôlement pour l'audit et le suivi
    """
    
    EVENT_TYPE_CHOICES = [
        ('session_started', 'Session démarrée'),
        ('payload_received', 'Payload reçu'),
        ('validation_started', 'Validation démarrée'),
        ('validation_completed', 'Validation terminée'),
        ('abis_check_started', 'Vérification ABIS démarrée'),
        ('abis_check_completed', 'Vérification ABIS terminée'),
        ('fgp_core_created', 'FGP Core créé'),
        ('extensions_created', 'Extensions créées'),
        ('session_completed', 'Session terminée'),
        ('session_failed', 'Session échouée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        EnrollmentSession,
        on_delete=models.CASCADE,
        related_name='events',
        help_text="Session d'enrôlement"
    )
    
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        help_text="Type d'événement"
    )
    event_data = models.JSONField(default=dict, help_text="Données de l'événement")
    message = models.TextField(help_text="Message descriptif")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'enrollment_events'
        verbose_name = 'Événement d\'enrôlement'
        verbose_name_plural = 'Événements d\'enrôlement'
        indexes = [
            models.Index(fields=['session', 'event_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.session.session_id} - {self.get_event_type_display()}"


class EnrollmentReceipt(models.Model):
    """
    Récépissé d'enrôlement généré
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(
        EnrollmentSession,
        on_delete=models.CASCADE,
        related_name='receipt',
        help_text="Session d'enrôlement"
    )
    
    registration_number = models.CharField(max_length=50, help_text="Matricule RH")
    receipt_number = models.CharField(max_length=50, unique=True, help_text="Numéro de récépissé")
    
    # Contenu du récépissé
    receipt_content = models.JSONField(help_text="Contenu du récépissé")
    receipt_pdf_url = models.URLField(blank=True, null=True, help_text="URL du PDF")
    qr_code_data = models.TextField(help_text="Données du QR code")
    qr_code_url = models.URLField(blank=True, null=True, help_text="URL du QR code")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Date d'expiration")
    
    class Meta:
        db_table = 'enrollment_receipts'
        verbose_name = 'Récépissé d\'enrôlement'
        verbose_name_plural = 'Récépissés d\'enrôlement'
    
    def __str__(self):
        return f"Récépissé {self.receipt_number} — {self.registration_number}"


class EnrollmentStatistics(models.Model):
    """
    Statistiques d'enrôlement pour le monitoring
    """
    
    id = models.AutoField(primary_key=True)
    date = models.DateField(help_text="Date des statistiques")
    channel = models.CharField(max_length=20, help_text="Canal d'enrôlement")
    
    # Compteurs
    total_sessions = models.IntegerField(default=0)
    completed_sessions = models.IntegerField(default=0)
    failed_sessions = models.IntegerField(default=0)
    abis_hits = models.IntegerField(default=0)
    abis_reviews = models.IntegerField(default=0)
    
    # Temps de traitement
    avg_processing_time_ms = models.IntegerField(default=0)
    min_processing_time_ms = models.IntegerField(default=0)
    max_processing_time_ms = models.IntegerField(default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'enrollment_statistics'
        verbose_name = 'Statistique d\'enrôlement'
        verbose_name_plural = 'Statistiques d\'enrôlement'
        unique_together = ['date', 'channel']
    
    def __str__(self):
        return f"Stats {self.date} - {self.channel}"
