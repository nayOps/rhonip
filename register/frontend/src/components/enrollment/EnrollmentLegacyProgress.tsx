'use client';

import React from 'react';
import type { WorkflowStep } from '@/components/forms/EnrollmentWorkflow.types';
import {
  RH_DISABLED_STEP_HINTS,
  RH_PROGRESS_STEP_LABELS,
  RH_PROGRESS_WORKFLOW_STEPS,
  getRhProgressStepIndex,
  isRhDisabledWorkflowStep,
} from '@/lib/rh-guichet-workflow';

interface EnrollmentLegacyProgressProps {
  currentStep: WorkflowStep;
  compact?: boolean;
  allowNavigation?: boolean;
  visitedSteps?: Set<WorkflowStep>;
  onStepSelect?: (step: WorkflowStep) => void;
}

export default function EnrollmentLegacyProgress({
  currentStep,
  compact = false,
  allowNavigation = false,
  visitedSteps,
  onStepSelect,
}: EnrollmentLegacyProgressProps) {
  const steps = RH_PROGRESS_WORKFLOW_STEPS;
  const currentIndex = getRhProgressStepIndex(currentStep);
  const safeIndex = currentIndex >= 0 ? currentIndex : 0;
  const activeCount = steps.filter((step) => !isRhDisabledWorkflowStep(step)).length;
  const completedActive = steps
    .slice(0, safeIndex + 1)
    .filter((step) => !isRhDisabledWorkflowStep(step)).length;
  const progress = activeCount > 0 ? (completedActive / activeCount) * 100 : 0;

  const handleStepClick = (step: WorkflowStep, index: number) => {
    if (isRhDisabledWorkflowStep(step)) return;
    if (!allowNavigation || !onStepSelect || !visitedSteps?.has(step)) return;
    if (index === safeIndex) return;
    onStepSelect(step);
  };

  return (
    <div
      className={`w-full bg-white border-b border-gray-200 shrink-0 ${
        compact ? 'px-3 py-2' : 'p-4 md:p-6'
      }`}
    >
      <div className="max-w-7xl mx-auto">
        <div className={compact ? 'mb-2' : 'mb-4'}>
          <div className={`flex justify-between text-gray-600 mb-1 ${compact ? 'text-xs' : 'text-sm'}`}>
            <span className="font-medium">
              Étape {completedActive} sur {activeCount}: {RH_PROGRESS_STEP_LABELS[currentStep]}
            </span>
            <span className="font-semibold">{Math.round(progress)}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className={`flex justify-between items-center ${compact ? 'gap-0.5' : ''}`}>
          {steps.map((step, index) => {
            const disabled = isRhDisabledWorkflowStep(step);
            const isCompleted = !disabled && index < safeIndex;
            const isCurrent = index === safeIndex;
            const isFuture = !disabled && index > safeIndex;
            const canNavigate =
              !disabled && allowNavigation && visitedSteps?.has(step) && onStepSelect;

            return (
              <div key={step} className="flex flex-col items-center flex-1">
                <button
                  type="button"
                  disabled={!canNavigate}
                  onClick={() => handleStepClick(step, index)}
                  title={disabled ? RH_DISABLED_STEP_HINTS[step] : RH_PROGRESS_STEP_LABELS[step]}
                  className={`${compact ? 'w-7 h-7 text-xs' : 'w-8 h-8 text-sm'} rounded-full flex items-center justify-center font-bold mb-1 transition-all
                    ${disabled ? 'bg-gray-100 text-gray-400 border border-dashed border-gray-300 cursor-not-allowed opacity-60' : ''}
                    ${!disabled && isCompleted ? 'bg-green-500 text-white' : ''}
                    ${!disabled && isCurrent ? `bg-blue-600 text-white ${compact ? 'ring-2' : 'ring-4'} ring-blue-200` : ''}
                    ${!disabled && isFuture ? 'bg-gray-200 text-gray-500' : ''}
                    ${canNavigate ? 'cursor-pointer hover:opacity-90' : disabled ? '' : 'cursor-default'}
                  `}
                >
                  {disabled ? '—' : isCompleted ? '✓' : index + 1}
                </button>
                <span
                  className={`text-xs font-medium text-center ${compact ? 'hidden' : 'hidden md:block'}
                    ${disabled ? 'text-gray-400 line-through' : ''}
                    ${!disabled && isCompleted ? 'text-green-600' : ''}
                    ${!disabled && isCurrent ? 'text-blue-600' : ''}
                    ${!disabled && isFuture ? 'text-gray-400' : ''}
                  `}
                >
                  {RH_PROGRESS_STEP_LABELS[step]}
                </span>
                {disabled && !compact && (
                  <span className="hidden md:block text-[10px] text-gray-400 mt-0.5">
                    {RH_DISABLED_STEP_HINTS[step]}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
