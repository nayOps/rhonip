import React, { useState } from 'react';
import { IrisCapture as IrisData, EyePosition, EyeStatus } from '@/types';

interface IrisCaptureProps {
  onComplete: (irisData: IrisData[]) => void;
  onBack: () => void;
}

const EYE_LABELS: Record<EyePosition, string> = {
  LEFT: 'Œil gauche',
  RIGHT: 'Œil droit',
};

export default function IrisCapture({ onComplete, onBack }: IrisCaptureProps) {
  const [irisData, setIrisData] = useState<IrisData[]>([
    { position: 'LEFT', status: 'PENDING' },
    { position: 'RIGHT', status: 'PENDING' },
  ]);

  const [selectedEye, setSelectedEye] = useState<EyePosition | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  const getIrisByPosition = (position: EyePosition): IrisData | undefined => {
    return irisData.find((iris) => iris.position === position);
  };

  const updateIris = (position: EyePosition, updates: Partial<IrisData>) => {
    setIrisData((prev) =>
      prev.map((iris) =>
        iris.position === position
          ? { ...iris, ...updates, timestamp: new Date().toISOString() }
          : iris
      )
    );
  };

  const simulateCapture = (position: EyePosition) => {
    setIsCapturing(true);
    setSelectedEye(position);

    // Simulation de capture (4 secondes)
    setTimeout(() => {
      const quality = Math.floor(Math.random() * 25) + 75; // 75-100%
      updateIris(position, {
        status: 'CAPTURED',
        quality,
        image: `data:image/png;base64,simulated_iris_${position}`,
      });
      setIsCapturing(false);
      setSelectedEye(null);
    }, 4000);
  };

  const markAsUnavailable = (position: EyePosition, status: EyeStatus, reason: string) => {
    updateIris(position, {
      status,
      reason,
    });
    setSelectedEye(null);
  };

  const getStatusColor = (status: EyeStatus): string => {
    switch (status) {
      case 'CAPTURED':
        return 'bg-green-500';
      case 'BLIND':
      case 'MISSING':
      case 'DAMAGED':
        return 'bg-yellow-500';
      case 'PENDING':
        return 'bg-gray-300';
      default:
        return 'bg-gray-300';
    }
  };

  const getStatusIcon = (status: EyeStatus): string => {
    switch (status) {
      case 'CAPTURED':
        return '✓';
      case 'BLIND':
      case 'MISSING':
        return '✗';
      case 'DAMAGED':
        return '⚠';
      case 'PENDING':
        return '○';
      default:
        return '○';
    }
  };

  const capturedCount = irisData.filter((iris) => iris.status === 'CAPTURED').length;
  const totalCount = irisData.length;
  const allProcessed = irisData.every((iris) => iris.status !== 'PENDING');

  const handleSubmit = () => {
    if (allProcessed) {
      onComplete(irisData);
    }
  };

  const renderEye = (position: EyePosition) => {
    const iris = getIrisByPosition(position);
    if (!iris) return null;

    const isSelected = selectedEye === position;
    const isLeft = position === 'LEFT';

    return (
      <div
        key={position}
        className={`
          relative flex flex-col items-center p-8 rounded-lg border-2 transition-all cursor-pointer
          ${isSelected ? 'border-secondary-600 bg-blue-50 scale-105' : 'border-gray-300 hover:border-secondary-600'}
          ${isCapturing && !isSelected ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        onClick={() => !isCapturing && setSelectedEye(position)}
      >
        {/* Schéma de l'œil */}
        <div className="relative w-40 h-40 mb-4">
          {/* Œil externe */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-full h-24 bg-white border-4 border-gray-400 rounded-full relative overflow-hidden">
              {/* Iris */}
              <div className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 rounded-full ${getStatusColor(iris.status)}`}>
                {/* Pupille */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-black rounded-full flex items-center justify-center">
                  <span className="text-white text-xl font-bold">
                    {getStatusIcon(iris.status)}
                  </span>
                </div>
              </div>

              {/* Paupières */}
              <div className="absolute -top-2 left-0 right-0 h-4 bg-gradient-to-b from-gray-200 to-transparent"></div>
              <div className="absolute -bottom-2 left-0 right-0 h-4 bg-gradient-to-t from-gray-200 to-transparent"></div>
            </div>
          </div>

          {/* Cils */}
          {isLeft ? (
            <>
              <div className="absolute top-6 left-2 w-12 h-1 bg-gray-800 rounded-full transform -rotate-45 origin-right"></div>
              <div className="absolute top-6 right-2 w-12 h-1 bg-gray-800 rounded-full transform rotate-45 origin-left"></div>
            </>
          ) : (
            <>
              <div className="absolute top-6 left-2 w-12 h-1 bg-gray-800 rounded-full transform rotate-45 origin-right"></div>
              <div className="absolute top-6 right-2 w-12 h-1 bg-gray-800 rounded-full transform -rotate-45 origin-left"></div>
            </>
          )}
        </div>

        {/* Label */}
        <div className="text-lg font-semibold text-gray-700 mb-2">
          {EYE_LABELS[position]}
        </div>

        {/* Statut */}
        <div className={`text-sm font-medium ${iris.status === 'CAPTURED' ? 'text-green-600' : 'text-gray-500'}`}>
          {iris.status === 'CAPTURED' ? 'Capturé' : iris.status === 'PENDING' ? 'En attente' : iris.reason}
        </div>

        {/* Qualité */}
        {iris.quality && (
          <div className="text-sm text-green-600 font-semibold mt-1">
            Qualité : {iris.quality}%
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* En-tête */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Capture de l'iris
        </h2>
        <p className="text-gray-600">
          Capturez l'iris des deux yeux. Signalez les handicaps visuels si nécessaire.
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
              className="h-full bg-gradient-to-r from-purple-500 to-pink-600 transition-all duration-500"
              style={{ width: `${(capturedCount / totalCount) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Corps */}
      <div className="p-6">
        {/* Visualisation des yeux */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {renderEye('LEFT')}
          {renderEye('RIGHT')}
        </div>

        {/* Panneau de contrôle */}
        {selectedEye && (
          <div className="mt-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">
              {EYE_LABELS[selectedEye]}
            </h4>

            {isCapturing ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-secondary-600 mb-4"></div>
                <p className="text-gray-600 font-medium">Capture en cours...</p>
                <p className="text-sm text-gray-500 mt-2">Regardez fixement la caméra</p>
                <p className="text-xs text-gray-400 mt-1">Ne clignez pas des yeux</p>
              </div>
            ) : (
              <div className="space-y-3">
                <button
                  onClick={() => simulateCapture(selectedEye)}
                  className="w-full px-4 py-3 bg-secondary-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  Capturer l'iris
                </button>

                <button
                  onClick={() => markAsUnavailable(selectedEye, 'BLIND', 'Œil aveugle')}
                  className="w-full px-4 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition font-medium"
                >
                  Œil aveugle
                </button>

                <button
                  onClick={() => markAsUnavailable(selectedEye, 'MISSING', 'Œil manquant')}
                  className="w-full px-4 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition font-medium"
                >
                  Œil manquant
                </button>

                <button
                  onClick={() => markAsUnavailable(selectedEye, 'DAMAGED', 'Œil endommagé')}
                  className="w-full px-4 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition font-medium"
                >
                  Œil endommagé
                </button>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        {!selectedEye && (
          <div className="mt-8 p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-purple-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-purple-800">Instructions</h3>
                <div className="mt-2 text-sm text-purple-700">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Cliquez sur un œil pour commencer la capture</li>
                    <li>Regardez fixement la caméra pendant la capture</li>
                    <li>En cas de handicap visuel, sélectionnez l'option appropriée</li>
                    <li>Assurez-vous que les deux yeux sont traités avant de continuer</li>
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

