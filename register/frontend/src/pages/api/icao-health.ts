import type { NextApiRequest, NextApiResponse } from 'next';

import { fetchTimeoutSignal } from '@/lib/fetch-timeout';

const ICAO_CANDIDATES = [
  process.env.ICAO_FACE_SERVICE_URL,
  process.env.NEXT_PUBLIC_ICAO_FACE_SERVICE_URL,
  'http://127.0.0.1:50270',
  'http://localhost:50270',
].filter((u, i, arr): u is string => !!u && arr.indexOf(u) === i);

/** Sonde ICAO côté serveur Next (évite CORS navigateur). */
export default async function handler(_req: NextApiRequest, res: NextApiResponse) {
  let lastError = 'aucune URL testée';

  for (const base of ICAO_CANDIDATES) {
    const url = `${base.replace(/\/$/, '')}/health`;
    try {
      const upstream = await fetch(url, { signal: fetchTimeoutSignal(6000) });
      const text = await upstream.text();
      if (!upstream.ok) {
        lastError = `HTTP ${upstream.status} sur ${url}`;
        continue;
      }
      res.status(200);
      res.setHeader('Content-Type', upstream.headers.get('content-type') || 'application/json');
      res.send(text);
      return;
    } catch (e) {
      lastError = e instanceof Error ? e.message : String(e);
    }
  }

  res.status(503).json({
    status: 'down',
    message:
      'Service ICAO injoignable — lancez scripts\\start-icao-face-service.cmd (port 50270)',
    detail: lastError,
  });
}
