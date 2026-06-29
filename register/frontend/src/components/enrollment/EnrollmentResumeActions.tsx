'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { launchEnrollmentFromSession } from '@/lib/enrollment-draft';
import type { EnrollmentEditMode } from '@/services/enrollment-session-api';

type Props = {
  sessionId: string;
  layout?: 'inline' | 'stack';
};

export default function EnrollmentResumeActions({ sessionId, layout = 'inline' }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState<EnrollmentEditMode | null>(null);
  const [error, setError] = useState<string | null>(null);

  const openGuichet = async (mode: EnrollmentEditMode) => {
    setLoading(mode);
    setError(null);
    try {
      await launchEnrollmentFromSession(sessionId, mode);
      await router.push('/enrollment');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ouverture guichet impossible');
      setLoading(null);
    }
  };

  const btnClass =
    layout === 'stack'
      ? 'w-full px-3 py-2 text-sm rounded-md border font-medium'
      : 'px-2 py-1 text-xs rounded border font-medium whitespace-nowrap';

  return (
    <div className={layout === 'stack' ? 'space-y-2' : 'flex flex-wrap gap-1 items-center'}>
      <button
        type="button"
        disabled={!!loading}
        onClick={() => void openGuichet('biographic')}
        className={`${btnClass} border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50`}
      >
        {loading === 'biographic' ? '…' : 'Modifier fiche'}
      </button>
      <button
        type="button"
        disabled={!!loading}
        onClick={() => void openGuichet('biometric')}
        className={`${btnClass} border-emerald-300 text-emerald-800 bg-emerald-50 hover:bg-emerald-100 disabled:opacity-50`}
      >
        {loading === 'biometric' ? '…' : 'Refaire biométrie'}
      </button>
      {error && <p className="text-xs text-red-600 w-full">{error}</p>}
    </div>
  );
}
