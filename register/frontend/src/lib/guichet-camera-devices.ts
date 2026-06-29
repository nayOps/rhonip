/**
 * Caméra guichet ONIP — Logitech C930c (libellé Windows souvent en chinois).
 * Ex. « 罗技高清网络摄像机 C930c »
 */

export const GUICHET_CAMERA_LABEL_PATTERNS: RegExp[] = [
  /罗技高清网络摄像机\s*c930c/i,
  /罗技.*c930/i,
  /高清网络摄像机/i,
  /网络摄像机/i,
  /logitech.*c930/i,
  /c930c/i,
  /罗技/,
  /logitech/i,
];

/** Caméras intégrées à ignorer quand une USB guichet est disponible. */
export const BUILTIN_CAMERA_LABEL_PATTERNS: RegExp[] = [
  /hp\s*5mp/i,
  /^hp\s/i,
  /integrated/i,
  /ir\s*camera/i,
  /truevision/i,
  /facetime/i,
];

export function isGuichetCameraLabel(label: string): boolean {
  const n = label.trim();
  if (!n) return false;
  if (BUILTIN_CAMERA_LABEL_PATTERNS.some((re) => re.test(n))) return false;
  if (GUICHET_CAMERA_LABEL_PATTERNS.some((re) => re.test(n))) return true;
  // Tout libellé avec caractères chinois (hors HP) = caméra USB guichet
  return /[\u4e00-\u9fff]/.test(n);
}

export function isBuiltinCameraLabel(label: string): boolean {
  const n = label.trim();
  if (!n) return false;
  return BUILTIN_CAMERA_LABEL_PATTERNS.some((re) => re.test(n));
}

/** Score pour choisir la bonne caméra (GPYScan, bridge, etc.). */
export function scoreGuichetCameraName(name: string): number {
  const n = name.trim();
  if (!n) return -100;
  const lower = n.toLowerCase();

  if (/xhy|gpy|d500|cameragp/.test(lower)) return 100;
  if (/罗技|高清网络摄像机|网络摄像机/.test(n)) return 95;
  if (/logitech|c930|c920|brio/.test(lower)) return 90;
  if (/[\u4e00-\u9fff]/.test(n) && !isBuiltinCameraLabel(n)) return 80;
  if (isBuiltinCameraLabel(n)) return -80;
  return 10;
}

export function pickGuichetCameraIdByName<T extends { id: number; name: string }>(
  devices: T[]
): number {
  if (devices.length === 0) return 0;

  let best = devices[0].id;
  let bestScore = scoreGuichetCameraName(devices[0].name);
  for (let i = 1; i < devices.length; i++) {
    const s = scoreGuichetCameraName(devices[i].name);
    if (s > bestScore) {
      bestScore = s;
      best = devices[i].id;
    }
  }
  return best;
}

export function bridgeComOnlyBuiltinCameras(message: string): boolean {
  if (!message) return false;
  return /non certifié|code -1|pas gpy|non reconnu \(pas gpy\)|hp 5mp/i.test(message);
}

export const GUICHET_CAMERA_HINT =
  'Caméra guichet : 罗技高清网络摄像机 C930c (Logitech C930c) — pas la HP intégrée du PC.';
