'use client';

import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import EnrollmentWorkflow from '../../components/forms/EnrollmentWorkflow';

const EnrollmentPage: React.FC = () => {
  return (
    <DashboardLayout>
      <EnrollmentWorkflow />
    </DashboardLayout>
  );
};

export default EnrollmentPage;
