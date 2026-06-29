'use client';

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { AuthSession, AuthUser, UserRole } from '@/types/auth';

const STORAGE_KEY = 'fgp_guichet_session';

interface AuthContextValue {
  session: AuthSession | null;
  isReady: boolean;
  loginAdmin: (email: string, password: string) => Promise<void>;
  loginOpsFingerprint: (hand?: 'left' | 'right') => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const MOCK_ADMIN = {
  email: 'admin@fgp.local',
  password: 'admin123',
  user: {
    id: 'admin-001',
    displayName: 'Administrateur FGP',
    role: 'admin' as UserRole,
  },
};

function loadSession(): AuthSession | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

function saveSession(session: AuthSession | null) {
  if (typeof window === 'undefined') return;
  if (!session) {
    sessionStorage.removeItem(STORAGE_KEY);
    return;
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    setSession(loadSession());
    setIsReady(true);
  }, []);

  const persist = useCallback((s: AuthSession | null) => {
    setSession(s);
    saveSession(s);
  }, []);

  const loginAdmin = useCallback(async (email: string, password: string) => {
    await new Promise((r) => setTimeout(r, 600));
    const normalized = email.trim().toLowerCase();
    if (normalized !== MOCK_ADMIN.email || password !== MOCK_ADMIN.password) {
      throw new Error('Identifiants incorrects (mock : admin@fgp.local / admin123)');
    }
    persist({
      user: MOCK_ADMIN.user,
      loggedInAt: new Date().toISOString(),
    });
  }, [persist]);

  const loginOpsFingerprint = useCallback(async (hand: 'left' | 'right' = 'right') => {
    await new Promise((r) => setTimeout(r, 1200));
    const handLabel = hand === 'left' ? 'gauche' : 'droite';
    persist({
      user: {
        id: 'ops-042',
        displayName: `Agent guichet — Ops (main ${handLabel})`,
        role: 'ops',
        stationId: 'GUICHET-01',
      },
      loggedInAt: new Date().toISOString(),
    });
  }, [persist]);

  const logout = useCallback(() => {
    persist(null);
  }, [persist]);

  const value = useMemo(
    () => ({ session, isReady, loginAdmin, loginOpsFingerprint, logout }),
    [session, isReady, loginAdmin, loginOpsFingerprint, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth doit être utilisé dans AuthProvider');
  return ctx;
}
