'use client';

import React, { useState } from 'react';
import BaseEnrollmentForm from './BaseEnrollmentForm';
import StrataExtensionsForms from './StrataExtensionsForms';
import PhotoCapture, { PhotoData } from '../biometrics/PhotoCapture';
import FingerprintCapture from '../biometrics/FingerprintCapture';
import IrisCapture from '../biometrics/IrisCapture';
import DocumentScan from '../biometrics/DocumentScan';
import VerificationMatching from '../biometrics/VerificationMatching';
import EnrollmentReceipt from '../biometrics/EnrollmentReceipt';
import {
  BaseEnrollmentData,
  FingerprintCapture as FingerprintData,
  IrisCapture as IrisData,
  ScannedDocument,
} from '@/types';

type WorkflowStep = 
  | 'base' 
  | 'extensions' 
  | 'photo'
  | 'fingerprints' 
  | 'iris' 
  | 'documents' 
  | 'verification' 
  | 'receipt';

const STEP_LABELS: Record<WorkflowStep, string> = {
  base: 'Formulaire de base',
  extensions: 'Extensions strate',
  photo: 'Photo d\'identité',
  fingerprints: 'Empreintes digitales',
  iris: 'Capture iris',
  documents: 'Documents',
  verification: 'Vérification',
  receipt: 'Récépissé',
};

const STEP_ORDER: WorkflowStep[] = [
  'base',
  'extensions',
  'photo',
  'fingerprints',
  'iris',
  'documents',
  'verification',
  'receipt',
];

export default function EnrollmentWorkflow() {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('base');
  const [baseData, setBaseData] = useState<BaseEnrollmentData | null>(null);
  const [extensions, setExtensions] = useState<Record<string, any>>({});
  const [photo, setPhoto] = useState<PhotoData | null>(null);
  const [fingerprints, setFingerprints] = useState<FingerprintData[]>([]);
  const [iris, setIris] = useState<IrisData[]>([]);
  const [documents, setDocuments] = useState<ScannedDocument[]>([]);
  const [enrollmentId, setEnrollmentId] = useState<string>('');

  const getCurrentStepIndex = () => STEP_ORDER.indexOf(currentStep);
  const totalSteps = STEP_ORDER.length;

  const goToNextStep = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < STEP_ORDER.length - 1) {
      setCurrentStep(STEP_ORDER[currentIndex + 1]);
    }
  };

  const goToPreviousStep = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      setCurrentStep(STEP_ORDER[currentIndex - 1]);
    }
  };

  const handleBaseFormComplete = (data: BaseEnrollmentData) => {
    setBaseData(data);
    goToNextStep();
  };

  const handleExtensionsComplete = (extensionData: Record<string, any>) => {
    setExtensions(extensionData);
    goToNextStep();
  };

  const handlePhotoComplete = (photoData: PhotoData) => {
    setPhoto(photoData);
    goToNextStep();
  };

  const handleFingerprintsComplete = (fingerprintData: FingerprintData[]) => {
    setFingerprints(fingerprintData);
    goToNextStep();
  };

  const handleIrisComplete = (irisData: IrisData[]) => {
    setIris(irisData);
    goToNextStep();
  };

  const handleDocumentsComplete = (documentData: ScannedDocument[]) => {
    setDocuments(documentData);
    goToNextStep();
  };

  const handleVerificationComplete = () => {
    // Générer un ID d'enrôlement unique
    const id = `FGP-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
    setEnrollmentId(id);
    goToNextStep();
  };

  const handleNewEnrollment = () => {
    // Réinitialiser tout le workflow
    setCurrentStep('base');
    setBaseData(null);
    setExtensions({});
    setPhoto(null);
    setFingerprints([]);
    setIris([]);
    setDocuments([]);
    setEnrollmentId('');
  };

  const renderProgressBar = () => {
    const currentIndex = getCurrentStepIndex();
    const progress = ((currentIndex + 1) / totalSteps) * 100;

    return (
      <div className="w-full bg-white border-b border-gray-200 p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          {/* Barre de progression */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span className="font-medium">
                Étape {currentIndex + 1} sur {totalSteps}: {STEP_LABELS[currentStep]}
              </span>
              <span className="font-semibold">{Math.round(progress)}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* Indicateurs d'étapes */}
          <div className="flex justify-between items-center">
            {STEP_ORDER.map((step, index) => {
              const isCompleted = index < currentIndex;
              const isCurrent = index === currentIndex;
              const isFuture = index > currentIndex;

              return (
                <div key={step} className="flex flex-col items-center flex-1">
                  <div
                    className={`
                      w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-1 transition-all
                      ${isCompleted ? 'bg-green-500 text-white' : ''}
                      ${isCurrent ? 'bg-blue-600 text-white ring-4 ring-blue-200' : ''}
                      ${isFuture ? 'bg-gray-200 text-gray-500' : ''}
                    `}
                  >
                    {isCompleted ? '✓' : index + 1}
                  </div>
                  <span
                    className={`
                      text-xs font-medium text-center hidden md:block
                      ${isCompleted ? 'text-green-600' : ''}
                      ${isCurrent ? 'text-blue-600' : ''}
                      ${isFuture ? 'text-gray-400' : ''}
                    `}
                  >
                    {STEP_LABELS[step]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Barre de progression */}
      {renderProgressBar()}

      {/* Contenu de l'étape actuelle */}
      <div className="p-4 md:p-6">
        {currentStep === 'base' && (
          <BaseEnrollmentForm onNext={handleBaseFormComplete} />
        )}

        {currentStep === 'extensions' && baseData && (
          <StrataExtensionsForms
            strata={baseData.strata}
            baseData={baseData}
            onSubmit={handleExtensionsComplete}
            onBack={goToPreviousStep}
          />
        )}

        {currentStep === 'photo' && (
          <PhotoCapture
            onComplete={handlePhotoComplete}
            onBack={goToPreviousStep}
          />
        )}

        {currentStep === 'fingerprints' && (
          <FingerprintCapture
            onComplete={handleFingerprintsComplete}
            onBack={goToPreviousStep}
          />
        )}

        {currentStep === 'iris' && (
          <IrisCapture
            onComplete={handleIrisComplete}
            onBack={goToPreviousStep}
          />
        )}

        {currentStep === 'documents' && (
          <DocumentScan
            onComplete={handleDocumentsComplete}
            onBack={goToPreviousStep}
          />
        )}

        {currentStep === 'verification' && baseData && (
          <VerificationMatching
            baseData={baseData}
            extensions={extensions}
            fingerprints={fingerprints}
            iris={iris}
            documents={documents}
            onComplete={handleVerificationComplete}
            onBack={goToPreviousStep}
          />
        )}

        {currentStep === 'receipt' && baseData && enrollmentId && (
          <EnrollmentReceipt
            enrollmentId={enrollmentId}
            baseData={baseData}
            onNewEnrollment={handleNewEnrollment}
          />
        )}
      </div>
    </div>
  );
}
