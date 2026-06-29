import React, { useState, useRef } from 'react';

interface PhotoCaptureProps {
  onComplete: (photoData: PhotoData) => void;
  onBack: () => void;
}

export interface PhotoData {
  image: string; // base64
  quality: number; // 0-100
  icaoCompliant: boolean;
  checks: {
    faceDetected: boolean;
    eyesOpen: boolean;
    lookingStraight: boolean;
    neutralExpression: boolean;
    noGlasses: boolean;
    goodLighting: boolean;
    noShadows: boolean;
    sharpness: boolean;
    resolution: boolean;
    background: boolean;
  };
  timestamp: string;
}

export default function PhotoCapture({ onComplete, onBack }: PhotoCaptureProps) {
  const [photoData, setPhotoData] = useState<PhotoData | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const simulateCapture = () => {
    setIsCapturing(true);

    // Simulation de capture avec vérifications ICAO (3 secondes)
    setTimeout(() => {
      const quality = Math.floor(Math.random() * 15) + 85; // 85-100%
      const icaoChecks = {
        faceDetected: true,
        eyesOpen: Math.random() > 0.1,
        lookingStraight: Math.random() > 0.15,
        neutralExpression: Math.random() > 0.2,
        noGlasses: Math.random() > 0.3,
        goodLighting: Math.random() > 0.1,
        noShadows: Math.random() > 0.15,
        sharpness: Math.random() > 0.1,
        resolution: true,
        background: Math.random() > 0.1,
      };

      const passedChecks = Object.values(icaoChecks).filter(Boolean).length;
      const icaoCompliant = passedChecks >= 8; // Au moins 8/10 critères

      const photo: PhotoData = {
        image: `data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD...simulated_photo_${Date.now()}`,
        quality: quality,
        icaoCompliant,
        checks: icaoChecks,
        timestamp: new Date().toISOString(),
      };

      setPhotoData(photo);
      setIsCapturing(false);
      setShowCamera(false);
    }, 3000);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setIsCapturing(true);

      // Simulation de vérification ICAO sur l'image uploadée
      setTimeout(() => {
        const quality = Math.floor(Math.random() * 10) + 90;
        const icaoChecks = {
          faceDetected: true,
          eyesOpen: true,
          lookingStraight: Math.random() > 0.2,
          neutralExpression: Math.random() > 0.2,
          noGlasses: Math.random() > 0.3,
          goodLighting: Math.random() > 0.15,
          noShadows: Math.random() > 0.15,
          sharpness: true,
          resolution: true,
          background: Math.random() > 0.1,
        };

        const passedChecks = Object.values(icaoChecks).filter(Boolean).length;
        const icaoCompliant = passedChecks >= 8;

        const photo: PhotoData = {
          image: result,
          quality,
          icaoCompliant,
          checks: icaoChecks,
          timestamp: new Date().toISOString(),
        };

        setPhotoData(photo);
        setIsCapturing(false);
      }, 2000);
    };
    reader.readAsDataURL(file);
  };

  const handleRetake = () => {
    setPhotoData(null);
    setShowCamera(false);
  };

  const handleSubmit = () => {
    if (photoData) {
      onComplete(photoData);
    }
  };

  const getCheckIcon = (passed: boolean) => {
    return passed ? (
      <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    ) : (
      <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
      </svg>
    );
  };

  const getCheckLabel = (check: keyof PhotoData['checks']): string => {
    const labels: Record<keyof PhotoData['checks'], string> = {
      faceDetected: 'Visage détecté',
      eyesOpen: 'Yeux ouverts',
      lookingStraight: 'Regard face caméra',
      neutralExpression: 'Expression neutre',
      noGlasses: 'Sans lunettes',
      goodLighting: 'Éclairage suffisant',
      noShadows: 'Sans ombres',
      sharpness: 'Netteté correcte',
      resolution: 'Résolution ≥ 600 DPI',
      background: 'Fond uni clair',
    };
    return labels[check];
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* En-tête */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-blue-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Capture de la photo d'identité
        </h2>
        <p className="text-gray-600">
          Capturez ou téléchargez une photo conforme aux normes ICAO (Organisation de l'Aviation Civile Internationale)
        </p>
      </div>

      {/* Corps */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Zone de capture/prévisualisation */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Photo</h3>

            {!photoData && !isCapturing && (
              <div className="space-y-4">
                {/* Zone de capture simulée */}
                <div className="relative w-full aspect-[3/4] bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <svg className="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-500">Aucune photo capturée</p>
                  </div>

                  {/* Cadre de guidage */}
                  <div className="absolute inset-8 border-4 border-blue-400 rounded-full opacity-30"></div>
                </div>

                {/* Boutons de capture */}
                <div className="space-y-3">
                  <button
                    onClick={simulateCapture}
                    className="w-full px-4 py-3 bg-secondary-600 text-white rounded-lg hover:bg-secondary-700 transition font-medium flex items-center justify-center space-x-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>Capturer avec la caméra</span>
                  </button>

                  <div className="relative">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full px-4 py-3 border-2 border-dashed border-gray-300 text-gray-700 rounded-lg hover:border-secondary-500 hover:bg-gray-50 transition font-medium flex items-center justify-center space-x-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <span>Télécharger une photo</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {isCapturing && (
              <div className="w-full aspect-[3/4] bg-gray-900 rounded-lg flex items-center justify-center">
                <div className="text-center text-white">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
                  <p className="font-medium">Capture en cours...</p>
                  <p className="text-sm text-gray-300 mt-2">Vérification ICAO en cours</p>
                </div>
              </div>
            )}

            {photoData && (
              <div className="space-y-4">
                {/* Prévisualisation */}
                <div className="relative w-full aspect-[3/4] bg-gray-100 border-2 border-gray-300 rounded-lg overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-200">
                    <svg className="w-32 h-32 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>

                  {/* Badge de conformité */}
                  <div className="absolute top-4 right-4">
                    {photoData.icaoCompliant ? (
                      <div className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full flex items-center space-x-1">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>ICAO OK</span>
                      </div>
                    ) : (
                      <div className="px-3 py-1 bg-yellow-500 text-white text-xs font-bold rounded-full flex items-center space-x-1">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        <span>Non conforme</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Score de qualité */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Qualité de la photo</span>
                    <span className={`text-2xl font-bold ${photoData.quality >= 90 ? 'text-green-600' : photoData.quality >= 75 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {photoData.quality}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${photoData.quality >= 90 ? 'bg-green-500' : photoData.quality >= 75 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${photoData.quality}%` }}
                    ></div>
                  </div>
                </div>

                <button
                  onClick={handleRetake}
                  className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                >
                  Reprendre la photo
                </button>
              </div>
            )}
          </div>

          {/* Vérifications ICAO */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Vérifications ICAO
            </h3>

            {!photoData && (
              <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="text-sm font-bold text-blue-900 mb-3">📋 Exigences ICAO :</h4>
                <ul className="text-sm text-blue-800 space-y-2">
                  <li>• Visage de face, regard vers la caméra</li>
                  <li>• Yeux ouverts, expression neutre (bouche fermée)</li>
                  <li>• Sans lunettes de soleil ou accessoires</li>
                  <li>• Fond uni de couleur claire (blanc, gris clair)</li>
                  <li>• Éclairage uniforme, sans ombres sur le visage</li>
                  <li>• Photo nette, résolution minimum 600 DPI</li>
                  <li>• Tête centrée, occupant 70-80% du cadre</li>
                  <li>• Pas de reflets ou de sur-exposition</li>
                </ul>
              </div>
            )}

            {photoData && (
              <div className="space-y-3">
                {/* Liste des vérifications */}
                {(Object.keys(photoData.checks) as Array<keyof PhotoData['checks']>).map((check) => (
                  <div
                    key={check}
                    className={`flex items-center justify-between p-3 rounded-lg border ${
                      photoData.checks[check]
                        ? 'bg-green-50 border-green-200'
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <span className={`text-sm font-medium ${
                      photoData.checks[check] ? 'text-green-900' : 'text-red-900'
                    }`}>
                      {getCheckLabel(check)}
                    </span>
                    {getCheckIcon(photoData.checks[check])}
                  </div>
                ))}

                {/* Résultat global */}
                <div className={`mt-6 p-4 rounded-lg border-2 ${
                  photoData.icaoCompliant
                    ? 'bg-green-50 border-green-300'
                    : 'bg-yellow-50 border-yellow-300'
                }`}>
                  <div className="flex items-start space-x-3">
                    {photoData.icaoCompliant ? (
                      <svg className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    )}
                    <div>
                      <h4 className={`text-sm font-bold ${
                        photoData.icaoCompliant ? 'text-green-900' : 'text-yellow-900'
                      }`}>
                        {photoData.icaoCompliant
                          ? 'Photo conforme aux normes ICAO'
                          : 'Photo partiellement conforme'}
                      </h4>
                      <p className={`text-xs mt-1 ${
                        photoData.icaoCompliant ? 'text-green-700' : 'text-yellow-700'
                      }`}>
                        {photoData.icaoCompliant
                          ? 'Tous les critères essentiels sont respectés. Vous pouvez continuer.'
                          : 'Certains critères ne sont pas respectés. Vous pouvez reprendre la photo ou continuer si acceptable.'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
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
          disabled={!photoData}
          className={`
            px-6 py-3 rounded-lg font-medium transition
            ${
              photoData
                ? 'bg-secondary-600 text-white hover:bg-secondary-700'
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

