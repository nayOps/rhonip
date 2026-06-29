'use client';

import React, { useEffect, useState } from 'react';
import { DashboardStats } from '../../types';
import { apiService } from '../../services/api';

const STATUS_LABELS: Record<string, string> = {
  PENDING: 'En attente',
  VALIDATING: 'En validation',
  PROCESSING: 'En traitement',
  ABIS_CHECK: 'Vérification ABIS',
  REVIEW: 'En révision',
  COMPLETED: 'Terminé',
  FAILED: 'Échoué',
  CANCELLED: 'Annulé',
};

const StatCard: React.FC<{ title: string; value: string | number; sub?: string }> = ({ title, value, sub }) => (
  <div className="p-5 bg-white rounded-lg shadow">
    <div className="text-sm text-gray-500">{title}</div>
    <div className="mt-2 text-2xl font-semibold text-gray-900">{value}</div>
    {sub && <div className="mt-1 text-xs text-gray-400">{sub}</div>}
  </div>
);

const DashboardStatsWidget: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await apiService.getDashboardStats();
        setStats(data);
      } catch (e: any) {
        setError(e.message || 'Erreur de chargement des statistiques');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="text-gray-600">Chargement des statistiques…</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!stats) return null;

  const byStatus = stats.by_status ?? {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Agents enrôlés" value={stats.total_enrolled} />
        <StatCard title="Aujourd'hui" value={stats.enrollments_today} />
        <StatCard title="Sessions totales" value={stats.sessions_total ?? 0} sub={`${stats.sessions_with_matricule ?? 0} matricules`} />
        <StatCard title="Taux de réussite" value={`${Math.round(stats.quality_score * 100)}%`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-5 bg-white rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Par statut</h3>
          <ul className="space-y-2 text-sm">
            {Object.entries(byStatus).map(([k, v]) => (
              <li key={k} className="flex justify-between">
                <span className="text-gray-600">{STATUS_LABELS[k] || k}</span>
                <span className="font-medium">{v}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="p-5 bg-white rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Par province</h3>
          <ul className="space-y-2 text-sm">
            {Object.entries(stats.by_province ?? {}).map(([k, v]) => (
              <li key={k} className="flex justify-between">
                <span className="text-gray-600">{k}</span>
                <span className="font-medium">{v}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="p-5 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">Santé du système</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-500">Statut</div>
            <div className="font-medium">{stats.system_health.status}</div>
          </div>
          <div>
            <div className="text-gray-500">Uptime</div>
            <div className="font-medium">{Math.round(stats.system_health.uptime / 3600)} h</div>
          </div>
          <div>
            <div className="text-gray-500">Temps de réponse</div>
            <div className="font-medium">{Math.round(stats.system_health.response_time)} ms</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardStatsWidget;
