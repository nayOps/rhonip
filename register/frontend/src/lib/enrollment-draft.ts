import type { WorkflowStep } from '@/components/forms/EnrollmentWorkflow.types';
import { visitedStepsUpTo } from '@/lib/enrollment-workflow-mappers';
import {
  getEnrollmentSessionDetail,
  prepareEnrollmentSessionEdit,
  type EnrollmentEditMode,
} from '@/services/enrollment-session-api';
import { DEFAULT_EMPLOYEE_FORM, type EmployeeFormData } from '@/types/employee';
import type { GuichetAgentRecord } from '@/services/rh-api';

export const WORKFLOW_DRAFT_STORAGE_KEY = 'fgp_enrollment_workflow_draft_v1';

export type EnrollmentLaunchMode = 'edit' | 'enroll' | 'biometric';

export interface EnrollmentWorkflowDraft {
  currentStep: WorkflowStep;
  visitedSteps?: WorkflowStep[];
  employeeData: EmployeeFormData | null;
  photo: unknown;
  fingerprints: unknown[];
  iris: unknown[];
  documents: unknown[];
  enrollmentId: string;
  gatewaySessionId: string;
  sessionInitError: string | null;
  verificationError: string | null;
  editMode?: EnrollmentEditMode | null;
}

export function readEnrollmentDraft(): EnrollmentWorkflowDraft | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.sessionStorage.getItem(WORKFLOW_DRAFT_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as EnrollmentWorkflowDraft;
  } catch {
    return null;
  }
}

function fkToString(value: unknown): string {
  if (value == null || value === '') return '';
  return String(value);
}

export function payloadEmployeeToFormData(
  employee: Record<string, unknown> | null | undefined
): EmployeeFormData {
  if (!employee) return { ...DEFAULT_EMPLOYEE_FORM };
  const str = (key: string) => String(employee[key] ?? '').trim();

  return {
    ...DEFAULT_EMPLOYEE_FORM,
    registration_number: str('registration_number'),
    social_security_number: str('social_security_number'),
    first_name: str('first_name'),
    middle_name: str('middle_name'),
    last_name: str('last_name'),
    gender: (employee.gender as EmployeeFormData['gender']) || undefined,
    marital_status: (employee.marital_status as EmployeeFormData['marital_status']) || undefined,
    date_of_birth: str('date_of_birth'),
    place_of_birth: str('place_of_birth'),
    citizenship: str('citizenship'),
    home_country: str('home_country'),
    home_province: fkToString(employee.home_province),
    home_territory: fkToString(employee.home_territory),
    home_sector: fkToString(employee.home_sector),
    home_groupement: fkToString(employee.home_groupement),
    home_village: fkToString(employee.home_village),
    type_of_identity: str('type_of_identity'),
    identity_number: str('identity_number'),
    date_of_issue: str('date_of_issue'),
    date_of_expiry: str('date_of_expiry'),
    place_of_issue: str('place_of_issue'),
    branch: fkToString(employee.branch),
    agreement: fkToString(employee.agreement),
    date_of_join: str('date_of_join'),
    direction: fkToString(employee.direction),
    sub_direction: fkToString(employee.sub_direction),
    service: fkToString(employee.service),
    grade: fkToString(employee.grade),
    designation: fkToString(employee.designation),
    telephone_number: str('telephone_number'),
    mobile_number: str('mobile_number'),
    email_professional: str('email_professional'),
    email: str('email'),
    physical_address: str('physical_address'),
    emergency_contact: str('emergency_contact'),
    emergency_phone: str('emergency_phone'),
    relationship: str('relationship'),
    emergency_information: str('emergency_information'),
    refering_doctor: str('refering_doctor'),
    refering_doctor_phone: str('refering_doctor_phone'),
    refering_doctor_email: str('refering_doctor_email'),
    payment_method: (employee.payment_method as EmployeeFormData['payment_method']) || undefined,
    payer_name: str('payer_name'),
    payment_account: str('payment_account'),
    comment: str('comment'),
    children: Array.isArray(employee.children) ? (employee.children as EmployeeFormData['children']) : [],
    educations: Array.isArray(employee.educations) ? (employee.educations as EmployeeFormData['educations']) : [],
    experiences: Array.isArray(employee.experiences) ? (employee.experiences as EmployeeFormData['experiences']) : [],
    documents: Array.isArray(employee.documents) ? (employee.documents as EmployeeFormData['documents']) : [],
  };
}

export function guichetAgentToFormData(agent: GuichetAgentRecord): EmployeeFormData {
  const fk = (value?: number | null) => (value != null ? String(value) : '');

  return {
    ...DEFAULT_EMPLOYEE_FORM,
    registration_number: agent.registration_number,
    social_security_number: agent.social_security_number || '',
    first_name: agent.first_name || '',
    middle_name: agent.middle_name || '',
    last_name: agent.last_name || '',
    gender: (agent.gender as EmployeeFormData['gender']) || undefined,
    marital_status: (agent.marital_status as EmployeeFormData['marital_status']) || undefined,
    date_of_birth: agent.date_of_birth || '',
    place_of_birth: agent.place_of_birth || '',
    citizenship: agent.citizenship || '',
    home_country: agent.home_country || '',
    home_province: fk(agent.home_province),
    home_territory: fk(agent.home_territory),
    home_sector: fk(agent.home_sector),
    home_groupement: fk(agent.home_groupement),
    home_village: fk(agent.home_village),
    type_of_identity: agent.type_of_identity || '',
    identity_number: agent.identity_number || '',
    date_of_issue: agent.date_of_issue || '',
    date_of_expiry: agent.date_of_expiry || '',
    place_of_issue: agent.place_of_issue || '',
    branch: fk(agent.branch),
    agreement: fk(agent.agreement),
    date_of_join: agent.date_of_join || '',
    direction: fk(agent.direction),
    sub_direction: fk(agent.sub_direction),
    service: fk(agent.service),
    grade: fk(agent.grade),
    designation: fk(agent.designation),
    telephone_number: agent.telephone_number || '',
    mobile_number: agent.mobile_number || '',
    email_professional: agent.email_professional || '',
    email: agent.email || '',
    physical_address: agent.physical_address || '',
    emergency_contact: agent.emergency_contact || '',
    emergency_phone: agent.emergency_phone || '',
    relationship: agent.relationship || '',
    emergency_information: agent.emergency_information || '',
    refering_doctor: agent.refering_doctor || '',
    refering_doctor_phone: agent.refering_doctor_phone || '',
    refering_doctor_email: agent.refering_doctor_email || '',
    payment_method: (agent.payment_method as EmployeeFormData['payment_method']) || undefined,
    payer_name: agent.payer_name || '',
    payment_account: agent.payment_account || '',
    comment: agent.comment || '',
  };
}

export function clearEnrollmentDraft(): void {
  if (typeof window === 'undefined') return;
  window.sessionStorage.removeItem(WORKFLOW_DRAFT_STORAGE_KEY);
}

function writeDraft(draft: EnrollmentWorkflowDraft): void {
  if (typeof window === 'undefined') return;
  window.sessionStorage.setItem(WORKFLOW_DRAFT_STORAGE_KEY, JSON.stringify(draft));
}

export function launchEnrollmentFromAgent(
  agent: GuichetAgentRecord,
  mode: EnrollmentLaunchMode
): void {
  if (typeof window === 'undefined') return;

  const initialStep: WorkflowStep = mode === 'biometric' ? 'photo' : 'employee';
  const draft: EnrollmentWorkflowDraft = {
    currentStep: initialStep,
    visitedSteps: visitedStepsUpTo(initialStep),
    employeeData: guichetAgentToFormData(agent),
    photo: null,
    fingerprints: [],
    iris: [],
    documents: [],
    enrollmentId: '',
    gatewaySessionId: '',
    sessionInitError: null,
    verificationError: null,
    editMode: null,
  };

  writeDraft(draft);
}

export async function launchEnrollmentFromSession(
  sessionId: string,
  mode: EnrollmentEditMode
): Promise<void> {
  await prepareEnrollmentSessionEdit(sessionId, mode);
  const detail = await getEnrollmentSessionDetail(sessionId);
  const payload = (detail.payload || {}) as Record<string, unknown>;
  const employee = payloadEmployeeToFormData(payload.employee as Record<string, unknown> | undefined);

  const initialStep: WorkflowStep = mode === 'biographic' ? 'employee' : 'photo';
  const visitedSteps: WorkflowStep[] =
    mode === 'biographic'
      ? visitedStepsUpTo('receipt')
      : (['employee', 'photo', 'fingerprints', 'iris', 'documents', 'verification'] as WorkflowStep[]);

  const draft: EnrollmentWorkflowDraft = {
    currentStep: initialStep,
    visitedSteps,
    employeeData: employee,
    photo: null,
    fingerprints: [],
    iris: [],
    documents: [],
    enrollmentId: '',
    gatewaySessionId: sessionId,
    sessionInitError: null,
    verificationError: null,
    editMode: mode,
  };

  writeDraft(draft);
}

export function launchBlankEnrollment(): void {
  if (typeof window === 'undefined') return;
  const draft: EnrollmentWorkflowDraft = {
    currentStep: 'employee',
    visitedSteps: ['employee'],
    employeeData: { ...DEFAULT_EMPLOYEE_FORM },
    photo: null,
    fingerprints: [],
    iris: [],
    documents: [],
    enrollmentId: '',
    gatewaySessionId: '',
    sessionInitError: null,
    verificationError: null,
    editMode: null,
  };
  writeDraft(draft);
}

export function agentDisplayName(agent: GuichetAgentRecord): string {
  if (agent.nom_postnom) return agent.nom_postnom;
  return [agent.last_name, agent.middle_name, agent.first_name].filter(Boolean).join(' ');
}
