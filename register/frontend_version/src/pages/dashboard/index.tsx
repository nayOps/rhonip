'use client';

import React from 'react';
import DashboardOverview from '../../components/dashboard/DashboardOverview';
import DashboardLayout from '../../components/layout/DashboardLayout';

const DashboardPage: React.FC = () => {
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-4 md:p-6 lg:p-8">
        <DashboardOverview />
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;


