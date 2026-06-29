import {
  GUICHET_COMPONENT_CATALOG,
  allComponentsOk,
  allRequiredComponentsReady,
  type ComponentHealthStatus,
  type GuichetComponentCheck,
} from '@/lib/guichet-components';

export type { ComponentHealthStatus, GuichetComponentCheck };
export { allComponentsOk, allRequiredComponentsReady };

/** Simule une sonde (tests / démo sans matériel). */
export async function probeGuichetComponentsMock(): Promise<GuichetComponentCheck[]> {
  const simulateFailure =
    typeof process !== 'undefined' &&
    process.env.NEXT_PUBLIC_MOCK_HEALTH_FAIL === 'true';

  await new Promise((r) => setTimeout(r, 800));

  return GUICHET_COMPONENT_CATALOG.map((c) => {
    const base: GuichetComponentCheck = {
      ...c,
      status: 'ok',
      message: mockOkMessage(c.id),
    };
    if (!simulateFailure) return base;
    if (c.id === 'iris') {
      return {
        ...base,
        status: 'down',
        message: 'Lecteur fermé (errcode=16777231) — mock dégradé',
      };
    }
    if (c.id === 'printer' || c.id === 'icao-face') {
      return { ...base, status: 'degraded', message: 'Optionnel — indisponible (mock)' };
    }
    return base;
  });
}

function mockOkMessage(id: string): string {
  switch (id) {
    case 'device-bridge':
      return 'Bridge actif — modules fingerprint, iris, camera, printer';
    case 'enrollment-gateway':
      return 'Gateway joignable';
    case 'fingerprint':
      return 'Mode fap60 — lecteur prêt';
    case 'iris':
      return 'Serveur HTTP iris — modèle détecté';
    case 'camera':
      return 'Sidecar CameraGP prêt';
    case 'icao-face':
      return 'Service ICAO mock OK';
    case 'printer':
      return 'Sidecar POS prêt (SP-USB1)';
    default:
      return 'OK';
  }
}
