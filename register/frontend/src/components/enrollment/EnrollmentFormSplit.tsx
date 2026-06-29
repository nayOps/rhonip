'use client';

import React from 'react';
import { ENROLLMENT_SPLIT_CLASS } from '@/lib/enrollment-ui';

interface EnrollmentFormSplitProps {
  children: React.ReactNode;
  className?: string;
}

/** Deux blocs formulaire côte à côte pour limiter la hauteur et le scroll. */
export default function EnrollmentFormSplit({
  children,
  className = '',
}: EnrollmentFormSplitProps) {
  return (
    <div className={`${ENROLLMENT_SPLIT_CLASS} ${className}`.trim()}>{children}</div>
  );
}
