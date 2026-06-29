'use client';

import React from 'react';
import {
  ENROLLMENT_SHELL_CLASS,
  getWorkflowStepIndex,
  WORKFLOW_STEP_LABELS,
  WORKFLOW_STEP_ORDER,
} from '@/lib/enrollment-ui';
import type { WorkflowStep } from '@/components/forms/EnrollmentWorkflow.types';

interface EnrollmentMainStepperProps {
  currentStep: WorkflowStep;
}

export default function EnrollmentMainStepper({ currentStep }: EnrollmentMainStepperProps) {
  const currentIndex = getWorkflowStepIndex(currentStep);
  const totalSteps = WORKFLOW_STEP_ORDER.length;
  const progress = ((currentIndex + 1) / totalSteps) * 100;
  const stepLabel = WORKFLOW_STEP_LABELS[currentStep];

  return (
    <div className="w-full bg-white border-b border-gray-200 p-4 md:p-6">
      <div className={ENROLLMENT_SHELL_CLASS}>
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span className="font-medium">
              Étape {currentIndex + 1} sur {totalSteps}: {stepLabel}
            </span>
            <span className="font-semibold">{Math.round(progress)}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-secondary-500 to-secondary-600 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="flex justify-between items-center">
          {WORKFLOW_STEP_ORDER.map((step, index) => {
            const isActive = index === currentIndex;
            const isCompleted = index < currentIndex;
            const isFuture = index > currentIndex;

            return (
              <div key={step} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all
                      ${isActive ? 'bg-secondary-600 text-white scale-110 shadow-lg' : ''}
                      ${isCompleted ? 'bg-green-500 text-white' : ''}
                      ${isFuture ? 'bg-gray-200 text-gray-400' : ''}
                    `}
                  >
                    {isCompleted ? '✓' : index + 1}
                  </div>
                  <span
                    className={`text-xs mt-1 hidden md:block text-center ${
                      isActive
                        ? 'text-secondary-600 font-semibold'
                        : isCompleted
                          ? 'text-green-600'
                          : 'text-gray-400'
                    }`}
                  >
                    {WORKFLOW_STEP_LABELS[step].split(' ')[0]}
                  </span>
                </div>
                {index < WORKFLOW_STEP_ORDER.length - 1 && (
                  <div
                    className={`h-1 flex-1 mx-2 rounded transition-all ${
                      isCompleted ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
