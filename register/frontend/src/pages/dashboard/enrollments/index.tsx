'use client';

import React, { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useAuth } from '@/context/AuthContext';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import {
  EnrollmentDbOverview,
  EnrollmentSessionSummary,
  formatModalitySummary,
  getEnrollmentDbOverview,
  getIdentificationBlockingSummary,
  identificationStatusClass,
  listEnrollmentSessions,
  resolveIdentificationDisplayStatus,
} from '@/services/enrollment-session-api';
import { generateCompletedEnrollmentsPdf } from '@/lib/enrollment-completed-report-pdf';
import EnrollmentResumeActions from '@/components/enrollment/EnrollmentResumeActions';

const statusClass = identificationStatusClass;

const EnrollmentSessionsPage: React.FC = () => {
  const router = useRouter();
  const { logout, session } = useAuth();
  const { isReady, isAuthenticated } = useRequireAuth(['admin']);

  const [rows, setRows] = useState<EnrollmentSessionSummary[]>([]);
  const [overview, setOverview] = useState<EnrollmentDbOverview | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [nextUrl, setNextUrl] = useState<string | null>(null);
  const [prevUrl, setPrevUrl] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfMessage, setPdfMessage] = useState<string | null>(null);

  const fetchRows = async (targetPage = page, targetPageSize = pageSize) => {
    try {
      const [listData, db] = await Promise.all([
        listEnrollmentSessions(targetPage, targetPageSize),
        getEnrollmentDbOverview(),
      ]);
      setRows(listData.results);
      setTotalCount(listData.count);
      setNextUrl(listData.next);
      setPrevUrl(listData.previous);
      setOverview(db);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRows(page, pageSize);
  }, [page, pageSize]);

  const handleExportPdf = async () => {
    setPdfLoading(true);
    setPdfMessage(null);
    try {
      await generateCompletedEnrollmentsPdf();
      setPdfMessage('Rapport PDF généré avec succès.');
    } catch (err: unknown) {
      setPdfMessage(err instanceof Error ? err.message : 'Échec génération PDF');
    } finally {
      setPdfLoading(false);
    }
  };

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) =>
      [
        r.session_id,
        r.registration_number || '',
        r.agent_name || '',
        r.status,
        r.error_message || '',
        formatModalitySummary(r.modality_status),
      ]
        .join(' ')
        .toLowerCase()
        .includes(q)
    );
  }, [rows, query]);

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
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Identification agents ONIP</h1>
            <p className="text-sm text-gray-600">
              Guichet biométrique — {totalCount} identification(s) au total
            </p>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Rechercher matricule, agent, session…"
              className="border border-gray-300 rounded-md px-3 py-2 text-sm min-w-[280px]"
            />
            <button onClick={() => fetchRows(page, pageSize)} className="px-3 py-2 text-sm rounded-md bg-secondary-600 text-white hover:bg-secondary-700">
              Actualiser
            </button>
            <button
              type="button"
              onClick={() => void handleExportPdf()}
              disabled={pdfLoading}
              className="px-3 py-2 text-sm rounded-md bg-teal-700 text-white hover:bg-teal-800 disabled:opacity-50 whitespace-nowrap"
            >
              {pdfLoading ? 'PDF…' : 'Rapport PDF (identifiés)'}
            </button>
          </div>
        </div>

        {pdfMessage && (
          <div className={`rounded-lg border px-4 py-2 text-sm ${pdfMessage.includes('succès') ? 'bg-green-50 border-green-200 text-green-800' : 'bg-amber-50 border-amber-200 text-amber-900'}`}>
            {pdfMessage}
          </div>
        )}

        {overview && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            <div className="bg-white rounded-lg shadow-soft p-4"><div className="text-xs text-gray-500">Identifications</div><div className="text-xl font-semibold">{overview.sessions_total}</div></div>
            <div className="bg-white rounded-lg shadow-soft p-4"><div className="text-xs text-gray-500">Avec matricule</div><div className="text-xl font-semibold">{overview.sessions_with_matricule}</div></div>
            <div className="bg-white rounded-lg shadow-soft p-4"><div className="text-xs text-gray-500">Biométrie (fgp_biometric)</div><div className="text-xl font-semibold">{overview.biometric_total}</div></div>
            <div className="bg-white rounded-lg shadow-soft p-4"><div className="text-xs text-gray-500">Empreintes (fgp_fingerprints)</div><div className="text-xl font-semibold">{overview.fingerprints_total}</div></div>
            <div className="bg-white rounded-lg shadow-soft p-4"><div className="text-xs text-gray-500">Documents</div><div className="text-xl font-semibold">{overview.documents_total}</div></div>
          </div>
        )}

        {loading ? (
          <div className="bg-white rounded-lg shadow-soft p-6 text-gray-500">Chargement des identifications…</div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">{error}</div>
        ) : (
          <div className="bg-white rounded-lg shadow-soft overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="text-left p-3">Matricule</th>
                  <th className="text-left p-3">Agent ONIP</th>
                  <th className="text-left p-3">Statut</th>
                  <th className="text-left p-3">Modalités</th>
                  <th className="text-left p-3">Créée le</th>
                  <th className="text-left p-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((row) => {
                  const displayStatus = resolveIdentificationDisplayStatus(row.status, row.modality_status);
                  const blocking = getIdentificationBlockingSummary(
                    row.status,
                    row.modality_status,
                    row.error_message
                  );
                  return (
                  <tr key={row.id} className="border-t border-gray-100">
                    <td className="p-3 font-mono text-xs font-semibold">{row.registration_number || '—'}</td>
                    <td className="p-3">{row.agent_name || '—'}</td>
                    <td className="p-3">
                      <div className="space-y-1">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusClass(displayStatus.code)}`}>
                          {displayStatus.label}
                        </span>
                        {blocking && (
                          <div className="text-[11px] text-amber-800 max-w-xs">{blocking}</div>
                        )}
                      </div>
                    </td>
                    <td className="p-3 text-xs text-gray-600">{formatModalitySummary(row.modality_status)}</td>
                    <td className="p-3">{new Date(row.created_at).toLocaleString('fr-FR')}</td>
                    <td className="p-3">
                      <div className="flex flex-col gap-1">
                        <Link href={`/dashboard/enrollments/${encodeURIComponent(row.session_id)}`} className="text-secondary-700 hover:underline font-medium">
                          Voir fiche
                        </Link>
                        <EnrollmentResumeActions sessionId={row.session_id} />
                      </div>
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between p-3 border-t border-gray-100">
              <div className="text-xs text-gray-500">
                Page {page} · {rows.length} résultat(s) affiché(s)
              </div>
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-600">Taille</label>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPage(1);
                    setPageSize(Number(e.target.value));
                  }}
                  className="border border-gray-300 rounded px-2 py-1 text-xs"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                </select>
                <button
                  disabled={!prevUrl}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-2 py-1 text-xs rounded border border-gray-300 disabled:opacity-40"
                >
                  Précédent
                </button>
                <button
                  disabled={!nextUrl}
                  onClick={() => setPage((p) => p + 1)}
                  className="px-2 py-1 text-xs rounded border border-gray-300 disabled:opacity-40"
                >
                  Suivant
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default EnrollmentSessionsPage;
