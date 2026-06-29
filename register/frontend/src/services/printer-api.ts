import type { EmployeeFormData } from '@/types/employee';
import {
  formatEmployeeFullName,
  formatGenderLabel,
  formatPaymentMethod,
} from '@/lib/employee-display';

const BRIDGE_URL = process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL || 'http://127.0.0.1:8765';

export interface PrinterStatus {
  available: boolean;
  mode: string;
  message: string;
  open?: boolean;
}

export interface ReceiptLine {
  text: string;
  align?: 'left' | 'center' | 'right';
  bold?: boolean;
  doubleWidth?: boolean;
  doubleHeight?: boolean;
}

function pickStr(obj: Record<string, unknown>, ...keys: string[]): string | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === 'string' && v) return v;
  }
  return undefined;
}

export async function getPrinterStatus(): Promise<PrinterStatus> {
  try {
    const res = await fetch(`${BRIDGE_URL}/api/v1/devices/printer/status`, {
      signal: AbortSignal.timeout(4000),
    });
    if (!res.ok) {
      return { available: false, mode: 'unknown', message: 'Device Bridge injoignable (8765)' };
    }
    const raw = (await res.json()) as Record<string, unknown>;
    return {
      available: Boolean(raw.available ?? raw.Available),
      mode: String(raw.mode ?? raw.Mode ?? 'pos'),
      message: pickStr(raw, 'message', 'Message') || '',
      open: Boolean(raw.open ?? raw.Open),
    };
  } catch (e) {
    return {
      available: false,
      mode: 'unknown',
      message: e instanceof Error ? e.message : 'Bridge hors ligne',
    };
  }
}

export function buildReceiptLines(
  employeeData: EmployeeFormData,
  enrollmentId: string
): ReceiptLine[] {
  const date = new Date().toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });
  const time = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  const fullName = formatEmployeeFullName(employeeData) || '-';

  return [
    { text: 'OFFICE NATIONAL D\'IDENTIFICATION', align: 'center', bold: true },
    { text: 'POPULATION - ONIP', align: 'center', bold: true },
    { text: 'ENROLEMENT BIOMETRIQUE PERSONNEL', align: 'center' },
    { text: '--------------------------------', align: 'center' },
    { text: 'RECU D\'ENROLEMENT', align: 'center', bold: true },
    { text: '--------------------------------', align: 'center' },
    { text: `N° session : ${enrollmentId}`, align: 'left' },
    { text: `Date : ${date} ${time}`, align: 'left' },
    { text: `Matricule : ${employeeData.registration_number}`, align: 'left', bold: true },
    { text: `Nom : ${fullName}`, align: 'left' },
    { text: `Sexe : ${formatGenderLabel(employeeData.gender)}`, align: 'left' },
    { text: `Naissance : ${employeeData.date_of_birth || '-'}`, align: 'left' },
    { text: `Lieu : ${employeeData.place_of_birth || '-'}`, align: 'left' },
    { text: `Nationalite : ${employeeData.citizenship || '-'}`, align: 'left' },
    { text: `Paie : ${formatPaymentMethod(employeeData.payment_method)}`, align: 'left' },
    { text: '--------------------------------', align: 'center' },
    { text: 'Conservez ce recu.', align: 'center' },
    { text: '\n', align: 'left' },
  ];
}

export async function printEnrollmentReceipt(
  employeeData: EmployeeFormData,
  enrollmentId: string
): Promise<{ success: boolean; message: string }> {
  const lines = buildReceiptLines(employeeData, enrollmentId);
  const res = await fetch(`${BRIDGE_URL}/api/v1/devices/printer/print-receipt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      lines,
      qr_content: enrollmentId,
      cut: true,
    }),
    signal: AbortSignal.timeout(60_000),
  });
  const raw = (await res.json()) as Record<string, unknown>;
  const success = Boolean(raw.success ?? raw.Success);
  const message = pickStr(raw, 'message', 'Message') || (success ? 'Impression OK' : 'Échec impression');
  if (!res.ok || !success) {
    throw new Error(message);
  }
  return { success, message };
}

export async function printTestPage(): Promise<void> {
  const res = await fetch(`${BRIDGE_URL}/api/v1/devices/printer/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: '{}',
    signal: AbortSignal.timeout(30_000),
  });
  const raw = (await res.json()) as Record<string, unknown>;
  if (!res.ok || !raw.success) {
    throw new Error(pickStr(raw, 'message', 'Message') || 'Test impression échoué');
  }
}
