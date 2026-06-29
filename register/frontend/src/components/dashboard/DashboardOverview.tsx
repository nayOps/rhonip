'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { DashboardStats } from '../../types';
import { apiService } from '../../services/api';
import {
  identificationStatusClass,
  resolveIdentificationDisplayStatus,
} from '../../services/enrollment-session-api';

const UsersIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

const TrendingUpIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
  </svg>
);

const CheckCircleIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const ServerIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
  </svg>
);

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

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'yellow' | 'red';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, changeType = 'neutral', icon, color }) => {
  const colorClasses = {
    blue: 'bg-secondary-50 text-secondary-600',
    green: 'bg-success-50 text-success-600',
    yellow: 'bg-accent-50 text-accent-600',
    red: 'bg-primary-50 text-primary-600',
  };

  const changeColorClasses = {
    positive: 'text-success-600',
    negative: 'text-error-600',
    neutral: 'text-gray-600',
  };

  return (
    <div className="bg-white rounded-lg shadow-soft p-6 hover:shadow-medium transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`mt-2 text-sm font-medium ${changeColorClasses[changeType]}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`flex-shrink-0 ${colorClasses[color]} p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

interface ProgressBarProps {
  name: string;
  count: number;
  total: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ name, count, total }) => {
  const percentage = total > 0 ? (count / total) * 100 : 0;

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center text-sm">
        <span className="font-medium text-gray-700">{name}</span>
        <span className="text-gray-600">{count.toLocaleString()}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-secondary-600 h-2.5 rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

const DashboardOverview: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchStats = async () => {
    try {
      const data = await apiService.getDashboardStats();
      setStats(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (e: any) {
      setError(e.message || 'Erreur de chargement des statistiques');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-secondary-600"></div>
          <p className="mt-4 text-gray-600">Chargement des statistiques…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error-50 border border-error-200 rounded-lg p-6">
        <div className="flex items-center">
          <svg className="h-6 w-6 text-error-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="text-sm font-medium text-error-800">Erreur de chargement</h3>
            <p className="text-sm text-error-700 mt-1">{error}</p>
          </div>
        </div>
        <button
          onClick={fetchStats}
          className="mt-4 px-4 py-2 bg-error-600 text-white text-sm font-medium rounded-md hover:bg-error-700"
        >
          Réessayer
        </button>
      </div>
    );
  }

  if (!stats) return null;

  const byStatus = stats.by_status ?? {};
  const byProvince = stats.by_province ?? {};
  const recentSessions = stats.recent_sessions ?? [];
  const totalStatus = Object.values(byStatus).reduce((acc, val) => acc + (val ?? 0), 0);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Guichet agents ONIP</h2>
          <p className="text-sm text-gray-600 mt-1">
            Dernière mise à jour : {lastUpdate.toLocaleTimeString('fr-FR')}
          </p>
        </div>
        <button
          onClick={fetchStats}
          className="px-4 py-2 bg-secondary-600 text-white text-sm font-medium rounded-md hover:bg-secondary-700 transition-colors"
        >
          Actualiser
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Agents identifiés"
          value={stats.total_enrolled.toLocaleString()}
          change={stats.enrollments_this_month > 0 ? `+${stats.enrollments_this_month} ce mois` : 'Aucune identification ce mois'}
          changeType={stats.enrollments_this_month > 0 ? 'positive' : 'neutral'}
          icon={<UsersIcon />}
          color="blue"
        />

        <StatCard
          title="Aujourd'hui"
          value={stats.enrollments_today.toLocaleString()}
          change={stats.enrollments_today > 0 ? 'En progression' : 'Aucune identification'}
          changeType={stats.enrollments_today > 0 ? 'positive' : 'neutral'}
          icon={<TrendingUpIcon />}
          color="green"
        />

        <StatCard
          title="Identifications totales"
          value={(stats.sessions_total ?? 0).toLocaleString()}
          change={`${stats.sessions_with_matricule ?? 0} avec matricule`}
          changeType="neutral"
          icon={<CheckCircleIcon />}
          color="yellow"
        />

        <StatCard
          title="Taux de réussite"
          value={`${Math.round(stats.quality_score * 100)}%`}
          change={(stats.sessions_failed ?? 0) > 0 ? `${stats.sessions_failed} échec(s)` : 'Aucun échec'}
          changeType={(stats.sessions_failed ?? 0) > 0 ? 'negative' : 'positive'}
          icon={<ServerIcon />}
          color="red"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-soft p-5">
          <p className="text-sm text-gray-500">Matricules liés</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{(stats.sessions_with_matricule ?? 0).toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow-soft p-5">
          <p className="text-sm text-gray-500">Enregistrements biométriques</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{(stats.biometric_total ?? 0).toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow-soft p-5">
          <p className="text-sm text-gray-500">Empreintes capturées</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{(stats.fingerprints_total ?? 0).toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-soft p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Identifications par statut</h3>
            <span className="text-sm font-medium text-gray-600">
              {totalStatus} total
            </span>
          </div>

          {Object.keys(byStatus).length > 0 ? (
            <div className="space-y-4">
              {Object.entries(byStatus)
                .sort(([, a], [, b]) => b - a)
                .map(([status, count]) => (
                  <ProgressBar
                    key={status}
                    name={STATUS_LABELS[status] || status}
                    count={count}
                    total={totalStatus}
                  />
                ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Aucune identification enregistrée</p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-soft p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Répartition par province</h3>
            <span className="text-sm font-medium text-gray-600">
              {Object.keys(byProvince).length} provinces
            </span>
          </div>

          {Object.keys(byProvince).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(byProvince)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 10)
                .map(([province, count]) => (
                  <div key={province} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                    <span className="text-sm font-medium text-gray-700">{province}</span>
                    <span className="text-sm text-gray-900 font-semibold">{count.toLocaleString()}</span>
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Aucune donnée disponible</p>
              <p className="text-sm mt-2">Les statistiques apparaîtront après les premières identifications</p>
            </div>
          )}
        </div>
      </div>

      {recentSessions.length > 0 && (
        <div className="bg-white rounded-lg shadow-soft p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Dernières identifications</h3>
            <Link href="/dashboard/enrollments" className="text-sm text-secondary-600 hover:text-secondary-700">
              Voir tout →
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 pr-4 font-medium">Agent</th>
                  <th className="pb-2 pr-4 font-medium">Matricule</th>
                  <th className="pb-2 pr-4 font-medium">Statut</th>
                  <th className="pb-2 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map((session) => {
                  const rowStatus = resolveIdentificationDisplayStatus(
                    session.status,
                    session.modality_status
                  );
                  return (
                  <tr key={session.session_id} className="border-b border-gray-50 last:border-0">
                    <td className="py-3 pr-4">
                      <Link
                        href={`/dashboard/enrollments/${session.session_id}`}
                        className="text-secondary-600 hover:underline"
                      >
                        {session.agent_name}
                      </Link>
                    </td>
                    <td className="py-3 pr-4 font-mono text-xs">{session.registration_number || '—'}</td>
                    <td className="py-3 pr-4">
                      <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${identificationStatusClass(rowStatus.code)}`}>
                        {rowStatus.label}
                      </span>
                    </td>
                    <td className="py-3 text-gray-600">
                      {session.created_at
                        ? new Date(session.created_at).toLocaleString('fr-FR')
                        : '—'}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-soft p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">État du système</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-3">
            <div className={`h-3 w-3 rounded-full ${stats.system_health.status === 'HEALTHY' ? 'bg-success-500' : 'bg-error-500'} animate-pulse`}></div>
            <div>
              <p className="text-sm font-medium text-gray-700">Statut</p>
              <p className="text-lg font-semibold text-gray-900">{stats.system_health.status}</p>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-700">Temps de disponibilité</p>
            <p className="text-lg font-semibold text-gray-900">
              {Math.floor(stats.system_health.uptime / 86400)}j {Math.floor((stats.system_health.uptime % 86400) / 3600)}h
            </p>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-700">Temps de réponse moyen</p>
            <p className="text-lg font-semibold text-gray-900">
              {stats.system_health.response_time} ms
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-secondary-50 to-primary-50 rounded-lg shadow-soft p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/dashboard/enrollments"
            className="block p-4 bg-white rounded-lg hover:shadow-md transition-shadow text-center"
          >
            <div className="text-secondary-600 font-semibold mb-1">Liste identification</div>
            <div className="text-sm text-gray-600">Fiches et modalités agents</div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
