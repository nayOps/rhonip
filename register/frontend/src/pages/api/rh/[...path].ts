import type { NextApiRequest, NextApiResponse } from 'next';

const GUICHET_KEY =
  process.env.NEXT_PUBLIC_GUICHET_INTERNAL_API_KEY || 'fgp_guichet_internal_dev';

function rhBaseCandidates(): string[] {
  const fromEnv = [
    process.env.RH_INTERNAL_API_URL,
    process.env.RH_FALLBACK_API_URL,
    process.env.NEXT_PUBLIC_RH_API_URL,
  ];
  const defaults = [
    'http://server:8000',
    'http://rh_server:8000',
    'http://host.docker.internal:8100',
    'http://127.0.0.1:8100',
    'http://localhost:8100',
  ];
  const seen = new Set<string>();
  const out: string[] = [];
  for (const raw of [...fromEnv, ...defaults]) {
    if (!raw?.trim()) continue;
    const base = raw.trim().replace(/\/$/, '');
    if (seen.has(base)) continue;
    seen.add(base);
    out.push(base);
  }
  return out;
}

function normalizeDjangoPath(path: string): string {
  const qIndex = path.indexOf('?');
  const pathname = qIndex >= 0 ? path.slice(0, qIndex) : path;
  const query = qIndex >= 0 ? path.slice(qIndex) : '';
  if (!pathname || pathname === '/') return path;
  if (pathname.endsWith('/')) return path;
  return `${pathname}/${query}`;
}

function hostHeaderForBase(base: string): string {
  try {
    return new URL(base).host;
  } catch {
    return 'localhost';
  }
}

async function fetchRhUpstream(
  targetUrl: string,
  init: RequestInit
): Promise<Response> {
  let lastError: Error | null = null;
  const djangoPath = normalizeDjangoPath(targetUrl);

  for (const base of rhBaseCandidates()) {
    const url = `${base}${djangoPath.startsWith('/') ? djangoPath : `/${djangoPath}`}`;
    const headers = new Headers(init.headers as HeadersInit);
    headers.set('Host', hostHeaderForBase(base));
    try {
      const res = await fetch(url, { ...init, headers, redirect: 'follow' });
      if (res.status >= 500) {
        lastError = new Error(`HTTP ${res.status} depuis ${base}`);
        continue;
      }
      return res;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
    }
  }

  throw lastError || new Error('Aucun serveur RH accessible');
}

export default async function rhProxyHandler(req: NextApiRequest, res: NextApiResponse) {
  const method = req.method || 'GET';
  if (!['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD'].includes(method)) {
    res.setHeader('Allow', 'GET, POST, PUT, PATCH, DELETE, HEAD');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const segments = req.query.path;
  const pathPart = Array.isArray(segments) ? segments.join('/') : segments || '';
  const query = req.url?.includes('?') ? req.url.substring(req.url.indexOf('?')) : '';
  const targetPath = `/${pathPart}${query}`;

  const headers: Record<string, string> = {
    'X-Guichet-Internal-Key': GUICHET_KEY,
  };
  if (req.headers['content-type']) {
    headers['Content-Type'] = req.headers['content-type'] as string;
  }

  try {
    const upstream = await fetchRhUpstream(targetPath, {
      method,
      headers,
      body:
        !['GET', 'HEAD'].includes(method)
          ? typeof req.body === 'string'
            ? req.body
            : JSON.stringify(req.body)
          : undefined,
    });

    const contentType = upstream.headers.get('content-type');
    if (contentType) res.setHeader('Content-Type', contentType);

    const text = await upstream.text();
    return res.status(upstream.status).send(text);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    return res.status(502).json({
      error: 'Connexion au service RH impossible',
      detail,
      hint: 'Démarrez rh_server : docker compose --profile rh up -d rh_server',
    });
  }
}

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
};
