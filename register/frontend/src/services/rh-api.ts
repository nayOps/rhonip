const RH_PUBLIC_URL = process.env.NEXT_PUBLIC_RH_API_URL || 'http://localhost:8100';
const RH_SERVER_URL = process.env.RH_INTERNAL_API_URL || RH_PUBLIC_URL;
const GUICHET_KEY =
  process.env.NEXT_PUBLIC_GUICHET_INTERNAL_API_KEY || 'fgp_guichet_internal_dev';

/** Base URL RH : proxy same-origin côté navigateur, URL directe côté serveur. */
function rhApiBase(): string {
  if (typeof window !== 'undefined') {
    return '/api/rh';
  }
  return RH_SERVER_URL;
}

function fetchWithTimeout(url: string, init: RequestInit = {}, ms = 15000): Promise<Response> {
  if (typeof AbortController === 'undefined') {
    return fetch(url, init);
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  return fetch(url, { ...init, signal: controller.signal }).finally(() => clearTimeout(timer));
}

async function parseRhError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { error?: string; detail?: string; hint?: string };
    if (body.detail) return body.detail;
    if (body.error) return body.error;
  } catch {
    // ignore
  }
  return `HTTP ${res.status}`;
}

export interface RhRefItem {
  id: number;
  name: string;
  direction_id?: number | null;
  sub_direction_id?: number | null;
}

export interface GuichetRefs {
  directions: RhRefItem[];
  sub_directions: RhRefItem[];
  services: RhRefItem[];
  grades: RhRefItem[];
  agreements: RhRefItem[];
  designations: RhRefItem[];
  branches: RhRefItem[];
  provinces: RhRefItem[];
  countries?: RhRefItem[];
}

const EMPTY_REFS: GuichetRefs = {
  directions: [],
  sub_directions: [],
  services: [],
  grades: [],
  agreements: [],
  designations: [],
  branches: [],
  provinces: [],
  countries: [],
};

function guichetHeaders(): HeadersInit {
  return { 'X-Guichet-Internal-Key': GUICHET_KEY };
}

async function rhFetch(path: string, init: RequestInit = {}, timeoutMs = 15000): Promise<Response> {
  const primary = `${rhApiBase()}${path.startsWith('/') ? path : `/${path}`}`;
  try {
    const res = await fetchWithTimeout(primary, init, timeoutMs);
    if (res.ok || res.status === 404) return res;
    if (res.status === 502 && typeof window !== 'undefined') {
      const direct = `${RH_PUBLIC_URL}${path.startsWith('/') ? path : `/${path}`}`;
      const fallback = await fetchWithTimeout(direct, init, timeoutMs);
      if (fallback.ok || fallback.status === 404) return fallback;
    }
    return res;
  } catch (primaryErr) {
    if (typeof window === 'undefined') throw primaryErr;
    const direct = `${RH_PUBLIC_URL}${path.startsWith('/') ? path : `/${path}`}`;
    return fetchWithTimeout(direct, init, timeoutMs);
  }
}

export async function fetchGuichetRefs(): Promise<GuichetRefs> {
  try {
    const res = await rhFetch('/api/guichet/refs', { headers: guichetHeaders() }, 8000);
    if (!res.ok) return EMPTY_REFS;
    const data = (await res.json()) as GuichetRefs;
    return { ...EMPTY_REFS, ...data, provinces: data.provinces || [], countries: data.countries || [] };
  } catch {
    return EMPTY_REFS;
  }
}

export type GeographyLevel = 'province' | 'territory' | 'sector' | 'groupement' | 'village';

export interface GeographyOption {
  id: number;
  name: string;
}

export interface GeographyVillageOption extends GeographyOption {
  label?: string;
  province_id: number;
  territory_id: number;
  sector_id: number;
  groupement_id: number;
}

export async function fetchGeographyOptions(
  level: GeographyLevel,
  params: {
    q?: string;
    province_id?: string;
    territory_id?: string;
    sector_id?: string;
    groupement_id?: string;
  } = {}
): Promise<GeographyOption[] | GeographyVillageOption[]> {
  const qs = new URLSearchParams({ level });
  if (params.q?.trim()) qs.set('q', params.q.trim());
  if (params.province_id) qs.set('province_id', params.province_id);
  if (params.territory_id) qs.set('territory_id', params.territory_id);
  if (params.sector_id) qs.set('sector_id', params.sector_id);
  if (params.groupement_id) qs.set('groupement_id', params.groupement_id);

  try {
    const res = await rhFetch(`/api/guichet/geography/?${qs.toString()}`, {
      headers: guichetHeaders(),
    }, 10000);
    if (!res.ok) return [];
    const body = (await res.json()) as { results?: GeographyVillageOption[] };
    return body.results || [];
  } catch {
    return [];
  }
}

export interface GuichetAgentRecord {
  employee_id?: number;
  registration_number: string;
  social_security_number?: string | null;
  first_name?: string | null;
  middle_name?: string | null;
  last_name?: string | null;
  gender?: string;
  marital_status?: string;
  date_of_birth?: string | null;
  place_of_birth?: string | null;
  citizenship?: string | null;
  home_country?: string | null;
  home_province?: number | null;
  home_province_name?: string | null;
  home_territory?: number | null;
  home_territory_name?: string | null;
  home_sector?: number | null;
  home_sector_name?: string | null;
  home_groupement?: number | null;
  home_groupement_name?: string | null;
  home_village?: number | null;
  home_village_name?: string | null;
  type_of_identity?: string | null;
  identity_number?: string | null;
  date_of_issue?: string | null;
  date_of_expiry?: string | null;
  place_of_issue?: string | null;
  branch?: number | null;
  agreement?: number | null;
  date_of_join?: string | null;
  direction?: number | null;
  sub_direction?: number | null;
  service?: number | null;
  grade?: number | null;
  designation?: number | null;
  designation_name?: string | null;
  telephone_number?: string | null;
  mobile_number?: string | null;
  email_professional?: string | null;
  email?: string | null;
  physical_address?: string | null;
  emergency_contact?: string | null;
  emergency_phone?: string | null;
  relationship?: string | null;
  emergency_information?: string | null;
  refering_doctor?: string | null;
  refering_doctor_phone?: string | null;
  refering_doctor_email?: string | null;
  payment_method?: string;
  payer_name?: string | null;
  payment_account?: string | null;
  comment?: string | null;
  nom_postnom?: string | null;
  payroll?: Record<string, unknown>;
  payroll_summary?: Record<string, unknown>;
}

export type GuichetEmployeeLookup = GuichetAgentRecord;

export interface GuichetAgentsListResponse {
  status: string;
  count: number;
  page: number;
  page_size: number;
  results: GuichetAgentRecord[];
}

export async function fetchEmployeeByMatricule(
  registrationNumber: string
): Promise<GuichetAgentRecord | null> {
  const matricule = registrationNumber.trim();
  if (!matricule) return null;
  try {
    const res = await rhFetch(
      `/api/guichet/employee/lookup?registration_number=${encodeURIComponent(matricule)}`,
      { headers: guichetHeaders() },
      8000
    );
    if (res.status === 404) return null;
    if (!res.ok) return null;
    const body = (await res.json()) as { status: string; data?: GuichetAgentRecord };
    return body.status === 'ok' && body.data ? body.data : null;
  } catch {
    return null;
  }
}

export async function fetchAgentsList(params: {
  q?: string;
  page?: number;
  page_size?: number;
}): Promise<GuichetAgentsListResponse> {
  const qs = new URLSearchParams();
  if (params.q?.trim()) qs.set('q', params.q.trim());
  qs.set('page', String(params.page ?? 1));
  qs.set('page_size', String(params.page_size ?? 25));

  try {
    const res = await rhFetch(`/api/guichet/employees?${qs.toString()}`, {
      headers: guichetHeaders(),
    });

    if (!res.ok) {
      const detail = await parseRhError(res);
      throw new Error(`Impossible de charger les agents (${detail})`);
    }

    return (await res.json()) as GuichetAgentsListResponse;
  } catch (err) {
    if (err instanceof Error && err.message.startsWith('Impossible')) throw err;
    throw new Error(
      'Connexion au service RH impossible. Lancez : docker compose --profile rh up -d rh_server'
    );
  }
}
