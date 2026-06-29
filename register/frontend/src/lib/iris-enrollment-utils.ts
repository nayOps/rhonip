import type { EyePosition, EyeStatus, IrisCapture } from '@/types';

export const IRIS_MIN_QUALITY_WARN = 50;

export const EYE_STATUS_LABELS: Record<EyeStatus, string> = {
  PENDING: 'En attente',
  CAPTURED: 'Capturé',
  BLIND: 'Aveugle / non voyant',
  MISSING: 'Œil absent',
  DAMAGED: 'Œil endommagé',
  FAILED: 'Échec capture',
};

export const EYE_UNAVAILABLE_OPTIONS: {
  status: Exclude<EyeStatus, 'CAPTURED' | 'PENDING' | 'FAILED'>;
  label: string;
  shortLabel: string;
  reason: string;
}[] = [
  { status: 'BLIND', label: 'Aveugle / malvoyant', shortLabel: 'Aveugle', reason: 'Handicap visuel — œil non capturable' },
  { status: 'MISSING', label: 'Œil absent', shortLabel: 'Absent', reason: 'Œil absent ou énucléation' },
  { status: 'DAMAGED', label: 'Œil endommagé', shortLabel: 'Endommagé', reason: 'Traumatisme ou pathologie — capture impossible' },
];

export const IRIS_ENROLLMENT_SCENARIOS: { id: string; title: string; hint: string }[] = [
  { id: 'both', title: 'Standard', hint: 'Capturer les 2 yeux (recommandé)' },
  { id: 'one', title: 'Un seul œil', hint: 'Capture d’un œil + signalement sur l’autre' },
  { id: 'none', title: 'Aucune capture', hint: 'Les 2 yeux signalés (aveugle, absent, etc.)' },
  { id: 'retry', title: 'Reprise', hint: 'Échec sur un œil → capturer à nouveau ou signaler' },
];

export function isEyeUnavailable(status: EyeStatus): boolean {
  return status === 'BLIND' || status === 'MISSING' || status === 'DAMAGED';
}

export function isEyeResolved(status: EyeStatus): boolean {
  return status === 'CAPTURED' || isEyeUnavailable(status);
}

export function isIrisEnrollmentComplete(eyes: IrisCapture[]): boolean {
  if (eyes.length < 2) return false;
  return eyes.every((e) => isEyeResolved(e.status));
}

export function countCapturedEyes(eyes: IrisCapture[]): number {
  return eyes.filter((e) => e.status === 'CAPTURED').length;
}

export function countResolvedEyes(eyes: IrisCapture[]): number {
  return eyes.filter((e) => isEyeResolved(e.status)).length;
}

export function detectIrisScenario(eyes: IrisCapture[]): string {
  const captured = countCapturedEyes(eyes);
  const unavailable = eyes.filter((e) => isEyeUnavailable(e.status)).length;
  if (captured === 2) return 'both';
  if (captured === 1 && unavailable === 1) return 'one';
  if (captured === 0 && unavailable === 2) return 'none';
  if (eyes.some((e) => e.status === 'FAILED')) return 'retry';
  return 'progress';
}

export function irisProgressLabel(eyes: IrisCapture[]): string {
  const resolved = countResolvedEyes(eyes);
  const captured = countCapturedEyes(eyes);
  const unavailable = eyes.filter((e) => isEyeUnavailable(e.status)).length;
  const failed = eyes.filter((e) => e.status === 'FAILED').length;
  const parts: string[] = [`${resolved}/2 yeux traités`];
  if (captured) parts.push(`${captured} capture(s)`);
  if (unavailable) parts.push(`${unavailable} non capturable(s)`);
  if (failed) parts.push(`${failed} échec(s)`);
  return parts.join(' · ');
}

export function formatIrisSaveMessage(eyes: IrisCapture[]): string {
  const captured = countCapturedEyes(eyes);
  const unavailable = eyes.filter((e) => isEyeUnavailable(e.status));
  if (captured === 2) return 'Iris — 2 yeux capturés';
  if (captured === 1 && unavailable.length === 1) {
    const u = EYE_STATUS_LABELS[unavailable[0].status];
    return `Iris — 1 capture, 1 ${u.toLowerCase()}`;
  }
  if (captured === 0 && unavailable.length === 2) {
    return 'Iris — aucune capture (2 yeux signalés)';
  }
  return `Iris — ${captured} capture(s), ${unavailable.length} signalé(s)`;
}

export function resolveIrisModalityStatus(
  eyes: IrisCapture[]
): 'completed' | 'failed' | 'skipped' {
  if (!isIrisEnrollmentComplete(eyes)) return 'failed';
  if (eyes.some((e) => e.status === 'FAILED')) return 'failed';
  return 'completed';
}

export function irisSummaryForGateway(eyes: IrisCapture[]) {
  return {
    captured: countCapturedEyes(eyes),
    blind: eyes.filter((e) => e.status === 'BLIND').length,
    missing: eyes.filter((e) => e.status === 'MISSING').length,
    damaged: eyes.filter((e) => e.status === 'DAMAGED').length,
    failed: eyes.filter((e) => e.status === 'FAILED').length,
    pending: eyes.filter((e) => e.status === 'PENDING').length,
    scenario: detectIrisScenario(eyes),
  };
}

export function initialIrisEnrollmentState(): IrisCapture[] {
  return [
    { position: 'LEFT', status: 'PENDING' },
    { position: 'RIGHT', status: 'PENDING' },
  ];
}

/** Garantit un tableau de 2 yeux (brouillon session ou données mal formées). */
export function normalizeIrisEnrollmentState(input: unknown): IrisCapture[] {
  const defaults = initialIrisEnrollmentState();
  if (!Array.isArray(input)) {
    if (input && typeof input === 'object') {
      const obj = input as Record<string, IrisCapture>;
      const left = obj.LEFT ?? obj.left;
      const right = obj.RIGHT ?? obj.right;
      if (left || right) {
        return defaults.map((eye) => {
          const from =
            eye.position === 'LEFT'
              ? left
              : eye.position === 'RIGHT'
                ? right
                : undefined;
          return from && typeof from === 'object' && from.position
            ? { ...eye, ...from, position: eye.position }
            : eye;
        });
      }
    }
    return defaults;
  }
  if (input.length === 0) return defaults;
  return defaults.map((eye) => {
    const found = input.find(
      (e) =>
        e &&
        typeof e === 'object' &&
        (e.position === eye.position ||
          (e as { position?: string }).position?.toUpperCase() === eye.position)
    );
    return found ? { ...eye, ...found, position: eye.position } : eye;
  });
}

export function eyePositionLabel(position: EyePosition): string {
  return position === 'LEFT' ? 'Œil gauche' : 'Œil droit';
}
