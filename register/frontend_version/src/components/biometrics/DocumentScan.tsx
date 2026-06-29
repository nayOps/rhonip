import React, { useState, useRef } from 'react';
import { ScannedDocument, DocumentType } from '@/types';

interface DocumentScanProps {
  onComplete: (documents: ScannedDocument[]) => void;
  onBack: () => void;
}

const DOCUMENT_TYPES: { value: DocumentType; label: string; required?: boolean }[] = [
  { value: 'FICHE_IDENTIFICATION', label: 'Fiche d\'identification physique', required: true },
  { value: 'ACTE_NAISSANCE', label: 'Acte de naissance' },
  { value: 'JUGEMENT_SUPPLETIF', label: 'Jugement supplétif' },
  { value: 'CARTE_ELECTEUR', label: 'Carte d\'électeur' },
  { value: 'CERTIFICAT_NATIONALITE', label: 'Certificat de nationalité' },
  { value: 'PASSEPORT', label: 'Passeport' },
  { value: 'CARTE_ETUDIANT', label: 'Carte d\'étudiant/élève' },
  { value: 'PERMIS_CONDUIRE', label: 'Permis de conduire' },
  { value: 'AUTRE', label: 'Autre document' },
];

export default function DocumentScan({ onComplete, onBack }: DocumentScanProps) {
  const [documents, setDocuments] = useState<ScannedDocument[]>([]);
  const [selectedType, setSelectedType] = useState<DocumentType>('FICHE_IDENTIFICATION');
  const [isScanning, setIsScanning] = useState(false);
  const [notes, setNotes] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const hasRequiredDocuments = documents.some(
    (doc) => doc.type === 'FICHE_IDENTIFICATION'
  );

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        addDocument(result, file);
      };
      reader.readAsDataURL(file);
    });
  };

  const addDocument = (imageData: string, file: File) => {
    const newDoc: ScannedDocument = {
      id: `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: selectedType,
      filename: file.name,
      image: imageData,
      size: file.size,
      mimeType: file.type,
      timestamp: new Date().toISOString(),
      notes: notes || undefined,
    };

    setDocuments((prev) => [...prev, newDoc]);
    setNotes('');
  };

  const simulateScan = () => {
    setIsScanning(true);

    // Simulation de scan (2 secondes)
    setTimeout(() => {
      const newDoc: ScannedDocument = {
        id: `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: selectedType,
        filename: `scanned_${selectedType}_${Date.now()}.jpg`,
        image: `data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAAA==`,
        size: 245678,
        mimeType: 'image/jpeg',
        timestamp: new Date().toISOString(),
        notes: notes || undefined,
      };

      setDocuments((prev) => [...prev, newDoc]);
      setNotes('');
      setIsScanning(false);
    }, 2000);
  };

  const removeDocument = (id: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  };

  const getDocumentTypeLabel = (type: DocumentType): string => {
    return DOCUMENT_TYPES.find((dt) => dt.value === type)?.label || type;
  };

  const handleSubmit = () => {
    if (hasRequiredDocuments) {
      onComplete(documents);
    }
  };

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* En-tête */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-green-50 to-teal-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Numérisation des documents
        </h2>
        <p className="text-gray-600">
          Scannez ou téléchargez la fiche d'identification physique et les pièces justificatives.
        </p>

        {/* Compteur */}
        <div className="mt-4 flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-green-500 text-white rounded-full flex items-center justify-center font-bold">
              {documents.length}
            </div>
            <span className="text-sm font-medium text-gray-700">
              Document{documents.length > 1 ? 's' : ''} numérisé{documents.length > 1 ? 's' : ''}
            </span>
          </div>

          {hasRequiredDocuments && (
            <div className="flex items-center space-x-2 text-green-600">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-semibold">Fiche d'identification capturée</span>
            </div>
          )}
        </div>
      </div>

      {/* Corps */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Panneau de capture */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Nouveau document
            </h3>

            {/* Sélection du type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de document
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value as DocumentType)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-600 focus:border-transparent"
              >
                {DOCUMENT_TYPES.map((docType) => (
                  <option key={docType.value} value={docType.value}>
                    {docType.label} {docType.required ? '(Obligatoire)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (optionnel)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                placeholder="Ajouter des notes sur ce document..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary-600 focus:border-transparent resize-none"
              />
            </div>

            {/* Boutons de capture */}
            <div className="space-y-3">
              <button
                onClick={simulateScan}
                disabled={isScanning}
                className={`
                  w-full px-4 py-3 rounded-lg font-medium transition flex items-center justify-center space-x-2
                  ${
                    isScanning
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-secondary-600 text-white hover:bg-blue-700'
                  }
                `}
              >
                {isScanning ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Scan en cours...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>Scanner le document</span>
                  </>
                )}
              </button>

              <div className="relative">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*,.pdf"
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isScanning}
                  className="w-full px-4 py-3 border-2 border-dashed border-gray-300 text-gray-700 rounded-lg hover:border-secondary-600 hover:bg-gray-50 transition font-medium flex items-center justify-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span>Télécharger depuis un fichier</span>
                </button>
              </div>
            </div>

            {/* Avertissement */}
            {!hasRequiredDocuments && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-700 font-medium">
                      La fiche d'identification physique est obligatoire
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Liste des documents */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Documents numérisés
            </h3>

            {documents.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">Aucun document numérisé</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[500px] overflow-y-auto">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-start space-x-3 p-3 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition"
                  >
                    {/* Miniature */}
                    <div className="flex-shrink-0 w-16 h-16 bg-white border border-gray-300 rounded overflow-hidden">
                      <img
                        src={doc.image}
                        alt={doc.filename}
                        className="w-full h-full object-cover"
                      />
                    </div>

                    {/* Infos */}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-900 truncate">
                        {getDocumentTypeLabel(doc.type)}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-gray-400">
                        {(doc.size / 1024).toFixed(1)} KB
                      </p>
                      {doc.notes && (
                        <p className="text-xs text-gray-600 mt-1 italic">
                          {doc.notes}
                        </p>
                      )}
                    </div>

                    {/* Bouton supprimer */}
                    <button
                      onClick={() => removeDocument(doc.id)}
                      className="flex-shrink-0 text-red-500 hover:text-red-700 transition"
                      title="Supprimer"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Conseils</h3>
              <div className="mt-2 text-sm text-green-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Assurez-vous que les documents sont lisibles et bien éclairés</li>
                  <li>La fiche d'identification physique doit être scannée en premier</li>
                  <li>Vous pouvez scanner plusieurs pièces justificatives</li>
                  <li>Les formats acceptés : JPG, PNG, PDF</li>
                </ul>
              </div>
            </div>
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
          disabled={!hasRequiredDocuments}
          className={`
            px-6 py-3 rounded-lg font-medium transition
            ${
              hasRequiredDocuments
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

