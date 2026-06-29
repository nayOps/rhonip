'use client';

import React, { useState } from 'react';

type StrataType = 
  | 'ENFANT'
  | 'ELEVES'
  | 'ELECTEUR'
  | 'PNC'
  | 'FARDC'
  | 'PRISON'
  | 'REFUGIE'
  | 'DEPLACE'
  | 'ETRANGER'
  | 'DIASPORA';

interface StrataExtensionsFormsProps {
  strata: string[] | string;
  baseData: any;
  onSubmit: (extensionData: any) => void;
  onBack: () => void;
}

// ============================================
// EXTENSION : ENFANT / ÉLÈVE
// ============================================
const EleveExtensionForm: React.FC<{ onSubmit: (data: any) => void; onBack: () => void }> = ({ onSubmit, onBack }) => {
  const [formData, setFormData] = useState({
    numeroPermanentScolaire: '',
    maternelleEtablissement: '',
    maternelleLieu: '',
    maternelleAnnee: '',
    primaireEtablissement: '',
    primaireLieu: '',
    primaireAnnee: '',
    secondaireEtablissement: '',
    secondaireLieu: '',
    secondaireAnnee: '',
    autresFormations: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          3.1 Parcours Scolaire <span className="text-error-600">*</span>
        </h3>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Numéro permanent scolaire
          </label>
          <input
            type="text"
            value={formData.numeroPermanentScolaire}
            onChange={(e) => handleChange('numeroPermanentScolaire', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            placeholder="Ex: 123456789"
          />
        </div>

        {/* Maternelle */}
        <div className="mb-6">
          <h4 className="font-medium text-gray-800 mb-3">Maternelle</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Établissement</label>
              <input
                type="text"
                value={formData.maternelleEtablissement}
                onChange={(e) => handleChange('maternelleEtablissement', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lieu</label>
              <input
                type="text"
                value={formData.maternelleLieu}
                onChange={(e) => handleChange('maternelleLieu', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Année</label>
              <input
                type="text"
                value={formData.maternelleAnnee}
                onChange={(e) => handleChange('maternelleAnnee', e.target.value)}
                placeholder="Ex: 2015-2018"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
          </div>
        </div>

        {/* Primaire */}
        <div className="mb-6">
          <h4 className="font-medium text-gray-800 mb-3">Primaire</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Établissement</label>
              <input
                type="text"
                value={formData.primaireEtablissement}
                onChange={(e) => handleChange('primaireEtablissement', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lieu</label>
              <input
                type="text"
                value={formData.primaireLieu}
                onChange={(e) => handleChange('primaireLieu', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Année</label>
              <input
                type="text"
                value={formData.primaireAnnee}
                onChange={(e) => handleChange('primaireAnnee', e.target.value)}
                placeholder="Ex: 2018-2024"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
          </div>
        </div>

        {/* Secondaire */}
        <div className="mb-6">
          <h4 className="font-medium text-gray-800 mb-3">Secondaire</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Établissement</label>
              <input
                type="text"
                value={formData.secondaireEtablissement}
                onChange={(e) => handleChange('secondaireEtablissement', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lieu</label>
              <input
                type="text"
                value={formData.secondaireLieu}
                onChange={(e) => handleChange('secondaireLieu', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Année</label>
              <input
                type="text"
                value={formData.secondaireAnnee}
                onChange={(e) => handleChange('secondaireAnnee', e.target.value)}
                placeholder="Ex: 2024-présent"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              />
            </div>
          </div>
        </div>

        {/* Autres formations */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Autres formations
          </label>
          <textarea
            value={formData.autresFormations}
            onChange={(e) => handleChange('autresFormations', e.target.value)}
            rows={3}
            placeholder="Décrivez les autres formations suivies..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
          />
        </div>
      </div>

      {/* Boutons */}
      <div className="flex justify-between pt-6 border-t border-gray-200">
        <button
          onClick={onBack}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
        >
          ← Retour
        </button>
        <button
          onClick={handleSubmit}
          className="px-6 py-2 bg-success-600 text-white rounded-md hover:bg-success-700 transition-colors"
        >
          Confirmer l'enrôlement ✓
        </button>
      </div>
    </div>
  );
};

// ============================================
// EXTENSION : MILITAIRE / POLICIER
// ============================================
const MilitaireExtensionForm: React.FC<{ strata: StrataType; onSubmit: (data: any) => void; onBack: () => void }> = ({ strata, onSubmit, onBack }) => {
  const [formData, setFormData] = useState({
    // 3.1 Formations
    etablissement: '',
    classe: '',
    lieu: '',
    annee: '',
    titre: '',
    specialisation: '',
    
    // 3.2 Données professionnelles
    administration: strata === 'PNC' ? 'Police Nationale Congolaise' : 'Forces Armées RDC',
    matricule: '',
    grade: '',
    acteNomination: '',
    dateNomination: '',
    uniteAffectation: '',
    ministere: '',
    historique: '',
    distinctions: '',
    datePriseFonction: '',
    dateFinFonction: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <div className="space-y-6">
      {/* 3.1 Formations */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          3.1 Formations {strata === 'PNC' ? 'Policières' : 'Militaires'}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Établissement {strata === 'PNC' ? 'policier' : 'militaire'}
            </label>
            <input
              type="text"
              value={formData.etablissement}
              onChange={(e) => handleChange('etablissement', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Classe</label>
            <input
              type="text"
              value={formData.classe}
              onChange={(e) => handleChange('classe', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Lieu</label>
            <input
              type="text"
              value={formData.lieu}
              onChange={(e) => handleChange('lieu', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Année</label>
            <input
              type="text"
              value={formData.annee}
              onChange={(e) => handleChange('annee', e.target.value)}
              placeholder="Ex: 2015-2017"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Titre / Option</label>
            <input
              type="text"
              value={formData.titre}
              onChange={(e) => handleChange('titre', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Spécialisation</label>
            <input
              type="text"
              value={formData.specialisation}
              onChange={(e) => handleChange('specialisation', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>
        </div>
      </div>

      {/* 3.2 Données professionnelles */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          3.2 Données Professionnelles <span className="text-error-600">*</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Administration <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.administration}
              onChange={(e) => handleChange('administration', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500 bg-gray-50"
              readOnly
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Matricule <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.matricule}
              onChange={(e) => handleChange('matricule', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Grade <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.grade}
              onChange={(e) => handleChange('grade', e.target.value)}
              placeholder={strata === 'PNC' ? 'Ex: Commissaire' : 'Ex: Colonel'}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Acte de nomination (numéro)
            </label>
            <input
              type="text"
              value={formData.acteNomination}
              onChange={(e) => handleChange('acteNomination', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date de nomination
            </label>
            <input
              type="date"
              value={formData.dateNomination}
              onChange={(e) => handleChange('dateNomination', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Unité d'affectation
            </label>
            <input
              type="text"
              value={formData.uniteAffectation}
              onChange={(e) => handleChange('uniteAffectation', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ministère / Service
            </label>
            <input
              type="text"
              value={formData.ministere}
              onChange={(e) => handleChange('ministere', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date de prise de fonction
            </label>
            <input
              type="date"
              value={formData.datePriseFonction}
              onChange={(e) => handleChange('datePriseFonction', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Historique de carrière
            </label>
            <textarea
              value={formData.historique}
              onChange={(e) => handleChange('historique', e.target.value)}
              rows={3}
              placeholder="Décrivez les postes occupés, promotions..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Distinctions honorifiques
            </label>
            <textarea
              value={formData.distinctions}
              onChange={(e) => handleChange('distinctions', e.target.value)}
              rows={2}
              placeholder="Médailles, décorations, mentions..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>
        </div>
      </div>

      {/* Boutons */}
      <div className="flex justify-between pt-6 border-t border-gray-200">
        <button
          onClick={onBack}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
        >
          ← Retour
        </button>
        <button
          onClick={handleSubmit}
          disabled={!formData.matricule || !formData.grade}
          className="px-6 py-2 bg-success-600 text-white rounded-md hover:bg-success-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Confirmer l'enrôlement ✓
        </button>
      </div>
    </div>
  );
};

// ============================================
// EXTENSION : PRISONNIER
// ============================================
const PrisonnierExtensionForm: React.FC<{ onSubmit: (data: any) => void; onBack: () => void }> = ({ onSubmit, onBack }) => {
  const [formData, setFormData] = useState({
    numeroEcrou: '',
    etablissement: '',
    ville: '',
    province: '',
    dateIncarceration: '',
    dateLiberation: '',
    motifCondamnation: '',
    tribunal: '',
    statut: 'Préventif',
    responsable: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          3.1 Informations Pénitentiaires <span className="text-error-600">*</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Numéro d'écrou / dossier <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.numeroEcrou}
              onChange={(e) => handleChange('numeroEcrou', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom de l'établissement pénitentiaire <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.etablissement}
              onChange={(e) => handleChange('etablissement', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ville
            </label>
            <input
              type="text"
              value={formData.ville}
              onChange={(e) => handleChange('ville', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Province
            </label>
            <input
              type="text"
              value={formData.province}
              onChange={(e) => handleChange('province', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date d'incarcération <span className="text-error-600">*</span>
            </label>
            <input
              type="date"
              value={formData.dateIncarceration}
              onChange={(e) => handleChange('dateIncarceration', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date prévue de libération
            </label>
            <input
              type="date"
              value={formData.dateLiberation}
              onChange={(e) => handleChange('dateLiberation', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Statut <span className="text-error-600">*</span>
            </label>
            <select
              value={formData.statut}
              onChange={(e) => handleChange('statut', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            >
              <option value="Préventif">Préventif</option>
              <option value="Condamné">Condamné</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tribunal d'origine / Juridiction
            </label>
            <input
              type="text"
              value={formData.tribunal}
              onChange={(e) => handleChange('tribunal', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Motif de condamnation
            </label>
            <textarea
              value={formData.motifCondamnation}
              onChange={(e) => handleChange('motifCondamnation', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Responsable de la détention (nom du chef d'établissement)
            </label>
            <input
              type="text"
              value={formData.responsable}
              onChange={(e) => handleChange('responsable', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>
        </div>
      </div>

      {/* Boutons */}
      <div className="flex justify-between pt-6 border-t border-gray-200">
        <button
          onClick={onBack}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
        >
          ← Retour
        </button>
        <button
          onClick={handleSubmit}
          disabled={!formData.numeroEcrou || !formData.etablissement || !formData.dateIncarceration}
          className="px-6 py-2 bg-success-600 text-white rounded-md hover:bg-success-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Confirmer l'enrôlement ✓
        </button>
      </div>
    </div>
  );
};

// ============================================
// EXTENSION : RÉFUGIÉ
// ============================================
const RefugieExtensionForm: React.FC<{ onSubmit: (data: any) => void; onBack: () => void }> = ({ onSubmit, onBack }) => {
  const [formData, setFormData] = useState({
    numeroIndividuel: '',
    dateArrivee: '',
    origineEthnique: '',
    religion: '',
    lieuResidence: '',
    organisationReference: '',
    statut: 'En cours',
  });

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          3.1 Données Spécifiques Réfugié <span className="text-error-600">*</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Numéro individuel <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.numeroIndividuel}
              onChange={(e) => handleChange('numeroIndividuel', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date d'arrivée en RDC <span className="text-error-600">*</span>
            </label>
            <input
              type="date"
              value={formData.dateArrivee}
              onChange={(e) => handleChange('dateArrivee', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Origine ethnique / communautaire
            </label>
            <input
              type="text"
              value={formData.origineEthnique}
              onChange={(e) => handleChange('origineEthnique', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Religion
            </label>
            <input
              type="text"
              value={formData.religion}
              onChange={(e) => handleChange('religion', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Lieu actuel de résidence / camp
            </label>
            <input
              type="text"
              value={formData.lieuResidence}
              onChange={(e) => handleChange('lieuResidence', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Organisation humanitaire de référence
            </label>
            <input
              type="text"
              value={formData.organisationReference}
              onChange={(e) => handleChange('organisationReference', e.target.value)}
              placeholder="Ex: UNHCR, OIM..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Statut
            </label>
            <select
              value={formData.statut}
              onChange={(e) => handleChange('statut', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            >
              <option value="En cours">En cours</option>
              <option value="Reconnu">Reconnu</option>
              <option value="En régularisation">En régularisation</option>
            </select>
          </div>
        </div>
      </div>

      {/* Boutons */}
      <div className="flex justify-between pt-6 border-t border-gray-200">
        <button
          onClick={onBack}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
        >
          ← Retour
        </button>
        <button
          onClick={handleSubmit}
          disabled={!formData.numeroIndividuel || !formData.dateArrivee}
          className="px-6 py-2 bg-success-600 text-white rounded-md hover:bg-success-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Confirmer l'enrôlement ✓
        </button>
      </div>
    </div>
  );
};

// ============================================
// EXTENSION : ÉTRANGER
// ============================================
const EtrangerExtensionForm: React.FC<{ onSubmit: (data: any) => void; onBack: () => void }> = ({ onSubmit, onBack }) => {
  const [formData, setFormData] = useState({
    paysOrigine: '',
    typeSejour: 'Temporaire',
    numeroPasseport: '',
    passeportDelivreLieu: '',
    passeportDelivreDate: '',
    passeportExpiration: '',
    numeroVisa: '',
    dateVisa: '',
    adresseRDC: '',
    professionRDC: '',
    employeurRDC: '',
    contactUrgence: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          3.1 Informations Spécifiques Étranger <span className="text-error-600">*</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pays d'origine <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.paysOrigine}
              onChange={(e) => handleChange('paysOrigine', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type de séjour
            </label>
            <select
              value={formData.typeSejour}
              onChange={(e) => handleChange('typeSejour', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            >
              <option value="Temporaire">Temporaire</option>
              <option value="Résident">Résident</option>
              <option value="Diplomatique">Diplomatique</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Numéro du passeport <span className="text-error-600">*</span>
            </label>
            <input
              type="text"
              value={formData.numeroPasseport}
              onChange={(e) => handleChange('numeroPasseport', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Délivré à (ville)
            </label>
            <input
              type="text"
              value={formData.passeportDelivreLieu}
              onChange={(e) => handleChange('passeportDelivreLieu', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Délivré le (date)
            </label>
            <input
              type="date"
              value={formData.passeportDelivreDate}
              onChange={(e) => handleChange('passeportDelivreDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date d'expiration
            </label>
            <input
              type="date"
              value={formData.passeportExpiration}
              onChange={(e) => handleChange('passeportExpiration', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Visa ou permis de séjour (numéro)
            </label>
            <input
              type="text"
              value={formData.numeroVisa}
              onChange={(e) => handleChange('numeroVisa', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date du visa
            </label>
            <input
              type="date"
              value={formData.dateVisa}
              onChange={(e) => handleChange('dateVisa', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Adresse de résidence en RDC
            </label>
            <input
              type="text"
              value={formData.adresseRDC}
              onChange={(e) => handleChange('adresseRDC', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Profession exercée en RDC
            </label>
            <input
              type="text"
              value={formData.professionRDC}
              onChange={(e) => handleChange('professionRDC', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Employeur / Organisation
            </label>
            <input
              type="text"
              value={formData.employeurRDC}
              onChange={(e) => handleChange('employeurRDC', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contact d'urgence
            </label>
            <input
              type="text"
              value={formData.contactUrgence}
              onChange={(e) => handleChange('contactUrgence', e.target.value)}
              placeholder="Nom et téléphone"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
            />
          </div>
        </div>
      </div>

      {/* Boutons */}
      <div className="flex justify-between pt-6 border-t border-gray-200">
        <button
          onClick={onBack}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
        >
          ← Retour
        </button>
        <button
          onClick={handleSubmit}
          disabled={!formData.paysOrigine || !formData.numeroPasseport}
          className="px-6 py-2 bg-success-600 text-white rounded-md hover:bg-success-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Confirmer l'enrôlement ✓
        </button>
      </div>
    </div>
  );
};

// ============================================
// COMPOSANT PRINCIPAL - ROUTEUR
// ============================================
const StrataExtensionsForms: React.FC<StrataExtensionsFormsProps> = ({ strata, baseData, onSubmit, onBack }) => {
  // Si strata est un tableau, prendre le premier élément
  const strataValue = Array.isArray(strata) ? strata[0] : strata;
  
  return (
    <div className="w-full bg-white">
      <div className="w-full p-6 md:p-8">
        {/* En-tête */}
        <div className="mb-6 pb-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Extensions Spécifiques : {strataValue}
          </h2>
          <p className="text-gray-600">
            Renseignez les informations complémentaires spécifiques à cette catégorie
          </p>
        </div>

        {/* Routage vers le bon formulaire */}
        {(strataValue === 'ENFANT' || strataValue === 'ELEVES') && (
          <EleveExtensionForm onSubmit={onSubmit} onBack={onBack} />
        )}

        {(strataValue === 'PNC' || strataValue === 'FARDC') && (
          <MilitaireExtensionForm strata={strataValue as 'PNC' | 'FARDC'} onSubmit={onSubmit} onBack={onBack} />
        )}

        {strataValue === 'PRISON' && (
          <PrisonnierExtensionForm onSubmit={onSubmit} onBack={onBack} />
        )}

        {strataValue === 'REFUGIE' && (
          <RefugieExtensionForm onSubmit={onSubmit} onBack={onBack} />
        )}

        {strataValue === 'ETRANGER' && (
          <EtrangerExtensionForm onSubmit={onSubmit} onBack={onBack} />
        )}

        {/* Strates sans extensions spécifiques */}
        {(strataValue === 'ELECTEUR' || strataValue === 'DEPLACE' || strataValue === 'DIASPORA') && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <svg className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div>
                <h3 className="text-lg font-medium text-blue-900 mb-2">
                  Aucune extension spécifique requise
                </h3>
                <p className="text-blue-800 mb-4">
                  La catégorie "{strataValue}" ne nécessite pas d'informations complémentaires. 
                  Vous pouvez procéder directement à la confirmation de l'enrôlement.
                </p>

                <div className="flex justify-between mt-6">
                  <button
                    onClick={onBack}
                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    ← Retour
                  </button>
                  <button
                    onClick={() => onSubmit({})}
                    className="px-6 py-2 bg-success-600 text-white rounded-md hover:bg-success-700 transition-colors"
                  >
                    Suivant →
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrataExtensionsForms;

