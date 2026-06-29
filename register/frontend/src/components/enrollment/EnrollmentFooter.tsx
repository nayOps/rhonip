'use client';

import React from 'react';
import { ENROLLMENT_SHELL_CLASS } from '@/lib/enrollment-ui';

interface EnrollmentFooterProps {
  onCancel?: () => void;
  onBack?: () => void;
  backLabel?: string;
  onNext?: () => void;
  nextLabel?: string;
  nextDisabled?: boolean;
  showBack?: boolean;
}

export default function EnrollmentFooter({
  onCancel,
  onBack,
  backLabel = '← Précédent',
  onNext,
  nextLabel = 'Suivant : Extensions →',
  nextDisabled = false,
  showBack = false,
}: EnrollmentFooterProps) {
  return (
    <>
      <footer className="mt-auto w-full border-t border-gray-200 bg-white">
        <div className={`${ENROLLMENT_SHELL_CLASS} py-2 flex items-center justify-between gap-4`}>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <svg className="w-4 h-4 text-secondary-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm5.134 3.052a1 1 0 011.414 0l3.172 3.172a1 1 0 001.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            <span>Session sécurisée — Chiffrement AES-256</span>
          </div>

          <div className="flex items-center gap-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Annuler l&apos;enrôlement
              </button>
            )}
            {showBack && onBack && (
              <button
                type="button"
                onClick={onBack}
                className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                {backLabel}
              </button>
            )}
            {onNext && (
              <button
                type="button"
                onClick={onNext}
                disabled={nextDisabled}
                className="px-5 py-2.5 text-sm font-semibold text-white bg-secondary-600 rounded-lg hover:bg-secondary-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
              >
                {nextLabel}
              </button>
            )}
          </div>
        </div>
      </footer>

      <button
        type="button"
        className="fixed bottom-6 right-6 z-40 h-12 w-12 rounded-full bg-secondary-700 text-white shadow-lg hover:bg-secondary-800 flex items-center justify-center text-lg font-bold"
        title="Aide"
        aria-label="Aide"
      >
        ?
      </button>
    </>
  );
}
