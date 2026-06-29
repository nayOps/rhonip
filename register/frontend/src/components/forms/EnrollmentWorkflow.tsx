'use client';

import React, { useEffect, useState } from 'react';
import {
  createGuichetEnrollmentSession,
  getEnrollmentSessionStatus,
  submitEnrollmentSession,
  updateEnrollmentSessionEmployee,
} from '@/services/enrollment-session-api';
import EmployeeEnrollmentForm from './EmployeeEnrollmentForm';
import type { EmployeeFormData } from '@/types/employee';
import PhotoCapture, { PhotoData } from '../biometrics/PhotoCapture';
import VerificationMatching from '../biometrics/VerificationMatching';
import EnrollmentReceipt from '../biometrics/EnrollmentReceipt';
import {
  FingerprintCapture as FingerprintData,
  IrisCapture as IrisData,
  ScannedDocument,
} from '@/types';
import type { WorkflowStep } from './EnrollmentWorkflow.types';
import EnrollmentMainStepper from '@/components/enrollment/EnrollmentMainStepper';
import EnrollmentLegacyProgress from '@/components/enrollment/EnrollmentLegacyProgress';
import { WORKFLOW_DRAFT_STORAGE_KEY, readEnrollmentDraft } from '@/lib/enrollment-draft';
import type { EnrollmentEditMode } from '@/services/enrollment-session-api';
import { visitedStepsUpTo } from '@/lib/enrollment-workflow-mappers';
import {
  RH_ACTIVE_WORKFLOW_STEPS,
  RH_PROGRESS_STEP_LABELS,
  getNextRhActiveStep,
  getPreviousRhActiveStep,
  isRhDisabledWorkflowStep,
  isRhHiddenWorkflowStep,
} from '@/lib/rh-guichet-workflow';

function StepPane({
  active,
  children,
}: {
  active: boolean;
  children: React.ReactNode;
}) {
  if (!active) {
    return <div className="hidden" aria-hidden>{children}</div>;
  }
  return <>{children}</>;
}

const FORM_PHASE_STEPS: WorkflowStep[] = ['employee'];
const BIOMETRIC_PHASE_STEPS: WorkflowStep[] = [
  'photo',
  'verification',
  'receipt',
];

function isFormPhase(step: WorkflowStep): boolean {
  return FORM_PHASE_STEPS.includes(step);
}

function isBiometricPhase(step: WorkflowStep): boolean {
  return BIOMETRIC_PHASE_STEPS.includes(step);
}

const STEP_LABELS = RH_PROGRESS_STEP_LABELS;

const STEP_ORDER = RH_ACTIVE_WORKFLOW_STEPS;

function normalizeRestoredStep(step: WorkflowStep | undefined): WorkflowStep {
  if (!step) return 'employee';
  if (isRhHiddenWorkflowStep(step)) return 'verification';
  if (isRhDisabledWorkflowStep(step)) return 'verification';
  return STEP_ORDER.includes(step) ? step : 'employee';
}

function initialWorkflowState() {
  const draft = readEnrollmentDraft();
  const currentStep = normalizeRestoredStep(draft?.currentStep as WorkflowStep | undefined);
  const visited =
    Array.isArray(draft?.visitedSteps) && draft.visitedSteps.length > 0
      ? draft.visitedSteps
          .map((s) => normalizeRestoredStep(s as WorkflowStep))
          .filter((s): s is WorkflowStep => STEP_ORDER.includes(s))
      : visitedStepsUpTo(currentStep);

  return {
    currentStep,
    visitedSteps: new Set<WorkflowStep>(visited),
    employeeData: (draft?.employeeData as EmployeeFormData | null) ?? null,
    photo: (draft?.photo as PhotoData | null) ?? null,
    fingerprints: (draft?.fingerprints as FingerprintData[]) ?? [],
    iris: [],
    documents: (draft?.documents as ScannedDocument[]) ?? [],
    enrollmentId: typeof draft?.enrollmentId === 'string' ? draft.enrollmentId : '',
    gatewaySessionId: typeof draft?.gatewaySessionId === 'string' ? draft.gatewaySessionId : '',
    sessionInitError:
      typeof draft?.sessionInitError === 'string' || draft?.sessionInitError === null
        ? (draft?.sessionInitError ?? null)
        : null,
    verificationError:
      typeof draft?.verificationError === 'string' || draft?.verificationError === null
        ? (draft?.verificationError ?? null)
        : null,
    editMode: (draft?.editMode as EnrollmentEditMode | null | undefined) ?? null,
  };
}

interface EnrollmentWorkflowProps {
  onCancelEnrollment?: () => void;
}

interface EnrollmentWorkflowDraft {
  currentStep: WorkflowStep;
  visitedSteps?: WorkflowStep[];
  employeeData: EmployeeFormData | null;
  photo: PhotoData | null;
  fingerprints: FingerprintData[];
  iris: IrisData[];
  documents: ScannedDocument[];
  enrollmentId: string;
  gatewaySessionId: string;
  sessionInitError: string | null;
  verificationError: string | null;
  editMode: EnrollmentEditMode | null;
}

export default function EnrollmentWorkflow({ onCancelEnrollment }: EnrollmentWorkflowProps) {
  const [boot] = useState(initialWorkflowState);
  const [currentStep, setCurrentStep] = useState<WorkflowStep>(boot.currentStep);
  const [visitedSteps, setVisitedSteps] = useState<Set<WorkflowStep>>(boot.visitedSteps);
  const [employeeData, setEmployeeData] = useState<EmployeeFormData | null>(boot.employeeData);
  const [photo, setPhoto] = useState<PhotoData | null>(boot.photo);
  const [fingerprints, setFingerprints] = useState<FingerprintData[]>(boot.fingerprints);
  const [iris, setIris] = useState<IrisData[]>(boot.iris);
  const [documents, setDocuments] = useState<ScannedDocument[]>(boot.documents);
  const [enrollmentId, setEnrollmentId] = useState<string>(boot.enrollmentId);
  const [gatewaySessionId, setGatewaySessionId] = useState<string>(boot.gatewaySessionId);
  const [sessionInitError, setSessionInitError] = useState<string | null>(boot.sessionInitError);
  const [verificationError, setVerificationError] = useState<string | null>(boot.verificationError);
  const [editMode, setEditMode] = useState<EnrollmentEditMode | null>(boot.editMode);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const draft = readEnrollmentDraft();
    if (!draft) return;
    if (draft.currentStep) {
      const restoredStep = normalizeRestoredStep(draft.currentStep as WorkflowStep);
      setCurrentStep(restoredStep);
      const restored =
        Array.isArray(draft.visitedSteps) && draft.visitedSteps.length > 0
          ? draft.visitedSteps.filter((s): s is WorkflowStep => STEP_ORDER.includes(s))
          : visitedStepsUpTo(restoredStep);
      setVisitedSteps(new Set(restored));
    }
    if (draft.employeeData) {
      setEmployeeData(draft.employeeData as EmployeeFormData);
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const draft: EnrollmentWorkflowDraft = {
      currentStep,
      visitedSteps: Array.from(visitedSteps),
      employeeData,
      photo,
      fingerprints,
      iris,
      documents,
      enrollmentId,
      gatewaySessionId,
      sessionInitError,
      verificationError,
      editMode,
    };
    try {
      window.sessionStorage.setItem(WORKFLOW_DRAFT_STORAGE_KEY, JSON.stringify(draft));
    } catch {
      // Ignore quota/storage errors. Workflow must continue in-memory.
    }
  }, [
    currentStep,
    visitedSteps,
    employeeData,
    photo,
    fingerprints,
    iris,
    documents,
    enrollmentId,
    gatewaySessionId,
    sessionInitError,
    verificationError,
    editMode,
  ]);

  useEffect(() => {
    setVisitedSteps((prev) => {
      if (prev.has(currentStep)) return prev;
      const next = new Set(prev);
      next.add(currentStep);
      return next;
    });
  }, [currentStep]);

  const goToNextStep = () => {
    const next = getNextRhActiveStep(currentStep);
    if (next) setCurrentStep(next);
  };

  const goToPreviousStep = () => {
    const prev = getPreviousRhActiveStep(currentStep);
    if (prev) setCurrentStep(prev);
  };

  const handleEmployeeFormComplete = async (data: EmployeeFormData) => {
    setEmployeeData(data);
    if (gatewaySessionId) {
      try {
        setSessionInitError(null);
        await updateEnrollmentSessionEmployee(gatewaySessionId, data);
      } catch (e) {
        setSessionInitError(e instanceof Error ? e.message : 'Mise à jour fiche agent échouée');
        return;
      }
    }
    goToNextStep();
  };

  const handlePhotoComplete = (photoData: PhotoData) => {
    setPhoto(photoData);
    goToNextStep();
  };

  useEffect(() => {
    if (currentStep !== 'photo' || !employeeData || gatewaySessionId || editMode) return;
    let cancelled = false;
    (async () => {
      try {
        setSessionInitError(null);
        const id = await createGuichetEnrollmentSession({
          employeeData,
          photo: null,
        });
        if (!cancelled) setGatewaySessionId(id);
      } catch (e) {
        if (!cancelled) {
          setSessionInitError(e instanceof Error ? e.message : 'Session gateway indisponible');
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [currentStep, employeeData, gatewaySessionId, editMode]);

  const ensureGatewaySession = async (): Promise<string> => {
    if (gatewaySessionId) {
      if (employeeData) {
        await updateEnrollmentSessionEmployee(gatewaySessionId, employeeData);
      }
      return gatewaySessionId;
    }
    if (!employeeData) throw new Error('Fiche employé requise.');
    const id = await createGuichetEnrollmentSession({ employeeData, photo });
    setGatewaySessionId(id);
    setSessionInitError(null);
    return id;
  };

  const handleVerificationComplete = async () => {
    setVerificationError(null);
    if (gatewaySessionId) {
      try {
        await submitEnrollmentSession(gatewaySessionId);
        let finalStatus: string | null = null;
        let finalError: string | null = null;
        for (let i = 0; i < 12; i += 1) {
          // Attendre le worker async
          await new Promise((resolve) => setTimeout(resolve, 1200));
          const s = await getEnrollmentSessionStatus(gatewaySessionId);
          if (s.status === 'COMPLETED') {
            finalStatus = 'COMPLETED';
            break;
          }
          if (s.status === 'FAILED') {
            finalStatus = 'FAILED';
            finalError = s.error_message || null;
            break;
          }
        }
        if (finalStatus === 'FAILED') {
          const msg = String(finalError || '').toLowerCase();
          const isPhoneFormatIssue =
            msg.includes('telephone') ||
            msg.includes('téléphone') ||
            msg.includes('+243');
          if (!isPhoneFormatIssue) {
            setVerificationError(
              finalError || "Doublon détecté pendant la vérification biométrique. Veuillez vérifier l'identité."
            );
            return;
          }
        }
      } catch {
        setVerificationError(
          'La vérification finale n’a pas pu être confirmée. Vérifiez la connexion backend puis réessayez.'
        );
        return;
      }
      setEnrollmentId(gatewaySessionId);
    } else {
      const id = `ONIP-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
      setEnrollmentId(id);
    }
    goToNextStep();
  };

  const handleNewEnrollment = () => {
    setCurrentStep('employee');
    setVisitedSteps(new Set(['employee']));
    setEmployeeData(null);
    setPhoto(null);
    setFingerprints([]);
    setIris([]);
    setDocuments([]);
    setEnrollmentId('');
    setGatewaySessionId('');
    setSessionInitError(null);
    setVerificationError(null);
    setEditMode(null);
    if (typeof window !== 'undefined') {
      window.sessionStorage.removeItem(WORKFLOW_DRAFT_STORAGE_KEY);
    }
  };

  return (
    <div
      className={`flex flex-col flex-1 min-h-0 w-full bg-gray-50 ${
        isFormPhase(currentStep) || currentStep === 'photo' ? 'overflow-hidden' : ''
      }`}
    >
      {editMode && (
        <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-sm text-amber-950 shrink-0">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <span>
              Modification en cours
              {employeeData?.registration_number ? (
                <> — matricule <strong className="font-mono">{employeeData.registration_number}</strong></>
              ) : null}
              {gatewaySessionId ? (
                <> — session <span className="font-mono text-xs">{gatewaySessionId}</span></>
              ) : null}
            </span>
            <div className="flex flex-wrap gap-1">
              {STEP_ORDER.filter((step) => visitedSteps.has(step)).map((step) => (
                <button
                  key={step}
                  type="button"
                  onClick={() => setCurrentStep(step)}
                  className={`px-2 py-0.5 rounded text-xs border ${
                    currentStep === step
                      ? 'bg-amber-200 border-amber-400 font-semibold'
                      : 'bg-white border-amber-300 hover:bg-amber-100'
                  }`}
                >
                  {STEP_LABELS[step]}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {isFormPhase(currentStep) && <EnrollmentMainStepper currentStep={currentStep} />}
      {isBiometricPhase(currentStep) && (
        <EnrollmentLegacyProgress
          currentStep={currentStep}
          compact={currentStep === 'photo'}
          allowNavigation={!!editMode}
          visitedSteps={visitedSteps}
          onStepSelect={(step) => {
            if (isRhDisabledWorkflowStep(step) || isRhHiddenWorkflowStep(step)) return;
            setCurrentStep(step);
          }}
        />
      )}

      {isFormPhase(currentStep) && employeeData?.registration_number && (
        <div className="px-4 py-2 text-sm text-gray-600 bg-white border-b">
          Matricule : <strong>{employeeData.registration_number}</strong>
        </div>
      )}

      <div
        className={
          isFormPhase(currentStep) || currentStep === 'photo'
            ? 'flex flex-col flex-1 min-h-0 w-full overflow-hidden'
            : 'flex-1 overflow-y-auto w-full'
        }
      >
        <div
          className={
            currentStep === 'photo'
              ? 'flex flex-col flex-1 min-h-0 w-full max-w-7xl mx-auto px-3 md:px-4 py-1'
              : isBiometricPhase(currentStep)
                ? 'p-4 md:p-6 max-w-7xl mx-auto w-full'
                : 'flex flex-col flex-1 min-h-0 w-full'
          }
        >
        {visitedSteps.has('employee') && (
          <StepPane active={currentStep === 'employee'}>
            <EmployeeEnrollmentForm
              key={employeeData?.registration_number || 'new-agent'}
              initialData={employeeData}
              onNext={handleEmployeeFormComplete}
              onCancel={onCancelEnrollment}
            />
          </StepPane>
        )}

        {visitedSteps.has('photo') && (
          <StepPane active={currentStep === 'photo'}>
            <PhotoCapture
              sessionId={gatewaySessionId || undefined}
              onEnsureSession={ensureGatewaySession}
              initialPhoto={photo}
              onComplete={handlePhotoComplete}
              onBack={goToPreviousStep}
            />
          </StepPane>
        )}

        {visitedSteps.has('verification') && employeeData && (
          <StepPane active={currentStep === 'verification'}>
            <VerificationMatching
              employeeData={employeeData}
              photo={photo}
              fingerprints={fingerprints}
              iris={iris}
              documents={documents}
              photoOnly
              submitError={verificationError}
              onComplete={handleVerificationComplete}
              onBack={goToPreviousStep}
            />
          </StepPane>
        )}

        {visitedSteps.has('receipt') && employeeData && (
          <StepPane active={currentStep === 'receipt'}>
            <EnrollmentReceipt
              employeeData={employeeData}
              enrollmentId={enrollmentId}
              onNewEnrollment={handleNewEnrollment}
            />
          </StepPane>
        )}
        </div>
      </div>
    </div>
  );
}
