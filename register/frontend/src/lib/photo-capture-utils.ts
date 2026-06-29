import type { PhotoData } from '@/components/biometrics/PhotoCapture';
import {
  GUICHET_CAMERA_LABEL_PATTERNS,
  GUICHET_CAMERA_HINT,
  isBuiltinCameraLabel,
  isGuichetCameraLabel,
} from '@/lib/guichet-camera-devices';

/** Dimensions minimales (photo type passeport, ratio 3:4). */
export const PHOTO_MIN_WIDTH = 480;
export const PHOTO_MIN_HEIGHT = 640;
export const ICAO_MIN_PASSED_CHECKS = 7;

export function stopMediaStream(stream: MediaStream | null | undefined): void {
  stream?.getTracks().forEach((t) => t.stop());
}

export function isCameraSecureContext(): boolean {
  return typeof window === 'undefined' || window.isSecureContext;
}

export async function listVideoInputDevices(): Promise<MediaDeviceInfo[]> {
  if (!navigator.mediaDevices?.enumerateDevices) return [];
  const devices = await navigator.mediaDevices.enumerateDevices();
  return devices.filter((d) => d.kind === 'videoinput');
}

/**
 * Webcam guichet ONIP — Logitech C930c.
 * Libellés Windows : « 罗技高清网络摄像机 C930c », « Logitech HD Webcam C930c », etc.
 */
const PREFERRED_WEBCAM_PATTERNS = GUICHET_CAMERA_LABEL_PATTERNS;

export function isPreferredGuichetWebcam(label: string): boolean {
  return isGuichetCameraLabel(label);
}

export function pickPreferredWebcamDevice(
  devices: MediaDeviceInfo[]
): MediaDeviceInfo | undefined {
  const inputs = devices.filter((d) => d.kind === 'videoinput');
  for (const pattern of PREFERRED_WEBCAM_PATTERNS) {
    const match = inputs.find((d) => pattern.test(d.label || ''));
    if (match) return match;
  }
  const chineseUsb = inputs.find(
    (d) => /[\u4e00-\u9fff]/.test(d.label || '') && !isBuiltinCameraLabel(d.label || '')
  );
  if (chineseUsb) return chineseUsb;
  const nonBuiltin = inputs.find((d) => !isBuiltinCameraLabel(d.label || ''));
  return nonBuiltin;
}

/** Libellés enumerateDevices souvent vides avant la première autorisation getUserMedia. */
export async function listVideoInputDevicesWithLabels(): Promise<MediaDeviceInfo[]> {
  let devices = await listVideoInputDevices();
  if (devices.some((d) => (d.label || '').length > 0)) return devices;
  if (!navigator.mediaDevices?.getUserMedia) return devices;
  try {
    const probe = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    stopMediaStream(probe);
    devices = await listVideoInputDevices();
  } catch {
    /* permission refusée — on garde la liste sans libellé */
  }
  return devices;
}

export async function queryCameraPermission(): Promise<PermissionState | 'unknown'> {
  if (!navigator.permissions?.query) return 'unknown';
  try {
    const status = await navigator.permissions.query({ name: 'camera' as PermissionName });
    return status.state;
  } catch {
    return 'unknown';
  }
}

export function formatWebcamPermissionHelp(permission: PermissionState | 'unknown'): string {
  const origin =
    typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000';
  if (permission === 'denied') {
    return (
      `Caméra bloquée pour ${origin}.\n` +
      '→ Chrome : ouvrez chrome://settings/content/siteDetails?site=http%3A%2F%2Flocalhost%3A3000 → Caméra → Autoriser.\n' +
      '→ Ou : icône cadenas dans la barre d’adresse → Paramètres du site → Caméra → Autoriser → Ctrl+F5.\n' +
      '→ Windows : Paramètres → Confidentialité → Caméra → autoriser les applications de bureau.\n' +
      '→ Fermez Teams/Zoom/Meet s’ils utilisent déjà la webcam.\n' +
      `→ ${GUICHET_CAMERA_HINT}`
    );
  }
  return (
    'Cliquez « Démarrer assistant ICAO » : le navigateur demandera l’accès caméra.\n' +
    '→ Choisissez « Autoriser » pour ce site (localhost:3000).\n' +
    `→ ${GUICHET_CAMERA_HINT}`
  );
}

const WEBCAM_VIDEO: MediaTrackConstraints = {
  width: { ideal: 1280, min: 640 },
  height: { ideal: 720, min: 480 },
  facingMode: 'user',
};

export async function openCameraStream(deviceId?: string): Promise<MediaStream> {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error(
      'Navigateur sans accès caméra (getUserMedia). Utilisez Chrome/Edge sur le poste guichet.'
    );
  }
  if (!isCameraSecureContext()) {
    throw new Error(
      `Caméra navigateur bloquée : ouvrez le guichet via ${typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'} (pas une adresse IP).`
    );
  }

  const attempts: MediaStreamConstraints[] = [];
  if (deviceId) {
    attempts.push({
      video: { ...WEBCAM_VIDEO, deviceId: { ideal: deviceId } },
      audio: false,
    });
  }
  attempts.push({ video: WEBCAM_VIDEO, audio: false });
  attempts.push({
    video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
    audio: false,
  });
  attempts.push({ video: true, audio: false });

  let lastErr: unknown;
  for (const constraints of attempts) {
    try {
      return await navigator.mediaDevices.getUserMedia(constraints);
    } catch (e) {
      lastErr = e;
      if (e instanceof DOMException && e.name === 'NotAllowedError') {
        throw e;
      }
    }
  }
  throw lastErr ?? new Error('Impossible d’ouvrir la webcam');
}

export function getActiveVideoDeviceId(stream: MediaStream | null): string | undefined {
  const track = stream?.getVideoTracks()[0];
  if (!track) return undefined;
  return track.getSettings().deviceId;
}

/** Ouvre la webcam guichet : permission d’abord, puis sélection 罗技 C930c si détectée. */
export async function openPreferredGuichetWebcam(): Promise<{
  stream: MediaStream;
  devices: MediaDeviceInfo[];
  selected: MediaDeviceInfo | undefined;
}> {
  let devices = await listVideoInputDevicesWithLabels();
  let selected = pickPreferredWebcamDevice(devices);

  let stream: MediaStream;
  if (selected?.deviceId) {
    stream = await openCameraStream(selected.deviceId);
  } else {
    stream = await openCameraStream();
    const activeId = getActiveVideoDeviceId(stream);
    devices = await listVideoInputDevices();
    selected = pickPreferredWebcamDevice(devices);
    if (selected?.deviceId && selected.deviceId !== activeId) {
      stopMediaStream(stream);
      stream = await openCameraStream(selected.deviceId);
    }
  }

  devices = await listVideoInputDevices();
  selected = pickPreferredWebcamDevice(devices) ?? selected;
  if (!selected && devices.length > 0) {
    selected = devices.find((d) => !isBuiltinCameraLabel(d.label || '')) ?? devices[0];
  }
  return { stream, devices, selected };
}

/** Capture JPEG base64 depuis la vidéo (orientation « titre », non miroir). */
export function captureFrameFromVideo(
  video: HTMLVideoElement,
  jpegQuality = 0.92
): string {
  const w = video.videoWidth;
  const h = video.videoHeight;
  if (!w || !h) {
    throw new Error('La caméra n\'est pas prête — attendez l\'aperçu live.');
  }

  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas 2D indisponible');

  ctx.translate(w, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, w, h);
  return canvas.toDataURL('image/jpeg', jpegQuality);
}

function loadImage(dataUrl: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('Image illisible'));
    img.src = dataUrl;
  });
}

function sampleRegion(
  data: Uint8ClampedArray,
  width: number,
  height: number,
  x0: number,
  y0: number,
  x1: number,
  y1: number
): { mean: number; variance: number } {
  let sum = 0;
  let sumSq = 0;
  let n = 0;
  const xs = Math.max(0, Math.floor(x0 * width));
  const xe = Math.min(width, Math.floor(x1 * width));
  const ys = Math.max(0, Math.floor(y0 * height));
  const ye = Math.min(height, Math.floor(y1 * height));

  for (let y = ys; y < ye; y++) {
    for (let x = xs; x < xe; x++) {
      const i = (y * width + x) * 4;
      const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      sum += lum;
      sumSq += lum * lum;
      n++;
    }
  }
  if (n === 0) return { mean: 0, variance: 0 };
  const mean = sum / n;
  return { mean, variance: sumSq / n - mean * mean };
}

/** Contrôles automatiques basiques (sans ML) — complétés côté serveur plus tard. */
export async function analyzeIdentityPhoto(dataUrl: string): Promise<{
  quality: number;
  checks: PhotoData['checks'];
  icaoCompliant: boolean;
}> {
  const img = await loadImage(dataUrl);
  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Analyse impossible');
  ctx.drawImage(img, 0, 0);
  const { data, width, height } = ctx.getImageData(0, 0, canvas.width, canvas.height);

  const full = sampleRegion(data, width, height, 0, 0, 1, 1);
  const center = sampleRegion(data, width, height, 0.25, 0.15, 0.75, 0.85);
  const border = sampleRegion(data, width, height, 0, 0, 0.15, 1);
  const borderR = sampleRegion(data, width, height, 0.85, 0, 1, 1);

  const resolution =
    width >= PHOTO_MIN_WIDTH && height >= PHOTO_MIN_HEIGHT;
  const goodLighting = full.mean >= 70 && full.mean <= 220;
  const sharpness = center.variance >= 120;
  const noShadows = Math.abs(center.mean - full.mean) < 55;
  const background =
    border.mean >= 160 && borderR.mean >= 160 && border.mean - center.mean > 15;
  const faceDetected =
    center.variance > full.variance * 0.85 && center.mean < border.mean - 10;

  const checks: PhotoData['checks'] = {
    faceDetected,
    eyesOpen: faceDetected && sharpness,
    lookingStraight: faceDetected && center.variance >= 100,
    neutralExpression: faceDetected,
    noGlasses: true,
    goodLighting,
    noShadows,
    sharpness,
    resolution,
    background,
  };

  const passed = Object.values(checks).filter(Boolean).length;
  const icaoCompliant = passed >= ICAO_MIN_PASSED_CHECKS;

  const quality = Math.min(
    100,
    Math.round(
      (passed / 10) * 55 +
        (resolution ? 15 : 0) +
        (sharpness ? 15 : 0) +
        (goodLighting ? 15 : 0)
    )
  );

  return { quality, checks, icaoCompliant };
}

export function cameraErrorMessage(
  err: unknown,
  permission: PermissionState | 'unknown' = 'unknown'
): string {
  if (err instanceof DOMException) {
    if (err.name === 'NotAllowedError') {
      return formatWebcamPermissionHelp(permission === 'unknown' ? 'prompt' : permission);
    }
    if (err.name === 'NotFoundError') {
      return 'Aucune webcam détectée — branchez une caméra USB et réessayez.';
    }
    if (err.name === 'NotReadableError') {
      return 'Caméra occupée — fermez FAP60Demo ou une autre application utilisant la webcam.';
    }
  }
  return err instanceof Error ? err.message : 'Erreur caméra';
}
