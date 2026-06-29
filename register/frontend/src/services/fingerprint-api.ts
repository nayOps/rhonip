import { FingerPosition } from '@/types';

const FINGERPRINT_API_URL =
  process.env.NEXT_PUBLIC_FINGERPRINT_URL || 'http://localhost:8010';

const BRIDGE_URL =
  process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL || 'http://127.0.0.1:8765';

/** Poste guichet : appels directs au bridge Windows (8765). Mettre false pour passer par Docker:8010. */
const USE_DIRECT_BRIDGE = process.env.NEXT_PUBLIC_USE_DEVICE_BRIDGE_DIRECT !== 'false';

const API_ROOT = USE_DIRECT_BRIDGE ? BRIDGE_URL : FINGERPRINT_API_URL;
const API_PREFIX = USE_DIRECT_BRIDGE ? '' : '/api/v1';

export type CaptureType = 'left_four' | 'right_four' | 'both_thumbs' | 'single';

export const CAPTURE_TYPE_LABELS: Record<CaptureType, string> = {
  left_four: 'Main gauche — 4 doigts',
  right_four: 'Main droite — 4 doigts',
  both_thumbs: 'Deux pouces',
  single: 'Un doigt',
};

/** Comme FAP60Demo : quelle main poser sur le plateau. */
export const CAPTURE_HAND_HINT: Record<CaptureType, string> = {
  left_four: 'Posez la MAIN GAUCHE (4 doigts au centre du plateau), comme dans FAP60Demo.',
  right_four: 'Posez la MAIN DROITE (4 doigts au centre du plateau).',
  both_thumbs: 'Posez les deux pouces au centre du plateau.',
  single: 'Un doigt au centre du plateau.',
};

export const CAPTURE_TYPE_FINGERS: Record<CaptureType, FingerPosition[]> = {
  left_four: ['LEFT_LITTLE', 'LEFT_RING', 'LEFT_MIDDLE', 'LEFT_INDEX'],
  right_four: ['RIGHT_INDEX', 'RIGHT_MIDDLE', 'RIGHT_RING', 'RIGHT_LITTLE'],
  both_thumbs: ['LEFT_THUMB', 'RIGHT_THUMB'],
  single: ['RIGHT_INDEX'],
};

const BRIDGE_POSITION: Record<FingerPosition, string> = {
  RIGHT_THUMB: 'right_thumb',
  RIGHT_INDEX: 'right_index',
  RIGHT_MIDDLE: 'right_middle',
  RIGHT_RING: 'right_ring',
  RIGHT_LITTLE: 'right_little',
  LEFT_THUMB: 'left_thumb',
  LEFT_INDEX: 'left_index',
  LEFT_MIDDLE: 'left_middle',
  LEFT_RING: 'left_ring',
  LEFT_LITTLE: 'left_little',
};

const BRIDGE_TO_FINGER: Record<string, FingerPosition> = Object.fromEntries(
  Object.entries(BRIDGE_POSITION).map(([k, v]) => [v, k as FingerPosition])
) as Record<string, FingerPosition>;

export interface FingerPreviewDto {
  position: string;
  image_base64: string;
  mime?: string;
  nfiq?: number;
  nfiq_label?: string;
  quality?: number;
  passes_nfiq?: boolean;
}

export interface BridgeCaptureResult {
  success: boolean;
  message: string;
  templates?: Array<{
    position: string;
    format_id: number;
    data_base64: string;
    quality: number;
    nfiq?: number;
    nfiq_label?: string;
  }>;
  previews?: FingerPreviewDto[];
  preview_plate_base64?: string;
  logs?: string[];
}

export interface BridgeHealth {
  status: string;
  modules?: {
    fingerprint?: { status: string; message?: string; mode?: string };
  };
}

function pickStr(obj: Record<string, unknown>, ...keys: string[]): string | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === 'string' && v) return v;
  }
  return undefined;
}

function normalizeCaptureResult(raw: Record<string, unknown>): BridgeCaptureResult {
  const previewsRaw = (raw.previews ?? raw.Previews) as Array<Record<string, unknown>> | undefined;
  return {
    success: Boolean(raw.success ?? raw.Success),
    message: pickStr(raw, 'message', 'Message') || 'Capture',
    preview_plate_base64: (raw.preview_plate_base64 ?? raw.previewPlateBase64) as string | undefined,
    logs: (raw.logs ?? raw.Logs) as string[] | undefined,
    previews: previewsRaw?.map((p) => ({
      position: String(p.position ?? p.Position ?? ''),
      image_base64: String(p.image_base64 ?? p.imageBase64 ?? ''),
      mime: (p.mime ?? p.Mime) as string | undefined,
      nfiq: (p.nfiq ?? p.Nfiq) as number | undefined,
      nfiq_label: (p.nfiq_label ?? p.nfiqLabel) as string | undefined,
      quality: (p.quality ?? p.Quality) as number | undefined,
      passes_nfiq: (p.passes_nfiq ?? p.passesNfiq) as boolean | undefined,
    })),
    templates: ((raw.templates ?? raw.Templates) as Array<Record<string, unknown>> | undefined)?.map(
      (t) => ({
        position: String(t.position ?? t.Position ?? ''),
        format_id: Number(t.format_id ?? t.formatId ?? t.FormatId ?? 4),
        data_base64: String(t.data_base64 ?? t.dataBase64 ?? ''),
        quality: Number(t.quality ?? t.Quality ?? 0),
        nfiq: (t.nfiq ?? t.Nfiq) as number | undefined,
        nfiq_label: (t.nfiq_label ?? t.nfiqLabel) as string | undefined,
      })
    ),
  };
}

async function apiPost<T>(path: string, body?: object): Promise<T> {
  const res = await fetch(`${API_ROOT}${API_PREFIX}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  });
  let data: Record<string, unknown> = {};
  try {
    data = (await res.json()) as Record<string, unknown>;
  } catch {
    /* corps vide */
  }
  if (!res.ok) {
    const msg = pickStr(data, 'message', 'Message') || `Erreur HTTP ${res.status}`;
    const logs = (data.logs ?? data.Logs) as string[] | undefined;
    const detail = logs?.length ? `${msg}\n${logs.join('\n')}` : msg;
    throw new Error(detail);
  }
  return data as T;
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_ROOT}${API_PREFIX}${path}`, {
    method: 'GET',
    signal: AbortSignal.timeout(5000),
  });
  if (!res.ok) throw new Error(`Erreur HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export async function getFingerprintHealth(): Promise<{
  ok: boolean;
  bridge?: BridgeHealth;
  mode?: string;
  via?: 'bridge' | 'fingerprint_service';
}> {
  try {
    const bridge = await fetch(`${BRIDGE_URL}/health`, { signal: AbortSignal.timeout(3000) });
    if (bridge.ok) {
      const data = (await bridge.json()) as BridgeHealth;
      return { ok: true, bridge: data, mode: data.modules?.fingerprint?.mode, via: 'bridge' };
    }
  } catch {
    /* bridge hors ligne */
  }
  if (!USE_DIRECT_BRIDGE) {
    try {
      const res = await fetch(`${FINGERPRINT_API_URL}/api/v1/health/`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        return { ok: true, bridge: data.bridge, mode: data.bridge?.modules?.fingerprint?.mode, via: 'fingerprint_service' };
      }
    } catch {
      /* ignore */
    }
  }
  return { ok: false };
}

export async function openFingerprintDevice(): Promise<{ success: boolean; message: string }> {
  const path = USE_DIRECT_BRIDGE
    ? '/api/v1/devices/fingerprint/open'
    : '/fingerprint/open/';
  return apiPost(path);
}

/** Aperçu live (captureVideo) — requête silencieuse (toujours HTTP 200 côté bridge). */
export async function fetchFingerprintPreview(
  captureType: CaptureType
): Promise<string | null> {
  if (!USE_DIRECT_BRIDGE) return null;
  try {
    const res = await fetch(`${BRIDGE_URL}/api/v1/devices/fingerprint/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ capture_type: captureType }),
    });
    const raw = (await res.json()) as Record<string, unknown>;
    const data = normalizeCaptureResult(raw);
    if (!data.preview_plate_base64) return null;
    return `data:image/png;base64,${data.preview_plate_base64}`;
  } catch {
    return null;
  }
}

export async function closeFingerprintDevice(): Promise<{ success: boolean; message: string }> {
  const path = USE_DIRECT_BRIDGE
    ? '/api/v1/devices/fingerprint/close'
    : '/fingerprint/close/';
  return apiPost(path);
}

export async function captureFingerprints(options: {
  captureType: CaptureType;
  presentFingers: FingerPosition[];
  nfiqThreshold: number;
  timeoutMs?: number;
  fingerPosition?: FingerPosition;
}): Promise<BridgeCaptureResult> {
  const present = options.presentFingers.map((p) => BRIDGE_POSITION[p]);
  const expected = CAPTURE_TYPE_FINGERS[options.captureType].map((p) => BRIDGE_POSITION[p]);
  const missingFingers = expected.filter((f) => !present.includes(f)).length;
  const path = USE_DIRECT_BRIDGE
    ? '/api/v1/devices/fingerprint/capture'
    : '/fingerprint/capture/';

  const body: Record<string, unknown> = {
    capture_type: options.captureType,
    present_fingers: present,
    missing_fingers: missingFingers,
    nfiq_threshold: options.nfiqThreshold,
    timeout_ms: options.timeoutMs ?? 45000,
    template_format: 4,
  };
  if (options.captureType === 'single' && options.fingerPosition) {
    body.finger_position = BRIDGE_POSITION[options.fingerPosition];
  }

  try {
    const isThumbs = options.captureType === 'both_thumbs';
    const bridgeBudgetMs = options.timeoutMs ?? 38000;
    // Le mode "both_thumbs" peut basculer en repli single côté bridge (2 captures).
    // On laisse un budget client plus large pour ne pas interrompre ce repli.
    const clientTimeoutMs = isThumbs
      ? Math.max(bridgeBudgetMs + 20_000, 65_000)
      : bridgeBudgetMs + 12_000;
    const res = await fetch(`${API_ROOT}${API_PREFIX}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(clientTimeoutMs),
    });
    let raw: Record<string, unknown> = {};
    try {
      raw = (await res.json()) as Record<string, unknown>;
    } catch {
      /* corps vide */
    }
    if (!res.ok) {
      const msg = pickStr(raw, 'message', 'Message') || `Erreur HTTP ${res.status}`;
      const logs = (raw.logs ?? raw.Logs) as string[] | undefined;
      throw new Error(logs?.length ? `${msg}\n${logs.join('\n')}` : msg);
    }
    const data = normalizeCaptureResult(raw);
    if (!data.success) {
      const detail = data.logs?.length ? `${data.message}\n${data.logs.join('\n')}` : data.message;
      throw new Error(detail || 'Capture échouée');
    }
    return data;
  } catch (e) {
    if (e instanceof Error && e.name === 'TimeoutError') {
      throw new Error(
        options.captureType === 'both_thumbs'
          ? 'Délai pouces dépassé (~65 s). Repositionnez les deux pouces au centre; un repli single automatique est tenté.'
          : 'Délai dépassé (~40 s). Placez les 4 doigts au centre du plateau (évite « edge finger ») et réessayez.'
      );
    }
    throw e;
  }
}

export function mapPreviewToFinger(position: string): FingerPosition | undefined {
  return BRIDGE_TO_FINGER[position.toLowerCase()];
}

/** @deprecated Préférer saveFingerprintBiometrics (enrollment-session-api). */
export async function updateFingerprintModality(
  sessionId: string,
  status: 'completed' | 'skipped' | 'failed' | 'pending',
  message?: string
): Promise<void> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
  const res = await fetch(
    `${apiUrl}/api/v1/enrolments/sessions/modality/fingerprint/${sessionId}/`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, message }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { error?: string }).error || `Modality update failed (${res.status})`);
  }
}

export { saveFingerprintBiometrics } from '@/services/enrollment-session-api';

/** @deprecated Utiliser captureFingerprints */
export async function checkFingerprintServiceHealth(): Promise<boolean> {
  const h = await getFingerprintHealth();
  return h.ok;
}
