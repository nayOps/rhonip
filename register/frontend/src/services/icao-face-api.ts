import type { PhotoData } from '@/components/biometrics/PhotoCapture';

import { fetchTimeoutSignal } from '@/lib/fetch-timeout';

/** Ports essayés si le service a démarré sur un autre port (50220 bloqué sous Windows). */
const ICAO_PORT_CANDIDATES = [50270, 50300, 50420, 50520, 50220] as const;

let resolvedIcaoBaseUrl: string | null = null;

function icaoWsUrl(base: string): string {
  return `${base.replace(/^http/, 'ws')}/face/ws`;
}

function healthUrlsForBase(base: string): string[] {
  const direct = `${base.replace(/\/$/, '')}/health`;
  if (typeof window === 'undefined') return [direct];
  const port = (() => {
    try {
      return new URL(base).port || '50270';
    } catch {
      return '50270';
    }
  })();
  const altHost =
    base.includes('127.0.0.1')
      ? `http://localhost:${port}/health`
      : `http://127.0.0.1:${port}/health`;
  // Direct d'abord (service local) ; proxy Next en secours
  return [direct, altHost, '/icao-proxy/health', '/api/icao-health'];
}

async function pingIcaoHealth(base: string): Promise<boolean> {
  for (const url of healthUrlsForBase(base)) {
    try {
      const res = await fetch(url, { signal: fetchTimeoutSignal(4000) });
      if (!res.ok) continue;
      const body = (await res.json()) as { status?: string };
      if (body.status === 'ok') return true;
    } catch {
      /* try next */
    }
  }
  return false;
}

/** URL HTTP du service ICAO (détection à la volée). */
export async function resolveIcaoBaseUrl(force = false): Promise<string | null> {
  if (!force && resolvedIcaoBaseUrl) {
    if (await pingIcaoHealth(resolvedIcaoBaseUrl)) return resolvedIcaoBaseUrl;
    resolvedIcaoBaseUrl = null;
  }

  const fromEnv = process.env.NEXT_PUBLIC_ICAO_FACE_SERVICE_URL?.replace(/\/$/, '');
  const candidates = [
    fromEnv,
    ...ICAO_PORT_CANDIDATES.map((p) => `http://127.0.0.1:${p}`),
  ].filter((u, i, arr): u is string => !!u && arr.indexOf(u) === i);

  for (const base of candidates) {
    if (await pingIcaoHealth(base)) {
      resolvedIcaoBaseUrl = base;
      return base;
    }
  }
  return null;
}

export function getResolvedIcaoBaseUrl(): string | null {
  return resolvedIcaoBaseUrl;
}

/** Valeurs par défaut (surchargées par GET /health → thresholds). */
export const ICAO_DEFAULTS = {
  scoreAccepted: Number(process.env.NEXT_PUBLIC_ICAO_SCORE_ACCEPTED) || 90,
  scoreReview: Number(process.env.NEXT_PUBLIC_ICAO_SCORE_REVIEW) || 75,
  realtimeReadyScore: Number(process.env.NEXT_PUBLIC_ICAO_REALTIME_READY_SCORE) || 82,
  autoCaptureStableFrames:
    Number(process.env.NEXT_PUBLIC_ICAO_AUTO_CAPTURE_FRAMES) || 12,
} as const;

export interface IcaoServiceConfig {
  scoreAccepted: number;
  scoreReview: number;
  realtimeReadyScore: number;
  autoCaptureStableFrames: number;
}

export type IcaoRealtimeStatus = 'NOT_READY' | 'READY';
export type IcaoFinalStatus = 'ACCEPTED' | 'REVIEW' | 'REJECTED';

export interface IcaoRealtimeChecks {
  faceDetected: boolean;
  singleFace: boolean;
  faceCentered: boolean;
  eyesOpen: boolean;
  mouthClosed: boolean;
  headPose: 'OK' | 'WARN' | 'FAIL';
  lighting: 'OK' | 'WARN' | 'FAIL';
  background: 'OK' | 'WARN' | 'FAIL';
  sharpness: 'OK' | 'WARN' | 'FAIL';
}

export interface IcaoPoint2D {
  x: number;
  y: number;
}

export interface IcaoLiveOverlay {
  facialLandmarks: IcaoPoint2D[];
  connections: number[][];
  boundingBox?: { xMin: number; yMin: number; xMax: number; yMax: number };
  eyeLine?: { left: IcaoPoint2D; right: IcaoPoint2D };
  faceAxis?: { top: IcaoPoint2D; bottom: IcaoPoint2D; nose?: IcaoPoint2D };
  cropFrame?: {
    x: number;
    y: number;
    width: number;
    height: number;
    ratio?: string;
    faceHeightPercent?: number;
    faceHeightTargetMin?: number;
    faceHeightTargetMax?: number;
  };
}

export interface IcaoRealtimeResult {
  mode: 'REAL_TIME';
  status: IcaoRealtimeStatus;
  message: string;
  qualityScore: number;
  checks: IcaoRealtimeChecks;
  overlay?: IcaoLiveOverlay | null;
}

export interface IcaoCropInfo {
  croppingApplied: boolean;
  stretchingApplied: boolean;
  rotationCorrectionApplied: boolean;
  rotationDegrees: number;
  ratio: string;
  faceCentered: boolean;
  eyesAligned: boolean;
  chinVisible: boolean;
  headTopMargin: string;
  outputWidth?: number;
  outputHeight?: number;
  cropRect?: Record<string, number>;
  error?: string | null;
}

export interface IcaoCaptureInfo {
  rawImageSaved: boolean;
  icaoImageSaved: boolean;
  rawSha256: string;
  icaoSha256: string;
  rawImageBase64: string;
  icaoImageBase64: string;
}

export interface IcaoProcessCaptureResult {
  capture: IcaoCaptureInfo;
  liveOverlay: Record<string, boolean>;
  crop: IcaoCropInfo;
  quality: IcaoFinalResult;
  recommendation: string;
}

export interface IcaoFinalChecks {
  faceDetected: boolean;
  singleFace: boolean;
  faceCentered: boolean;
  eyesOpen: boolean;
  gazeToCamera: boolean;
  mouthClosed: boolean;
  neutralExpression: boolean;
  headStraight: boolean;
  yaw: string;
  pitch: string;
  roll: string;
  lighting: string;
  overExposure: boolean;
  underExposure: boolean;
  sharpness: string;
  backgroundUniform: boolean;
  occlusionDetected: boolean;
  resolution: boolean;
}

export interface IcaoFinalResult {
  mode: 'FINAL_CAPTURE';
  status: IcaoFinalStatus;
  icaoCompliant: boolean;
  isoCompliant: boolean;
  qualityScore: number;
  checks: IcaoFinalChecks;
  metadata: Record<string, string>;
  recommendation: string;
  errors: string[];
}

export async function fetchIcaoServiceConfig(): Promise<IcaoServiceConfig | null> {
  try {
    const base = await resolveIcaoBaseUrl();
    if (!base) return null;

    for (const healthUrl of healthUrlsForBase(base)) {
      try {
        const res = await fetch(healthUrl, {
          signal: fetchTimeoutSignal(6000),
        });
        if (!res.ok) continue;
        const body = (await res.json()) as {
          status?: string;
          thresholds?: Partial<IcaoServiceConfig>;
        };
        if (body.status !== 'ok') continue;
        const t = body.thresholds ?? {};
        return {
          scoreAccepted: t.scoreAccepted ?? ICAO_DEFAULTS.scoreAccepted,
          scoreReview: t.scoreReview ?? ICAO_DEFAULTS.scoreReview,
          realtimeReadyScore: t.realtimeReadyScore ?? ICAO_DEFAULTS.realtimeReadyScore,
          autoCaptureStableFrames:
            t.autoCaptureStableFrames ?? ICAO_DEFAULTS.autoCaptureStableFrames,
        };
      } catch {
        continue;
      }
    }
    return null;
  } catch {
    return null;
  }
}

export async function probeIcaoFaceService(): Promise<boolean> {
  return (await fetchIcaoServiceConfig()) !== null;
}

export function createIcaoFaceStream(
  onResult: (result: IcaoRealtimeResult) => void,
  onError?: (message: string) => void
): {
  connect: () => Promise<void>;
  sendFrame: (dataUrl: string) => void;
  close: () => void;
} {
  let ws: WebSocket | null = null;
  let pending = false;

  const connect = () =>
    new Promise<void>(async (resolve, reject) => {
      const base = await resolveIcaoBaseUrl();
      if (!base) {
        reject(new Error('Service ICAO introuvable (ports 50270, 50300)'));
        return;
      }
      const port = new URL(base).port || '50270';
      ws = new WebSocket(icaoWsUrl(base));
      const timer = setTimeout(() => {
        ws?.close();
        reject(new Error(`Connexion assistant ICAO expirée (port ${port})`));
      }, 8000);
      ws.onopen = () => {
        clearTimeout(timer);
        resolve();
      };
      ws.onerror = () => {
        clearTimeout(timer);
        reject(new Error(`WebSocket ICAO injoignable (port ${port})`));
      };
      ws.onclose = () => {
        clearTimeout(timer);
        ws = null;
      };
      ws.onmessage = (ev) => {
        pending = false;
        try {
          const data = JSON.parse(String(ev.data)) as IcaoRealtimeResult;
          onResult(data);
        } catch {
          onError?.('Réponse ICAO invalide');
        }
      };
    });

  const sendFrame = (dataUrl: string) => {
    if (!ws || ws.readyState !== WebSocket.OPEN || pending) return;
    pending = true;
    ws.send(JSON.stringify({ image: dataUrl }));
  };

  const close = () => {
    pending = false;
    ws?.close();
    ws = null;
  };

  return { connect, sendFrame, close };
}

export async function processFaceCapture(
  dataUrl: string,
  meta?: { enrollmentId?: string; deviceId?: string; operatorId?: string; camera?: string }
): Promise<IcaoProcessCaptureResult> {
  const buildForm = async () => {
    const blob = await dataUrlToBlob(dataUrl);
    const form = new FormData();
    form.append('image', blob, 'photo_originale.jpg');
    if (meta?.enrollmentId) form.append('enrollmentId', meta.enrollmentId);
    if (meta?.deviceId) form.append('deviceId', meta.deviceId ?? 'KIT-ONIP-WEBCAM');
    if (meta?.operatorId) form.append('operatorId', meta.operatorId);
    if (meta?.camera) form.append('camera', meta.camera);
    return form;
  };

  const base = (await resolveIcaoBaseUrl()) ?? '';
  const endpoints = base
    ? [`${base}/face/process-capture`, '/icao-proxy/face/process-capture']
    : ['/icao-proxy/face/process-capture'];

  let lastError = 'Service ICAO non disponible';
  for (const url of endpoints) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        body: await buildForm(),
        signal: AbortSignal.timeout(120_000),
      });
      if (!res.ok) {
        const text = await res.text().catch(() => '');
        lastError = text || `ICAO process-capture HTTP ${res.status}`;
        continue;
      }
      return (await res.json()) as IcaoProcessCaptureResult;
    } catch (e) {
      lastError = e instanceof Error ? e.message : 'ICAO process-capture échoué';
    }
  }
  throw new Error(lastError);
}

export function base64ToDataUrl(b64: string, mime = 'image/jpeg'): string {
  if (b64.startsWith('data:')) return b64;
  return `data:${mime};base64,${b64}`;
}

export async function checkFaceQuality(
  dataUrl: string,
  meta?: { enrollmentId?: string; deviceId?: string; operatorId?: string; camera?: string }
): Promise<IcaoFinalResult> {
  const blob = await dataUrlToBlob(dataUrl);
  const form = new FormData();
  form.append('image', blob, 'face.jpg');
  if (meta?.enrollmentId) form.append('enrollmentId', meta.enrollmentId);
  if (meta?.deviceId) form.append('deviceId', meta.deviceId);
  if (meta?.operatorId) form.append('operatorId', meta.operatorId);
  if (meta?.camera) form.append('camera', meta.camera);

  const base = (await resolveIcaoBaseUrl()) ?? '';
  if (!base) throw new Error('Service ICAO non disponible');
  const res = await fetch(`${base}/face/quality-check`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `ICAO service HTTP ${res.status}`);
  }
  return (await res.json()) as IcaoFinalResult;
}

async function dataUrlToBlob(dataUrl: string): Promise<Blob> {
  const res = await fetch(dataUrl);
  return res.blob();
}

export function mapIcaoProcessToPhotoData(
  processed: IcaoProcessCaptureResult
): Pick<
  PhotoData,
  | 'image'
  | 'rawImage'
  | 'icaoImage'
  | 'quality'
  | 'icaoCompliant'
  | 'checks'
  | 'timestamp'
  | 'captureMeta'
  | 'cropInfo'
> & {
  recommendation?: string;
  finalStatus?: IcaoFinalStatus;
} {
  const { capture, crop, quality } = processed;
  const mapped = mapIcaoFinalToPhotoData(
    capture.icaoImageBase64 ? base64ToDataUrl(capture.icaoImageBase64) : '',
    quality
  );
  return {
    ...mapped,
    image: capture.icaoImageBase64
      ? base64ToDataUrl(capture.icaoImageBase64)
      : base64ToDataUrl(capture.rawImageBase64),
    rawImage: base64ToDataUrl(capture.rawImageBase64),
    icaoImage: capture.icaoImageBase64
      ? base64ToDataUrl(capture.icaoImageBase64)
      : undefined,
    captureMeta: {
      rawSha256: capture.rawSha256,
      icaoSha256: capture.icaoSha256,
      rawImageSaved: capture.rawImageSaved,
      icaoImageSaved: capture.icaoImageSaved,
      deviceId: quality.metadata?.deviceId,
      camera: quality.metadata?.camera,
      enrollmentId: quality.metadata?.enrollmentId,
      operatorId: quality.metadata?.operatorId,
      captureTimestamp: quality.metadata?.captureTimestamp,
    },
    cropInfo: crop,
  };
}

export function mapIcaoFinalToPhotoData(
  image: string,
  final: IcaoFinalResult
): Pick<PhotoData, 'quality' | 'icaoCompliant' | 'checks' | 'timestamp'> & {
  recommendation?: string;
  finalStatus?: IcaoFinalStatus;
} {
  const c = final.checks;
  return {
    quality: final.qualityScore,
    icaoCompliant: final.status === 'ACCEPTED' && final.icaoCompliant,
    finalStatus: final.status,
    recommendation: final.recommendation,
    checks: {
      faceDetected: c.faceDetected,
      eyesOpen: c.eyesOpen,
      lookingStraight: c.faceCentered && c.gazeToCamera,
      neutralExpression: c.neutralExpression,
      noGlasses: !c.occlusionDetected,
      goodLighting: c.lighting === 'OK',
      noShadows: !c.overExposure && !c.underExposure,
      sharpness: c.sharpness === 'OK',
      resolution: c.resolution,
      background: c.backgroundUniform,
    },
    timestamp: final.metadata?.captureTimestamp || new Date().toISOString(),
  };
}

/** Frame JPEG réduit pour le flux temps réel (perf). */
export function captureFrameForIcaoStream(
  video: HTMLVideoElement,
  maxWidth = 640,
  jpegQuality = 0.72
): string | null {
  const w = video.videoWidth;
  const h = video.videoHeight;
  if (!w || !h) return null;
  const scale = w > maxWidth ? maxWidth / w : 1;
  const cw = Math.round(w * scale);
  const ch = Math.round(h * scale);
  const canvas = document.createElement('canvas');
  canvas.width = cw;
  canvas.height = ch;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.translate(cw, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, cw, ch);
  return canvas.toDataURL('image/jpeg', jpegQuality);
}

export const ICAO_FACE_SERVICE_HELP =
  'Service ICAO Assistant (port 50270) non détecté.\n' +
  '→ PowerShell : cd register\\scripts puis .\\start-icao-face-service.cmd\n' +
  '→ Garder la fenêtre ouverte ; vérifier http://127.0.0.1:50270/health\n' +
  '→ Actualisez cette page, puis Photo → Webcam → Démarrer';
