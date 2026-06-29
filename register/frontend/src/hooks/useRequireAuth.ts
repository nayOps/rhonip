'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/context/AuthContext';
import type { UserRole } from '@/types/auth';

export function useRequireAuth(allowedRoles?: UserRole[]) {
  const router = useRouter();
  const { session, isReady } = useAuth();

  useEffect(() => {
    if (!isReady) return;
    if (!session) {
      if (router.pathname !== '/auth') {
        void router.replace('/auth');
      }
      return;
    }
    if (allowedRoles && !allowedRoles.includes(session.user.role)) {
      const target = session.user.role === 'admin' ? '/dashboard' : '/agents';
      if (router.pathname !== target) {
        void router.replace(target);
      }
    }
  }, [isReady, session, allowedRoles, router]);

  return { session, isReady, isAuthenticated: !!session };
}
