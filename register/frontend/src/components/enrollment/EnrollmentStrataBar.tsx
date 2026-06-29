'use client';

import React from 'react';
import { ENROLLMENT_SHELL_CLASS, ENROLLMENT_STRATA_OPTIONS } from '@/lib/enrollment-ui';

interface EnrollmentStrataBarProps {
  selected: string | null;
  onSelect?: (value: string) => void;
  readOnly?: boolean;
}

export default function EnrollmentStrataBar({
  selected,
  onSelect,
  readOnly = false,
}: EnrollmentStrataBarProps) {
  return (
    <div className="w-full bg-white border-b border-gray-200">
      <div className={`${ENROLLMENT_SHELL_CLASS} py-2.5`}>
        <p className="text-[11px] font-semibold tracking-wider text-gray-500 uppercase mb-3 text-center">
          Catégorie du requérant
        </p>
        <div className="w-full overflow-x-auto">
          <div className="flex flex-nowrap justify-center gap-2 min-w-full w-max mx-auto px-1">
          {ENROLLMENT_STRATA_OPTIONS.map((item) => {
            const isSelected = selected === item.value;
            const interactive = !readOnly && onSelect;

            return (
              <button
                key={item.value}
                type="button"
                disabled={readOnly && !isSelected}
                onClick={() => interactive && onSelect(item.value)}
                className={`flex shrink-0 items-center gap-1.5 whitespace-nowrap px-3 py-2 rounded-lg border-2 transition-all text-sm font-medium
                  ${isSelected
                    ? 'border-secondary-500 bg-secondary-50 text-secondary-900 shadow-sm'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'}
                  ${readOnly && !isSelected ? 'opacity-40 cursor-default' : ''}
                  ${interactive ? 'cursor-pointer' : ''}
                `}
              >
                <span className="text-lg leading-none">{item.icon}</span>
                <span>{item.label}</span>
                {isSelected && (
                  <span className="ml-1 flex h-5 w-5 items-center justify-center rounded-full bg-secondary-600 text-white text-xs">
                    ✓
                  </span>
                )}
              </button>
            );
          })}
          </div>
        </div>
      </div>
    </div>
  );
}
