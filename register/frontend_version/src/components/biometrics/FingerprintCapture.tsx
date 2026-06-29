import React, { useState } from 'react';
import { FingerprintCapture as FingerprintData, FingerPosition, FingerStatus } from '@/types';

interface FingerprintCaptureProps {
  onComplete: (fingerprints: FingerprintData[]) => void;
  onBack: () => void;
}

const FINGER_LABELS: Record<FingerPosition, string> = {
  RIGHT_THUMB: 'Pouce',
  RIGHT_INDEX: 'Index',
  RIGHT_MIDDLE: 'Majeur',
  RIGHT_RING: 'Annulaire',
  RIGHT_LITTLE: 'Auriculaire',
  LEFT_THUMB: 'Pouce',
  LEFT_INDEX: 'Index',
  LEFT_MIDDLE: 'Majeur',
  LEFT_RING: 'Annulaire',
  LEFT_LITTLE: 'Auriculaire',
};

const RIGHT_FINGERS: FingerPosition[] = [
  'RIGHT_THUMB',
  'RIGHT_INDEX',
  'RIGHT_MIDDLE',
  'RIGHT_RING',
  'RIGHT_LITTLE',
];

const LEFT_FINGERS: FingerPosition[] = [
  'LEFT_THUMB',
  'LEFT_INDEX',
  'LEFT_MIDDLE',
  'LEFT_RING',
  'LEFT_LITTLE',
];

export default function FingerprintCapture({ onComplete, onBack }: FingerprintCaptureProps) {
  const [fingerprints, setFingerprints] = useState<FingerprintData[]>(() => {
    const initial: FingerprintData[] = [];
    [...RIGHT_FINGERS, ...LEFT_FINGERS].forEach((position) => {
      initial.push({
        position,
        status: 'PENDING',
      });
    });
    return initial;
  });

  const [selectedFinger, setSelectedFinger] = useState<FingerPosition | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  const getFingerprintByPosition = (position: FingerPosition): FingerprintData | undefined => {
    return fingerprints.find((fp) => fp.position === position);
  };

  const updateFingerprint = (position: FingerPosition, updates: Partial<FingerprintData>) => {
    setFingerprints((prev) =>
      prev.map((fp) =>
        fp.position === position
          ? { ...fp, ...updates, timestamp: new Date().toISOString() }
          : fp
      )
    );
  };

  const simulateCapture = (position: FingerPosition) => {
    setIsCapturing(true);
    setSelectedFinger(position);

    // Simulation de capture (3 secondes)
    setTimeout(() => {
      const quality = Math.floor(Math.random() * 30) + 70; // 70-100%
      updateFingerprint(position, {
        status: 'CAPTURED',
        quality,
        image: `data:image/png;base64,simulated_fingerprint_${position}`,
      });
      setIsCapturing(false);
      setSelectedFinger(null);
    }, 3000);
  };

  const markAsMissing = (position: FingerPosition, status: FingerStatus, reason: string) => {
    updateFingerprint(position, {
      status,
      reason,
    });
    setSelectedFinger(null);
  };

  const getStatusColor = (status: FingerStatus): string => {
    switch (status) {
      case 'CAPTURED':
        return 'bg-green-500';
      case 'MISSING':
      case 'AMPUTATED':
      case 'DAMAGED':
        return 'bg-yellow-500';
      case 'PENDING':
        return 'bg-gray-300';
      default:
        return 'bg-gray-300';
    }
  };

  const getStatusIcon = (status: FingerStatus): string => {
    switch (status) {
      case 'CAPTURED':
        return '✓';
      case 'MISSING':
      case 'AMPUTATED':
        return '✗';
      case 'DAMAGED':
        return '⚠';
      case 'PENDING':
        return '○';
      default:
        return '○';
    }
  };

  const capturedCount = fingerprints.filter((fp) => fp.status === 'CAPTURED').length;
  const totalCount = fingerprints.length;
  const allProcessed = fingerprints.every((fp) => fp.status !== 'PENDING');

  const handleSubmit = () => {
    if (allProcessed) {
      onComplete(fingerprints);
    }
  };

  const renderFinger = (position: FingerPosition) => {
    const fingerprint = getFingerprintByPosition(position);
    if (!fingerprint) return null;

    const isSelected = selectedFinger === position;

    return (
      <button
        key={position}
        onClick={() => setSelectedFinger(position)}
        disabled={isCapturing}
        className={`
          relative flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all
          ${isSelected ? 'border-secondary-600 bg-blue-50 scale-105' : 'border-gray-300 hover:border-secondary-600'}
          ${isCapturing && !isSelected ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        {/* Icône de doigt */}
        <div className="relative w-16 h-20 mb-2">
          <div className={`w-full h-full rounded-t-full ${getStatusColor(fingerprint.status)} opacity-80`}></div>
          <div className="absolute inset-0 flex items-center justify-center text-white text-2xl font-bold">
            {getStatusIcon(fingerprint.status)}
          </div>
        </div>

        {/* Label */}
        <div className="text-xs font-medium text-gray-700 text-center">
          {FINGER_LABELS[position]}
        </div>

        {/* Qualité */}
        {fingerprint.quality && (
          <div className="text-xs text-green-600 font-semibold mt-1">
            {fingerprint.quality}%
          </div>
        )}

        {/* Raison si manquant */}
        {fingerprint.reason && (
          <div className="text-xs text-yellow-600 mt-1 text-center">
            {fingerprint.reason}
          </div>
        )}
      </button>
    );
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* En-tête */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Capture des empreintes digitales
        </h2>
        <p className="text-gray-600">
          Capturez les empreintes des 10 doigts. Signalez les doigts manquants ou endommagés.
        </p>

        {/* Barre de progression */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progression</span>
            <span className="font-semibold">
              {capturedCount} / {totalCount} capturés
            </span>
          </div>
          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
              style={{ width: `${(capturedCount / totalCount) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Corps */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Main droite */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
              Main droite
            </h3>
            <div className="grid grid-cols-5 gap-3">
              {RIGHT_FINGERS.map(renderFinger)}
            </div>
          </div>

          {/* Main gauche */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
              Main gauche
            </h3>
            <div className="grid grid-cols-5 gap-3">
              {LEFT_FINGERS.map(renderFinger)}
            </div>
          </div>
        </div>

        {/* Panneau de contrôle */}
        {selectedFinger && (
          <div className="mt-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              {FINGER_LABELS[selectedFinger]} - {selectedFinger.includes('RIGHT') ? 'Main droite' : 'Main gauche'}
            </h4>

            {isCapturing ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-secondary-600 mb-4"></div>
                <p className="text-gray-600 font-medium">Capture en cours...</p>
                <p className="text-sm text-gray-500 mt-2">Veuillez maintenir le doigt sur le capteur</p>
              </div>
            ) : (
              <div className="space-y-3">
                <button
                  onClick={() => simulateCapture(selectedFinger)}
                  className="w-full px-4 py-3 bg-secondary-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  Capturer l'empreinte
                </button>

                <button
                  onClick={() => markAsMissing(selectedFinger, 'AMPUTATED', 'Doigt amputé')}
                  className="w-full px-4 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition font-medium"
                >
                  Doigt amputé
                </button>

                <button
                  onClick={() => markAsMissing(selectedFinger, 'DAMAGED', 'Doigt endommagé')}
                  className="w-full px-4 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition font-medium"
                >
                  Doigt endommagé
                </button>

                <button
                  onClick={() => markAsMissing(selectedFinger, 'MISSING', 'Autre raison')}
                  className="w-full px-4 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition font-medium"
                >
                  Autre raison
                </button>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        {!selectedFinger && (
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Instructions</h3>
                <div className="mt-2 text-sm text-blue-700">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Cliquez sur un doigt pour commencer la capture</li>
                    <li>En cas de handicap, sélectionnez l'option appropriée</li>
                    <li>Assurez-vous que tous les doigts sont traités avant de continuer</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Pied de page */}
      <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium"
        >
          ← Précédent
        </button>

        <button
          onClick={handleSubmit}
          disabled={!allProcessed}
          className={`
            px-6 py-3 rounded-lg font-medium transition
            ${
              allProcessed
                ? 'bg-secondary-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          Suivant →
        </button>
      </div>
    </div>
  );
}

