'use client';

import React from 'react';
import { type BaseFormStrata, getStrataRuleLines } from '@/lib/base-enrollment-rules';

export default function StrataRulesBanner({ strata }: { strata: BaseFormStrata }) {
  const lines = getStrataRuleLines(strata);
  return (
    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h3 className="text-sm font-semibold text-blue-900 mb-2">
        Règles applicables — catégorie {strata}
      </h3>
      <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
        {lines.map((line) => (
          <li key={line.label}>
            {line.required ? '★ ' : '○ '}
            {line.label}
            {line.required && <span className="text-red-600 font-medium"> (obligatoire)</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
