'use client';

import React, { useState, useEffect } from 'react';
import { EnrollmentRequest, PersonCore, BiometricData, StrataType } from '../../types';
import { apiService } from '../../services/api';

interface EnrollmentFormProps {
  onSuccess: (response: any) => void;
  onError: (error: string) => void;
}

const EnrollmentForm: React.FC<EnrollmentFormProps> = ({ onSuccess, onError }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedStrata, setSelectedStrata] = useState<StrataType[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form data states
  const [coreData, setCoreData] = useState<Partial<PersonCore>>({
    sexe: 'M',
    statut_matrimonial: 'Célibataire',
    nationalite: 'Congolaise',
    niveau_etude: 'Primaire',
    type_piece: 'Acte de naissance',
  });

  const [biometricData, setBiometricData] = useState<Partial<BiometricData>>({});
  const [extensions, setExtensions] = useState<Record<string, any>>({});
  const [attachments, setAttachments] = useState<File[]>([]);

  const totalSteps = 6;

  // Available strata
  const availableStrata: { value: StrataType; label: string; description: string }[] = [
    { value: 'ELEVES', label: 'Élève', description: 'Élève du primaire ou secondaire' },
    { value: 'ETUDIANT', label: 'Étudiant', description: 'Étudiant du supérieur' },
    { value: 'ELECTEUR', label: 'Électeur', description: 'Citoyen en âge de voter (18+)' },
    { value: 'PNC', label: 'Policier', description: 'Membre de la Police Nationale' },
    { value: 'FARDC', label: 'Militaire', description: 'Membre des Forces Armées' },
    { value: 'PRISON', label: 'Détenu', description: 'Personne incarcérée' },
    { value: 'REFUGIE', label: 'Réfugié', description: 'Réfugié ou demandeur d\'asile' },
    { value: 'ENFANT', label: 'Enfant', description: 'Mineur non scolarisé' },
    { value: 'FONCTIONNAIRE', label: 'Fonctionnaire', description: 'Agent de l\'État' },
  ];

  const handleStrataToggle = (strata: StrataType) => {
    setSelectedStrata(prev => 
      prev.includes(strata) 
        ? prev.filter(s => s !== strata)
        : [...prev, strata]
    );
  };

  const handleCoreDataChange = (field: keyof PersonCore, value: string) => {
    setCoreData(prev => ({ ...prev, [field]: value }));
  };

  const handleExtensionChange = (strata: string, field: string, value: any) => {
    setExtensions(prev => ({
      ...prev,
      [strata]: {
        ...prev[strata],
        [field]: value,
      },
    }));
  };

  const handleBiometricUpload = async (type: 'face' | 'fingerprints' | 'iris', file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const result = await apiService.uploadBiometric(formData);
      
      setBiometricData(prev => ({
        ...prev,
        [`${type}_uri`]: result.uri,
        [`${type}_quality`]: result.quality,
      }));
    } catch (error) {
      onError(`Erreur lors de l'upload biométrique: ${error}`);
    }
  };

  const handleDocumentUpload = async (file: File, type: string) => {
    try {
      const result = await apiService.uploadDocument(file, type);
      // Add to attachments list
      console.log('Document uploaded:', result);
    } catch (error) {
      onError(`Erreur lors de l'upload du document: ${error}`);
    }
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1: // Strata selection
        return selectedStrata.length > 0;
      case 2: // Core data
        return !!(
          coreData.nom && 
          coreData.prenom && 
          coreData.date_naissance && 
          coreData.lieu_naissance &&
          coreData.nom_pere &&
          coreData.nom_mere
        );
      case 3: // Extensions
        return true; // Optional for now
      case 4: // Biometrics
        return !!(
          biometricData.face_uri && 
          biometricData.fingerprints_uri
        );
      case 5: // Documents
        return attachments.length > 0;
      default:
        return true;
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) {
      onError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setIsSubmitting(true);

    try {
      const enrollmentRequest: EnrollmentRequest = {
        core: coreData as PersonCore,
        biometrics: biometricData as BiometricData,
        strata: selectedStrata,
        extensions,
        attachments: attachments.map(file => ({
          type: 'document',
          uri: '', // Will be set after upload
          hash: '',
          filename: file.name,
          size: file.size,
          mime_type: file.type,
        })),
        metadata: {
          device_id: 'WEB-001',
          operator_id: 'USER-001',
          location: {
            province: 'Kinshasa',
            territoire: 'Funa',
            commune: 'Kalamu',
          },
          timestamp: new Date().toISOString(),
        },
      };

      const response = await apiService.submitEnrollment(enrollmentRequest);
      onSuccess(response);
    } catch (error) {
      onError(`Erreur lors de l'enrôlement: ${error}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            Étape {currentStep} sur {totalSteps}
          </span>
          <span className="text-sm text-gray-500">
            {Math.round((currentStep / totalSteps) * 100)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(currentStep / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      {/* Step 1: Strata Selection */}
      {currentStep === 1 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Sélection de la Strata</h2>
          <p className="text-gray-600 mb-6">
            Sélectionnez la ou les strates auxquelles appartient cette personne :
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableStrata.map((strata) => (
              <div
                key={strata.value}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedStrata.includes(strata.value)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleStrataToggle(strata.value)}
              >
                <h3 className="font-semibold text-lg">{strata.label}</h3>
                <p className="text-sm text-gray-600">{strata.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: Core Data */}
      {currentStep === 2 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Informations Personnelles</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom *
              </label>
              <input
                type="text"
                value={coreData.nom || ''}
                onChange={(e) => handleCoreDataChange('nom', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Postnom
              </label>
              <input
                type="text"
                value={coreData.postnom || ''}
                onChange={(e) => handleCoreDataChange('postnom', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prénom *
              </label>
              <input
                type="text"
                value={coreData.prenom || ''}
                onChange={(e) => handleCoreDataChange('prenom', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sexe *
              </label>
              <select
                value={coreData.sexe || 'M'}
                onChange={(e) => handleCoreDataChange('sexe', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="M">Masculin</option>
                <option value="F">Féminin</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date de naissance *
              </label>
              <input
                type="date"
                value={coreData.date_naissance || ''}
                onChange={(e) => handleCoreDataChange('date_naissance', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lieu de naissance *
              </label>
              <input
                type="text"
                value={coreData.lieu_naissance || ''}
                onChange={(e) => handleCoreDataChange('lieu_naissance', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom du père *
              </label>
              <input
                type="text"
                value={coreData.nom_pere || ''}
                onChange={(e) => handleCoreDataChange('nom_pere', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom de la mère *
              </label>
              <input
                type="text"
                value={coreData.nom_mere || ''}
                onChange={(e) => handleCoreDataChange('nom_mere', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Extensions */}
      {currentStep === 3 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Informations Spécifiques par Strata</h2>
          
          {selectedStrata.map((strata) => (
            <div key={strata} className="mb-6 p-4 border rounded-lg">
              <h3 className="text-lg font-semibold mb-4">
                {availableStrata.find(s => s.value === strata)?.label}
              </h3>
              
              {strata === 'ELEVES' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Matricule scolaire
                    </label>
                    <input
                      type="text"
                      value={extensions[strata]?.matricule_scolaire || ''}
                      onChange={(e) => handleExtensionChange(strata, 'matricule_scolaire', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Établissement
                    </label>
                    <input
                      type="text"
                      value={extensions[strata]?.etablissement || ''}
                      onChange={(e) => handleExtensionChange(strata, 'etablissement', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              )}
              
              {/* Add other strata forms here */}
            </div>
          ))}
        </div>
      )}

      {/* Step 4: Biometrics */}
      {currentStep === 4 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Capture Biométrique</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 border rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Photo du visage</h3>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleBiometricUpload('face', file);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              {biometricData.face_uri && (
                <p className="text-sm text-green-600 mt-2">
                  ✓ Photo capturée (Qualité: {biometricData.face_quality?.toFixed(2)})
                </p>
              )}
            </div>

            <div className="p-4 border rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Empreintes digitales</h3>
              <input
                type="file"
                accept=".iso,.wsq"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleBiometricUpload('fingerprints', file);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
              {biometricData.fingerprints_uri && (
                <p className="text-sm text-green-600 mt-2">
                  ✓ Empreintes capturées (Qualité: {biometricData.fingerprints_quality?.toFixed(2)})
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Step 5: Documents */}
      {currentStep === 5 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Documents Justificatifs</h2>
          
          <div className="space-y-4">
            <div className="p-4 border rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Acte de naissance</h3>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleDocumentUpload(file, 'acte_naissance');
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>

            <div className="p-4 border rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Autres documents</h3>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                multiple
                onChange={(e) => {
                  const files = Array.from(e.target.files || []);
                  files.forEach(file => handleDocumentUpload(file, 'autre'));
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        </div>
      )}

      {/* Step 6: Review & Submit */}
      {currentStep === 6 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Récapitulatif et Validation</h2>
          
          <div className="space-y-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">Informations personnelles</h3>
              <p><strong>Nom:</strong> {coreData.nom} {coreData.postnom} {coreData.prenom}</p>
              <p><strong>Sexe:</strong> {coreData.sexe}</p>
              <p><strong>Date de naissance:</strong> {coreData.date_naissance}</p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">Strates sélectionnées</h3>
              <ul className="list-disc list-inside">
                {selectedStrata.map(strata => (
                  <li key={strata}>
                    {availableStrata.find(s => s.value === strata)?.label}
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">Biométrie</h3>
              <p>Photo: {biometricData.face_uri ? '✓ Capturée' : '✗ Manquante'}</p>
              <p>Empreintes: {biometricData.fingerprints_uri ? '✓ Capturées' : '✗ Manquantes'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between mt-8">
        <button
          onClick={prevStep}
          disabled={currentStep === 1}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-400"
        >
          Précédent
        </button>

        {currentStep < totalSteps ? (
          <button
            onClick={nextStep}
            disabled={!validateStep(currentStep)}
            className="px-6 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
          >
            Suivant
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !validateStep(currentStep)}
            className="px-6 py-2 bg-green-600 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-green-700"
          >
            {isSubmitting ? 'Envoi en cours...' : 'Soumettre l\'enrôlement'}
          </button>
        )}
      </div>
    </div>
  );
};

export default EnrollmentForm;
