import type { WorkflowStep } from '@/components/forms/EnrollmentWorkflow.types';
import {
  type BaseFormStrata,
  isFiliationSectionVisible,
} from '@/lib/base-enrollment-rules';

export type BaseFormSubTab = 'identite' | 'residence' | 'filiation' | 'situation';

export const SUB_TAB_LABELS: Record<BaseFormSubTab, string> = {
  identite: 'Identité',
  residence: 'Résidence',
  filiation: 'Filiation',
  situation: 'Situation',
};

/** Onglets affichés selon la strate (filiation masqué si non concerné). */
export function getVisibleFormSubTabs(strata: BaseFormStrata | null): BaseFormSubTab[] {
  if (!strata) return [];
  const tabs: BaseFormSubTab[] = ['identite', 'residence'];
  if (isFiliationSectionVisible(strata)) tabs.push('filiation');
  tabs.push('situation');
  return tabs;
}

export const WORKFLOW_STEP_ORDER: WorkflowStep[] = [
  'base',
  'extensions',
  'photo',
  'fingerprints',
  'iris',
  'documents',
  'verification',
  'receipt',
];

export const WORKFLOW_STEP_LABELS: Record<WorkflowStep, string> = {
  base: 'Formulaire de base',
  extensions: 'Extensions strate',
  photo: "Photo d'identité",
  fingerprints: 'Empreintes digitales',
  iris: 'Capture iris',
  documents: 'Documents',
  verification: 'Vérification',
  receipt: 'Récépissé',
};

export function getWorkflowStepIndex(step: WorkflowStep): number {
  return WORKFLOW_STEP_ORDER.indexOf(step);
}

export const ENROLLMENT_STRATA_OPTIONS = [
  { value: 'ENFANT', label: 'Enfant', icon: '👶' },
  { value: 'ELEVES', label: 'Élève', icon: '🎓' },
  { value: 'ELECTEUR', label: 'Électeur', icon: '🗳️' },
  { value: 'FARDC', label: 'Militaire', icon: '🪖' },
  { value: 'PNC', label: 'Policier', icon: '👮' },
  { value: 'PRISON', label: 'Prisonnier', icon: '🔒' },
  { value: 'REFUGIE', label: 'Réfugié', icon: '🛂' },
  { value: 'DEPLACE', label: 'Déplacé', icon: '🏠' },
  { value: 'ETRANGER', label: 'Étranger', icon: '🌍' },
  { value: 'DIASPORA', label: 'Diaspora', icon: '✈️' },
] as const;

/** Conteneur pleine largeur (sans max-width centrée) */
export const ENROLLMENT_SHELL_CLASS = 'w-full px-4 md:px-6';

/** Zone formulaire : colonne flexible au-dessus du footer */
export const ENROLLMENT_FORM_BODY_CLASS =
  'flex-1 w-full min-h-0 flex flex-col py-3';

/** Défilement léger quand le contenu dépasse (filiation, situation, extensions…) */
export const ENROLLMENT_FORM_SCROLL_CLASS =
  'flex-1 min-h-0 overflow-y-auto overscroll-contain pr-1 -mr-1 flex flex-col gap-4 px-2 py-3';

/** Deux blocs côte à côte (Origine | Résidence, Père | Mère, etc.) */
export const ENROLLMENT_SPLIT_CLASS =
  'grid grid-cols-1 lg:grid-cols-2 gap-3 min-h-0 items-start';

/** Panneau secondaire dans un split */
export const ENROLLMENT_PANEL_CLASS =
  'rounded-lg border border-gray-200 bg-gray-50/80 p-3 min-h-0';

export const ENROLLMENT_PANEL_TITLE_CLASS =
  'text-sm font-semibold text-gray-800 mb-2 pb-1 border-b border-gray-200';

/** Grille champs : toujours 2 colonnes (demi-largeur) */
export const ENROLLMENT_FIELD_GRID_CLASS = 'grid grid-cols-2 gap-x-4 gap-y-4';

export const ENROLLMENT_LABEL_CLASS =
  'block text-xs font-medium text-gray-700 mb-1 leading-tight';

export const ENROLLMENT_INPUT_CLASS =
  'w-full px-2.5 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500';

export const ENROLLMENT_TEXTAREA_CLASS =
  'w-full px-2.5 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500 resize-y min-h-[2.5rem]';

/** Section compacte (onglet Situation) */
export const ENROLLMENT_SECTION_CLASS =
  'rounded-lg border border-gray-200 bg-white p-4';

export const ENROLLMENT_SECTION_TITLE_CLASS =
  'text-sm font-semibold text-gray-900 mb-3';
