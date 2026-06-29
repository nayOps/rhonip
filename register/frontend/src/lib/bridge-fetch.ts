import { fetchTimeoutSignal } from '@/lib/fetch-timeout';

const DIRECT_BRIDGE =
  process.env.NEXT_PUBLIC_DEVICE_BRIDGE_URL || 'http://127.0.0.1:8765';

/** URLs à tenter : proxy Next côté navigateur, puis accès direct (dev local). */
export function bridgeFetchUrls(path: string): string[] {
  const p = path.startsWith('/') ? path.slice(1) : path;
  const direct = DIRECT_BRIDGE.replace(/\/$/, '');
  if (typeof window === 'undefined') {
    return [`${direct}/${p}`];
  }
  return [`/bridge-proxy/${p}`, `${direct}/${p}`];
}

export async function fetchBridgeJson<T>(
  path: string,
  init?: RequestInit,
  timeoutMs = 8000
): Promise<{ ok: boolean; status: number; data: T | null }> {
  for (const url of bridgeFetchUrls(path)) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(url, {
        ...init,
        signal: init?.signal ?? controller.signal,
      });
      let data: T | null = null;
      try {
        data = (await res.json()) as T;
      } catch {
        data = null;
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

/** Retourne la première réponse HTTP reçue (même 4xx), ou null si tout échoue. */
export async function fetchBridgeResponse(
  path: string,
  init?: RequestInit,
  timeoutMs = 8000
): Promise<Response | null> {
  for (const url of bridgeFetchUrls(path)) {
    try {
      const res = await fetch(url, {
        ...init,
        signal: init?.signal ?? fetchTimeoutSignal(timeoutMs),
      });
      return res;
    } catch {
      /* essai URL suivante */
    }
  }
  return null;
}
