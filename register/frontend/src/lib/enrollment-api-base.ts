/** URL publique du gateway (SSR, liens media-proxy absolus). */
export function getEnrollmentGatewayPublicBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001').replace(/\/$/, '');
}

/**
 * URL des appels API enrollment (toujours vers le gateway exposé sur l'hôte).
 * Le proxy Next (/api → enrollment_gateway) échoue dans Docker : Host avec underscore
 * ou localhost:8001 inexistant dans le conteneur frontend.
 */
export function enrollmentApiUrl(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${getEnrollmentGatewayPublicBase()}${normalized}`;
}
