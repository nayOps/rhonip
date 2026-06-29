// Types TypeScript pour le système FGP

export interface PersonCore {
  nin: string;
  nom: string;
  postnom?: string;
  prenom: string;
  sexe: 'M' | 'F';
  date_naissance: string;
  lieu_naissance: string;
  province_naissance: string;
  nationalite: string;
  statut_matrimonial: string;
  nom_pere: string;
  nom_mere: string;
  adresse_province: string;
  adresse_territoire: string;
  adresse_commune: string;
  adresse_quartier: string;
  adresse_avenue?: string;
  adresse_numero?: string;
  telephone?: string;
  email?: string;
  profession?: string;
  niveau_etude: string;
  type_piece: string;
  numero_piece: string;
  date_emission: string;
  lieu_emission: string;
  photo_uri?: string;
  created_at: string;
  updated_at: string;
}

// Types pour les empreintes digitales
export type FingerPosition = 
  | 'RIGHT_THUMB' | 'RIGHT_INDEX' | 'RIGHT_MIDDLE' | 'RIGHT_RING' | 'RIGHT_LITTLE'
  | 'LEFT_THUMB' | 'LEFT_INDEX' | 'LEFT_MIDDLE' | 'LEFT_RING' | 'LEFT_LITTLE';

export type FingerStatus = 'CAPTURED' | 'MISSING' | 'AMPUTATED' | 'DAMAGED' | 'PENDING';

export interface FingerprintCapture {
  position: FingerPosition;
  status: FingerStatus;
  quality?: number; // 0-100
  image?: string; // base64 ou URI
  timestamp?: string;
  reason?: string; // raison si manquant/endommagé
  /** Gabarit ISO / ANSI (base64) — FAP60 via device-bridge */
  templateBase64?: string;
  formatId?: number;
  nfiq?: number;
}

// Types pour l'iris
export type EyePosition = 'LEFT' | 'RIGHT';
export type EyeStatus = 'CAPTURED' | 'BLIND' | 'MISSING' | 'DAMAGED' | 'PENDING' | 'FAILED';

export interface IrisCapture {
  position: EyePosition;
  status: EyeStatus;
  quality?: number; // 0-100
  image?: string; // base64 ou URI
  timestamp?: string;
  reason?: string; // raison si aveugle/manquant
}

// Types pour les documents
export type DocumentType = 
  | 'FICHE_IDENTIFICATION' 
  | 'ACTE_NAISSANCE' 
  | 'JUGEMENT_SUPPLETIF'
  | 'CARTE_ELECTEUR'
  | 'CERTIFICAT_NATIONALITE'
  | 'PASSEPORT'
  | 'CARTE_ETUDIANT'
  | 'PERMIS_CONDUIRE'
  | 'AUTRE';

/** Structure logique du document scanné. */
export type DocumentStructure =
  | 'SINGLE'
  | 'RECTO_VERSO'
  | 'MULTI_PAGE'
  | 'MULTI_PAGE_RECTO_VERSO';

export type DocumentPageSide = 'RECTO' | 'VERSO' | 'PAGE';

export interface DocumentPage {
  id: string;
  side: DocumentPageSide;
  pageNumber: number;
  image: string;
  filename: string;
  size: number;
  mimeType: string;
  scannedAt: string;
}

/** Un document = une pièce (éventuellement plusieurs pages / recto-verso). */
export interface ScannedDocument {
  id: string;
  type: DocumentType;
  structure: DocumentStructure;
  pages: DocumentPage[];
  notes?: string;
  createdAt: string;
}

// Données biométriques complètes
export interface BiometricData {
  face_quality: number;
  face_uri: string;
  fingerprints: FingerprintCapture[];
  iris: IrisCapture[];
  fingerprints_quality?: number;
  fingerprints_uri?: string;
  iris_quality?: number;
  iris_uri?: string;
}

export interface EnrollmentRequest {
  core: PersonCore;
  biometrics: BiometricData;
  strata: string[];
  extensions: Record<string, any>;
  attachments: DocumentAttachment[];
  metadata: {
    device_id: string;
    operator_id: string;
    location: {
      province: string;
      territoire: string;
      commune: string;
    };
    timestamp: string;
  };
}

export interface DocumentAttachment {
  type: string;
  uri: string;
  hash: string;
  filename: string;
  size: number;
  mime_type: string;
}

// Données complètes d'enrôlement (workflow)
export interface EnrollmentWorkflowData {
  // Étape 1: Données de base
  baseData?: BaseEnrollmentData;
  
  // Étape 2: Extensions par strate
  extensions?: Record<string, any>;
  
  // Étape 3: Empreintes digitales
  fingerprints?: FingerprintCapture[];
  
  // Étape 4: Iris
  iris?: IrisCapture[];
  
  // Étape 5: Documents scannés
  documents?: ScannedDocument[];
  
  // Métadonnées
  currentStep?: 'base' | 'extensions' | 'fingerprints' | 'iris' | 'documents' | 'verification' | 'receipt';
  enrollmentId?: string;
  timestamp?: string;
}

// Données du formulaire de base
export interface BaseEnrollmentData {
  // Identité
  prenom: string;
  nom: string;
  postnom?: string;
  autres_noms?: string;
  sexe: 'M' | 'F';
  date_naissance: string;
  lieu_naissance: string;
  nationalite: string;
  taille?: number;
  couleur_yeux?: string;
  groupe_sanguin?: string;
  telephone?: string;
  email?: string;
  boite_postale?: string;
  
  // Origine
  origine_pays: string;
  origine_province: string;
  origine_ville: string;
  origine_commune: string;
  origine_quartier: string;
  
  // Résidence
  residence_pays: string;
  residence_province: string;
  residence_ville: string;
  residence_commune: string;
  residence_quartier: string;
  residence_rue?: string;
  residence_numero?: string;
  
  // Situation familiale
  etat_matrimonial?: string;
  nombre_enfants?: number;
  conjoint_nom?: string;
  conjoint_prenom?: string;
  conjoint_nationalite?: string;
  conjoint_lieu_naissance?: string;
  conjoint_date_naissance?: string;
  conjoint_telephone?: string;
  
  // Filiation
  pere_statut: 'EN_VIE' | 'DECEDE';
  pere_nom?: string;
  pere_prenom?: string;
  pere_nationalite?: string;
  pere_nin?: string;
  pere_lieu_naissance?: string;
  pere_date_naissance?: string;
  pere_adresse?: string;
  
  mere_statut: 'EN_VIE' | 'DECEDEE';
  mere_nom?: string;
  mere_prenom?: string;
  mere_nationalite?: string;
  mere_nin?: string;
  mere_lieu_naissance?: string;
  mere_date_naissance?: string;
  mere_adresse?: string;
  
  // Tuteur
  tuteur_nom?: string;
  tuteur_prenom?: string;
  tuteur_nationalite?: string;
  tuteur_lien?: string;
  tuteur_lieu_naissance?: string;
  tuteur_date_naissance?: string;
  tuteur_sexe?: 'M' | 'F';
  tuteur_adresse?: string;
  
  // Études
  niveau_etude?: string;
  certificat_diplome?: string;
  pays_obtention?: string;
  etablissement?: string;
  ville_etablissement?: string;
  annee_debut?: string;
  annee_obtention?: string;
  domaine?: string;
  specialisation?: string;
  mention?: string;
  numero_document?: string;
  
  // Profession
  profession?: string;
  employeur?: string;
  fonction?: string;
  
  // Pièces présentées
  piece_presentee?: string;
  numero_piece?: string;
  date_piece?: string;
  
  // Handicaps
  handicaps?: string[];
  
  // Strate(s)
  strata: string[];
  type_requete: string;
}

export interface EnrollmentResponse {
  nin: string;
  status: 'PENDING' | 'ENROLLED' | 'REJECTED' | 'UNDER_REVIEW';
  core_persisted: boolean;
  extensions_persisted: string[];
  abis_result: {
    match: boolean;
    score: number;
    candidate_nin?: string;
  };
  events: string[];
  created_at: string;
}

export interface StrataExtension {
  education?: EducationExtension;
  electoral?: ElectoralExtension;
  pnc?: PNCExtension;
  fardc?: FARDCExtension;
  prison?: PrisonExtension;
  refugee?: RefugeeExtension;
  enfant?: EnfantExtension;
  fonctionnaire?: FonctionnaireExtension;
}

export interface EducationExtension {
  matricule_scolaire: string;
  etablissement: string;
  code_etablissement: string;
  niveau: string;
  cycle: string;
  annee_scolaire: string;
  section?: string;
  statut_scolaire: string;
  responsable_tuteur: string;
  contact_tuteur: string;
  lien_tuteur: string;
}

export interface ElectoralExtension {
  centre_vote: string;
  code_centre_vote: string;
  circonscription: string;
  secteur_vote: string;
  statut_inscription: string;
  date_inscription_ceni: string;
  bureau_vote: string;
}

export interface PNCExtension {
  matricule_pnc: string;
  grade: string;
  unite: string;
  fonction: string;
  date_integration: string;
  statut_service: string;
  zone_affectation: string;
  type_arme?: string;
}

export interface FARDCExtension {
  matricule_fardc: string;
  grade: string;
  unite_affectation: string;
  zone_operation: string;
  fonction: string;
  date_integration: string;
  statut_militaire: string;
  type_mission: string;
}

export interface PrisonExtension {
  numero_dossier_judiciaire: string;
  centre_detention: string;
  statut_detention: string;
  date_incarceration: string;
  date_liberation_prevue?: string;
  infraction: string;
  autorite_judiciaire: string;
}

export interface RefugeeExtension {
  numero_hcr: string;
  pays_origine: string;
  statut_juridique: string;
  document_sejour: string;
  date_entree_territoire: string;
  camp_refugie?: string;
  organisme_encadrement: string;
}

export interface EnfantExtension {
  tuteur_nom: string;
  tuteur_nin: string;
  lien_tuteur: string;
  adresse_tuteur: string;
  document_parentalite: string;
  autorisation_parentale: boolean;
  structure_accueil?: string;
}

export interface FonctionnaireExtension {
  matricule_fonctionnaire: string;
  ministere_affectation: string;
  service_affectation: string;
  poste: string;
  date_recrutement: string;
  statut_service: string;
  salaire_brut?: number;
}

export interface SearchFilters {
  nin?: string;
  nom?: string;
  prenom?: string;
  telephone?: string;
  strata?: string[];
  province?: string;
  date_from?: string;
  date_to?: string;
}

export interface SearchResult {
  nin: string;
  nom: string;
  prenom: string;
  strata: string[];
  last_updated: string;
  status: string;
}

export interface DashboardRecentSession {
  session_id: string;
  registration_number: string;
  agent_name: string;
  status: string;
  modality_status?: Record<string, unknown>;
  created_at: string | null;
}

export interface DashboardStats {
  total_enrolled: number;
  enrollments_today: number;
  enrollments_this_month: number;
  sessions_total?: number;
  sessions_failed?: number;
  sessions_with_matricule?: number;
  biometric_total?: number;
  fingerprints_total?: number;
  by_status?: Record<string, number>;
  by_province: Record<string, number>;
  recent_sessions?: DashboardRecentSession[];
  quality_score: number;
  system_health: {
    status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
    uptime: number;
    response_time: number;
  };
}

export interface AuditTrail {
  id: string;
  nin: string;
  action: string;
  operator_id: string;
  timestamp: string;
  details: Record<string, any>;
  ip_address: string;
  user_agent: string;
}

export type StrataType = 
  | 'ELEVES' 
  | 'ETUDIANT' 
  | 'ELECTEUR' 
  | 'PNC' 
  | 'FARDC' 
  | 'PRISON' 
  | 'REFUGIE' 
  | 'ENFANT' 
  | 'FONCTIONNAIRE';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
  page: number;
  page_size: number;
}
