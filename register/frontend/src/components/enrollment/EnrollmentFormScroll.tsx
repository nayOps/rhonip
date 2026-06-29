'use client';

import React from 'react';
import { ENROLLMENT_FORM_SCROLL_CLASS } from '@/lib/enrollment-ui';

interface EnrollmentFormScrollProps {
  children: React.ReactNode;
  className?: string;
}

/** Zone défilante légère pour les étapes avec beaucoup de champs. */
export default function EnrollmentFormScroll({
  children,
  className = '',
}: EnrollmentFormScrollProps) {
  return (
    <div className={`${ENROLLMENT_FORM_SCROLL_CLASS} ${className}`.trim()}>
      {children}
    </div>
  );
}
