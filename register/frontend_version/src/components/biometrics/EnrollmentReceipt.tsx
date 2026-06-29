import React, { useRef } from 'react';
import { BaseEnrollmentData } from '@/types';

interface EnrollmentReceiptProps {
  enrollmentId: string;
  baseData: BaseEnrollmentData;
  onNewEnrollment: () => void;
}

export default function EnrollmentReceipt({
  enrollmentId,
  baseData,
  onNewEnrollment,
}: EnrollmentReceiptProps) {
  const receiptRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    // Simulation du téléchargement
    alert('Téléchargement du récépissé en cours...');
  };

  const enrollmentDate = new Date().toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  const enrollmentTime = new Date().toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="w-full">
      {/* Boutons d'action (non imprimables) */}
      <div className="mb-6 flex justify-end space-x-3 print:hidden">
        <button
          onClick={handleDownload}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>Télécharger PDF</span>
        </button>

        <button
          onClick={handlePrint}
          className="px-4 py-2 bg-secondary-600 text-white rounded-lg hover:bg-blue-700 transition font-medium flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          <span>Imprimer</span>
        </button>
      </div>

      {/* Récépissé */}
      <div
        ref={receiptRef}
        className="bg-white rounded-lg shadow-lg border-2 border-gray-200 overflow-hidden print:shadow-none print:border-0"
      >
        {/* En-tête officiel */}
        <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 text-white p-8 print:bg-blue-900">
          <div className="flex items-center justify-between mb-4">
            {/* Logo RDC */}
            <div className="flex items-center space-x-3">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-blue-900">RDC</span>
              </div>
              <div>
                <div className="text-sm font-medium">République Démocratique du Congo</div>
                <div className="text-xs opacity-90">Ministère de l'Intérieur</div>
              </div>
            </div>

            {/* QR Code simulé */}
            <div className="w-20 h-20 bg-white rounded p-1">
              <div className="w-full h-full bg-gradient-to-br from-blue-900 to-blue-600 opacity-80"></div>
            </div>
          </div>

          <div className="text-center">
            <h1 className="text-3xl font-bold mb-2">RÉCÉPISSÉ D'ENRÔLEMENT</h1>
            <p className="text-sm opacity-90">Fichier de la Population Générale (FGP)</p>
          </div>
        </div>

        {/* Corps du récépissé */}
        <div className="p-8">
          {/* Bannière de statut */}
          <div className="mb-6 p-4 bg-green-50 border-2 border-green-300 rounded-lg">
            <div className="flex items-center justify-center space-x-3">
              <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <div>
                <div className="text-lg font-bold text-green-800">Enrôlement réussi</div>
                <div className="text-sm text-green-600">Votre demande a été enregistrée avec succès</div>
              </div>
            </div>
          </div>

          {/* Numéro de dossier */}
          <div className="mb-6 text-center p-6 bg-gray-50 rounded-lg border border-gray-200">
            <div className="text-sm text-gray-600 mb-2">Numéro de dossier d'enrôlement</div>
            <div className="text-3xl font-bold text-blue-900 tracking-wider">{enrollmentId}</div>
            <div className="text-xs text-gray-500 mt-2">Conservez ce numéro pour le suivi de votre dossier</div>
          </div>

          {/* Informations du requérant */}
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-200">
              Informations du requérant
            </h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-gray-500 mb-1">Nom complet</div>
                <div className="text-sm font-semibold text-gray-900">
                  {baseData.prenom} {baseData.nom} {baseData.postnom}
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Date de naissance</div>
                <div className="text-sm font-semibold text-gray-900">{baseData.date_naissance}</div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Lieu de naissance</div>
                <div className="text-sm font-semibold text-gray-900">{baseData.lieu_naissance}</div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Sexe</div>
                <div className="text-sm font-semibold text-gray-900">
                  {baseData.sexe === 'M' ? 'Masculin' : 'Féminin'}
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Nationalité</div>
                <div className="text-sm font-semibold text-gray-900">{baseData.nationalite}</div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Téléphone</div>
                <div className="text-sm font-semibold text-gray-900">{baseData.telephone || 'N/A'}</div>
              </div>
            </div>
          </div>

          {/* Résidence */}
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-200">
              Adresse de résidence
            </h2>
            
            <div className="text-sm text-gray-900">
              {baseData.residence_quartier}, {baseData.residence_commune}<br />
              {baseData.residence_ville}, {baseData.residence_province}<br />
              {baseData.residence_pays}
              {baseData.residence_rue && (
                <>
                  <br />
                  {baseData.residence_rue} {baseData.residence_numero}
                </>
              )}
            </div>
          </div>

          {/* Strate */}
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-200">
              Strate(s) d'enrôlement
            </h2>
            
            <div className="flex flex-wrap gap-2">
              {(Array.isArray(baseData.strata) ? baseData.strata : [baseData.strata]).map((strate) => (
                <span
                  key={strate}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full border border-blue-300"
                >
                  {strate}
                </span>
              ))}
            </div>
          </div>

          {/* Informations d'enrôlement */}
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-200">
              Détails de l'enrôlement
            </h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-gray-500 mb-1">Date d'enrôlement</div>
                <div className="text-sm font-semibold text-gray-900">{enrollmentDate}</div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Heure d'enrôlement</div>
                <div className="text-sm font-semibold text-gray-900">{enrollmentTime}</div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Type de requête</div>
                <div className="text-sm font-semibold text-gray-900">{baseData.type_requete}</div>
              </div>

              <div>
                <div className="text-xs text-gray-500 mb-1">Statut</div>
                <div className="text-sm font-semibold text-green-600">En cours de traitement</div>
              </div>
            </div>
          </div>

          {/* Données biométriques collectées */}
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-200">
              Données biométriques collectées
            </h2>
            
            <div className="flex space-x-6">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-gray-700">Empreintes digitales (10)</span>
              </div>

              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-gray-700">Iris (2 yeux)</span>
              </div>

              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-gray-700">Reconnaissance faciale</span>
              </div>
            </div>
          </div>

          {/* Prochaines étapes */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-sm font-bold text-blue-900 mb-2">📋 Prochaines étapes</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Votre dossier sera traité dans un délai de 15 jours ouvrables</li>
              <li>• Vous serez contacté par SMS/Email une fois le traitement terminé</li>
              <li>• Vous pourrez retirer votre Numéro d'Identification National (NIN)</li>
              <li>• Présentez ce récépissé lors du retrait de votre NIN</li>
            </ul>
          </div>

          {/* Avertissement */}
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-xs text-yellow-800">
                  <strong>Important :</strong> Conservez précieusement ce récépissé. Il vous sera demandé lors du retrait de votre NIN. 
                  En cas de perte, contactez le centre d'enrôlement avec votre numéro de dossier.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Pied de page */}
        <div className="bg-gray-100 p-6 border-t border-gray-300 print:bg-gray-100">
          <div className="text-center text-xs text-gray-600">
            <p className="mb-1">
              <strong>Centre d'enrôlement FGP</strong> • Kinshasa, République Démocratique du Congo
            </p>
            <p className="mb-1">
              Tél : +243 XXX XXX XXX • Email : contact@fgp.gouv.cd • Web : www.fgp.gouv.cd
            </p>
            <p className="text-gray-500 mt-2">
              Document généré électroniquement le {enrollmentDate} à {enrollmentTime}
            </p>
          </div>
        </div>
      </div>

      {/* Bouton nouvelle inscription (non imprimable) */}
      <div className="mt-6 text-center print:hidden">
        <button
          onClick={onNewEnrollment}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
        >
          Nouvel enrôlement
        </button>
      </div>
    </div>
  );
}

