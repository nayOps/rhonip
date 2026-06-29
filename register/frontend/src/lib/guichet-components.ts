export type ComponentHealthStatus = 'ok' | 'degraded' | 'down' | 'checking';

export interface GuichetComponentCheck {
  id: string;
  label: string;
  description: string;
  endpoint?: string;
  status: ComponentHealthStatus;
  message: string;
  /** Requis pour débloquer « Entrer » */
  required: boolean;
}

export type GuichetComponentDefinition = Omit<GuichetComponentCheck, 'status' | 'message'>;

export const GUICHET_COMPONENT_CATALOG: GuichetComponentDefinition[] = [
  {
    id: 'device-bridge',
    label: 'Device Bridge',
    description: 'Pont matériel (empreintes, iris, caméra, imprimante)',
    endpoint: 'http://127.0.0.1:8765/health',
    required: true,
  },
  {
    id: 'enrollment-gateway',
    label: 'Enrollment Gateway',
    description: 'API session et enrôlement',
    endpoint: 'http://localhost:8001/api/v1/enrolments/health/',
    required: true,
  },
  {
    id: 'fingerprint',
    label: 'Lecteur empreintes FAP60',
    description: 'Capture 10 doigts',
    required: true,
  },
  {
    id: 'iris',
    label: 'Lecteur iris (JD5)',
    description: 'Iris Device Server — JD5 / IRIS-SCANNER',
    endpoint: 'http://127.0.0.1:50219',
    required: true,
  },
  {
    id: 'camera',
    label: 'Caméra / scan GPY',
    description: 'Photo certifiée, documents et webcam ICAO',
    required: true,
  },
  {
    id: 'icao-face',
    label: 'Assistant ICAO (webcam)',
    description: 'Guidage et validation photo sans XHY-D500',
    endpoint: 'http://127.0.0.1:50270/health',
    required: false,
  },
  {
    id: 'printer',
    label: 'Imprimante POS',
    description: 'Ticket récépissé thermique',
    required: false,
  },
];

export function allRequiredComponentsReady(components: GuichetComponentCheck[]): boolean {
  return components
    .filter((c) => c.required)
    .every((c) => c.status === 'ok' || c.status === 'degraded');
}

export function allComponentsOk(components: GuichetComponentCheck[]): boolean {
  return components.every((c) => c.status === 'ok');
}

function def(id: string): GuichetComponentDefinition {
  const found = GUICHET_COMPONENT_CATALOG.find((c) => c.id === id);
  if (!found) throw new Error(`Unknown component: ${id}`);
  return found;
}

export function checkingState(componentId: string): GuichetComponentCheck {
  const d = def(componentId);
  return { ...d, status: 'checking', message: 'Vérification…' };
}

export function resultState(
  componentId: string,
  status: ComponentHealthStatus,
  message: string
): GuichetComponentCheck {
  const d = def(componentId);
  return { ...d, status, message };
}
