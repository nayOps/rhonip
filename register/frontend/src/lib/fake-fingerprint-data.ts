import { FingerPosition, FingerprintCapture } from '@/types';

const ALL_POSITIONS: FingerPosition[] = [
  'LEFT_LITTLE',
  'LEFT_RING',
  'LEFT_MIDDLE',
  'LEFT_INDEX',
  'LEFT_THUMB',
  'RIGHT_THUMB',
  'RIGHT_INDEX',
  'RIGHT_MIDDLE',
  'RIGHT_RING',
  'RIGHT_LITTLE',
];

/** Miniature SVG (empreinte stylisée) — distincte des captures réelles. */
const FAKE_FP_IMAGE =
  'data:image/svg+xml;base64,' +
  btoa(
    `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="160" viewBox="0 0 120 160">
      <rect width="120" height="160" fill="#e8eef5"/>
      <ellipse cx="60" cy="72" rx="28" ry="38" fill="none" stroke="#64748b" stroke-width="2"/>
      <path d="M60 34 Q45 50 42 72 Q40 95 60 110 Q80 95 78 72 Q75 50 60 34" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
      <text x="60" y="145" text-anchor="middle" font-size="9" fill="#64748b" font-family="sans-serif">FAKE DEV</text>
    </svg>`
  );

/** Gabarit factice (non utilisable en ABIS prod). */
export const FAKE_FINGERPRINT_TEMPLATE_B64 = btoa('FGP_FAKE_FINGERPRINT_TEMPLATE_V1');

/**
 * Jeu complet 4+4+2 pour tests sans lecteur.
 * Au bureau, brancher le FAP60 et capturer normalement — les vraies empreintes remplacent ce jeu.
 */
export function buildFakeFingerprints(): FingerprintCapture[] {
  const ts = new Date().toISOString();
  return ALL_POSITIONS.map((position) => ({
    position,
    status: 'CAPTURED' as const,
    quality: 88,
    nfiq: 2,
    image: FAKE_FP_IMAGE,
    templateBase64: FAKE_FINGERPRINT_TEMPLATE_B64,
    formatId: 0,
    timestamp: ts,
    reason: 'FAKE_DEV',
  }));
}
