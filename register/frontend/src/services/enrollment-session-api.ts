import {
  FingerprintCapture,
  FingerPosition,
  IrisCapture,
  ScannedDocument,
} from '@/types';
import { PhotoData } from '@/components/biometrics/PhotoCapture';
import type { EmployeeFormData } from '@/types/employee';
import { formatIrisSaveMessage, resolveIrisModalityStatus } from '@/lib/iris-enrollment-utils';
import { enrollmentApiUrl, getEnrollmentGatewayPublicBase } from '@/lib/enrollment-api-base';

const API_URL = getEnrollmentGatewayPublicBase();

export interface CreateGuichetSessionInput {
  employeeData: EmployeeFormData;
  photo?: PhotoData | null;
}

function trimString(value: unknown): string {
  if (value == null) return '';
  return String(value).trim();
}

function fkValue(raw: unknown): number | null {
  const text = trimString(raw);
  if (!text) return null;
  const n = Number(text);
  return Number.isFinite(n) ? n : null;
}

function textOrNull(v: unknown): string | null {
  const t = trimString(v);
  return t || null;
}

function rowOrNull<T extends Record<string, unknown>>(rows: T[] | undefined, predicate: (r: T) => boolean): T[] | undefined {
  if (!rows?.length) return undefined;
  const filtered = rows.filter(predicate);
  return filtered.length ? filtered : undefined;
}

export function buildEmployeePayload(data: EmployeeFormData): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    registration_number: textOrNull(data.registration_number),
    social_security_number: textOrNull(data.social_security_number),
    branch: fkValue(data.branch),
    agreement: fkValue(data.agreement),
    date_of_join: data.date_of_join || null,
    direction: fkValue(data.direction),
    sub_direction: fkValue(data.sub_direction),
    service: fkValue(data.service),
    grade: fkValue(data.grade),
    designation: fkValue(data.designation),
    first_name: textOrNull(data.first_name),
    middle_name: textOrNull(data.middle_name),
    last_name: textOrNull(data.last_name),
    gender: data.gender || null,
    date_of_birth: data.date_of_birth || null,
    place_of_birth: textOrNull(data.place_of_birth),
    citizenship: textOrNull(data.citizenship),
    home_country: textOrNull(data.home_country),
    home_province: fkValue(data.home_province),
    home_territory: fkValue(data.home_territory),
    home_sector: fkValue(data.home_sector),
    home_groupement: fkValue(data.home_groupement),
    home_village: fkValue(data.home_village),
    type_of_identity: data.type_of_identity || null,
    identity_number: textOrNull(data.identity_number),
    date_of_issue: data.date_of_issue || null,
    date_of_expiry: data.date_of_expiry || null,
    place_of_issue: textOrNull(data.place_of_issue),
    appointment_number: textOrNull(data.appointment_number),
    marital_status: data.marital_status || null,
    spouse: textOrNull(data.spouse),
    telephone_number: textOrNull(data.telephone_number),
    mobile_number: textOrNull(data.mobile_number),
    email_professional: textOrNull(data.email_professional),
    email: textOrNull(data.email),
    physical_address: textOrNull(data.physical_address),
    emergency_contact: textOrNull(data.emergency_contact),
    emergency_phone: textOrNull(data.emergency_phone),
    relationship: textOrNull(data.relationship),
    emergency_information: textOrNull(data.emergency_information),
    refering_doctor: textOrNull(data.refering_doctor),
    refering_doctor_phone: textOrNull(data.refering_doctor_phone),
    refering_doctor_email: textOrNull(data.refering_doctor_email),
    payment_method: data.payment_method || null,
    payer_name: textOrNull(data.payer_name),
    payment_account: textOrNull(data.payment_account),
    comment: textOrNull(data.comment),
  };

  if (data.photo_base64) {
    payload.photo_base64 = data.photo_base64;
  }

  if (data.appointment_letter_base64) {
    payload.appointment_letter_base64 = data.appointment_letter_base64;
    payload.appointment_letter_name =
      data.appointment_letter_name || `${textOrNull(data.registration_number) || 'employe'}_nomination.pdf`;
  }

  const children = rowOrNull(data.children || [], (r) => Boolean(trimString(r.full_name)));
  if (children) payload.children = children;

  const educations = rowOrNull(
    data.educations || [],
    (r) => Boolean(trimString(r.institution) || trimString(r.degree))
  );
  if (educations) payload.educations = educations;

  const experiences = rowOrNull(
    data.experiences || [],
    (r) => Boolean(trimString(r.organization) || trimString(r.position))
  );
  if (experiences) {
    payload.experiences = experiences.map((r) => ({
      organization: r.organization,
      position: r.position,
      start_date: r.start_date || null,
      end_date: r.end_date || null,
      photo_base64: r.photo_base64,
      photo_name: r.photo_name,
    }));
  }

  const docs = rowOrNull(
    data.employee_documents || [],
    (r) => Boolean(trimString(r.name) && r.file_base64)
  );
  if (docs) {
    payload.employee_documents = docs.map((d) => ({
      name: trimString(d.name),
      file_name: d.file_name,
      file_base64: d.file_base64,
    }));
  }

  return payload;
}

function gatewayHeaders(): HeadersInit {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export function formatGatewayValidationError(
  err: { error?: string; details?: unknown },
  status: number
): string {
  const details = err.details;
  const detailStr =
    details != null
      ? typeof details === 'string'
        ? details
        : JSON.stringify(details)
      : '';
  return (
    err.error ||
    `Création session échouée (${status})${detailStr ? ` — ${detailStr}` : ''}`
  );
}

export function generateSessionId(registrationNumber?: string | null): string {
  const suffix = Math.random().toString(36).slice(2, 8).toUpperCase();
  const matricule = trimString(registrationNumber);
  if (matricule) {
    return `ONIP-${matricule}-${suffix}`;
  }
  return `ONIP-${Date.now()}-${suffix}`;
}

export function formatSessionReference(
  sessionId: string,
  registrationNumber?: string | null
): string {
  const matricule = trimString(registrationNumber);
  if (matricule) {
    return matricule;
  }
  return sessionId.replace(/^FGP-/i, 'ONIP-');
}

export async function createGuichetEnrollmentSession(
  input: CreateGuichetSessionInput
): Promise<string> {
  const sessionId = generateSessionId(input.employeeData.registration_number);
  const faceQuality = input.photo?.quality != null ? input.photo.quality / 100 : 0;
  const photoRaw = input.photo?.image;
  const photoBase64 =
    photoRaw?.includes('base64,') ? photoRaw.split('base64,')[1] : photoRaw;

  const body = {
    session_id: sessionId,
    channel: 'fixed',
    device_id: process.env.NEXT_PUBLIC_DEVICE_ID || 'GUICHET-FAP60',
    operator_id: process.env.NEXT_PUBLIC_OPERATOR_ID || 'OPERATOR-001',
    location: {
      province: input.employeeData.home_province || 'Kinshasa',
      territoire: input.employeeData.home_territory,
    },
    schema_version: '2.0',
    employee: buildEmployeePayload(input.employeeData),
    biometrics: {
      face: {
        ref: photoBase64 ? `inline://photo/${sessionId}` : 'pending://photo',
        quality: faceQuality,
        ...(photoBase64 ? { image_base64: photoBase64 } : {}),
      },
      fingerprints: {
        ref: 'pending://fingerprints',
        quality: 0,
      },
    },
    auto_process: false,
  };

  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/v1/enrolments/sessions/`, {
      method: 'POST',
      headers: gatewayHeaders(),
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error(
      `enrollment_gateway injoignable — vérifiez docker compose up -d enrollment_gateway (${getEnrollmentGatewayPublicBase()})`
    );
  }

  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as {
      error?: string;
      details?: unknown;
    };
    throw new Error(formatGatewayValidationError(err, res.status));
  }

  const data = (await res.json()) as { session_id?: string };
  return data.session_id || sessionId;
}

export interface FingerprintFingerPayload {
  position: FingerPosition;
  status: string;
  quality?: number;
  nfiq?: number;
  template_base64?: string;
  format_id?: number;
  image_base64?: string;
  reason?: string;
  timestamp?: string;
}

export function buildFingerprintSavePayload(
  fingerprints: FingerprintCapture[],
  options?: { fake?: boolean }
) {
  const captured = fingerprints.filter((f) => f.status === 'CAPTURED');
  const qualities = captured
    .map((f) => f.quality)
    .filter((q): q is number => q != null)
    .map((q) => (q > 1 ? q / 100 : q));

  const aggregateQuality =
    qualities.length > 0
      ? Math.round((qualities.reduce((a, b) => a + b, 0) / qualities.length) * 10000) / 10000
      : 0;

  const fingers: FingerprintFingerPayload[] = fingerprints.map((fp) => {
    const imageBase64 = fp.image?.includes('base64,')
      ? fp.image.split('base64,')[1]
      : fp.image;
    return {
      position: fp.position,
      status: fp.status,
      quality: fp.quality,
      nfiq: fp.nfiq,
      template_base64: fp.templateBase64,
      format_id: fp.formatId,
      image_base64: imageBase64,
      reason: fp.reason,
      timestamp: fp.timestamp,
    };
  });

  const isFake =
    options?.fake === true ||
    fingerprints.some((f) => f.reason === 'FAKE_DEV');

  return {
    quality: aggregateQuality,
    device: isFake ? 'fake-dev' : 'fap60',
    source: isFake ? 'fake-dev' : 'live',
    summary: {
      captured: captured.length,
      damaged: fingerprints.filter((f) => f.status === 'DAMAGED').length,
      missing: fingerprints.filter((f) => f.status === 'AMPUTATED' || f.status === 'MISSING').length,
      pending: fingerprints.filter((f) => f.status === 'PENDING').length,
      dev_fake: isFake,
    },
    fingers,
  };
}

export async function saveFingerprintBiometrics(
  sessionId: string,
  fingerprints: FingerprintCapture[],
  status: 'completed' | 'skipped' | 'failed' = 'completed'
): Promise<void> {
  const res = await fetch(
    enrollmentApiUrl(`/api/v1/enrolments/sessions/modality/fingerprint/${sessionId}/`),
    {
      method: 'PATCH',
      headers: gatewayHeaders(),
      body: JSON.stringify({
        status,
        message: `Enrôlement 4-4-2 — ${fingerprints.filter((f) => f.status === 'CAPTURED').length} gabarit(s)`,
        fingerprints: buildFingerprintSavePayload(fingerprints, {
          fake: fingerprints.some((f) => f.reason === 'FAKE_DEV'),
        }),
      }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Sauvegarde empreintes échouée (${res.status})`);
  }
}

export function buildIrisSavePayload(iris: IrisCapture[]) {
  const captured = iris.filter((e) => e.status === 'CAPTURED');
  const qualities = captured
    .map((e) => e.quality)
    .filter((q): q is number => q != null);
  const aggregateQuality =
    qualities.length > 0
      ? Math.round((qualities.reduce((a, b) => a + b, 0) / qualities.length) * 100) / 100
      : 0;

  const eyes = iris.map((eye) => {
    const imageBase64 = eye.image?.includes('base64,')
      ? eye.image.split('base64,')[1]
      : eye.image;
    return {
      position: eye.position,
      status: eye.status,
      quality: eye.quality,
      image_base64: imageBase64,
      reason: eye.reason,
      timestamp: eye.timestamp,
    };
  });

  return {
    quality: aggregateQuality,
    device: 'iris-device-server',
    summary: {
      captured: captured.length,
      blind: iris.filter((e) => e.status === 'BLIND').length,
      missing: iris.filter((e) => e.status === 'MISSING').length,
      damaged: iris.filter((e) => e.status === 'DAMAGED').length,
      failed: iris.filter((e) => e.status === 'FAILED').length,
      pending: iris.filter((e) => e.status === 'PENDING').length,
    },
    eyes,
  };
}

export interface IcaoCaptureMeta {
  rawSha256?: string;
  icaoSha256?: string;
  rawImageSaved?: boolean;
  icaoImageSaved?: boolean;
  deviceId?: string;
  camera?: string;
  enrollmentId?: string;
  operatorId?: string;
  captureTimestamp?: string;
}

function stripDataUrl(dataUrl: string): string {
  return dataUrl?.includes('base64,') ? dataUrl.split('base64,')[1] : dataUrl;
}

export function buildFaceSavePayload(photo: PhotoData) {
  const icaoB64 = photo.icaoImage
    ? stripDataUrl(photo.icaoImage)
    : stripDataUrl(photo.image);
  const rawB64 = photo.rawImage ? stripDataUrl(photo.rawImage) : undefined;
  return {
    quality: photo.quality,
    device: photo.captureMeta?.deviceId || 'KIT-ONIP-WEBCAM',
    icao_compliant: photo.icaoCompliant,
    source: photo.rawImage || photo.icaoImage ? 'webcam-icao' : 'gpy',
    checks: photo.checks,
    image_base64: icaoB64,
    raw_image_base64: rawB64,
    icao_image_base64: photo.icaoImage ? icaoB64 : undefined,
    raw_sha256: photo.captureMeta?.rawSha256,
    icao_sha256: photo.captureMeta?.icaoSha256,
    capture_metadata: photo.captureMeta,
    crop: photo.cropInfo,
    camera: photo.captureMeta?.camera,
    capture_timestamp: photo.captureMeta?.captureTimestamp ?? photo.timestamp,
  };
}

export async function saveFaceBiometrics(
  sessionId: string,
  photo: PhotoData,
  status: 'completed' | 'skipped' | 'failed' = 'completed'
): Promise<void> {
  const res = await fetch(
    enrollmentApiUrl(`/api/v1/enrolments/sessions/modality/face/${sessionId}/`),
    {
      method: 'PATCH',
      headers: gatewayHeaders(),
      body: JSON.stringify({
        status,
        message: `Photo — qualité ${photo.quality}%`,
        face: buildFaceSavePayload(photo),
      }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(
      formatGatewayValidationError(err as { error?: string; details?: unknown }, res.status) ||
        `Sauvegarde photo échouée (${res.status})`
    );
  }
}

export async function saveIrisBiometrics(
  sessionId: string,
  iris: IrisCapture[],
  status?: 'completed' | 'skipped' | 'failed',
  message?: string
): Promise<void> {
  const modalityStatus = status ?? resolveIrisModalityStatus(iris);
  const res = await fetch(
    enrollmentApiUrl(`/api/v1/enrolments/sessions/modality/iris/${sessionId}/`),
    {
      method: 'PATCH',
      headers: gatewayHeaders(),
      body: JSON.stringify({
        status: modalityStatus,
        message: message ?? formatIrisSaveMessage(iris),
        iris: buildIrisSavePayload(iris),
      }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(
      formatGatewayValidationError(err as { error?: string; details?: unknown }, res.status) ||
        `Sauvegarde iris échouée (${res.status})`
    );
  }
}

const DOCUMENT_TYPE_API: Record<string, string> = {
  FICHE_IDENTIFICATION: 'FICHE_IDENTIFICATION',
  ACTE_NAISSANCE: 'ACTE_NAISSANCE',
  JUGEMENT_SUPPLETIF: 'JUGEMENT_SUPPLETIF',
  CARTE_ELECTEUR: 'CARTE_ELECTEUR',
  CERTIFICAT_NATIONALITE: 'CERTIFICAT_NATIONALITE',
  PASSEPORT: 'PASSEPORT',
  CARTE_ETUDIANT: 'CARTE_ETUDIANT',
  PERMIS_CONDUIRE: 'PERMIS_CONDUIRE',
  AUTRE: 'AUTRE',
};

export function buildDocumentSavePayload(documents: ScannedDocument[]) {
  const pageCount = documents.reduce((n, d) => n + d.pages.length, 0);
  return {
    summary: {
      document_count: documents.length,
      page_count: pageCount,
    },
    documents: documents.map((doc) => ({
      id: doc.id,
      type: DOCUMENT_TYPE_API[doc.type] || doc.type,
      structure: doc.structure,
      notes: doc.notes,
      created_at: doc.createdAt,
      pages: doc.pages.map((p) => ({
        id: p.id,
        side: p.side,
        page_number: p.pageNumber,
        mime_type: p.mimeType,
        filename: p.filename,
        size: p.size,
        scanned_at: p.scannedAt,
        image_base64: stripDataUrl(p.image),
      })),
    })),
  };
}

export async function saveDocumentBiometrics(
  sessionId: string,
  documents: ScannedDocument[],
  status: 'completed' | 'skipped' | 'failed' = 'completed'
): Promise<void> {
  const res = await fetch(
    enrollmentApiUrl(`/api/v1/enrolments/sessions/modality/document/${sessionId}/`),
    {
      method: 'PATCH',
      headers: gatewayHeaders(),
      body: JSON.stringify({
        status,
        message: `${documents.length} document(s), ${documents.reduce((n, d) => n + d.pages.length, 0)} page(s)`,
        documents: buildDocumentSavePayload(documents),
      }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(
      formatGatewayValidationError(err as { error?: string; details?: unknown }, res.status) ||
        `Sauvegarde documents échouée (${res.status})`
    );
  }
}

export type EnrollmentEditMode = 'biographic' | 'biometric' | 'full';

export async function prepareEnrollmentSessionEdit(
  sessionId: string,
  mode: EnrollmentEditMode
): Promise<EnrollmentSessionSummary> {
  const res = await fetch(enrollmentApiUrl(`/api/v1/enrolments/sessions/prepare-edit/${sessionId}/`), {
    method: 'POST',
    headers: gatewayHeaders(),
    body: JSON.stringify({ mode }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Préparation modification échouée (${res.status})`);
  }
  return (await res.json()) as EnrollmentSessionSummary;
}

export async function updateEnrollmentSessionEmployee(
  sessionId: string,
  employeeData: EmployeeFormData
): Promise<void> {
  const res = await fetch(enrollmentApiUrl(`/api/v1/enrolments/sessions/employee/${sessionId}/`), {
    method: 'PATCH',
    headers: gatewayHeaders(),
    body: JSON.stringify({ employee: buildEmployeePayload(employeeData) }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(
      formatGatewayValidationError(err as { error?: string; details?: unknown }, res.status) ||
        `Mise à jour fiche agent échouée (${res.status})`
    );
  }
}

export async function findLatestSessionForMatricule(
  registrationNumber: string
): Promise<EnrollmentSessionSummary | null> {
  const matricule = trimString(registrationNumber);
  if (!matricule) return null;
  const page = await listEnrollmentSessions(1, 100);
  const matches = page.results
    .filter((row) => row.registration_number === matricule && row.status !== 'CANCELLED')
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  return matches[0] ?? null;
}

export async function submitEnrollmentSession(sessionId: string): Promise<void> {
  const res = await fetch(enrollmentApiUrl(`/api/v1/enrolments/sessions/submit/${sessionId}/`), {
    method: 'POST',
    headers: gatewayHeaders(),
    body: JSON.stringify({}),
  });
  if (!res.ok && res.status !== 202) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Soumission session échouée (${res.status})`);
  }
}

export async function getEnrollmentSessionStatus(sessionId: string): Promise<EnrollmentSessionSummary> {
  const res = await fetch(enrollmentApiUrl(`/api/v1/enrolments/sessions/status/${sessionId}/`), {
    method: 'GET',
    headers: gatewayHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Statut session échoué (${res.status})`);
  }
  return (await res.json()) as EnrollmentSessionSummary;
}

export interface EnrollmentSessionSummary {
  id: string;
  session_id: string;
  status: string;
  progress_percentage: number;
  registration_number?: string | null;
  agent_name?: string | null;
  employee_status?: string | null;
  abis_result?: Record<string, unknown>;
  modality_status?: Record<string, unknown>;
  error_message?: string | null;
  validation_errors?: unknown[];
  created_at: string;
  updated_at: string;
}

export interface EnrollmentSessionDetail extends EnrollmentSessionSummary {
  channel: string;
  device_id: string;
  operator_id: string;
  location: Record<string, unknown>;
  payload?: Record<string, unknown>;
  events?: Array<{
    id: string;
    event_type: string;
    event_data: Record<string, unknown>;
    message: string;
    created_at: string;
    created_by?: string;
  }>;
}

export interface EnrollmentDbSnapshot {
  session_id: string;
  registration_number: string | null;
  agent_name?: string | null;
  employee?: Record<string, unknown> | null;
  db: {
    employee?: Record<string, unknown> | null;
    person_core?: Record<string, unknown> | null;
    biometric?: Record<string, unknown> | null;
    fingerprints?: Array<Record<string, unknown>>;
    documents?: Array<Record<string, unknown>>;
    extensions?: Record<string, Array<Record<string, unknown>>>;
  };
  repair?: {
    requested: boolean;
    performed: boolean;
    error?: string | null;
  };
}

interface EnrollmentListResponse {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: EnrollmentSessionSummary[];
}

export interface EnrollmentSessionListPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: EnrollmentSessionSummary[];
}

export interface EnrollmentDbOverview {
  sessions_total: number;
  sessions_with_matricule: number;
  biometric_total: number;
  fingerprints_total: number;
  documents_total: number;
}

export function formatModalitySummary(
  modalityStatus?: Record<string, unknown> | null
): string {
  if (!modalityStatus) return '—';
  const labels: Record<string, string> = {
    face: 'Photo',
    fingerprint: 'Empreintes',
    iris: 'Iris',
    document: 'Docs',
    signature: 'Signature',
  };
  return Object.entries(modalityStatus)
    .map(([key, value]) => {
      const status =
        typeof value === 'object' && value !== null && 'status' in value
          ? String((value as { status?: string }).status || 'pending')
          : String(value || 'pending');
      return `${labels[key] || key}: ${status}`;
    })
    .join(' · ');
}

function extractModalityStates(modalityStatus?: Record<string, unknown> | null): string[] {
  if (!modalityStatus) return [];
  return Object.values(modalityStatus).map((value) => {
    if (typeof value === 'object' && value !== null && 'status' in value) {
      return String((value as { status?: string }).status || 'pending').toLowerCase();
    }
    return String(value || 'pending').toLowerCase();
  });
}

const IDENTIFICATION_STATUS_LABELS: Record<string, string> = {
  COMPLETED: 'Terminé',
  FAILED: 'Échoué',
  CANCELLED: 'Annulé',
  VALIDATING: 'En validation',
  PROCESSING: 'En traitement',
  ABIS_CHECK: 'Vérification ABIS',
  REVIEW: 'En révision',
  PENDING: 'En attente',
  IN_PROGRESS: 'En cours',
  READY_TO_SUBMIT: 'À soumettre',
};

const MODALITY_LABELS: Record<string, string> = {
  face: 'Photo',
  fingerprint: 'Empreintes',
  iris: 'Iris',
  document: 'Docs',
  signature: 'Signature',
};

function modalityState(modalityStatus: Record<string, unknown> | null | undefined, key: string): string {
  if (!modalityStatus) return 'pending';
  const value = modalityStatus[key];
  if (typeof value === 'object' && value !== null && 'status' in value) {
    return String((value as { status?: string }).status || 'pending').toLowerCase();
  }
  return String(value || 'pending').toLowerCase();
}

export function resolveIdentificationDisplayStatus(
  sessionStatus: string,
  modalityStatus?: Record<string, unknown> | null
): { code: string; label: string } {
  if (sessionStatus !== 'PENDING') {
    return {
      code: sessionStatus,
      label: IDENTIFICATION_STATUS_LABELS[sessionStatus] || sessionStatus,
    };
  }

  const states = extractModalityStates(modalityStatus);
  if (!states.length) {
    return { code: 'PENDING', label: IDENTIFICATION_STATUS_LABELS.PENDING };
  }

  const isDone = (state: string) => state === 'completed' || state === 'skipped';
  if (states.every(isDone)) {
    return { code: 'READY_TO_SUBMIT', label: IDENTIFICATION_STATUS_LABELS.READY_TO_SUBMIT };
  }
  if (states.some((state) => isDone(state) || state === 'failed')) {
    return { code: 'IN_PROGRESS', label: IDENTIFICATION_STATUS_LABELS.IN_PROGRESS };
  }

  return { code: 'PENDING', label: IDENTIFICATION_STATUS_LABELS.PENDING };
}

export function getIdentificationBlockingSummary(
  sessionStatus: string,
  modalityStatus?: Record<string, unknown> | null,
  errorMessage?: string | null
): string | null {
  if (sessionStatus === 'COMPLETED') return null;
  if (sessionStatus === 'FAILED') {
    return errorMessage || 'Échec lors de la finalisation — vérifiez la fiche agent RH.';
  }
  if (sessionStatus === 'CANCELLED') return 'Identification annulée.';

  const pendingModalities = Object.entries(MODALITY_LABELS)
    .filter(([key]) => {
      const state = modalityState(modalityStatus, key);
      return state !== 'completed' && state !== 'skipped';
    })
    .map(([, label]) => label);

  if (pendingModalities.length > 0) {
    return `Modalités restantes : ${pendingModalities.join(', ')}. Finalisez le parcours guichet puis soumettez.`;
  }

  if (sessionStatus === 'PENDING') {
    return 'Parcours guichet terminé — soumission requise pour passer en Terminé.';
  }

  return 'Traitement en cours côté serveur…';
}

export function identificationStatusClass(code: string): string {
  const classes: Record<string, string> = {
    COMPLETED: 'bg-green-100 text-green-700',
    FAILED: 'bg-red-100 text-red-700',
    VALIDATING: 'bg-yellow-100 text-yellow-700',
    PROCESSING: 'bg-blue-100 text-blue-700',
    ABIS_CHECK: 'bg-blue-100 text-blue-700',
    REVIEW: 'bg-yellow-100 text-yellow-700',
    PENDING: 'bg-gray-100 text-gray-700',
    IN_PROGRESS: 'bg-indigo-100 text-indigo-700',
    READY_TO_SUBMIT: 'bg-amber-100 text-amber-800',
    CANCELLED: 'bg-gray-100 text-gray-600',
  };
  return classes[code] || 'bg-gray-100 text-gray-700';
}

export async function listEnrollmentSessions(page = 1, pageSize = 20): Promise<EnrollmentSessionListPage> {
  const res = await fetch(enrollmentApiUrl(`/api/v1/enrolments/sessions/?page=${page}&page_size=${pageSize}`), {
    method: 'GET',
    headers: gatewayHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Liste sessions échouée (${res.status})`);
  }
  const data = (await res.json()) as EnrollmentListResponse | EnrollmentSessionSummary[];
  if (Array.isArray(data)) {
    return { count: data.length, next: null, previous: null, results: data };
  }
  return {
    count: data.count || 0,
    next: data.next || null,
    previous: data.previous || null,
    results: data.results || [],
  };
}

export async function getEnrollmentSessionDetail(sessionId: string): Promise<EnrollmentSessionDetail> {
  const res = await fetch(enrollmentApiUrl(`/api/v1/enrolments/sessions/detail/${sessionId}/`), {
    method: 'GET',
    headers: gatewayHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Détail session échoué (${res.status})`);
  }
  return (await res.json()) as EnrollmentSessionDetail;
}

export async function getEnrollmentDbSnapshot(sessionId: string): Promise<EnrollmentDbSnapshot> {
  const res = await fetch(enrollmentApiUrl(`/api/v1/enrolments/sessions/db-snapshot/${sessionId}/?repair=true`), {
    method: 'GET',
    headers: gatewayHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Snapshot BD échoué (${res.status})`);
  }
  return (await res.json()) as EnrollmentDbSnapshot;
}

export interface CompletedEnrollmentReportRow {
  session_id: string;
  nom: string;
  postnom: string;
  prenom?: string;
  agent_name?: string;
  statut: string;
  registration_number: string | null;
  created_at: string | null;
  photo_uri: string | null;
}

export interface CompletedEnrollmentReport {
  count: number;
  generated_at: string;
  rows: CompletedEnrollmentReportRow[];
}

export function mediaProxyUrl(uri: string): string {
  return enrollmentApiUrl(`/api/v1/enrolments/sessions/media-proxy/?uri=${encodeURIComponent(uri)}`);
}

export async function getCompletedEnrollmentReport(): Promise<CompletedEnrollmentReport> {
  const res = await fetch(enrollmentApiUrl('/api/v1/enrolments/sessions/completed-report/'), {
    method: 'GET',
    headers: gatewayHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Rapport enrôlements échoué (${res.status})`);
  }
  return (await res.json()) as CompletedEnrollmentReport;
}

export async function getEnrollmentDbOverview(): Promise<EnrollmentDbOverview> {
  const res = await fetch(enrollmentApiUrl('/api/v1/enrolments/sessions/db-overview/'), {
    method: 'GET',
    headers: gatewayHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Vue BD échouée (${res.status})`);
  }
  return (await res.json()) as EnrollmentDbOverview;
}
