import React, { useEffect, useRef, useState } from 'react';
import type { EmployeeFormData } from '@/types/employee';
import {
  formatEmployeeFullName,
  formatGenderLabel,
  formatIdCardType,
  formatPaymentMethod,
} from '@/lib/employee-display';
import { getPrinterStatus, printEnrollmentReceipt, printTestPage } from '@/services/printer-api';

interface EnrollmentReceiptProps {
  enrollmentId: string;
  employeeData: EmployeeFormData;
  onNewEnrollment: () => void;
}

export default function EnrollmentReceipt({
  enrollmentId,
  employeeData,
  onNewEnrollment,
}: EnrollmentReceiptProps) {
  const receiptRef = useRef<HTMLDivElement>(null);
  const [printerAvailable, setPrinterAvailable] = useState<boolean | null>(null);
  const [printError, setPrintError] = useState<string | null>(null);
  const [isPrinting, setIsPrinting] = useState(false);

  useEffect(() => {
    getPrinterStatus().then((s) => setPrinterAvailable(s.available));
  }, []);

  const handlePrintBrowser = () => window.print();

  const handlePrintThermal = async () => {
    setPrintError(null);
    setIsPrinting(true);
    try {
      await printEnrollmentReceipt(employeeData, enrollmentId);
    } catch (e) {
      setPrintError(e instanceof Error ? e.message : 'Impression thermique échouée');
    } finally {
      setIsPrinting(false);
    }
  };

  const handlePrintTest = async () => {
    setPrintError(null);
    try {
      await printTestPage();
      alert("Page test envoyée à l'imprimante");
    } catch (e) {
      setPrintError(e instanceof Error ? e.message : 'Test échoué');
    }
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
  const fullName = formatEmployeeFullName(employeeData);

  return (
    <div className="w-full">
      {printError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 text-sm rounded print:hidden">
          {printError}
        </div>
      )}

      {printerAvailable === false && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 text-amber-900 text-sm rounded print:hidden">
          Imprimante POS indisponible — utilisez « Imprimer (navigateur) ».
        </div>
      )}

      <div className="mb-6 flex flex-wrap justify-end gap-2 print:hidden">
        <button
          type="button"
          onClick={() => void handlePrintTest()}
          className="px-3 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50"
        >
          Test imprimante
        </button>
        <button
          onClick={handlePrintBrowser}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
        >
          Imprimer (navigateur)
        </button>
        <button
          type="button"
          onClick={() => void handlePrintThermal()}
          disabled={isPrinting}
          className="px-4 py-2 bg-secondary-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50"
        >
          {isPrinting ? 'Impression…' : 'Imprimer ticket POS'}
        </button>
      </div>

      <div
        ref={receiptRef}
        className="bg-white rounded-lg shadow-lg border-2 border-gray-200 overflow-hidden print:shadow-none print:border-0"
      >
        <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 text-white p-8 print:bg-blue-900">
          <div className="text-center space-y-1 border-t border-white/20 pt-4 mt-2">
            <p className="text-sm font-bold">République Démocratique du Congo</p>
            <p className="text-xs sm:text-sm font-semibold tracking-wide uppercase">
              Office National d&apos;Identification de la Population
            </p>
            <p className="text-[11px] sm:text-xs opacity-95">
              Enrôlement biométrique du personnel ONIP
            </p>
            <h1 className="text-2xl sm:text-3xl font-bold pt-2">RÉCÉPISSÉ D&apos;ENRÔLEMENT</h1>
          </div>
        </div>

        <div className="p-8">
          <div className="mb-6 p-4 bg-green-50 border-2 border-green-300 rounded-lg text-center">
            <div className="text-lg font-bold text-green-800">Enrôlement réussi</div>
            <div className="text-sm text-green-600">Biographie RH et biométrie enregistrées</div>
          </div>

          <div className="mb-6 text-center p-6 bg-gray-50 rounded-lg border border-gray-200">
            <div className="text-sm text-gray-600 mb-2">Numéro de session</div>
            <div className="text-3xl font-bold text-blue-900 tracking-wider">{enrollmentId}</div>
            <div className="text-xs text-gray-500 mt-2">Matricule : {employeeData.registration_number}</div>
          </div>

          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-200">
              Informations employé
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-gray-500 mb-1">Nom complet</div>
                <div className="text-sm font-semibold text-gray-900">{fullName}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Matricule</div>
                <div className="text-sm font-semibold text-gray-900">{employeeData.registration_number}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Date de naissance</div>
                <div className="text-sm font-semibold text-gray-900">{employeeData.date_of_birth || '-'}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Genre</div>
                <div className="text-sm font-semibold text-gray-900">
                  {formatGenderLabel(employeeData.gender)}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Nationalité</div>
                <div className="text-sm font-semibold text-gray-900">{employeeData.citizenship || '-'}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Mobile</div>
                <div className="text-sm font-semibold text-gray-900">{employeeData.mobile_number || 'N/A'}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Pièce d&apos;identité</div>
                <div className="text-sm font-semibold text-gray-900">
                  {formatIdCardType(employeeData.type_of_identity)}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Mode de paie</div>
                <div className="text-sm font-semibold text-gray-900">
                  {formatPaymentMethod(employeeData.payment_method)}
                </div>
              </div>
            </div>
          </div>

          {employeeData.physical_address && (
            <div className="mb-6">
              <h2 className="text-lg font-bold text-gray-900 mb-2">Adresse</h2>
              <p className="text-sm text-gray-900">{employeeData.physical_address}</p>
            </div>
          )}

          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-gray-200">
              Détails de l&apos;enrôlement
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-gray-500 mb-1">Date</div>
                <div className="text-sm font-semibold text-gray-900">{enrollmentDate}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Heure</div>
                <div className="text-sm font-semibold text-gray-900">{enrollmentTime}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Statut</div>
                <div className="text-sm font-semibold text-green-600">Traitement terminé</div>
              </div>
            </div>
          </div>

          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-xs text-yellow-800">
              <strong>Important :</strong> Conservez ce récépissé avec votre matricule{' '}
              {employeeData.registration_number} pour toute vérification ultérieure.
            </p>
          </div>
        </div>

        <div className="bg-gray-100 p-6 border-t border-gray-300 print:bg-gray-100 text-center text-xs text-gray-600">
          Document généré le {enrollmentDate} à {enrollmentTime}
        </div>
      </div>

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


