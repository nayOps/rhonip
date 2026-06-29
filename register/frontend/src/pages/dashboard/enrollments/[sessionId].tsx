'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useAuth } from '@/context/AuthContext';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import EnrollmentResumeActions from '@/components/enrollment/EnrollmentResumeActions';
import {
  EnrollmentDbSnapshot,
  EnrollmentSessionDetail,
  getEnrollmentDbSnapshot,
  getEnrollmentSessionDetail,
  getIdentificationBlockingSummary,
  identificationStatusClass,
  resolveIdentificationDisplayStatus,
} from '@/services/enrollment-session-api';

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="bg-white rounded-lg shadow-soft p-4 md:p-5">
    <h2 className="text-base font-semibold text-gray-900 mb-3">{title}</h2>
    {children}
  </section>
);

const EnrollmentSessionDetailPage: React.FC = () => {
  const router = useRouter();
  const { sessionId } = router.query;
  const { logout, session } = useAuth();
  const { isReady, isAuthenticated } = useRequireAuth(['admin']);
  const [detail, setDetail] = useState<EnrollmentSessionDetail | null>(null);
  const [dbSnapshot, setDbSnapshot] = useState<EnrollmentDbSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = async () => {
    if (typeof sessionId !== 'string') return;
    try {
      const [data, db] = await Promise.all([
        getEnrollmentSessionDetail(sessionId),
        getEnrollmentDbSnapshot(sessionId),
      ]);
      setDetail(data);
      setDbSnapshot(db);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [sessionId]);

  const db = dbSnapshot?.db || {};
  const dbEmployee = (db.employee as Record<string, unknown>) || (dbSnapshot?.employee as Record<string, unknown>) || {};
  const dbBiometric = (db.biometric as Record<string, unknown>) || {};
  const dbFingerprints = (db.fingerprints as Array<Record<string, unknown>>) || [];
  const dbDocuments = (db.documents as Array<Record<string, unknown>>) || [];
  const payload = (detail?.payload as Record<string, unknown> | undefined) || {};
  const persistedMedia = (payload.persisted_media as Record<string, unknown> | undefined) || {};

  const asImageSrc = (value: unknown): string | null => {
    if (typeof value !== 'string' || !value) return null;
    if (value.startsWith('http://') || value.startsWith('https://') || value.startsWith('data:')) return value;
    return `http://localhost:8001/api/v1/enrolments/sessions/media-proxy/?uri=${encodeURIComponent(value)}`;
  };

  const faceSrc = asImageSrc(dbBiometric.photo_uri);
  const irisList = (persistedMedia.iris as Array<Record<string, unknown>>) || [];
  const irisLeftFromList = irisList.find((x) => String(x.position || '').toLowerCase().includes('left'));
  const irisRightFromList = irisList.find((x) => String(x.position || '').toLowerCase().includes('right'));
  const irisUri = typeof dbBiometric.iris_uri === 'string' ? dbBiometric.iris_uri : '';
  const inferredLeftUri =
    irisUri && !irisLeftFromList && !irisUri.includes('/right.')
      ? irisUri
      : irisUri.replace('/right.', '/left.');
  const inferredRightUri =
    irisUri && !irisRightFromList && !irisUri.includes('/left.')
      ? irisUri
      : irisUri.replace('/left.', '/right.');
  const irisLeftSrc = asImageSrc(irisLeftFromList?.uri || inferredLeftUri || '');
  const irisRightSrc = asImageSrc(irisRightFromList?.uri || inferredRightUri || '');

  const displayStatus = detail
    ? resolveIdentificationDisplayStatus(detail.status, detail.modality_status)
    : null;

  if (!isReady || !isAuthenticated) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-500">Chargement…</div>;
  }

  return (
    <DashboardLayout
      userName={session?.user.displayName}
      onLogout={() => {
        logout();
        router.replace('/auth');
      }}
    >
      <div className="max-w-7xl mx-auto p-4 md:p-6 lg:p-8 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <Link href="/dashboard/enrollments" className="text-sm text-secondary-700 hover:underline">
              ← Retour à la liste
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 mt-1">Fiche identification agent ONIP</h1>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center gap-2">
            <EnrollmentResumeActions sessionId={typeof sessionId === 'string' ? sessionId : ''} layout="stack" />
            <button onClick={fetchDetail} className="px-3 py-2 text-sm rounded-md bg-secondary-600 text-white hover:bg-secondary-700">
              Actualiser
            </button>
          </div>
        </div>

        {loading ? (
          <div className="bg-white rounded-lg shadow-soft p-6 text-gray-500">Chargement de la fiche…</div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">{error}</div>
        ) : !detail ? (
          <div className="bg-white rounded-lg shadow-soft p-6 text-gray-500">Aucune donnée.</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {dbSnapshot?.repair?.requested && (
              <Section title="Synchronisation des données">
                <div className="text-sm space-y-1">
                  <div><span className="font-medium">Statut:</span> {dbSnapshot.repair.performed ? 'mise à jour effectuée' : 'en attente'}</div>
                  {dbSnapshot.repair.error ? (
                    <div className="text-amber-700">
                      Certaines données biométriques n'ont pas pu être resynchronisées automatiquement.
                    </div>
                  ) : (
                    <div className="text-green-700">Les données sont bien synchronisées.</div>
                  )}
                </div>
              </Section>
            )}
            <Section title="Résumé session">
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Session:</span> <span className="font-mono">{detail.session_id}</span></div>
                <div><span className="font-medium">Agent:</span> {detail.agent_name || dbSnapshot?.agent_name || '—'}</div>
                <div><span className="font-medium">Matricule:</span> <span className="font-mono">{detail.registration_number || dbSnapshot?.registration_number || '—'}</span></div>
                {displayStatus && (
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Statut:</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${identificationStatusClass(displayStatus.code)}`}>
                      {displayStatus.label}
                    </span>
                  </div>
                )}
                {detail && getIdentificationBlockingSummary(detail.status, detail.modality_status, detail.error_message) && (
                  <div className="rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-900">
                    {getIdentificationBlockingSummary(detail.status, detail.modality_status, detail.error_message)}
                  </div>
                )}
                <div><span className="font-medium">Progression:</span> {detail.progress_percentage}%</div>
                <div><span className="font-medium">Canal:</span> {detail.channel}</div>
                <div><span className="font-medium">Opérateur:</span> {detail.operator_id}</div>
                <div><span className="font-medium">Créée le:</span> {new Date(detail.created_at).toLocaleString('fr-FR')}</div>
                <div><span className="font-medium">Erreur:</span> {detail.error_message || '—'}</div>
              </div>
            </Section>

            <Section title="Scores biométriques">
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Photo (bd.photo_quality):</span> {String(dbBiometric.photo_quality ?? '-')}</div>
                <div><span className="font-medium">Iris (bd.iris_quality):</span> {String(dbBiometric.iris_quality ?? '-')}</div>
                <div><span className="font-medium">Empreintes (bd.fingerprints_quality):</span> {String(dbBiometric.fingerprints_quality ?? '-')}</div>
                <div><span className="font-medium">ABIS:</span> {JSON.stringify(detail.abis_result || {})}</div>
              </div>
            </Section>

            <Section title="Photo">
              {faceSrc ? (
                <img src={faceSrc} alt="Photo identification" className="w-full max-h-72 object-contain rounded-md border mb-3" />
              ) : (
                <div className="text-xs text-gray-500 mb-2">Aucune image photo persistée en BD.</div>
              )}
            </Section>

            <Section title="Iris">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="border rounded-md p-2">
                  <div className="text-xs font-semibold text-gray-700 mb-1">Oeil gauche</div>
                  {irisLeftSrc ? (
                    <img src={irisLeftSrc} alt="Iris gauche" className="w-full h-48 object-contain rounded bg-gray-50" />
                  ) : (
                    <div className="text-xs text-gray-500">Image non disponible.</div>
                  )}
                </div>
                <div className="border rounded-md p-2">
                  <div className="text-xs font-semibold text-gray-700 mb-1">Oeil droit</div>
                  {irisRightSrc ? (
                    <img src={irisRightSrc} alt="Iris droit" className="w-full h-48 object-contain rounded bg-gray-50" />
                  ) : (
                    <div className="text-xs text-gray-500">Image non disponible.</div>
                  )}
                </div>
              </div>
            </Section>

            <Section title="Données BD - Empreintes (fgp_fingerprints)">
              <div className="text-sm text-gray-700 mb-2">Empreintes persistées: {dbFingerprints.length}</div>
              {dbFingerprints.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  {dbFingerprints.map((fp, idx) => {
                    const src = asImageSrc(fp.image_uri);
                    return (
                      <div key={`${fp.id || idx}`} className="border rounded-md p-2">
                        <div className="text-xs font-semibold text-gray-700 mb-1">
                          {String(fp.finger_position || 'UNKNOWN')} - {String(fp.capture_status || '-')}
                        </div>
                        {src ? (
                          <img src={src} alt={`fingerprint-${idx}`} className="w-full h-40 object-contain bg-gray-50 rounded" />
                        ) : (
                          <div className="text-xs text-gray-500">Image brute indisponible ({String(fp.image_uri || '')})</div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </Section>

            <Section title="Fiche employé ONIP (payload)">
              <div className="text-sm space-y-1">
                <div><span className="font-medium">Nom complet:</span> {String(dbEmployee.first_name || '')} {String(dbEmployee.middle_name || '')} {String(dbEmployee.last_name || '')}</div>
                <div><span className="font-medium">Matricule:</span> {String(dbEmployee.registration_number || detail.registration_number || '—')}</div>
                <div><span className="font-medium">Sexe:</span> {String(dbEmployee.gender || '—')}</div>
                <div><span className="font-medium">Date naissance:</span> {String(dbEmployee.date_of_birth || '—')}</div>
                <div><span className="font-medium">Lieu naissance:</span> {String(dbEmployee.place_of_birth || '—')}</div>
                <div><span className="font-medium">Email:</span> {String(dbEmployee.email_professional || dbEmployee.email || '—')}</div>
                <div><span className="font-medium">Téléphone:</span> {String(dbEmployee.mobile_number || dbEmployee.telephone_number || '—')}</div>
              </div>
            </Section>

            <Section title="Données BD - Documents (fgp_documents)">
              <div className="text-sm text-gray-700 mb-2">Documents persistés: {dbDocuments.length}</div>
              {dbDocuments.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  {dbDocuments.slice(0, 6).map((doc, idx) => {
                    const src = asImageSrc(doc.document_uri);
                    const mimeType = String(doc.mime_type || '').toLowerCase();
                    const isImage = mimeType.startsWith('image/');
                    const isPdf = mimeType.includes('pdf');
                    return (
                      <div key={`${doc.id || idx}`} className="border rounded-md p-2">
                        <div className="text-xs font-semibold text-gray-700 mb-1">{String(doc.document_type || 'DOCUMENT')}</div>
                        <div className="text-[10px] text-gray-500 mb-1">{mimeType || 'type inconnu'}</div>
                        {src ? (
                          isImage ? (
                            <img src={src} alt={`document-${idx}`} className="w-full h-40 object-contain bg-gray-50 rounded" />
                          ) : isPdf ? (
                            <iframe src={src} title={`document-${idx}`} className="w-full h-40 bg-gray-50 rounded border" />
                          ) : (
                            <a
                              href={src}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs text-secondary-700 hover:underline"
                            >
                              Ouvrir le document
                            </a>
                          )
                        ) : (
                          <div className="text-xs text-gray-500">Aperçu indisponible ({String(doc.document_uri || '')})</div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </Section>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default EnrollmentSessionDetailPage;
