'use client';

import React from 'react';
import {
  ENROLLMENT_SHELL_CLASS,
  SUB_TAB_LABELS,
  type BaseFormSubTab,
} from '@/lib/enrollment-ui';

interface EnrollmentSubTabsProps {
  tabs: BaseFormSubTab[];
  active: BaseFormSubTab;
  onChange: (tab: BaseFormSubTab) => void;
}

export default function EnrollmentSubTabs({ tabs, active, onChange }: EnrollmentSubTabsProps) {
  return (
    <div className="w-full bg-white border-b border-gray-100">
      <div className={ENROLLMENT_SHELL_CLASS}>
        <nav className="flex justify-center gap-6 overflow-x-auto">
          {tabs.map((tabId, index) => {
            const isActive = active === tabId;
            return (
              <button
                key={tabId}
                type="button"
                onClick={() => onChange(tabId)}
                className={`flex items-center gap-2 py-2.5 border-b-2 text-sm font-medium whitespace-nowrap transition-colors
                  ${isActive
                    ? 'border-secondary-600 text-secondary-700'
                    : 'border-transparent text-gray-500 hover:text-gray-700'}
                `}
              >
                <span
                  className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold
                    ${isActive ? 'bg-secondary-600 text-white' : 'bg-gray-100 text-gray-500'}
                  `}
                >
                  {index + 1}
                </span>
                {SUB_TAB_LABELS[tabId]}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
