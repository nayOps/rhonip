"""
Modèles pour les extensions par strate du système FGP
"""

from django.db import models
from django.core.validators import RegexValidator
from django.db.models import JSONField


class ExtensionBase(models.Model):
    """Modèle de base pour toutes les extensions"""
    nin = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^CD-\d{4}-\d{4}-\d{7}$',
            message='Format NIN invalide: CD-YYYY-NNNN-NNNNNNN'
        )],
        help_text="Numéro d'Identification Nationale"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class ExtensionEducation(ExtensionBase):
    """Extension pour les élèves et étudiants"""
    # Champs obligatoires
    matricule_scolaire = models.CharField(
        max_length=50,
        help_text="Matricule de l'élève/étudiant"
    )
    etablissement = models.CharField(
        max_length=200,
        help_text="Nom de l'établissement"
    )
    code_etablissement = models.CharField(
        max_length=20,
        help_text="Code officiel de l'établissement (MENPS)"
    )
    niveau = models.CharField(
        max_length=50,
        choices=[
            ('1re Primaire', '1re Primaire'),
            ('2e Primaire', '2e Primaire'),
            ('3e Primaire', '3e Primaire'),
            ('4e Primaire', '4e Primaire'),
            ('5e Primaire', '5e Primaire'),
            ('6e Primaire', '6e Primaire'),
            ('1re Secondaire', '1re Secondaire'),
            ('2e Secondaire', '2e Secondaire'),
            ('3e Secondaire', '3e Secondaire'),
            ('4e Secondaire', '4e Secondaire'),
            ('5e Secondaire', '5e Secondaire'),
            ('6e Secondaire', '6e Secondaire'),
            ('L1', 'L1'),
            ('L2', 'L2'),
            ('L3', 'L3'),
            ('M1', 'M1'),
            ('M2', 'M2'),
            ('Doctorat', 'Doctorat'),
        ],
        help_text="Niveau d'études"
    )
    cycle = models.CharField(
        max_length=20,
        choices=[
            ('Primaire', 'Primaire'),
            ('Secondaire', 'Secondaire'),
            ('Supérieur', 'Supérieur'),
        ],
        help_text="Cycle d'études"
    )
    annee_scolaire = models.CharField(
        max_length=9,
        help_text="Année académique (ex: 2024-2025)"
    )
    statut_scolaire = models.CharField(
        max_length=20,
        choices=[
            ('Régulier', 'Régulier'),
            ('Redoublant', 'Redoublant'),
            ('Boursier', 'Boursier'),
            ('Suspension', 'Suspension'),
            ('Abandon', 'Abandon'),
        ],
        default='Régulier',
        help_text="Statut scolaire"
    )
    
    # Champs optionnels
    section = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Section ou spécialité (ex: Scientifique, Littéraire)"
    )
    responsable_tuteur = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nom complet du tuteur légal"
    )
    contact_tuteur = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Téléphone du tuteur"
    )
    lien_tuteur = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('Père', 'Père'),
            ('Mère', 'Mère'),
            ('Tuteur légal', 'Tuteur légal'),
            ('Oncle', 'Oncle'),
            ('Tante', 'Tante'),
            ('Grand-père', 'Grand-père'),
            ('Grand-mère', 'Grand-mère'),
            ('Autre', 'Autre'),
        ],
        help_text="Lien de parenté avec le tuteur"
    )
    
    # Métadonnées
    type_etablissement = models.CharField(
        max_length=20,
        choices=[
            ('Public', 'Public'),
            ('Privé', 'Privé'),
            ('Confessionnel', 'Confessionnel'),
            ('International', 'International'),
        ],
        default='Public',
        help_text="Type d'établissement"
    )
    province_etablissement = models.CharField(
        max_length=50,
        help_text="Province de l'établissement"
    )
    
    class Meta:
        db_table = 'ext_education'
        verbose_name = "Extension Éducation"
        verbose_name_plural = "Extensions Éducation"
        unique_together = ['nin', 'matricule_scolaire']
    
    def __str__(self):
        return f"{self.nin} - {self.etablissement} ({self.niveau})"


class ExtensionElectoral(ExtensionBase):
    """Extension pour les électeurs"""
    centre_vote = models.CharField(
        max_length=200,
        help_text="Nom du centre de vote"
    )
    code_centre_vote = models.CharField(
        max_length=20,
        help_text="Code CENI du centre de vote"
    )
    circonscription = models.CharField(
        max_length=100,
        help_text="Circonscription électorale"
    )
    secteur_vote = models.CharField(
        max_length=100,
        help_text="Secteur de vote"
    )
    statut_inscription = models.CharField(
        max_length=20,
        choices=[
            ('Inscrit', 'Inscrit'),
            ('Radié', 'Radié'),
            ('En attente', 'En attente'),
            ('Suspendu', 'Suspendu'),
        ],
        default='Inscrit',
        help_text="Statut d'inscription électorale"
    )
    date_inscription_ceni = models.DateField(
        help_text="Date d'inscription à la CENI"
    )
    bureau_vote = models.CharField(
        max_length=20,
        help_text="Code du bureau de vote"
    )
    
    # Informations géographiques
    province_vote = models.CharField(
        max_length=50,
        help_text="Province de vote"
    )
    territoire_vote = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Territoire de vote"
    )
    commune_vote = models.CharField(
        max_length=50,
        help_text="Commune de vote"
    )
    
    # Historique électoral
    derniere_election = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Dernière élection participée"
    )
    participation_historique = JSONField(
        default=list,
        blank=True,
        help_text="Historique des participations électorales"
    )
    
    class Meta:
        db_table = 'ext_electoral'
        verbose_name = "Extension Électorale"
        verbose_name_plural = "Extensions Électorales"
        unique_together = ['nin', 'code_centre_vote']
    
    def __str__(self):
        return f"{self.nin} - {self.centre_vote} ({self.secteur_vote})"


class ExtensionPNC(ExtensionBase):
    """Extension pour les membres de la Police Nationale Congolaise"""
    matricule_pnc = models.CharField(
        max_length=20,
        help_text="Matricule PNC"
    )
    grade = models.CharField(
        max_length=50,
        choices=[
            ('Commissaire Général', 'Commissaire Général'),
            ('Commissaire Divisionnaire', 'Commissaire Divisionnaire'),
            ('Commissaire Principal', 'Commissaire Principal'),
            ('Commissaire', 'Commissaire'),
            ('Commissaire Adjoint', 'Commissaire Adjoint'),
            ('Inspecteur Principal', 'Inspecteur Principal'),
            ('Inspecteur', 'Inspecteur'),
            ('Sous-Inspecteur', 'Sous-Inspecteur'),
            ('Sergent Major', 'Sergent Major'),
            ('Sergent', 'Sergent'),
            ('Caporal Chef', 'Caporal Chef'),
            ('Caporal', 'Caporal'),
            ('Agent Principal', 'Agent Principal'),
            ('Agent', 'Agent'),
        ],
        help_text="Grade hiérarchique"
    )
    unite = models.CharField(
        max_length=200,
        help_text="Unité d'affectation"
    )
    fonction = models.CharField(
        max_length=100,
        help_text="Fonction occupée"
    )
    date_integration = models.DateField(
        help_text="Date d'entrée dans la PNC"
    )
    statut_service = models.CharField(
        max_length=20,
        choices=[
            ('Actif', 'Actif'),
            ('Suspendu', 'Suspendu'),
            ('Retraité', 'Retraité'),
            ('Démissionnaire', 'Démissionnaire'),
            ('Décédé', 'Décédé'),
        ],
        default='Actif',
        help_text="Statut de service"
    )
    zone_affectation = models.CharField(
        max_length=100,
        help_text="Zone d'affectation"
    )
    
    # Informations spécialisées
    type_arme = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Type d'arme de dotation"
    )
    numero_arme = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Numéro de série de l'arme"
    )
    specialite = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Spécialité policière"
    )
    
    # Historique de service
    historique_affectations = JSONField(
        default=list,
        blank=True,
        help_text="Historique des affectations"
    )
    sanctions = JSONField(
        default=list,
        blank=True,
        help_text="Historique des sanctions disciplinaires"
    )
    
    class Meta:
        db_table = 'ext_pnc'
        verbose_name = "Extension PNC"
        verbose_name_plural = "Extensions PNC"
        unique_together = ['nin', 'matricule_pnc']
    
    def __str__(self):
        return f"{self.nin} - {self.matricule_pnc} ({self.grade})"


class ExtensionFARDC(ExtensionBase):
    """Extension pour les membres des Forces Armées de la RDC"""
    matricule_fardc = models.CharField(
        max_length=20,
        help_text="Matricule FARDC"
    )
    grade = models.CharField(
        max_length=50,
        choices=[
            ('Général', 'Général'),
            ('Lieutenant Général', 'Lieutenant Général'),
            ('Major Général', 'Major Général'),
            ('Brigadier Général', 'Brigadier Général'),
            ('Colonel', 'Colonel'),
            ('Lieutenant Colonel', 'Lieutenant Colonel'),
            ('Major', 'Major'),
            ('Capitaine', 'Capitaine'),
            ('Lieutenant', 'Lieutenant'),
            ('Sous-Lieutenant', 'Sous-Lieutenant'),
            ('Adjudant Chef', 'Adjudant Chef'),
            ('Adjudant', 'Adjudant'),
            ('Sergent Major', 'Sergent Major'),
            ('Sergent', 'Sergent'),
            ('Caporal Chef', 'Caporal Chef'),
            ('Caporal', 'Caporal'),
            ('Soldat de 1ère Classe', 'Soldat de 1ère Classe'),
            ('Soldat', 'Soldat'),
        ],
        help_text="Grade militaire"
    )
    unite_affectation = models.CharField(
        max_length=200,
        help_text="Unité d'affectation (Brigade, Bataillon)"
    )
    zone_operation = models.CharField(
        max_length=100,
        help_text="Zone d'opération"
    )
    fonction = models.CharField(
        max_length=100,
        help_text="Fonction occupée"
    )
    date_integration = models.DateField(
        help_text="Date d'entrée dans les FARDC"
    )
    statut_militaire = models.CharField(
        max_length=20,
        choices=[
            ('Actif', 'Actif'),
            ('Réserviste', 'Réserviste'),
            ('Blessé', 'Blessé'),
            ('Retraité', 'Retraité'),
            ('Démissionnaire', 'Démissionnaire'),
            ('Décédé', 'Décédé'),
        ],
        default='Actif',
        help_text="Statut militaire"
    )
    type_mission = models.CharField(
        max_length=20,
        choices=[
            ('Interne', 'Interne'),
            ('Externe', 'Externe'),
            ('ONU', 'ONU'),
            ('UA', 'UA'),
        ],
        default='Interne',
        help_text="Type de mission"
    )
    
    # Informations spécialisées
    arme_service = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Arme de service"
    )
    specialite = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Spécialité militaire"
    )
    
    # Historique militaire
    historique_affectations = JSONField(
        default=list,
        blank=True,
        help_text="Historique des affectations"
    )
    missions = JSONField(
        default=list,
        blank=True,
        help_text="Historique des missions"
    )
    decorations = JSONField(
        default=list,
        blank=True,
        help_text="Décorations et médailles"
    )
    
    class Meta:
        db_table = 'ext_fardc'
        verbose_name = "Extension FARDC"
        verbose_name_plural = "Extensions FARDC"
        unique_together = ['nin', 'matricule_fardc']
    
    def __str__(self):
        return f"{self.nin} - {self.matricule_fardc} ({self.grade})"


class ExtensionPrison(ExtensionBase):
    """Extension pour les détenus"""
    numero_dossier_judiciaire = models.CharField(
        max_length=50,
        help_text="Numéro du dossier judiciaire"
    )
    centre_detention = models.CharField(
        max_length=200,
        help_text="Nom du centre de détention"
    )
    statut_detention = models.CharField(
        max_length=30,
        choices=[
            ('Préventif', 'Préventif'),
            ('Condamné', 'Condamné'),
            ('Liberté conditionnelle', 'Liberté conditionnelle'),
            ('Assignation à résidence', 'Assignation à résidence'),
            ('Libéré', 'Libéré'),
        ],
        help_text="Statut de détention"
    )
    date_incarceration = models.DateField(
        help_text="Date d'incarcération"
    )
    date_liberation_prevue = models.DateField(
        blank=True,
        null=True,
        help_text="Date prévue de libération"
    )
    infraction = models.CharField(
        max_length=200,
        help_text="Nature de l'infraction"
    )
    autorite_judiciaire = models.CharField(
        max_length=200,
        help_text="Autorité judiciaire compétente"
    )
    
    # Informations judiciaires
    duree_peine = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Durée de la peine"
    )
    type_peine = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Type de peine"
    )
    
    # Informations pénitentiaires
    pavillon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Pavillon d'affectation"
    )
    cellule = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Numéro de cellule"
    )
    
    # Historique pénitentiaire
    historique_detention = JSONField(
        default=list,
        blank=True,
        help_text="Historique des détentions"
    )
    sanctions_disciplinaires = JSONField(
        default=list,
        blank=True,
        help_text="Sanctions disciplinaires"
    )
    
    class Meta:
        db_table = 'ext_prison'
        verbose_name = "Extension Prison"
        verbose_name_plural = "Extensions Prison"
        unique_together = ['nin', 'numero_dossier_judiciaire']
    
    def __str__(self):
        return f"{self.nin} - {self.centre_detention} ({self.statut_detention})"


class ExtensionRefugie(ExtensionBase):
    """Extension pour les réfugiés et demandeurs d'asile"""
    numero_hcr = models.CharField(
        max_length=50,
        help_text="Numéro HCR"
    )
    pays_origine = models.CharField(
        max_length=100,
        help_text="Pays d'origine"
    )
    statut_juridique = models.CharField(
        max_length=20,
        choices=[
            ('Réfugié', 'Réfugié'),
            ('Demandeur d\'asile', 'Demandeur d\'asile'),
            ('Apatride', 'Apatride'),
            ('Statut humanitaire', 'Statut humanitaire'),
        ],
        help_text="Statut juridique"
    )
    document_sejour = models.CharField(
        max_length=100,
        help_text="Type de document de séjour"
    )
    date_entree_territoire = models.DateField(
        help_text="Date d'entrée sur le territoire"
    )
    camp_refugie = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Nom du camp de réfugiés"
    )
    organisme_encadrement = models.CharField(
        max_length=100,
        choices=[
            ('HCR', 'HCR'),
            ('DGM', 'DGM'),
            ('ONG', 'ONG'),
            ('Autre', 'Autre'),
        ],
        default='HCR',
        help_text="Organisme d'encadrement"
    )
    
    # Informations additionnelles
    motif_fuite = models.TextField(
        blank=True,
        null=True,
        help_text="Motif de la fuite du pays d'origine"
    )
    situation_familiale = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('Célibataire', 'Célibataire'),
            ('Marié(e)', 'Marié(e)'),
            ('Divorcé(e)', 'Divorcé(e)'),
            ('Veuf/Veuve', 'Veuf/Veuve'),
            ('Séparé(e)', 'Séparé(e)'),
        ],
        help_text="Situation familiale"
    )
    nombre_enfants = models.IntegerField(
        default=0,
        help_text="Nombre d'enfants"
    )
    
    # Historique
    historique_demande = JSONField(
        default=list,
        blank=True,
        help_text="Historique de la demande d'asile"
    )
    
    class Meta:
        db_table = 'ext_refugie'
        verbose_name = "Extension Réfugié"
        verbose_name_plural = "Extensions Réfugiés"
        unique_together = ['nin', 'numero_hcr']
    
    def __str__(self):
        return f"{self.nin} - {self.numero_hcr} ({self.statut_juridique})"


class ExtensionEnfant(ExtensionBase):
    """Extension pour les enfants mineurs"""
    tuteur_nom = models.CharField(
        max_length=200,
        help_text="Nom complet du tuteur"
    )
    tuteur_nin = models.CharField(
        max_length=20,
        help_text="NIN du tuteur"
    )
    lien_tuteur = models.CharField(
        max_length=50,
        choices=[
            ('Père', 'Père'),
            ('Mère', 'Mère'),
            ('Oncle', 'Oncle'),
            ('Tante', 'Tante'),
            ('Grand-père', 'Grand-père'),
            ('Grand-mère', 'Grand-mère'),
            ('Tuteur légal', 'Tuteur légal'),
            ('Autre', 'Autre'),
        ],
        help_text="Lien avec le tuteur"
    )
    adresse_tuteur = models.TextField(
        help_text="Adresse complète du tuteur"
    )
    document_parentalite = models.CharField(
        max_length=100,
        choices=[
            ('Acte de naissance', 'Acte de naissance'),
            ('Jugement supplétif', 'Jugement supplétif'),
            ('Déclaration de naissance', 'Déclaration de naissance'),
            ('Autre', 'Autre'),
        ],
        help_text="Document de parenté"
    )
    autorisation_parentale = models.BooleanField(
        default=True,
        help_text="Autorisation parentale pour l'enrôlement"
    )
    structure_accueil = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Structure d'accueil (orphelinat, centre, etc.)"
    )
    
    # Informations additionnelles
    contact_tuteur = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact du tuteur"
    )
    situation_familiale = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('Famille complète', 'Famille complète'),
            ('Famille monoparentale', 'Famille monoparentale'),
            ('Orphelin', 'Orphelin'),
            ('Abandonné', 'Abandonné'),
            ('Autre', 'Autre'),
        ],
        help_text="Situation familiale"
    )
    
    class Meta:
        db_table = 'ext_enfant'
        verbose_name = "Extension Enfant"
        verbose_name_plural = "Extensions Enfants"
        unique_together = ['nin', 'tuteur_nin']
    
    def __str__(self):
        return f"{self.nin} - Enfant de {self.tuteur_nom}"


class ExtensionEtranger(ExtensionBase):
    """Extension pour les étrangers résidant en RDC"""
    # Champs obligatoires
    pays_origine = models.CharField(
        max_length=100,
        help_text="Pays d'origine"
    )
    numero_passeport = models.CharField(
        max_length=50,
        help_text="Numéro du passeport"
    )
    
    # Informations passeport
    ville_delivrance = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ville de délivrance du passeport"
    )
    date_delivrance = models.DateField(
        blank=True,
        null=True,
        help_text="Date de délivrance"
    )
    date_expiration = models.DateField(
        blank=True,
        null=True,
        help_text="Date d'expiration"
    )
    
    # Visa/Permis de séjour
    numero_visa_permis = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Numéro du visa ou permis de séjour"
    )
    date_visa = models.DateField(
        blank=True,
        null=True,
        help_text="Date du visa"
    )
    type_sejour = models.CharField(
        max_length=50,
        choices=[
            ('Temporaire', 'Temporaire'),
            ('Permanent', 'Permanent'),
            ('Transit', 'Transit'),
            ('Diplomatique', 'Diplomatique'),
            ('Autre', 'Autre'),
        ],
        blank=True,
        null=True,
        help_text="Type de séjour"
    )
    
    # Résidence en RDC
    adresse_residence_rdc = models.TextField(
        blank=True,
        null=True,
        help_text="Adresse de résidence en RDC"
    )
    profession_rdc = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Profession exercée en RDC"
    )
    employeur_organisation = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Employeur ou organisation en RDC"
    )
    
    class Meta:
        db_table = 'ext_etrangers'
        verbose_name = "Extension Étranger"
        verbose_name_plural = "Extensions Étrangers"
        unique_together = ['nin', 'numero_passeport']
    
    def __str__(self):
        return f"{self.nin} - {self.pays_origine} ({self.numero_passeport})"


class ExtensionDeplace(ExtensionBase):
    """Extension pour les déplacés internes"""
    # Tous les champs sont optionnels
    lieu_origine = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Lieu d'origine avant déplacement"
    )
    province_origine = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Province d'origine"
    )
    territoire_origine = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Territoire d'origine"
    )
    raison_deplacement = models.TextField(
        blank=True,
        null=True,
        help_text="Raison du déplacement"
    )
    date_deplacement = models.DateField(
        blank=True,
        null=True,
        help_text="Date du déplacement"
    )
    site_camp_deplaces = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Site ou camp de déplacés"
    )
    numero_carte_deplace = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Numéro de carte de déplacé"
    )
    organisme_assistance = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Organisme d'assistance"
    )
    type_hebergement = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Type d'hébergement"
    )
    chef_menage_nin = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="NIN du chef de ménage"
    )
    situation_sanitaire = models.TextField(
        blank=True,
        null=True,
        help_text="Situation sanitaire"
    )
    besoins_prioritaires = models.TextField(
        blank=True,
        null=True,
        help_text="Besoins prioritaires"
    )
    
    class Meta:
        db_table = 'ext_deplaces'
        verbose_name = "Extension Déplacé Interne"
        verbose_name_plural = "Extensions Déplacés Internes"
    
    def __str__(self):
        return f"{self.nin} - Déplacé de {self.lieu_origine or 'N/A'}"


class ExtensionDiaspora(ExtensionBase):
    """Extension pour la diaspora congolaise"""
    # Tous les champs sont optionnels
    pays_residence_actuelle = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Pays de résidence actuelle"
    )
    ville_residence = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ville de résidence"
    )
    date_depart_rdc = models.DateField(
        blank=True,
        null=True,
        help_text="Date de départ de la RDC"
    )
    type_residence = models.CharField(
        max_length=50,
        choices=[
            ('Permanent', 'Permanent'),
            ('Temporaire', 'Temporaire'),
            ('Étudiant', 'Étudiant'),
            ('Travailleur', 'Travailleur'),
            ('Autre', 'Autre'),
        ],
        blank=True,
        null=True,
        help_text="Type de résidence à l'étranger"
    )
    document_etranger = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Type de document étranger (carte de résident, passeport du pays hôte, etc.)"
    )
    numero_document_etranger = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Numéro du document étranger"
    )
    profession_etranger = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Profession à l'étranger"
    )
    employeur_etranger = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Employeur à l'étranger"
    )
    souhait_retour = models.BooleanField(
        default=False,
        help_text="Souhaite retourner en RDC"
    )
    date_retour_prevue = models.DateField(
        blank=True,
        null=True,
        help_text="Date de retour prévue"
    )
    representation_consulaire = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Représentation consulaire de rattachement"
    )
    ville_consulat = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ville du consulat"
    )
    statut_legal_etranger = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Statut légal dans le pays hôte"
    )
    double_nationalite = models.BooleanField(
        default=False,
        help_text="Possède une double nationalité"
    )
    pays_autre_nationalite = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Pays de l'autre nationalité"
    )
    
    class Meta:
        db_table = 'ext_diaspora'
        verbose_name = "Extension Diaspora"
        verbose_name_plural = "Extensions Diaspora"
    
    def __str__(self):
        return f"{self.nin} - Diaspora en {self.pays_residence_actuelle or 'N/A'}"


class ExtensionFonctionnaire(ExtensionBase):
    """Extension pour les fonctionnaires de l'État"""
    matricule = models.CharField(max_length=50, default='', blank=True)
    ministere = models.CharField(max_length=200, default='', blank=True)
    grade = models.CharField(max_length=50, default='', blank=True)

    class Meta:
        db_table = 'ext_fonctionnaire'
        verbose_name = 'Extension Fonctionnaire'
        verbose_name_plural = 'Extensions Fonctionnaires'

    def __str__(self):
        return f'{self.nin} - {self.ministere or "Fonctionnaire"}'
