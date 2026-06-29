import { fetchBridgeJson, fetchBridgeResponse } from '@/lib/bridge-fetch';

export interface CameraStatus {
  available: boolean;
  mode: string;
  message: string;
  device_count?: number;
}

export interface CameraPreviewResult {
  success: boolean;
  message: string;
  image_base64?: string;
  mime?: string;
}

export interface CameraCaptureResult {
  success: boolean;
  message: string;
  image_base64?: string;
  mime?: string;
  face_detected?: boolean;
}

export interface CameraProbeResult {
  health?: Record<string, unknown>;
  status?: CameraStatus;
  open?: { success: boolean; message: string };
  close?: { success: boolean; message: string };
  probed_at?: string;
}

function pickStr(obj: Record<string, unknown>, ...keys: string[]): string | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === 'string' && v) return v;
  }
  return undefined;
}

function mapCameraStatus(raw: Record<string, unknown>): CameraStatus {
  return {
    available: Boolean(raw.available ?? raw.Available),
    mode: String(raw.mode ?? raw.Mode ?? 'gpy-com'),
    message: pickStr(raw, 'message', 'Message') || '',
    device_count: (raw.device_count ?? raw.deviceCount) as number | undefined,
  };
}

export async function getCameraStatus(): Promise<CameraStatus> {
  try {
    const { ok, data } = await fetchBridgeJson<Record<string, unknown>>(
      '/api/v1/devices/camera/status',
      undefined,
      4000
    );
    if (!ok || !data) {
      return {
        available: false,
        mode: 'unknown',
        message: 'Device Bridge injoignable (8765) — vérifiez start-device-bridge.cmd',
      };
    }
    return mapCameraStatus(data);
  } catch (e) {
    return {
      available: false,
      mode: 'unknown',
      message: e instanceof Error ? e.message : 'Bridge hors ligne',
    };
  }
}

export async function probeCameraBridge(): Promise<CameraProbeResult | null> {
  const { ok, data } = await fetchBridgeJson<CameraProbeResult>(
    '/api/v1/devices/camera/probe',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    },
    45_000
  );
  return ok && data ? data : null;
}

export async function openCameraDevice(): Promise<{ success: boolean; message: string }> {
  const res = await fetchBridgeResponse(
    '/api/v1/devices/camera/open',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    },
    15_000
  );
  if (!res) {
    throw new Error('Device Bridge injoignable (8765)');
  }
  const raw = (await res.json()) as Record<string, unknown>;
  const success = Boolean(raw.success ?? raw.Success);
  const message = pickStr(raw, 'message', 'Message') || (success ? 'OK' : 'Ouverture caméra échouée');
  if (!res.ok || !success) {
    throw new Error(message || `Erreur HTTP ${res.status}`);
  }
  return { success, message };
}

export async function closeCameraDevice(): Promise<void> {
  await fetchBridgeResponse(
    '/api/v1/devices/camera/close',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    },
    8000
  );
}

export async function fetchCameraPreview(): Promise<string | null> {
  try {
    const res = await fetchBridgeResponse('/api/v1/devices/camera/preview', undefined, 3000);
    if (!res?.ok) return null;
    const raw = (await res.json()) as Record<string, unknown>;
    const ok = Boolean(raw.success ?? raw.Success ?? true);
    const b64 = pickStr(raw, 'image_base64', 'imageBase64');
    if (!ok || !b64) return null;
    const mime = pickStr(raw, 'mime', 'Mime') || 'image/jpeg';
    return `data:${mime};base64,${b64}`;
  } catch {
    return null;
  }
}

export async function captureDocumentScan(autoCut = true): Promise<string> {
  const res = await fetchBridgeResponse(
    '/api/v1/devices/camera/capture-document',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auto_cut: autoCut }),
    },
    45_000
  );
  if (!res) throw new Error('Device Bridge injoignable');
  const raw = (await res.json()) as Record<string, unknown>;
  const b64 = pickStr(raw, 'image_base64', 'imageBase64');
  if (!res.ok || !b64) {
    throw new Error(pickStr(raw, 'message', 'Message') || 'Scan document échoué');
  }
  const mime = pickStr(raw, 'mime', 'Mime') || 'image/jpeg';
  return `data:${mime};base64,${b64}`;
}

export async function captureCameraPhoto(): Promise<string> {
  const res = await fetchBridgeResponse(
    '/api/v1/devices/camera/capture',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    },
    45_000
  );
  if (!res) throw new Error('Device Bridge injoignable');
  const raw = (await res.json()) as Record<string, unknown>;
  const b64 = pickStr(raw, 'image_base64', 'imageBase64');
  if (!res.ok || !b64) {
    throw new Error(pickStr(raw, 'message', 'Message') || 'Capture échouée');
  }
  const mime = pickStr(raw, 'mime', 'Mime') || 'image/jpeg';
  return `data:${mime};base64,${b64}`;
}
