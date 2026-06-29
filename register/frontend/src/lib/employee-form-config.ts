/**
 * Métadonnées alignées sur rh/employee/models/employee.py (layout Crispy Payday).
 */
import type { EmployeeFormData, EmployeeGender, EmployeeMaritalStatus, EmployeePaymentMethod, IdCardType } from '@/types/employee';

export const EMPLOYEE_GENDER_OPTIONS: { value: EmployeeGender; label: string }[] = [
  { value: 'male', label: 'Masculin' },
  { value: 'female', label: 'Féminin' },
];

export const EMPLOYEE_MARITAL_OPTIONS: { value: EmployeeMaritalStatus; label: string }[] = [
  { value: 'single', label: 'Célibataire' },
  { value: 'maried', label: 'Marié(e)' },
  { value: 'divorced', label: 'Divorcé(e)' },
];

export const EMPLOYEE_PAYMENT_OPTIONS: { value: EmployeePaymentMethod; label: string }[] = [
  { value: 'cash', label: 'Cash' },
  { value: 'bank', label: 'Banque' },
  { value: 'mobile money', label: 'Mobile money' },
];

/** Libellés identiques au formulaire RH (verbose_name Django) */
export const EMPLOYEE_FIELD_LABELS = {
  photo: 'Photo',
  registration_number: 'Matricule',
  social_security_number: 'Numéro de sécurité sociale',
  branch: 'Site',
  agreement: 'Type de contrat',
  date_of_join: "Date d'engagement",
  direction: 'Direction',
  sub_direction: 'Sous-direction',
  service: 'Service',
  grade: 'Grade',
  designation: 'Position',
  first_name: 'Prénom',
  middle_name: 'Post-nom',
  last_name: 'Nom',
  gender: 'Genre',
  date_of_birth: 'Date de naissance',
  place_of_birth: 'Lieu de naissance',
  citizenship: 'Nationalité',
  home_country: "Pays d'origine",
  home_province: "Province d'origine",
  home_territory: "Territoire d'origine",
  home_sector: "Secteur d'origine",
  home_groupement: "Groupement d'origine",
  home_village: "Village d'origine",
  type_of_identity: "Type de pièce d'identité",
  identity_number: "Numéro de pièce d'identité",
  date_of_issue: 'Date de délivrance',
  date_of_expiry: "Date d'expiration",
  place_of_issue: 'Lieu de délivrance',
  appointment_letter: 'Lettre de nomination',
  appointment_number: 'Numéro de nomination',
  marital_status: 'État civil',
  spouse: 'Conjoint',
  telephone_number: 'Numéro de téléphone professional',
  mobile_number: 'Numéro de téléphone mobile',
  email_professional: 'Email professional',
  email: 'Email',
  physical_address: 'Adresse physique',
  emergency_information: "Informations d'urgence",
  emergency_contact: "Contact d'urgence",
  emergency_phone: "Numéro de téléphone d'urgence",
  relationship: 'Relation',
  refering_doctor: 'Médecin référent',
  refering_doctor_phone: 'Numéro de téléphone du médecin référent',
  refering_doctor_email: 'Email du médecin référent',
  payment_method: 'Mode de paiement',
  payer_name: 'Nom du payeur',
  payment_account: 'Numéro de compte',
  comment: 'Commentaire',
  child_full_name: 'Nom complet',
  child_date_of_birth: 'Date de naissance',
  education_institution: 'Institution',
  education_degree: 'Diplôme',
  experience_organization: 'Organisation',
  experience_position: 'Poste',
  experience_start_date: 'Date de début',
  experience_end_date: 'Date de fin',
  experience_photo: 'Photo',
  document_name: 'Nom',
  document_file: 'Document',
} as const;

export const ID_CARD_TYPE_OPTIONS: { value: IdCardType; label: string }[] = [
  { value: 'driver_license', label: 'Permis de conduire' },
  { value: "voter's card", label: "Carte d'électeur" },
  { value: 'national_id', label: 'National ID' },
  { value: 'passport', label: 'Passeport' },
  { value: 'document', label: 'Document' },
  { value: 'other', label: 'Other' },
];

/** Aucun champ obligatoire côté guichet (aligné RH). */
export const RH_UI_REQUIRED_FIELDS = [] as const satisfies readonly (keyof EmployeeFormData)[];

export type RhRequiredField = keyof typeof EMPLOYEE_FIELD_LABELS;

export function isRhFormValid(_data: EmployeeFormData): boolean {
  return true;
}

export function requiredLabel(label: string, _required?: boolean): string {
  return label;
}
