import type { EmployeeFormData } from '@/types/employee';
import { ID_CARD_TYPE_OPTIONS } from '@/lib/employee-form-config';

export function formatEmployeeFullName(data: EmployeeFormData): string {
  return [data.first_name, data.last_name, data.middle_name]
    .map((p) => (p == null ? '' : String(p).trim()))
    .filter(Boolean)
    .join(' ');
}

export function formatEmployeeShortName(data: EmployeeFormData): string {
  return [data.last_name, data.first_name].filter(Boolean).join(' ');
}

export function formatGenderLabel(gender?: string): string {
  if (gender === 'male') return 'Masculin';
  if (gender === 'female') return 'Féminin';
  return gender || '-';
}

export function formatMaritalStatus(status?: string): string {
  if (status === 'single') return 'Célibataire';
  if (status === 'maried') return 'Marié(e)';
  return status || '-';
}

export function formatPaymentMethod(method?: string): string {
  if (method === 'bank') return 'Banque';
  if (method === 'cash') return 'Cash';
  if (method === 'mobile money') return 'Mobile money';
  return method || '-';
}

export function formatIdCardType(type?: string): string {
  if (!type) return '-';
  const found = ID_CARD_TYPE_OPTIONS.find((o) => o.value === type);
  return found?.label || type;
}

export function refLabel(
  refs: { id: number; name: string }[] | undefined,
  id?: string
): string {
  if (!id) return '-';
  const num = Number(id);
  const item = refs?.find((r) => r.id === num);
  return item?.name || id;
}
