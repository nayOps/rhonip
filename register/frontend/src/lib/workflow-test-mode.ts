/**
 * Permet de passer les étapes sans capture complète (tests scan, imprimante, etc.).
 * Désactiver en production : NEXT_PUBLIC_WORKFLOW_ALLOW_SKIP=false
 */
export function isWorkflowSkipEnabled(): boolean {
  return process.env.NEXT_PUBLIC_WORKFLOW_ALLOW_SKIP !== 'false';
}
