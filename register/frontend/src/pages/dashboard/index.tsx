'use client';

import React from 'react';
import { useRouter } from 'next/router';
import DashboardOverview from '../../components/dashboard/DashboardOverview';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { useAuth } from '@/context/AuthContext';

const DashboardPage: React.FC = () => {
  const router = useRouter();
  const { logout, session } = useAuth();
  const { isReady, isAuthenticated } = useRequireAuth(['admin']);

  if (!isReady || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Chargement…</p>
      </div>
    );
  }

  return (
    <DashboardLayout
      userName={session?.user.displayName}
      onLogout={() => {
        logout();
        router.replace('/auth');
      }}
    >
      <div className="max-w-7xl mx-auto p-4 md:p-6 lg:p-8">
        <DashboardOverview />
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
