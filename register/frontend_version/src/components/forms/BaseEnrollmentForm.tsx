'use client';

import React, { useState, useEffect } from 'react';

// Types pour les strates
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

interface BaseEnrollmentFormProps {
  onNext: (data: any) => void;
}

// Composant de sélection de strate
const StrataSelector: React.FC<{
  selectedStrata: StrataType | null;
  onSelect: (strata: StrataType) => void;
}> = ({ selectedStrata, onSelect }) => {
  const strata: { value: StrataType; label: string; icon: string }[] = [
    { value: 'ENFANT', label: 'Enfant', icon: '👶' },
    { value: 'ELEVES', label: 'Élève', icon: '🎓' },
    { value: 'ELECTEUR', label: 'Électeur/Majeur', icon: '🗳️' },
    { value: 'FARDC', label: 'Militaire', icon: '🪖' },
    { value: 'PNC', label: 'Policier', icon: '👮' },
    { value: 'PRISON', label: 'Prisonnier', icon: '🔒' },
    { value: 'REFUGIE', label: 'Réfugié', icon: '🛂' },
    { value: 'DEPLACE', label: 'Déplacé interne', icon: '🏠' },
    { value: 'ETRANGER', label: 'Étranger', icon: '🌍' },
    { value: 'DIASPORA', label: 'Diaspora', icon: '✈️' },
  ];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
      <h2 className="text-xl font-bold mb-4 text-gray-900">📋 Sélection de la Catégorie</h2>
      <p className="text-sm text-gray-600 mb-4">
        Sélectionnez une seule catégorie correspondant au profil du requérant :
      </p>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {strata.map((item) => (
          <label
            key={item.value}
            className={`flex items-center gap-2 p-3 border-2 rounded-lg cursor-pointer transition-all ${
              selectedStrata === item.value
                ? 'border-secondary-500 bg-secondary-50 shadow-md'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              type="radio"
              name="strata"
              value={item.value}
              checked={selectedStrata === item.value}
              onChange={() => onSelect(item.value)}
              className="sr-only"
            />
            <span className="text-2xl">{item.icon}</span>
            <span className="text-sm font-medium">{item.label}</span>
          </label>
        ))}
      </div>

      {selectedStrata && (
        <div className="mt-4 p-3 bg-secondary-50 rounded-lg">
          <p className="text-sm font-medium text-secondary-800">
            ✓ Catégorie sélectionnée : <strong>{strata.find(s => s.value === selectedStrata)?.label}</strong>
          </p>
        </div>
      )}
    </div>
  );
};

// Composant pour section désactivée
const DisabledSection: React.FC<{ title: string; reason: string }> = ({ title, reason }) => (
  <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6 opacity-60">
    <h3 className="text-lg font-semibold text-gray-600 mb-3">{title}</h3>
    <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded">
      <svg className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
      </svg>
      <p className="text-sm text-blue-800">{reason}</p>
    </div>
  </div>
);

// Composant principal
const BaseEnrollmentForm: React.FC<BaseEnrollmentFormProps> = ({ onNext }) => {
  const [selectedStrata, setSelectedStrata] = useState<StrataType | null>(null);
  const [formData, setFormData] = useState<any>({
    // 2.1 Identité
    prenom: '',
    nom: '',
    postnom: '',
    autresNoms: '',
    sexe: 'M',
    dateNaissance: '',
    lieuNaissance: '',
    nationalite: 'Congolaise',
    taille: '',
    couleurYeux: '',
    groupeSanguin: '',
    telephone: '',
    email: '',
    boitePostale: '',
    
    // 2.2 Origine et résidence
    origineProvince: '',
    origineVille: '',
    origineCommune: '',
    origineQuartier: '',
    residenceProvince: '',
    residenceVille: '',
    residenceCommune: '',
    residenceQuartier: '',
    residenceRue: '',
    
    // 2.3 Situation familiale
    etatMatrimonial: 'Célibataire',
    nombreEnfants: '',
    conjointNom: '',
    conjointNationalite: '',
    conjointLieuNaissance: '',
    
    // 2.4 Filiation
    pereStatut: 'En vie',
    pereNom: '',
    pereNationalite: '',
    pereNIN: '',
    pereLieuNaissance: '',
    mereStatut: 'En vie',
    mereNom: '',
    mereNationalite: '',
    mereNIN: '',
    mereLieuNaissance: '',
    tuteurNom: '',
    tuteurNationalite: '',
    tuteurLien: '',
    
    // 2.5 Études
    niveauEtude: '',
    etablissement: '',
    anneeObtention: '',
    domaine: '',
    
    // 2.6 Profession
    profession: '',
    employeur: '',
    fonction: '',
    
    // 2.7 Pièces présentées
    typePiece: 'Acte de naissance',
    numeroPiece: '',
    datePiece: '',
    
    // 2.8 Éléments signalétiques
    handicap: 'Aucun',
    handicapDetails: '',
  });

  const handleChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  };

  // Logique conditionnelle selon la strate
  const isSituationFamilialeActive = () => {
    return selectedStrata && !['ENFANT', 'ELEVES'].includes(selectedStrata);
  };

  const isFiliationRequired = () => {
    return selectedStrata && ['ENFANT', 'ELEVES'].includes(selectedStrata);
  };

  const isTuteurVisible = () => {
    return selectedStrata && ['ENFANT', 'ELEVES', 'REFUGIE'].includes(selectedStrata);
  };

  const isEtudesRequired = () => {
    return selectedStrata && ['ELEVES', 'ETUDIANT'].includes(selectedStrata);
  };

  // Validation du formulaire
  const isFormValid = () => {
    if (!selectedStrata) return false;
    
    // Champs de base obligatoires
    if (!formData.prenom || !formData.nom || !formData.dateNaissance || !formData.lieuNaissance) {
      return false;
    }
    
    // Validation conditionnelle selon strate
    if (isFiliationRequired()) {
      if (!formData.pereNom || !formData.mereNom) return false;
    }
    
    return true;
  };

  const handleSubmit = () => {
    if (isFormValid()) {
      onNext({ strata: selectedStrata, ...formData });
    }
  };

  return (
    <div className="w-full bg-gray-50">
      <div className="w-full p-6 md:p-8">
        {/* Sélection de strate */}
        <StrataSelector selectedStrata={selectedStrata} onSelect={setSelectedStrata} />

        {!selectedStrata && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <p className="text-yellow-800 font-medium">
              ⚠️ Veuillez d'abord sélectionner une catégorie pour commencer le formulaire
            </p>
          </div>
        )}

        {selectedStrata && (
          <div className="space-y-6">
            {/* 2.1 IDENTITÉ DU REQUÉRANT */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2.1 Identité du Requérant <span className="text-error-600">*</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prénom <span className="text-error-600">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.prenom}
                    onChange={(e) => handleChange('prenom', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom <span className="text-error-600">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.nom}
                    onChange={(e) => handleChange('nom', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Postnom
                  </label>
                  <input
                    type="text"
                    value={formData.postnom}
                    onChange={(e) => handleChange('postnom', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Autres noms
                  </label>
                  <input
                    type="text"
                    value={formData.autresNoms}
                    onChange={(e) => handleChange('autresNoms', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sexe <span className="text-error-600">*</span>
                  </label>
                  <select
                    value={formData.sexe}
                    onChange={(e) => handleChange('sexe', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  >
                    <option value="M">Masculin</option>
                    <option value="F">Féminin</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date de naissance <span className="text-error-600">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.dateNaissance}
                    onChange={(e) => handleChange('dateNaissance', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Lieu de naissance <span className="text-error-600">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.lieuNaissance}
                    onChange={(e) => handleChange('lieuNaissance', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nationalité <span className="text-error-600">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.nationalite}
                    onChange={(e) => handleChange('nationalite', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Taille (cm)
                  </label>
                  <input
                    type="number"
                    value={formData.taille}
                    onChange={(e) => handleChange('taille', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Couleur des yeux
                  </label>
                  <input
                    type="text"
                    value={formData.couleurYeux}
                    onChange={(e) => handleChange('couleurYeux', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Groupe sanguin
                  </label>
                  <select
                    value={formData.groupeSanguin}
                    onChange={(e) => handleChange('groupeSanguin', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  >
                    <option value="">Sélectionner...</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    value={formData.telephone}
                    onChange={(e) => handleChange('telephone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    E-mail
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Boîte postale (BP)
                  </label>
                  <input
                    type="text"
                    value={formData.boitePostale}
                    onChange={(e) => handleChange('boitePostale', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>
              </div>
            </div>

            {/* 2.2 ORIGINE ET RÉSIDENCE */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2.2 Origine et Résidence <span className="text-error-600">*</span>
              </h3>
              
              <div className="space-y-6">
                {/* Origine */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">Origine (domicile coutumier)</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Province / Région
                      </label>
                      <input
                        type="text"
                        value={formData.origineProvince}
                        onChange={(e) => handleChange('origineProvince', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Ville / Territoire
                      </label>
                      <input
                        type="text"
                        value={formData.origineVille}
                        onChange={(e) => handleChange('origineVille', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Commune / Secteur
                      </label>
                      <input
                        type="text"
                        value={formData.origineCommune}
                        onChange={(e) => handleChange('origineCommune', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Quartier / Village
                      </label>
                      <input
                        type="text"
                        value={formData.origineQuartier}
                        onChange={(e) => handleChange('origineQuartier', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Résidence actuelle */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">Adresse de résidence actuelle</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Province / Région
                      </label>
                      <input
                        type="text"
                        value={formData.residenceProvince}
                        onChange={(e) => handleChange('residenceProvince', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Ville / Territoire
                      </label>
                      <input
                        type="text"
                        value={formData.residenceVille}
                        onChange={(e) => handleChange('residenceVille', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Commune / Secteur
                      </label>
                      <input
                        type="text"
                        value={formData.residenceCommune}
                        onChange={(e) => handleChange('residenceCommune', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Quartier
                      </label>
                      <input
                        type="text"
                        value={formData.residenceQuartier}
                        onChange={(e) => handleChange('residenceQuartier', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Rue / Avenue / N°
                      </label>
                      <input
                        type="text"
                        value={formData.residenceRue}
                        onChange={(e) => handleChange('residenceRue', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 2.3 SITUATION FAMILIALE - Conditionnelle */}
            {!isSituationFamilialeActive() ? (
              <DisabledSection
                title="2.3 Situation Familiale"
                reason={`Cette section n'est pas requise pour la catégorie "${selectedStrata}". Elle concerne uniquement les adultes et majeurs.`}
              />
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  2.3 Situation Familiale
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      État matrimonial
                    </label>
                    <select
                      value={formData.etatMatrimonial}
                      onChange={(e) => handleChange('etatMatrimonial', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    >
                      <option value="Célibataire">Célibataire</option>
                      <option value="Marié(e)">Marié(e)</option>
                      <option value="Divorcé(e)">Divorcé(e)</option>
                      <option value="Veuf/Veuve">Veuf/Veuve</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nombre d'enfants
                    </label>
                    <input
                      type="number"
                      value={formData.nombreEnfants}
                      onChange={(e) => handleChange('nombreEnfants', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    />
                  </div>

                  {formData.etatMatrimonial === 'Marié(e)' && (
                    <>
                      <div className="md:col-span-2">
                        <h4 className="font-medium text-gray-800 mb-3">Conjoint(e)</h4>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Prénom / Nom / Postnom
                        </label>
                        <input
                          type="text"
                          value={formData.conjointNom}
                          onChange={(e) => handleChange('conjointNom', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Nationalité
                        </label>
                        <input
                          type="text"
                          value={formData.conjointNationalite}
                          onChange={(e) => handleChange('conjointNationalite', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Lieu de naissance
                        </label>
                        <input
                          type="text"
                          value={formData.conjointLieuNaissance}
                          onChange={(e) => handleChange('conjointLieuNaissance', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        />
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* 2.4 FILIATION - Conditionnelle */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2.4 Filiation {isFiliationRequired() && <span className="text-error-600">*</span>}
              </h3>

              {isFiliationRequired() && (
                <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded">
                  <p className="text-sm text-orange-800">
                    ⭐ <strong>Section obligatoire</strong> pour la catégorie "{selectedStrata}". Les informations sur les parents sont requises.
                  </p>
                </div>
              )}
              
              <div className="space-y-6">
                {/* Père */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">Père</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Statut
                      </label>
                      <select
                        value={formData.pereStatut}
                        onChange={(e) => handleChange('pereStatut', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      >
                        <option value="En vie">En vie</option>
                        <option value="Décédé">Décédé</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Prénom / Nom / Postnom {isFiliationRequired() && <span className="text-error-600">*</span>}
                      </label>
                      <input
                        type="text"
                        value={formData.pereNom}
                        onChange={(e) => handleChange('pereNom', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        required={isFiliationRequired()}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nationalité
                      </label>
                      <input
                        type="text"
                        value={formData.pereNationalite}
                        onChange={(e) => handleChange('pereNationalite', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        NIN
                      </label>
                      <input
                        type="text"
                        value={formData.pereNIN}
                        onChange={(e) => handleChange('pereNIN', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Lieu de naissance
                      </label>
                      <input
                        type="text"
                        value={formData.pereLieuNaissance}
                        onChange={(e) => handleChange('pereLieuNaissance', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Mère */}
                <div>
                  <h4 className="font-medium text-gray-800 mb-3">Mère</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Statut
                      </label>
                      <select
                        value={formData.mereStatut}
                        onChange={(e) => handleChange('mereStatut', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      >
                        <option value="En vie">En vie</option>
                        <option value="Décédée">Décédée</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Prénom / Nom / Postnom {isFiliationRequired() && <span className="text-error-600">*</span>}
                      </label>
                      <input
                        type="text"
                        value={formData.mereNom}
                        onChange={(e) => handleChange('mereNom', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        required={isFiliationRequired()}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nationalité
                      </label>
                      <input
                        type="text"
                        value={formData.mereNationalite}
                        onChange={(e) => handleChange('mereNationalite', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        NIN
                      </label>
                      <input
                        type="text"
                        value={formData.mereNIN}
                        onChange={(e) => handleChange('mereNIN', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Lieu de naissance
                      </label>
                      <input
                        type="text"
                        value={formData.mereLieuNaissance}
                        onChange={(e) => handleChange('mereLieuNaissance', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Tuteur - Visible seulement pour certaines strates */}
                {isTuteurVisible() && (
                  <div>
                    <h4 className="font-medium text-gray-800 mb-3">Tuteur (si applicable)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Prénom / Nom / Postnom
                        </label>
                        <input
                          type="text"
                          value={formData.tuteurNom}
                          onChange={(e) => handleChange('tuteurNom', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Nationalité
                        </label>
                        <input
                          type="text"
                          value={formData.tuteurNationalite}
                          onChange={(e) => handleChange('tuteurNationalite', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Nature du lien
                        </label>
                        <input
                          type="text"
                          value={formData.tuteurLien}
                          onChange={(e) => handleChange('tuteurLien', e.target.value)}
                          placeholder="Ex: Oncle, Tante, Grand-parent..."
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 2.5 ÉTUDES FAITES - Conditionnelle */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2.5 Études Faites {isEtudesRequired() && <span className="text-error-600">*</span>}
              </h3>

              {isEtudesRequired() && (
                <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded">
                  <p className="text-sm text-orange-800">
                    ⭐ <strong>Section obligatoire</strong> pour la catégorie "{selectedStrata}". Renseignez le niveau d'étude actuel.
                  </p>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Niveau d'étude {isEtudesRequired() && <span className="text-error-600">*</span>}
                  </label>
                  <select
                    value={formData.niveauEtude}
                    onChange={(e) => handleChange('niveauEtude', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    required={isEtudesRequired()}
                  >
                    <option value="">Sélectionner...</option>
                    <option value="Aucun">Aucun</option>
                    <option value="Primaire">Primaire</option>
                    <option value="Secondaire">Secondaire</option>
                    <option value="Graduat">Graduat</option>
                    <option value="Licence">Licence</option>
                    <option value="Master">Master</option>
                    <option value="Doctorat">Doctorat</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Établissement / Université
                  </label>
                  <input
                    type="text"
                    value={formData.etablissement}
                    onChange={(e) => handleChange('etablissement', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Année d'obtention
                  </label>
                  <input
                    type="number"
                    value={formData.anneeObtention}
                    onChange={(e) => handleChange('anneeObtention', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Domaine / Filière
                  </label>
                  <input
                    type="text"
                    value={formData.domaine}
                    onChange={(e) => handleChange('domaine', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>
              </div>
            </div>

            {/* 2.6 PROFESSION / OCCUPATION */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2.6 Profession / Occupation
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Profession / Occupation
                  </label>
                  <select
                    value={formData.profession}
                    onChange={(e) => handleChange('profession', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  >
                    <option value="">Sélectionner...</option>
                    <option value="Élève">Élève</option>
                    <option value="Étudiant">Étudiant</option>
                    <option value="Agent de l'État">Agent de l'État</option>
                    <option value="Policier">Policier</option>
                    <option value="Militaire">Militaire</option>
                    <option value="Commerçant">Commerçant</option>
                    <option value="Agriculteur">Agriculteur</option>
                    <option value="Sans emploi">Sans emploi</option>
                    <option value="Autre">Autre</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom de l'employeur / institution
                  </label>
                  <input
                    type="text"
                    value={formData.employeur}
                    onChange={(e) => handleChange('employeur', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fonction ou occupation principale
                  </label>
                  <input
                    type="text"
                    value={formData.fonction}
                    onChange={(e) => handleChange('fonction', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>
              </div>
            </div>

            {/* 2.7 PIÈCE(S) PRÉSENTÉE(S) */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2.7 Pièce(s) Présentée(s) <span className="text-error-600">*</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type de pièce <span className="text-error-600">*</span>
                  </label>
                  <select
                    value={formData.typePiece}
                    onChange={(e) => handleChange('typePiece', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  >
                    <option value="Acte de naissance">Acte de naissance</option>
                    <option value="Jugement supplétif">Jugement supplétif</option>
                    <option value="Carte d'électeur">Carte d'électeur</option>
                    <option value="Certificat de nationalité">Certificat de nationalité</option>
                    <option value="Passeport">Passeport</option>
                    <option value="Carte d'élève">Carte d'élève / étudiant</option>
                    <option value="Autre">Autre</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Numéro du document
                  </label>
                  <input
                    type="text"
                    value={formData.numeroPiece}
                    onChange={(e) => handleChange('numeroPiece', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date du document
                  </label>
                  <input
                    type="date"
                    value={formData.datePiece}
                    onChange={(e) => handleChange('datePiece', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  />
                </div>
              </div>
            </div>

            {/* 2.8 ÉLÉMENTS SIGNALÉTIQUES */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                2.8 Éléments Signalétiques
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Présence de handicap(s)
                  </label>
                  <select
                    value={formData.handicap}
                    onChange={(e) => handleChange('handicap', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                  >
                    <option value="Aucun">Aucun</option>
                    <option value="Moteur">Moteur</option>
                    <option value="Visuel">Visuel</option>
                    <option value="Auditif">Auditif</option>
                    <option value="Autre">Autre</option>
                  </select>
                </div>

                {formData.handicap !== 'Aucun' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Précisions sur le handicap
                    </label>
                    <input
                      type="text"
                      value={formData.handicapDetails}
                      onChange={(e) => handleChange('handicapDetails', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary-500 focus:border-secondary-500"
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Bouton SUIVANT */}
            <div className="flex justify-end pt-6 border-t border-gray-200">
              <button
                onClick={handleSubmit}
                disabled={!isFormValid()}
                className={`px-8 py-3 rounded-md font-medium transition-all ${
                  isFormValid()
                    ? 'bg-secondary-600 text-white hover:bg-secondary-700 shadow-md'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Suivant : Extensions spécifiques →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BaseEnrollmentForm;

