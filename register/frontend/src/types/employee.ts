import { DEFAULT_COUNTRY } from '@/lib/countries';

export type EmployeeGender = 'male' | 'female';
export type EmployeeMaritalStatus = 'single' | 'maried' | 'divorced';
export type EmployeePaymentMethod = 'cash' | 'bank' | 'mobile money';

export type IdCardType =
  | 'driver_license'
  | "voter's card"
  | 'national_id'
  | 'passport'
  | 'document'
  | 'other';

export interface EmployeeChildRow {
  full_name: string;
  date_of_birth?: string;
}

export interface EmployeeEducationRow {
  institution?: string;
  degree?: string;
  start_date?: string;
  end_date?: string;
}

export interface EmployeeExperienceRow {
  organization?: string;
  position?: string;
  start_date?: string;
  end_date?: string;
  photo_name?: string;
  photo_base64?: string;
}

export interface EmployeeDocumentRow {
  name: string;
  file_name?: string;
  file_base64?: string;
}

export interface EmployeeFormData {
  photo_name?: string;
  photo_base64?: string;
  registration_number?: string;
  social_security_number?: string;

  branch?: string;
  agreement?: string;
  date_of_join?: string;
  direction?: string;
  sub_direction?: string;
  service?: string;
  grade?: string;
  designation?: string;

  first_name?: string;
  middle_name?: string;
  last_name?: string;
  gender?: EmployeeGender;
  date_of_birth?: string;
  place_of_birth?: string;

  citizenship?: string;
  home_country?: string;
  home_province?: string;
  home_territory?: string;
  home_sector?: string;
  home_groupement?: string;
  home_village?: string;

  type_of_identity?: IdCardType | string;
  identity_number?: string;
  date_of_issue?: string;
  date_of_expiry?: string;
  place_of_issue?: string;

  appointment_number?: string;
  appointment_letter_name?: string;
  appointment_letter_base64?: string;

  marital_status?: EmployeeMaritalStatus;
  spouse?: string;

  telephone_number?: string;
  mobile_number?: string;
  email_professional?: string;
  email?: string;
  physical_address?: string;

  emergency_contact?: string;
  emergency_phone?: string;
  relationship?: string;
  emergency_information?: string;

  refering_doctor?: string;
  refering_doctor_phone?: string;
  refering_doctor_email?: string;

  payment_method?: EmployeePaymentMethod;
  payer_name?: string;
  payment_account?: string;
  comment?: string;

  /** Inlines RH (employee.Child, Education, Experience, Document) */
  children?: EmployeeChildRow[];
  educations?: EmployeeEducationRow[];
  experiences?: EmployeeExperienceRow[];
  employee_documents?: EmployeeDocumentRow[];
}

export { ID_CARD_TYPE_OPTIONS } from '@/lib/employee-form-config';

export { DEFAULT_COUNTRY } from '@/lib/countries';

export const DEFAULT_EMPLOYEE_FORM: EmployeeFormData = {
  registration_number: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  gender: undefined,
  citizenship: DEFAULT_COUNTRY,
  home_country: DEFAULT_COUNTRY,
  marital_status: undefined,
  payment_method: undefined,
  children: [],
  educations: [],
  experiences: [],
  employee_documents: [],
};
