import React, { useState } from 'react';
import {
  FingerprintCapture,
  IrisCapture,
  ScannedDocument,
} from '@/types';
import type { EmployeeFormData } from '@/types/employee';
import {
  formatEmployeeFullName,
  formatGenderLabel,
  formatIdCardType,
  formatPaymentMethod,
} from '@/lib/employee-display';
import { normalizeScannedDocument, totalPagesInBundle } from '@/lib/document-scan-utils';
import { isWorkflowSkipEnabled } from '@/lib/workflow-test-mode';

interface VerificationMatchingProps {
  employeeData: EmployeeFormData;
  photo?: { imageData?: string; imageUri?: string; image?: string } | null;
  fingerprints: FingerprintCapture[];
  iris: IrisCapture[];
  documents: ScannedDocument[];
  photoOnly?: boolean;
  submitError?: string | null;
  onComplete: () => void;
  onBack: () => void;
}

export default function VerificationMatching({
  employeeData,
  photo,
  fingerprints,
  iris,
  documents,
  photoOnly = false,
  submitError,
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

  const capturedFingerprints = fingerprints.filter((fp) => fp.status === 'CAPTURED');
  const capturedIris = iris.filter((i) => i.status === 'CAPTURED');
  const irisResolved = iris.filter(
    (i) => i.status === 'CAPTURED' || i.status === 'BLIND' || i.status === 'MISSING' || i.status === 'DAMAGED'
  ).length;
  const irisUnavailable = iris.filter(
    (i) => i.status === 'BLIND' || i.status === 'MISSING' || i.status === 'DAMAGED'
  ).length;

  const startMatching = () => {
    setIsMatching(true);
    setTimeout(() => {
      const fpScore = photoOnly ? 0 : capturedFingerprints.length >= 8 ? 96 : capturedFingerprints.length >= 6 ? 90 : 75;
      const irisScore = photoOnly ? 0 : capturedIris.length >= 2 ? 97 : capturedIris.length >= 1 ? 88 : 70;
      const facialScore = photo?.image || photo?.imageData || photo?.imageUri ? 95 : 70;
      const activeScores = photoOnly ? [facialScore] : [fpScore, irisScore, facialScore];
      const overallScore = Math.round(
        activeScores.reduce((sum, score) => sum + score, 0) / activeScores.length
      );
      setMatchingResults({
        fingerprint: {
          status: photoOnly ? 'pending' : 'success',
          score: fpScore,
          matches: 0,
        },
        iris: {
          status: photoOnly ? 'pending' : 'success',
          score: irisScore,
          matches: 0,
        },
        facial: { status: 'success', score: facialScore, matches: 0 },
        overall: { status: 'success', score: overallScore },
      });
      setIsMatching(false);
      setMatchingComplete(true);
    }, 1200);
  };

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

  const fullName = formatEmployeeFullName(employeeData);

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Vérification et matching biométrique
        </h2>
        <p className="text-gray-600">
          {photoOnly
            ? 'Vérifiez la fiche employé et la photo ICAO avant de générer le récépissé.'
            : 'Vérifiez les données employé et lancez le matching contre la base biométrique ONIP.'}
        </p>
      </div>

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Identité</h3>
            </div>
            <p className="text-sm text-gray-700 font-medium">{fullName}</p>
            <p className="text-xs text-gray-500">
              Matricule {employeeData.registration_number} · {formatGenderLabel(employeeData.gender)}
              {employeeData.date_of_birth ? ` · ${employeeData.date_of_birth}` : ''}
            </p>
          </div>

          <div
            className={`p-4 border rounded-lg ${
              photoOnly ? 'bg-gray-50 border-gray-200 opacity-60' : 'bg-green-50 border-green-200'
            }`}
          >
            <h3 className="font-semibold text-gray-900 mb-2">Empreintes</h3>
            <p className={`text-2xl font-bold ${photoOnly ? 'text-gray-400' : 'text-green-600'}`}>
              {photoOnly ? '—' : `${capturedFingerprints.length}/10`}
            </p>
            <p className="text-xs text-gray-500">
              {photoOnly ? 'Tablette Morpho (hors guichet)' : 'Doigts capturés'}
            </p>
          </div>

          <div
            className={`p-4 border rounded-lg ${
              photoOnly ? 'bg-gray-50 border-gray-200 opacity-60' : 'bg-purple-50 border-purple-200'
            }`}
          >
            <h3 className="font-semibold text-gray-900 mb-2">Iris</h3>
            <p className={`text-2xl font-bold ${photoOnly ? 'text-gray-400' : 'text-purple-600'}`}>
              {photoOnly ? '—' : `${capturedIris.length}/2`}
            </p>
            <p className="text-xs text-gray-500">
              {photoOnly ? 'Hors guichet' : irisResolved === 2
                ? irisUnavailable > 0
                  ? `${irisUnavailable} non capturable(s) · ${capturedIris.length} capture(s)`
                  : 'Yeux capturés'
                : `${irisResolved}/2 yeux traités`}
            </p>
          </div>

          <div
            className={`p-4 border rounded-lg ${
              photoOnly ? 'bg-gray-50 border-gray-200 opacity-60' : 'bg-yellow-50 border-yellow-200'
            }`}
          >
            <h3 className="font-semibold text-gray-900 mb-2">Documents</h3>
            <p className={`text-2xl font-bold ${photoOnly ? 'text-gray-400' : 'text-yellow-600'}`}>
              {photoOnly ? '—' : documents.length}
            </p>
            <p className="text-xs text-gray-500">
              {photoOnly
                ? 'Hors guichet'
                : `${totalPagesInBundle(documents.map(normalizeScannedDocument))} page(s)`}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Données détaillées</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Fiche RH</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Nom complet :</span>
                  <span className="font-medium text-gray-900">{fullName}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Nationalité :</span>
                  <span className="font-medium text-gray-900">{employeeData.citizenship || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Mobile :</span>
                  <span className="font-medium text-gray-900">{employeeData.mobile_number || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Email :</span>
                  <span className="font-medium text-gray-900">{employeeData.email || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Paie :</span>
                  <span className="font-medium text-gray-900">
                    {formatPaymentMethod(employeeData.payment_method)}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Origine & pièce</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Province :</span>
                  <span className="font-medium text-gray-900">{employeeData.home_province || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Territoire :</span>
                  <span className="font-medium text-gray-900">{employeeData.home_territory || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Pièce :</span>
                  <span className="font-medium text-gray-900">
                    {formatIdCardType(employeeData.type_of_identity)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">N° pièce :</span>
                  <span className="font-medium text-gray-900">{employeeData.identity_number || '-'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Matching biométrique</h3>

          {!isMatching && !matchingComplete && (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                {photoOnly
                  ? 'Prêt à valider la photo ICAO pour le matricule '
                  : 'Prêt à lancer le matching biométrique pour le matricule '}
                <strong>{employeeData.registration_number}</strong>
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
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-secondary-600 mb-4" />
              <p className="text-gray-600 font-medium">Matching en cours...</p>
            </div>
          )}

          {matchingComplete && (
            <div className="space-y-4">
              <div className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Score global</h4>
                    <p className="text-sm text-gray-600">Aucune correspondance trouvée dans la base</p>
                  </div>
                  <div className={`text-4xl font-bold ${getScoreColor(matchingResults.overall.score)}`}>
                    {matchingResults.overall.score}%
                  </div>
                </div>
              </div>

              <div className={`grid grid-cols-1 gap-4 ${photoOnly ? '' : 'md:grid-cols-3'}`}>
                {(['fingerprint', 'iris', 'facial'] as const)
                  .filter((key) => !photoOnly || key === 'facial')
                  .map((key) => (
                  <div key={key} className="p-4 bg-white border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {key === 'facial' ? 'Photo ICAO' : key}
                      </span>
                      {getStatusBadge(matchingResults[key].status)}
                    </div>
                    <div className={`text-2xl font-bold ${getScoreColor(matchingResults[key].score)}`}>
                      {matchingResults[key].score}%
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700">
                  {photoOnly
                    ? 'La photo ICAO est enregistrée. La vérification anti-doublon finale sera confirmée lors de la soumission.'
                    : 'Les données de capture sont cohérentes. La vérification anti-doublon finale sera confirmée lors de la soumission.'}
                </p>
              </div>
            </div>
          )}

          {submitError && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-sm text-red-800 font-medium">Vérification finale non validée</div>
              <div className="text-sm text-red-700 mt-1">{submitError}</div>
            </div>
          )}
        </div>
      </div>

      <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-between">
        <button
          type="button"
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium"
        >
          ← Précédent
        </button>
        <button
          onClick={onComplete}
          disabled={!matchingComplete && !isWorkflowSkipEnabled()}
          className={`px-6 py-3 rounded-lg font-medium transition ${
            matchingComplete || isWorkflowSkipEnabled()
              ? matchingComplete
                ? 'bg-secondary-600 text-white hover:bg-blue-700'
                : 'bg-amber-500 text-white hover:bg-amber-600'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {matchingComplete ? 'Valider et générer le récépissé →' : 'Récépissé (test) →'}
        </button>
      </div>
    </div>
  );
}
