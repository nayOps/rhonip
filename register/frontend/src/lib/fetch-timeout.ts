/** Signal fetch compatible Node 16 / Edge / vieux navigateurs (pas AbortSignal.timeout). */
export function fetchTimeoutSignal(ms: number): AbortSignal {
  if (typeof AbortSignal !== 'undefined' && 'timeout' in AbortSignal) {
    try {
      return AbortSignal.timeout(ms);
    } catch {
      /* fallback */
    }
  }
  const controller = new AbortController();
  setTimeout(() => controller.abort(), ms);
  return controller.signal;
}
