import type { WorkflowStep } from '@/components/forms/EnrollmentWorkflow.types';

/** Étapes réellement parcourues au guichet RH (photo uniquement). */
export const RH_ACTIVE_WORKFLOW_STEPS: WorkflowStep[] = [
  'employee',
  'photo',
  'verification',
  'receipt',
];

/** Étapes masquées (gérées ailleurs, ex. tablette Morpho). */
export const RH_HIDDEN_WORKFLOW_STEPS: WorkflowStep[] = ['fingerprints'];

/** Étapes visibles mais grisées / non accessibles. */
export const RH_DISABLED_WORKFLOW_STEPS: WorkflowStep[] = ['iris', 'documents'];

/** Barre de progression : empreintes exclues, iris/documents grisés. */
export const RH_PROGRESS_WORKFLOW_STEPS: WorkflowStep[] = [
  'employee',
  'photo',
  'iris',
  'documents',
  'verification',
  'receipt',
];

export const RH_PROGRESS_STEP_LABELS: Record<WorkflowStep, string> = {
  employee: 'Fiche employé',
  photo: "Photo d'identité",
  fingerprints: 'Empreintes digitales',
  iris: 'Capture iris',
  documents: 'Documents',
  verification: 'Vérification',
  receipt: 'Récépissé',
};

export const RH_DISABLED_STEP_HINTS: Partial<Record<WorkflowStep, string>> = {
  iris: 'Hors guichet',
  documents: 'Hors guichet',
};

export function isRhHiddenWorkflowStep(step: WorkflowStep): boolean {
  return RH_HIDDEN_WORKFLOW_STEPS.includes(step);
}

export function isRhDisabledWorkflowStep(step: WorkflowStep): boolean {
  return RH_DISABLED_WORKFLOW_STEPS.includes(step);
}

export function getRhActiveStepIndex(step: WorkflowStep): number {
  return RH_ACTIVE_WORKFLOW_STEPS.indexOf(step);
}

export function getRhProgressStepIndex(step: WorkflowStep): number {
  return RH_PROGRESS_WORKFLOW_STEPS.indexOf(step);
}

export function getNextRhActiveStep(step: WorkflowStep): WorkflowStep | null {
  const index = getRhActiveStepIndex(step);
  if (index < 0 || index >= RH_ACTIVE_WORKFLOW_STEPS.length - 1) return null;
  return RH_ACTIVE_WORKFLOW_STEPS[index + 1];
}

export function getPreviousRhActiveStep(step: WorkflowStep): WorkflowStep | null {
  const index = getRhActiveStepIndex(step);
  if (index <= 0) return null;
  return RH_ACTIVE_WORKFLOW_STEPS[index - 1];
}

export function visitedRhActiveStepsUpTo(step: WorkflowStep): WorkflowStep[] {
  const index = getRhActiveStepIndex(step);
  const end = index >= 0 ? index + 1 : 1;
  return RH_ACTIVE_WORKFLOW_STEPS.slice(0, end);
}
