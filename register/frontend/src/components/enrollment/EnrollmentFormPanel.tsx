'use client';

import React from 'react';
import {
  ENROLLMENT_PANEL_CLASS,
  ENROLLMENT_PANEL_TITLE_CLASS,
} from '@/lib/enrollment-ui';

interface EnrollmentFormPanelProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export default function EnrollmentFormPanel({
  title,
  children,
  className = '',
}: EnrollmentFormPanelProps) {
  return (
    <div className={`${ENROLLMENT_PANEL_CLASS} ${className}`.trim()}>
      <h4 className={ENROLLMENT_PANEL_TITLE_CLASS}>{title}</h4>
      {children}
    </div>
  );
}
