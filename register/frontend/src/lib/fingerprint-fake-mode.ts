/**
 * Empreintes de démonstration lorsque le lecteur FAP60 n'est pas au poste.
 * Désactiver en production stricte : NEXT_PUBLIC_FINGERPRINT_ALLOW_FAKE=false
 */
export function isFakeFingerprintAllowed(): boolean {
  return process.env.NEXT_PUBLIC_FINGERPRINT_ALLOW_FAKE !== 'false';
}
