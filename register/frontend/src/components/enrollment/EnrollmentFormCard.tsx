'use client';

import React from 'react';

interface EnrollmentFormCardProps {
  title: string;
  subtitle?: string;
  badge?: string;
  children: React.ReactNode;
  className?: string;
}

export default function EnrollmentFormCard({
  title,
  subtitle,
  badge = 'INFORMATION REQUISE',
  children,
  className = '',
}: EnrollmentFormCardProps) {
  return (
    <div className={`bg-white border border-gray-200 rounded-xl shadow-sm h-full min-h-0 flex flex-col ${className}`.trim()}>
      <div className="px-4 py-2.5 border-b border-gray-100 flex flex-wrap items-center justify-between gap-2 shrink-0">
        <div>
          <h3 className="text-base font-semibold text-gray-900 leading-tight">{title}</h3>
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        {badge && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold tracking-wide bg-amber-100 text-amber-900 border border-amber-200">
            {badge}
          </span>
        )}
      </div>
      <div className="p-3 flex-1 min-h-0 flex flex-col">{children}</div>
    </div>
  );
}
