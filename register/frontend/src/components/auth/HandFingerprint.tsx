'use client';

import React from 'react';

export type HandSide = 'left' | 'right';

type HandFingerprintProps = {
  side: HandSide;
  selected: boolean;
  scanning: boolean;
  onSelect: () => void;
};

function HandFingerprint({ side, selected, scanning, onSelect }: HandFingerprintProps) {
  const isLeft = side === 'left';
  const label = isLeft ? 'Main gauche' : 'Main droite';

  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={scanning}
      className={`group relative flex flex-col items-center gap-3 rounded-2xl border-2 p-5 sm:p-6 transition-all duration-300 w-full max-w-[200px] ${
        selected
          ? 'border-emerald-500 bg-emerald-950/40 shadow-lg shadow-emerald-500/20 scale-[1.03]'
          : 'border-slate-600 bg-slate-800/50 hover:border-emerald-500/50 hover:bg-slate-800'
      } ${scanning && !selected ? 'opacity-40' : ''}`}
    >
      <svg
        viewBox="0 0 120 160"
        className={`w-24 h-32 sm:w-28 sm:h-36 transition-transform duration-300 ${
          isLeft ? 'scale-x-[-1]' : ''
        } ${selected ? 'drop-shadow-md' : 'opacity-80 group-hover:opacity-100'}`}
        aria-hidden
      >
        <path
          d="M60 148c-22 0-38-14-38-32V72c0-6 5-11 11-11 4 0 7 2 9 5V38c0-6 5-11 11-11s11 5 11 11v22c0-6 5-11 11-11s11 5 11 11v18c0-6 5-11 11-11s11 5 11 11v12c0-6 5-11 11-11s11 5 11 11v8c0 18-16 32-38 32z"
          fill={selected ? '#064e3b' : '#1e293b'}
          stroke={selected ? '#34d399' : '#64748b'}
          strokeWidth="2"
        />
        {/* Index finger highlight */}
        <circle
          cx={isLeft ? 78 : 42}
          cy="42"
          r={selected ? 10 : 7}
          className={`transition-all ${selected ? 'fill-emerald-400' : 'fill-slate-500'}`}
        />
        {selected && scanning && (
          <circle
            cx={isLeft ? 78 : 42}
            cy="42"
            r="14"
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
            className="animate-ping origin-center"
            style={{ transformOrigin: `${isLeft ? 78 : 42}px 42px` }}
          />
        )}
      </svg>
      <span
        className={`text-sm font-semibold ${selected ? 'text-emerald-300' : 'text-slate-400'}`}
      >
        {label}
      </span>
      {selected && (
        <span className="absolute -top-2 right-3 h-5 w-5 rounded-full bg-emerald-500 text-white text-xs flex items-center justify-center">
          ✓
        </span>
      )}
    </button>
  );
}

export default HandFingerprint;
