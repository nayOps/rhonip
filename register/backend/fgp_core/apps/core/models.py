"""
Modèles pour le FGP Core - 27 variables obligatoires
"""
import re
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils import timezone


class PersonCore(models.Model):
    """
    Modèle principal contenant les 27 variables obligatoires du FGP
    """
    
    # Identifiant unique
    nin = models.CharField(
        max_length=20,
        primary_key=True,
        validators=[
            RegexValidator(
                regex=r'^CD-\d{4}-\d{4}-\d{7}$',
                message='Format NIN invalide. Doit être: CD-YYYY-NNNN-NNNNNNN'
            )
        ],
        help_text="Numéro d'Identification Nationale"
    )
    
    # Variables d'identité (27 du décret)
    nom = models.CharField(max_length=100, help_text="Nom de famille")
    postnom = models.CharField(max_length=100, blank=True, null=True, help_text="Postnom")
    prenom = models.CharField(max_length=100, help_text="Prénom")
    sexe = models.CharField(
        max_length=1,
        choices=[('M', 'Masculin'), ('F', 'Féminin')],
        help_text="Sexe"
    )
    
    # Informations de naissance
    date_naissance = models.DateField(help_text="Date de naissance")
    lieu_naissance = models.CharField(max_length=200, help_text="Lieu de naissance")
    province_naissance = models.CharField(max_length=100, help_text="Province de naissance")
    nationalite = models.CharField(
        max_length=100,
        default='Congolaise',
        help_text="Nationalité"
    )
    
    # Statut matrimonial
    statut_matrimonial = models.CharField(
        max_length=20,
        choices=[
            ('Célibataire', 'Célibataire'),
            ('Marié(e)', 'Marié(e)'),
            ('Divorcé(e)', 'Divorcé(e)'),
            ('Veuf(ve)', 'Veuf(ve)'),
            ('Union libre', 'Union libre'),
        ],
        blank=True,
        null=True,
        help_text="Statut matrimonial"
    )
    
    # Parents
    nom_pere = models.CharField(max_length=200, blank=True, null=True, help_text="Nom du père")
    nom_mere = models.CharField(max_length=200, blank=True, null=True, help_text="Nom de la mère")
    
    # Adresse actuelle
    province_residence = models.CharField(max_length=100, help_text="Province de résidence")
    territoire_residence = models.CharField(max_length=100, blank=True, null=True, help_text="Territoire de résidence")
    commune_residence = models.CharField(max_length=100, blank=True, null=True, help_text="Commune de résidence")
    quartier_residence = models.CharField(max_length=100, blank=True, null=True, help_text="Quartier de résidence")
    avenue_residence = models.CharField(max_length=200, blank=True, null=True, help_text="Avenue de résidence")
    numero_residence = models.CharField(max_length=20, blank=True, null=True, help_text="Numéro de résidence")
    
    # Contact
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?243[0-9]{9}$',
                message='Numéro de téléphone invalide. Format: +243XXXXXXXXX'
            )
        ],
        help_text="Numéro de téléphone"
    )
    email = models.EmailField(blank=True, null=True, help_text="Adresse email")
    
    # Profession et éducation
    profession = models.CharField(max_length=200, blank=True, null=True, help_text="Profession")
    niveau_etude = models.CharField(
        max_length=50,
        choices=[
            ('Aucun', 'Aucun'),
            ('Primaire', 'Primaire'),
            ('Secondaire', 'Secondaire'),
            ('Supérieur', 'Supérieur'),
            ('Universitaire', 'Universitaire'),
        ],
        blank=True,
        null=True,
        help_text="Niveau d'étude"
    )
    
    # Pièce d'identité
    type_piece_identite = models.CharField(
        max_length=50,
        choices=[
            ('Acte de naissance', 'Acte de naissance'),
            ('Jugement supplétif', 'Jugement supplétif'),
            ('Carte d\'identité', 'Carte d\'identité'),
            ('Passeport', 'Passeport'),
            ('Autre', 'Autre'),
        ],
        help_text="Type de pièce d'identité"
    )
    numero_piece_identite = models.CharField(max_length=50, help_text="Numéro de pièce d'identité")
    date_emission_piece = models.DateField(help_text="Date d'émission de la pièce")
    lieu_emission_piece = models.CharField(max_length=200, help_text="Lieu d'émission de la pièce")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    version = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'fgp_person_core'
        managed = False
        verbose_name = 'Personne FGP'
        verbose_name_plural = 'Personnes FGP'
        indexes = [
            models.Index(fields=['nom']),
            models.Index(fields=['prenom']),
            models.Index(fields=['date_naissance']),
            models.Index(fields=['province_residence']),
            models.Index(fields=['telephone']),
        ]
    
    def __str__(self):
        return f"{self.nin} - {self.nom} {self.prenom}"
    
    def get_full_name(self):
        """Retourne le nom complet"""
        parts = [self.nom]
        if self.postnom:
            parts.append(self.postnom)
        parts.append(self.prenom)
        return ' '.join(parts)
    
    def get_address(self):
        """Retourne l'adresse complète"""
        parts = []
        if self.numero_residence:
            parts.append(self.numero_residence)
        if self.avenue_residence:
            parts.append(self.avenue_residence)
        if self.quartier_residence:
            parts.append(self.quartier_residence)
        if self.commune_residence:
            parts.append(self.commune_residence)
        if self.territoire_residence:
            parts.append(self.territoire_residence)
        if self.province_residence:
            parts.append(self.province_residence)
        return ', '.join(parts)
    
    def get_age(self):
        """Calcule l'âge en années"""
        today = timezone.now().date()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )


class StrataMembership(models.Model):
    """
    Appartenance aux différentes strates
    """
    
    STRATE_CHOICES = [
        ('ELEVES', 'Élèves'),
        ('ETUDIANTS', 'Étudiants'),
        ('ELECTEURS', 'Électeurs'),
        ('PNC', 'Police Nationale Congolaise'),
        ('FARDC', 'Forces Armées'),
        ('PRISON', 'Prisonniers'),
        ('REFUGIE', 'Réfugiés/Apatrides'),
        ('ENFANT', 'Enfants'),
        ('FONCTIONNAIRE', 'Fonctionnaires'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Actif'),
        ('INACTIVE', 'Inactif'),
        ('SUSPENDED', 'Suspendu'),
    ]
    
    nin = models.ForeignKey(
        PersonCore,
        on_delete=models.CASCADE,
        related_name='strata_memberships',
        help_text="Personne concernée"
    )
    strate_code = models.CharField(
        max_length=20,
        choices=STRATE_CHOICES,
        help_text="Code de la strate"
    )
    valid_from = models.DateField(help_text="Date de début de validité")
    valid_to = models.DateField(blank=True, null=True, help_text="Date de fin de validité")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        help_text="Statut dans la strate"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'fgp_strata_membership'
        managed = False
        verbose_name = 'Appartenance à une strate'
        verbose_name_plural = 'Appartenances aux strates'
        unique_together = ['nin', 'strate_code', 'valid_from']
        indexes = [
            models.Index(fields=['strate_code']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.nin.nin} - {self.get_strate_code_display()} ({self.status})"


class Document(models.Model):
    """
    Documents et pièces jointes
    """
    
    DOCUMENT_TYPES = [
        ('acte_naissance', 'Acte de naissance'),
        ('carte_identite', 'Carte d\'identité'),
        ('passeport', 'Passeport'),
        ('diplome', 'Diplôme'),
        ('attestation', 'Attestation'),
        ('autre', 'Autre'),
    ]
    
    nin = models.ForeignKey(
        PersonCore,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Personne concernée"
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES,
        help_text="Type de document"
    )
    document_uri = models.URLField(help_text="URI du document")
    document_hash = models.CharField(
        max_length=64,
        help_text="Hash SHA-256 du document"
    )
    file_size = models.BigIntegerField(blank=True, null=True, help_text="Taille du fichier en octets")
    mime_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type MIME")
    is_verified = models.BooleanField(default=False, help_text="Document vérifié")
    verified_by = models.CharField(max_length=100, blank=True, null=True, help_text="Vérifié par")
    verified_at = models.DateTimeField(blank=True, null=True, help_text="Date de vérification")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'fgp_documents'
        managed = False
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.nin.nin} - {self.get_document_type_display()}"
