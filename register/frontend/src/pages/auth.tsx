import { useEffect } from 'react';
import { useRouter } from 'next/router';
import GuichetAuth from '@/components/auth/GuichetAuth';
import { useAuth } from '@/context/AuthContext';

export default function AuthPage() {
  const router = useRouter();
  const { session, isReady } = useAuth();

  useEffect(() => {
    if (!isReady || !session) return;
    const target = session.user.role === 'admin' ? '/dashboard' : '/agents';
    if (router.pathname === target) return;
    void router.replace(target);
  }, [isReady, session, router]);

  if (!isReady || session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-gray-500">Chargement…</p>
      </div>
    );
  }

  return <GuichetAuth />;
}
