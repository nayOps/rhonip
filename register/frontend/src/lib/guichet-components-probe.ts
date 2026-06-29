import { describeIrisErrcode } from '@/lib/iris-error-codes';
import {
  GUICHET_COMPONENT_CATALOG,
  checkingState,
  resultState,
  type ComponentHealthStatus,
  type GuichetComponentCheck,
} from '@/lib/guichet-components';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
const ENROLLMENT_HEALTH = `${API_URL}/api/v1/enrolments/health/`;

const PROBE_TIMEOUT_MS = 8000;

/** Navigateur : rewrite Next `/bridge-proxy/*` → Device Bridge (8765). */
function bridgeUrl(path: string): string {
  const p = path.startsWith('/') ? path.slice(1) : path;
  if (typeof window !== 'undefined') {
    return `/bridge-proxy/${p}`;
  }
  const base = process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL || 'http://127.0.0.1:8765';
  return `${base.replace(/\/$/, '')}/${p}`;
}

type BridgeModuleHealth = {
  status?: string;
  message?: string;
  mode?: string;
};

type BridgeHealthBody = {
  status?: string;
  version?: string;
  modules?: Record<string, BridgeModuleHealth>;
};

function bridgeFetchUrls(path: string): string[] {
  const p = path.startsWith('/') ? path.slice(1) : path;
  const direct = (process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL || 'http://127.0.0.1:8765').replace(
    /\/$/,
    ''
  );
  if (typeof window === 'undefined') {
    return [`${direct}/${p}`];
  }
  return [`/bridge-proxy/${p}`, `${direct}/${p}`];
}

async function fetchBridge<T>(path: string, init?: RequestInit, timeoutMs = PROBE_TIMEOUT_MS): Promise<{
  ok: boolean;
  status: number;
  data: T | null;
}> {
  for (const url of bridgeFetchUrls(path)) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(url, { ...init, signal: controller.signal });
      let data: T | null = null;
      try {
        data = (await res.json()) as T;
      } catch {
        data = null;
      }
      if (res.ok && data != null) {
        return { ok: true, status: res.status, data };
      }
      if (res.ok) {
        return { ok: true, status: res.status, data };
      }
    } catch {
      /* essai URL suivante */
    } finally {
      clearTimeout(timer);
    }
  }
  return { ok: false, status: 0, data: null };
}

function mapModuleStatus(raw?: string, optional = false): ComponentHealthStatus {
  if (raw === 'ok') return 'ok';
  if (raw === 'degraded') return 'degraded';
  if (raw === 'unknown') return 'degraded';
  if (raw === 'down' || raw === 'unhealthy') return optional ? 'degraded' : 'down';
  return 'degraded';
}

function mapBridgeGlobalStatus(raw?: string): ComponentHealthStatus {
  if (raw === 'healthy') return 'ok';
  if (raw === 'degraded' || raw === 'unhealthy') return 'degraded';
  return 'down';
}

async function fetchBridgeHealth(): Promise<BridgeHealthBody | null> {
  const { ok, data } = await fetchBridge<BridgeHealthBody>('/health');
  if (!ok || !data) return null;
  return data;
}

async function probeDeviceBridge(bridgeHealth: BridgeHealthBody | null): Promise<GuichetComponentCheck> {
  if (!bridgeHealth) {
    return resultState(
      'device-bridge',
      'down',
      'Device Bridge injoignable (8765) — lancez start-device-bridge.cmd'
    );
  }
  const status = mapBridgeGlobalStatus(bridgeHealth.status);
  const modules = bridgeHealth.modules ?? {};
  const parts = Object.entries(modules).map(([k, m]) => `${k}:${m.status ?? '?'}`);
  const version = bridgeHealth.version ? ` v${bridgeHealth.version}` : '';
  const summary = parts.length > 0 ? parts.join(', ') : 'Bridge joignable';
  const note =
    bridgeHealth.status === 'unhealthy'
      ? ' — au moins un module en panne (souvent iris)'
      : '';
  return resultState('device-bridge', status, `${summary}${version}${note}`);
}

async function probeEnrollmentGateway(): Promise<GuichetComponentCheck> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), PROBE_TIMEOUT_MS);
  try {
    const res = await fetch(ENROLLMENT_HEALTH, { signal: controller.signal });
    clearTimeout(timer);

    if (res.status >= 500) {
      return resultState(
        'enrollment-gateway',
        'degraded',
        `Gateway HTTP ${res.status} — redémarrez enrollment_gateway`
      );
    }

    if (!res.ok) {
      return resultState(
        'enrollment-gateway',
        res.status === 401 ? 'degraded' : 'down',
        `Gateway HTTP ${res.status} — port 8001`
      );
    }

    const data = (await res.json()) as { status?: string; service?: string };
    if (data.status === 'healthy') {
      return resultState(
        'enrollment-gateway',
        'ok',
        data.service ? `${data.service} — joignable` : 'Gateway joignable'
      );
    }
    return resultState('enrollment-gateway', 'degraded', `Réponse : ${data.status ?? 'inconnue'}`);
  } catch (e) {
    clearTimeout(timer);
    return resultState(
      'enrollment-gateway',
      'down',
      e instanceof Error ? e.message : 'Enrollment Gateway injoignable (8001)'
    );
  }
}

function probeFingerprintFromBridge(
  modules: Record<string, BridgeModuleHealth>
): GuichetComponentCheck {
  const mod = modules.fingerprint;
  if (!mod) {
    return resultState('fingerprint', 'down', 'Module empreintes absent du bridge');
  }
  return resultState(
    'fingerprint',
    mapModuleStatus(mod.status),
    mod.message?.trim() || mod.mode || 'Empreintes'
  );
}

async function probeIris(modules: Record<string, BridgeModuleHealth>): Promise<GuichetComponentCheck> {
  const mod = modules.iris;
  const { data: statusRaw } = await fetchBridge<Record<string, unknown>>(
    '/api/v1/devices/iris/status',
    undefined,
    12_000
  );

  if (statusRaw) {
    const available = Boolean(statusRaw.available ?? statusRaw.Available);
    const message =
      (typeof statusRaw.message === 'string' && statusRaw.message) ||
      (typeof statusRaw.Message === 'string' && statusRaw.Message) ||
      mod?.message ||
      'Iris';
    const errcode =
      typeof statusRaw.errcode === 'number'
        ? statusRaw.errcode
        : typeof statusRaw.Errcode === 'number'
          ? (statusRaw.Errcode as number)
          : undefined;

    const serverPort =
      typeof statusRaw.server_port === 'number'
        ? statusRaw.server_port
        : typeof statusRaw.serverPort === 'number'
          ? (statusRaw.serverPort as number)
          : 50219;
    const deviceModel =
      typeof statusRaw.device_model === 'string'
        ? statusRaw.device_model
        : typeof statusRaw.deviceModel === 'string'
          ? (statusRaw.deviceModel as string)
          : '';

    if (available) {
      const modelSuffix = deviceModel ? ` — ${deviceModel}` : '';
      return resultState('iris', 'ok', `${message}${modelSuffix}`);
    }

    const hint =
      errcode != null && errcode !== 0 && !message.includes('Ouvrir lecteur')
        ? describeIrisErrcode(errcode, message)
        : message;
    const httpDown = /IrisDeviceServer arrêté|aucun HTTP|injoignable|start-server/i.test(message);
    const modelEmpty = /model vide|non détecté/i.test(message);
    const httpUp = !httpDown && (mod?.status === 'ok' || /http actif/i.test(message));
    const readerLabel = deviceModel ? `lecteur ${deviceModel}` : 'lecteur iris (JD5)';
    const detail = modelEmpty
      ? `${hint} (le bip/LED du lecteur peut quand même s’allumer ; il faut le serveur en admin.)`
      : httpUp
        ? `Serveur HTTP OK (port ${serverPort}) — ${readerLabel} : ${hint}`
        : hint;
    return resultState('iris', 'degraded', detail);
  }

  if (mod?.status === 'ok') {
    return resultState('iris', 'ok', mod.message || 'Lecteur iris prêt');
  }

  return resultState(
    'iris',
    'degraded',
    mod?.message ||
      'Iris Device Server inactif — lancez IrisDeviceServer.exe (50218/50219) depuis iris\\bin'
  );
}

async function probeCamera(modules: Record<string, BridgeModuleHealth>): Promise<GuichetComponentCheck> {
  const mod = modules.camera;
  const { data: cam } = await fetchBridge<Record<string, unknown>>(
    '/api/v1/devices/camera/status'
  );

  const camAvailable = Boolean(cam?.available ?? cam?.Available);
  const camMessage =
    (typeof cam?.message === 'string' && cam.message) ||
    (typeof cam?.Message === 'string' && cam.Message) ||
    mod?.message ||
    '';

  if (mod?.status === 'ok' || camAvailable) {
    const count = cam?.device_count ?? cam?.deviceCount;
    const detail =
      typeof count === 'number'
        ? `${count} caméra(s) détectée(s) — ${camMessage || mod?.message || 'GPY COM'}`
        : camMessage || mod?.message || 'Caméra GPY prête';
    return resultState('camera', 'ok', detail);
  }

  const { data: gpy } = await fetchBridge<Record<string, unknown>>(
    '/api/v1/devices/camera/gpy-status'
  );
  if (Boolean(gpy?.available ?? gpy?.Available)) {
    return resultState(
      'camera',
      'degraded',
      (typeof gpy?.message === 'string' && gpy.message) || 'GPY — statut partiel'
    );
  }

  return resultState(
    'camera',
    'degraded',
    mod?.message || camMessage || 'Caméra — vérifiez GPYScan ou Device Bridge'
  );
}

async function probePrinter(modules: Record<string, BridgeModuleHealth>): Promise<GuichetComponentCheck> {
  const mod = modules.print ?? modules.printer;
  const { data: prn } = await fetchBridge<Record<string, unknown>>(
    '/api/v1/devices/printer/status'
  );

  const available = Boolean(prn?.available ?? prn?.Available);
  const message =
    (typeof prn?.message === 'string' && prn.message) ||
    (typeof prn?.Message === 'string' && prn.Message) ||
    mod?.message ||
    '';

  if (mod?.status === 'ok' || available) {
    const open = Boolean(prn?.open ?? prn?.Open);
    const note = open ? 'ouverte' : 'SDK prêt (ouvrir avant impression)';
    return resultState(
      'printer',
      'ok',
      message ? `${message} — ${note}` : `POS SDK — ${note}`
    );
  }

  return resultState(
    'printer',
    'degraded',
    message || mod?.message || 'Imprimante optionnelle — sidecar POS'
  );
}

async function probeIcaoFace(): Promise<GuichetComponentCheck> {
  const { probeIcaoFaceService, getResolvedIcaoBaseUrl, resolveIcaoBaseUrl } =
    await import('@/services/icao-face-api');
  try {
    const ok = await probeIcaoFaceService();
    if (ok) {
      const base = getResolvedIcaoBaseUrl() ?? (await resolveIcaoBaseUrl());
      const port = base ? new URL(base).port : '50270';
      return resultState('icao-face', 'ok', `Service ICAO actif (port ${port})`);
    }
  } catch {
    /* ignore */
  }
  return resultState(
    'icao-face',
    'degraded',
    'Service ICAO arrêté — lancez scripts\\start-icao-face-service.cmd (port 50270), puis Actualiser'
  );
}

/** Sonde réelle — alignée sur GET /health et routes du Device Bridge. */
export async function probeGuichetComponents(): Promise<GuichetComponentCheck[]> {
  const initial = GUICHET_COMPONENT_CATALOG.map((c) => checkingState(c.id));

  const bridgeHealth = await fetchBridgeHealth();
  const modules = bridgeHealth?.modules ?? {};
  const bridgeReachable = bridgeHealth != null;

  const [deviceBridge, gateway, fingerprint, iris, camera, icaoFace, printer] =
    await Promise.all([
      probeDeviceBridge(bridgeHealth),
      probeEnrollmentGateway(),
      bridgeReachable
        ? Promise.resolve(probeFingerprintFromBridge(modules))
        : resultState('fingerprint', 'down', 'Device Bridge requis'),
      bridgeReachable
        ? probeIris(modules)
        : resultState('iris', 'degraded', 'Device Bridge requis pour iris'),
      bridgeReachable
        ? probeCamera(modules)
        : resultState('camera', 'degraded', 'Device Bridge requis pour caméra'),
      probeIcaoFace(),
      bridgeReachable
        ? probePrinter(modules)
        : resultState('printer', 'degraded', 'Device Bridge requis pour imprimante'),
    ]);

  const byId: Record<string, GuichetComponentCheck> = {
    'device-bridge': deviceBridge,
    'enrollment-gateway': gateway,
    fingerprint,
    iris,
    camera,
    'icao-face': icaoFace,
    printer,
  };

  return initial.map((c) => byId[c.id] ?? c);
}
