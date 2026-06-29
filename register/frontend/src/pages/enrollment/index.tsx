'use client';

import React from 'react';
import { useRouter } from 'next/router';
import EnrollmentWorkflow from '../../components/forms/EnrollmentWorkflow';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { useAuth } from '@/context/AuthContext';
import { ENROLLMENT_SHELL_CLASS } from '@/lib/enrollment-ui';

const EnrollmentPage: React.FC = () => {
  const router = useRouter();
  const { logout } = useAuth();
  const { session, isReady, isAuthenticated } = useRequireAuth(['ops', 'admin']);

  if (!isReady || !isAuthenticated || !session) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Chargement…</p>
      </div>
    );
  }

  const initials = session.user.displayName
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="h-screen w-full bg-gray-50 flex flex-col overflow-hidden">
      <header className="shrink-0 z-30 bg-white border-b border-gray-200 shadow-sm w-full">
        <div className={`${ENROLLMENT_SHELL_CLASS} py-3 flex items-center justify-between gap-4`}>
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-10 w-10 rounded-lg bg-secondary-600 text-white flex items-center justify-center shrink-0">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm5.134 3.052a1 1 0 011.414 0l3.172 3.172a1 1 0 001.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="min-w-0">
              <p className="text-base font-bold text-gray-900 leading-tight">ONIP System</p>
              <p className="text-xs text-gray-500 truncate">
                Enrôlement — mode Ops · {session.user.displayName}
                {session.user.stationId ? ` — ${session.user.stationId}` : ''}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            <button
              type="button"
              onClick={() => router.replace('/agents')}
              className="text-sm text-secondary-700 hover:text-secondary-900 px-3 py-1.5 rounded border border-secondary-200 bg-secondary-50"
            >
              ← Agents
            </button>
            <span className="hidden sm:inline text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded">
              Plein écran
            </span>
            <button
              type="button"
              onClick={() => {
                logout();
                router.replace('/auth');
              }}
              className="text-sm text-gray-600 hover:text-gray-900 px-3 py-1.5 rounded border border-gray-300 bg-white"
            >
              Déconnexion
            </button>
            <div
              className="h-9 w-9 rounded-full bg-secondary-100 text-secondary-800 border-2 border-secondary-200 flex items-center justify-center text-xs font-bold"
              title={session.user.displayName}
            >
              {initials}
            </div>
          </div>
        </div>
      </header>

      <EnrollmentWorkflow onCancelEnrollment={() => router.replace('/agents')} />
    </div>
  );
};

export default EnrollmentPage;
