/** Catalogue des strates FGP — affichage accueil & enrôlement */
export interface StratumInfo {
  id: string;
  label: string;
  description: string;
  icon: string;
  /** Couleur d’accent Tailwind (sans préfixe) */
  accent: 'sky' | 'emerald' | 'violet' | 'amber' | 'rose' | 'cyan' | 'indigo' | 'orange' | 'teal' | 'fuchsia' | 'lime' | 'slate';
  layer: number;
}

export const FGP_STRATA_CATALOG: StratumInfo[] = [
  { id: 'ENFANT', label: 'Enfant', description: 'Mineurs — prise en charge spécifique NIN', icon: '👶', accent: 'sky', layer: 1 },
  { id: 'ELEVES', label: 'Élève', description: 'Primaire & secondaire — scolarisation', icon: '🎓', accent: 'emerald', layer: 2 },
  { id: 'ETUDIANT', label: 'Étudiant', description: 'Enseignement supérieur & universités', icon: '📚', accent: 'violet', layer: 2 },
  { id: 'ELECTEUR', label: 'Électeur', description: 'Citoyens majeurs — registre électoral', icon: '🗳️', accent: 'amber', layer: 3 },
  { id: 'FONCTIONNAIRE', label: 'Fonctionnaire', description: 'Agents de l’État & administrations', icon: '🏛️', accent: 'cyan', layer: 3 },
  { id: 'PNC', label: 'PNC', description: 'Police Nationale Congolaise', icon: '👮', accent: 'indigo', layer: 4 },
  { id: 'FARDC', label: 'FARDC', description: 'Forces Armées de la RDC', icon: '🪖', accent: 'rose', layer: 4 },
  { id: 'PRISON', label: 'Détenu', description: 'Établissements pénitentiaires', icon: '🔒', accent: 'orange', layer: 4 },
  { id: 'REFUGIE', label: 'Réfugié', description: 'Protection internationale & asylum', icon: '🛂', accent: 'teal', layer: 5 },
  { id: 'DEPLACE', label: 'Déplacé interne', description: 'Populations déplacées sur le territoire', icon: '🏠', accent: 'fuchsia', layer: 5 },
  { id: 'ETRANGER', label: 'Étranger résident', description: 'Résidents étrangers enregistrés', icon: '🌍', accent: 'lime', layer: 5 },
  { id: 'DIASPORA', label: 'Diaspora', description: 'Congolais à l’étranger — enrôlement dédié', icon: '✈️', accent: 'slate', layer: 5 },
];

export const STRATA_LAYER_LABELS: Record<number, string> = {
  1: 'Première enfance',
  2: 'Éducation',
  3: 'Citoyenneté & service public',
  4: 'Sécurité & justice',
  5: 'Mobilité & situations spéciales',
};
