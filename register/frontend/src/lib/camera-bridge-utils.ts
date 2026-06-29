import type { CameraProbeResult, CameraStatus } from '@/services/camera-api';

/** L'OCX CameraGP refuse HP / Logitech (code -1) — seule la XHY-D500 est certifiée COM. */
export function bridgeComOnlyGenericWebcams(...messages: Array<string | undefined | null>): boolean {
  const text = messages.filter(Boolean).join(' ').toLowerCase();
  if (!text) return false;
  return (
    /non certifié|code -1|pas gpy|non reconnu \(pas gpy\)|modèle non certifié|hp 5mp|hp\d+mp/.test(
      text
    ) || (/périphériques vus/i.test(text) && !/xhy|d500|cameragp/.test(text))
  );
}

export function bridgeComSupportsCertifiedCamera(
  status: CameraStatus | null | undefined,
  probe?: CameraProbeResult | null
): boolean {
  if (!status?.available) return false;
  if (bridgeComOnlyGenericWebcams(status.message, probe?.open?.message)) return false;
  if (probe?.open && !probe.open.success) return false;
  return true;
}

export function formatChromeCameraUnblockSteps(origin?: string): string {
  const site = origin || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000');
  return (
    `1. Ouvrez le guichet sur ${site} (de préférence http://localhost:3000).\n` +
    `2. Chrome → icône cadenas à gauche de l'URL → Caméra → Autoriser.\n` +
    '3. Ou : chrome://settings/content/camera → autorisez ce site.\n' +
    '4. Windows → Paramètres → Confidentialité → Caméra → applications de bureau activées.\n' +
    '5. Fermez Teams/Zoom si la webcam est déjà utilisée, puis rechargez la page (Ctrl+F5).'
  );
}
