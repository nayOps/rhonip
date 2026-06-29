import { describeIrisErrcode } from '@/lib/iris-error-codes';
import { EyePosition } from '@/types';

const BRIDGE_URL =
  process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL || 'http://127.0.0.1:8765';

export type IrisEyeSide = 'left' | 'right' | 'both';

export interface IrisBridgeStatus {
  available: boolean;
  mode: string;
  message: string;
  server_port?: number;
  device_model?: string;
  device_status?: number;
  errcode?: number;
}

export interface IrisEyeCaptureDto {
  eye: string;
  success: boolean;
  image_base64?: string;
  mime?: string;
  quality?: number;
  message?: string;
}

export interface IrisCaptureResult {
  success: boolean;
  message: string;
  eyes?: IrisEyeCaptureDto[];
  raw_response?: string;
}

export interface IrisLivePreview {
  success: boolean;
  message: string;
  left_image_base64?: string;
  right_image_base64?: string;
  mime?: string;
}

function pickStr(obj: Record<string, unknown>, ...keys: string[]): string | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === 'string' && v) return v;
  }
  return undefined;
}

function pickNum(obj: Record<string, unknown>, ...keys: string[]): number | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === 'number' && !Number.isNaN(v)) return v;
  }
  return undefined;
}

function pickBool(obj: Record<string, unknown>, ...keys: string[]): boolean | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === 'boolean') return v;
  }
  return undefined;
}

function fetchTimeoutMessage(err: unknown, label: string): string {
  if (err instanceof Error && /timed out|timeout|aborted/i.test(err.message)) {
    return `${label} — délai dépassé. Vérifiez Device Bridge (8765) et start-iris-server-admin.bat (admin).`;
  }
  return err instanceof Error ? err.message : label;
}

/** Bridge peut renvoyer du texte brut (ex. exception ASP.NET) au lieu de JSON. */
async function parseBridgeBody(
  res: Response
): Promise<{ raw: Record<string, unknown>; text: string }> {
  const text = await res.text();
  if (!text.trim()) return { raw: {}, text };
  try {
    const parsed = JSON.parse(text) as unknown;
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return { raw: parsed as Record<string, unknown>, text };
    }
  } catch {
    /* non-JSON */
  }
  const snippet = text.length > 400 ? `${text.slice(0, 400)}…` : text;
  const firstLine = snippet.split(/\r?\n/)[0]?.trim() || snippet;
  return {
    raw: { message: firstLine, success: false, available: false },
    text,
  };
}

function toDataUrl(b64: string | undefined, mime = 'image/bmp'): string | undefined {
  if (!b64) return undefined;
  if (b64.startsWith('data:')) return b64;
  return `data:${mime};base64,${b64}`;
}

function mapIrisStatus(raw: Record<string, unknown>, httpOk: boolean): IrisBridgeStatus {
  const errcode = pickNum(raw, 'errcode', 'errcode');
  const rawMsg = pickStr(raw, 'message', 'Message') ?? (httpOk ? 'OK' : 'Erreur');
  const message =
    errcode && errcode !== 0 ? describeIrisErrcode(errcode, rawMsg) : rawMsg;

  return {
    available: pickBool(raw, 'available', 'Available') ?? httpOk,
    mode: pickStr(raw, 'mode', 'Mode') ?? 'unknown',
    message,
    server_port: pickNum(raw, 'server_port', 'serverPort'),
    device_model: pickStr(raw, 'device_model', 'deviceModel'),
    device_status: pickNum(raw, 'device_status', 'deviceStatus'),
    errcode,
  };
}

export async function getIrisStatus(): Promise<IrisBridgeStatus> {
  try {
    const res = await fetch(`${BRIDGE_URL}/api/v1/devices/iris/status`, {
      signal: AbortSignal.timeout(20_000),
    });
    const { raw } = await parseBridgeBody(res);
    return mapIrisStatus(raw, res.ok);
  } catch (e) {
    throw new Error(fetchTimeoutMessage(e, 'Statut lecteur iris'));
  }
}

export function isIrisHttpServerDown(message: string): boolean {
  return /injoignable|arrêté|50218|50219|non démarré|start-server/i.test(message);
}

export async function startIrisServer(): Promise<{
  success: boolean;
  message: string;
  baseUrl?: string;
}> {
  const res = await fetch(`${BRIDGE_URL}/api/v1/devices/iris/start-server`, {
    method: 'POST',
    signal: AbortSignal.timeout(60_000),
  });
  const { raw } = await parseBridgeBody(res);
  const success = pickBool(raw, 'success', 'Success') ?? false;
  const message =
    pickStr(raw, 'message', 'Message') ??
    (success ? 'IrisDeviceServer démarré' : `Démarrage échoué (HTTP ${res.status})`);
  const baseUrl = pickStr(raw, 'base_url', 'baseUrl');
  return { success, message, baseUrl };
}

export async function openIrisDevice(): Promise<{
  success: boolean;
  message: string;
  errcode?: number;
}> {
  const res = await fetch(`${BRIDGE_URL}/api/v1/devices/iris/open`, {
    method: 'POST',
    signal: AbortSignal.timeout(30_000),
  });
  const { raw } = await parseBridgeBody(res);
  const errcode = pickNum(raw, 'errcode', 'errcode');
  const rawMsg = pickStr(raw, 'message', 'Message') ?? 'Ouverture lecteur';
  const message =
    errcode && errcode !== 0 ? describeIrisErrcode(errcode, rawMsg) : rawMsg;
  const success = pickBool(raw, 'success', 'Success') ?? false;
  return { success, message, errcode };
}

export async function probeIrisDevice(): Promise<{
  status: IrisBridgeStatus;
  open?: { success: boolean; message: string };
}> {
  const res = await fetch(`${BRIDGE_URL}/api/v1/devices/iris/probe`, {
    method: 'POST',
    signal: AbortSignal.timeout(30_000),
  });
  const { raw } = await parseBridgeBody(res);
  const statusRaw = (raw.status ?? {}) as Record<string, unknown>;
  const openRaw = raw.open as Record<string, unknown> | undefined;
  return {
    status: mapIrisStatus(statusRaw, res.ok),
    open: openRaw
      ? {
          success: pickBool(openRaw, 'success', 'Success') ?? false,
          message: pickStr(openRaw, 'message', 'Message') ?? '',
        }
      : undefined,
  };
}

export async function fetchIrisLivePreview(): Promise<IrisLivePreview> {
  const res = await fetch(`${BRIDGE_URL}/api/v1/devices/iris/preview/live`);
  const { raw } = await parseBridgeBody(res);
  return {
    success: pickBool(raw, 'success', 'Success') ?? false,
    message: pickStr(raw, 'message', 'Message') ?? '',
    left_image_base64: pickStr(raw, 'left_image_base64', 'leftImageBase64'),
    right_image_base64: pickStr(raw, 'right_image_base64', 'rightImageBase64'),
    mime: pickStr(raw, 'mime', 'Mime') ?? 'image/bmp',
  };
}

export async function captureIris(
  eye: IrisEyeSide,
  timeoutSeconds = 30
): Promise<IrisCaptureResult> {
  const res = await fetch(`${BRIDGE_URL}/api/v1/devices/iris/capture`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      eye,
      timeout_seconds: timeoutSeconds,
    }),
  });
  const { raw } = await parseBridgeBody(res);
  if (!res.ok && !raw.message && !raw.Message) {
    return {
      success: false,
      message: `Capture iris HTTP ${res.status}`,
      eyes: undefined,
    };
  }
  const eyesRaw = (raw.eyes ?? raw.Eyes) as Array<Record<string, unknown>> | undefined;
  const eyes: IrisEyeCaptureDto[] | undefined = eyesRaw?.map((e) => ({
    eye: pickStr(e, 'eye', 'Eye') ?? '',
    success: pickBool(e, 'success', 'Success') ?? false,
    image_base64: pickStr(e, 'image_base64', 'imageBase64'),
    mime: pickStr(e, 'mime', 'Mime'),
    quality: pickNum(e, 'quality', 'Quality'),
    message: pickStr(e, 'message', 'Message'),
  }));

  const rawMsg = pickStr(raw, 'message', 'Message') ?? `HTTP ${res.status}`;
  const errcode = pickNum(raw, 'errcode', 'errcode');
  const message =
    errcode && errcode !== 0 ? describeIrisErrcode(errcode, rawMsg) : rawMsg;

  return {
    success: pickBool(raw, 'success', 'Success') ?? false,
    message,
    eyes,
    raw_response: pickStr(raw, 'raw_response', 'rawResponse'),
  };
}

export async function stopIrisCapture(): Promise<void> {
  await fetch(`${BRIDGE_URL}/api/v1/devices/iris/stop`, { method: 'POST' });
}

export function bridgeEyeToPosition(eye: string): EyePosition | null {
  const e = eye.toLowerCase();
  if (e === 'left') return 'LEFT';
  if (e === 'right') return 'RIGHT';
  return null;
}

export function previewToDataUrls(preview: IrisLivePreview): {
  left?: string;
  right?: string;
} {
  const mime = preview.mime ?? 'image/bmp';
  return {
    left: toDataUrl(preview.left_image_base64, mime),
    right: toDataUrl(preview.right_image_base64, mime),
  };
}

export function eyeResultToDataUrl(dto: IrisEyeCaptureDto): string | undefined {
  return toDataUrl(dto.image_base64, dto.mime ?? 'image/bmp');
}
