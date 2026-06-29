import React, { useState } from 'react';
import { 
  BaseEnrollmentData, 
  FingerprintCapture, 
  IrisCapture, 
  ScannedDocument 
} from '@/types';

interface VerificationMatchingProps {
  baseData: BaseEnrollmentData;
  extensions: Record<string, any>;
  fingerprints: FingerprintCapture[];
  iris: IrisCapture[];
  documents: ScannedDocument[];
  onComplete: () => void;
  onBack: () => void;
}

export default function VerificationMatching({
  baseData,
  extensions,
  fingerprints,
  iris,
  documents,
  onComplete,
  onBack,
}: VerificationMatchingProps) {
  const [isMatching, setIsMatching] = useState(false);
  const [matchingComplete, setMatchingComplete] = useState(false);
  const [matchingResults, setMatchingResults] = useState({
    fingerprint: { status: 'pending', score: 0, matches: 0 },
    iris: { status: 'pending', score: 0, matches: 0 },
    facial: { status: 'pending', score: 0, matches: 0 },
    overall: { status: 'pending', score: 0 },
  });

  const startMatching = () => {
    setIsMatching(true);

    // Simulation du matching biométrique
    setTimeout(() => {
      setMatchingResults({
        fingerprint: {
          status: 'success',
          score: Math.floor(Math.random() * 10) + 90,
          matches: 0,
        },
        iris: {
          status: 'success',
          score: Math.floor(Math.random() * 8) + 92,
          matches: 0,
        },
        facial: {
          status: 'success',
          score: Math.floor(Math.random() * 12) + 88,
          matches: 0,
        },
        overall: {
          status: 'success',
          score: Math.floor(Math.random() * 5) + 95,
        },
      });
      setIsMatching(false);
      setMatchingComplete(true);
    }, 5000);
  };

  const capturedFingerprints = fingerprints.filter((fp) => fp.status === 'CAPTURED');
  const capturedIris = iris.filter((i) => i.status === 'CAPTURED');

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <span className="px-3 py-1 text-xs font-semibold text-gray-600 bg-gray-200 rounded-full">
            En attente
          </span>
        );
      case 'processing':
        return (
          <span className="px-3 py-1 text-xs font-semibold text-blue-600 bg-blue-100 rounded-full animate-pulse">
            Traitement...
          </span>
        );
      case 'success':
        return (
          <span className="px-3 py-1 text-xs font-semibold text-green-600 bg-green-100 rounded-full">
            ✓ Vérifié
          </span>
        );
      default:
        return null;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 95) return 'text-green-600';
    if (score >= 85) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* En-tête */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Vérification et matching biométrique
        </h2>
        <p className="text-gray-600">
          Vérifiez les données et lancez le matching biométrique contre la base de données nationale.
        </p>
      </div>

      {/* Corps */}
      <div className="p-6 space-y-6">
        {/* Résumé des données */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Identité */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Identité</h3>
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <p className="text-sm text-gray-700 font-medium">
              {baseData.prenom} {baseData.nom}
            </p>
            <p className="text-xs text-gray-500">
              {baseData.sexe === 'M' ? 'Masculin' : 'Féminin'} • {baseData.date_naissance}
            </p>
          </div>

          {/* Empreintes */}
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Empreintes</h3>
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-green-600">
              {capturedFingerprints.length}/10
            </p>
            <p className="text-xs text-gray-500">Doigts capturés</p>
          </div>

          {/* Iris */}
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Iris</h3>
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-purple-600">
              {capturedIris.length}/2
            </p>
            <p className="text-xs text-gray-500">Yeux capturés</p>
          </div>

          {/* Documents */}
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Documents</h3>
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-yellow-600">{documents.length}</p>
            <p className="text-xs text-gray-500">Pièces scannées</p>
          </div>
        </div>

        {/* Données détaillées */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Données détaillées</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Informations personnelles */}
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Informations personnelles</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Nom complet :</span>
                  <span className="font-medium text-gray-900">
                    {baseData.prenom} {baseData.nom} {baseData.postnom}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Nationalité :</span>
                  <span className="font-medium text-gray-900">{baseData.nationalite}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Téléphone :</span>
                  <span className="font-medium text-gray-900">{baseData.telephone || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Email :</span>
                  <span className="font-medium text-gray-900">{baseData.email || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Localisation */}
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Résidence actuelle</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Province :</span>
                  <span className="font-medium text-gray-900">{baseData.residence_province}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Ville :</span>
                  <span className="font-medium text-gray-900">{baseData.residence_ville}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Commune :</span>
                  <span className="font-medium text-gray-900">{baseData.residence_commune}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Quartier :</span>
                  <span className="font-medium text-gray-900">{baseData.residence_quartier}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Strate */}
          <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <h4 className="font-semibold text-gray-900 mb-3">Strate(s) sélectionnée(s)</h4>
            <div className="flex flex-wrap gap-2">
              {(Array.isArray(baseData.strata) ? baseData.strata : [baseData.strata]).map((strate) => (
                <span
                  key={strate}
                  className="px-3 py-1 bg-indigo-100 text-indigo-800 text-sm font-medium rounded-full"
                >
                  {strate}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Section de matching */}
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Matching biométrique
          </h3>

          {!isMatching && !matchingComplete && (
            <div className="text-center py-8">
              <div className="mb-4">
                <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <p className="text-gray-600 mb-4">
                Prêt à lancer le matching biométrique contre la base de données nationale
              </p>
              <button
                onClick={startMatching}
                className="px-6 py-3 bg-secondary-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
              >
                Lancer le matching
              </button>
            </div>
          )}

          {isMatching && (
            <div className="space-y-4">
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-secondary-600 mb-4"></div>
                <p className="text-gray-600 font-medium">Matching en cours...</p>
                <p className="text-sm text-gray-500 mt-2">Comparaison avec la base de données nationale</p>
              </div>

              {/* Barre de progression des étapes */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">Empreintes digitales</div>
                    <div className="text-xs text-gray-500">Comparaison des {capturedFingerprints.length} empreintes...</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">Iris</div>
                    <div className="text-xs text-gray-500">Comparaison des {capturedIris.length} iris...</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">Reconnaissance faciale</div>
                    <div className="text-xs text-gray-500">Analyse en cours...</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {matchingComplete && (
            <div className="space-y-4">
              {/* Score global */}
              <div className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Score global</h4>
                    <p className="text-sm text-gray-600">Aucune correspondance trouvée dans la base</p>
                  </div>
                  <div className="text-right">
                    <div className={`text-4xl font-bold ${getScoreColor(matchingResults.overall.score)}`}>
                      {matchingResults.overall.score}%
                    </div>
                    <div className="text-sm text-gray-500">Nouveau profil</div>
                  </div>
                </div>
              </div>

              {/* Détails par modalité */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Empreintes</span>
                    {getStatusBadge(matchingResults.fingerprint.status)}
                  </div>
                  <div className={`text-2xl font-bold ${getScoreColor(matchingResults.fingerprint.score)}`}>
                    {matchingResults.fingerprint.score}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">0 correspondance</p>
                </div>

                <div className="p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Iris</span>
                    {getStatusBadge(matchingResults.iris.status)}
                  </div>
                  <div className={`text-2xl font-bold ${getScoreColor(matchingResults.iris.score)}`}>
                    {matchingResults.iris.score}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">0 correspondance</p>
                </div>

                <div className="p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Facial</span>
                    {getStatusBadge(matchingResults.facial.status)}
                  </div>
                  <div className={`text-2xl font-bold ${getScoreColor(matchingResults.facial.score)}`}>
                    {matchingResults.facial.score}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">0 correspondance</p>
                </div>
              </div>

              {/* Message de validation */}
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-green-800">Vérification réussie</h3>
                    <p className="text-sm text-green-700 mt-1">
                      Les données biométriques sont de bonne qualité et aucune duplication n'a été détectée.
                      Vous pouvez procéder à la validation finale.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Pied de page */}
      <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-between">
        <button
          onClick={onBack}
          disabled={isMatching}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Précédent
        </button>

        <button
          onClick={onComplete}
          disabled={!matchingComplete}
          className={`
            px-6 py-3 rounded-lg font-medium transition
            ${
              matchingComplete
                ? 'bg-secondary-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          Valider et générer le récépissé →
        </button>
      </div>
    </div>
  );
}

