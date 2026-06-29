'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { probeGuichetComponents } from '@/lib/guichet-components-probe';
import {
  GUICHET_COMPONENT_CATALOG,
  allComponentsOk,
  allRequiredComponentsReady,
  checkingState,
  type GuichetComponentCheck,
  type ComponentHealthStatus,
} from '@/lib/guichet-components';
import { probeGuichetComponentsMock } from '@/lib/guichet-components-mock';

function statusStyles(status: ComponentHealthStatus) {
  switch (status) {
    case 'ok':
      return {
        dot: 'bg-green-500',
        border: 'border-green-200 bg-green-50',
        text: 'text-green-800',
        badge: 'bg-green-100 text-green-800',
        label: 'OK',
      };
    case 'degraded':
      return {
        dot: 'bg-amber-500',
        border: 'border-amber-200 bg-amber-50',
        text: 'text-amber-900',
        badge: 'bg-amber-100 text-amber-800',
        label: 'Dégradé',
      };
    case 'down':
      return {
        dot: 'bg-red-500',
        border: 'border-red-200 bg-red-50',
        text: 'text-red-800',
        badge: 'bg-red-100 text-red-800',
        label: 'Arrêt',
      };
    default:
      return {
        dot: 'bg-gray-400 animate-pulse',
        border: 'border-gray-200 bg-gray-50',
        text: 'text-gray-600',
        badge: 'bg-gray-100 text-gray-700',
        label: 'Vérification…',
      };
  }
}

const useMockProbe =
  typeof process !== 'undefined' && process.env.NEXT_PUBLIC_MOCK_HEALTH === 'true';

export default function SystemHealthCheck() {
  const router = useRouter();
  const [components, setComponents] = useState<GuichetComponentCheck[]>(() =>
    GUICHET_COMPONENT_CATALOG.map((c) => checkingState(c.id))
  );
  const [loading, setLoading] = useState(true);

  const runProbe = useCallback(async () => {
    setLoading(true);
    setComponents(GUICHET_COMPONENT_CATALOG.map((c) => checkingState(c.id)));
    try {
      const result = useMockProbe
        ? await probeGuichetComponentsMock()
        : await probeGuichetComponents();
      setComponents(result);
    } catch {
      setComponents(
        GUICHET_COMPONENT_CATALOG.map((c) =>
          checkingState(c.id)
        ).map((c) => ({
          ...c,
          status: 'degraded' as const,
          message: 'Sonde interrompue — vous pouvez entrer en mode test',
        }))
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    runProbe();
  }, [runProbe]);

  const allGreen = !loading && allComponentsOk(components);
  const requiredReady = !loading && allRequiredComponentsReady(components);
  /** Mode test guichet : toujours permettre d’entrer pour valider composant par composant. */
  const canEnter = !loading;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex flex-col">
      <header className="px-6 py-8 max-w-5xl mx-auto w-full">
        <div className="flex items-center justify-between gap-4 mb-4">
          <p className="text-sm text-slate-400 uppercase tracking-widest">Guichet FGP — ONIP</p>
          <button
            type="button"
            onClick={() => router.push('/')}
            className="text-sm text-slate-400 hover:text-white shrink-0"
          >
            ← Accueil
          </button>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold mt-2">Analyse du poste</h1>
        <p className="text-slate-300 mt-2 max-w-2xl">
          Diagnostic du poste — vous pouvez entrer même si des cartes sont en alerte, pour tester chaque
          composant à son étape d&apos;enrôlement.
        </p>
      </header>

      <main className="flex-1 px-6 pb-8 max-w-5xl mx-auto w-full">
        <div
          className={`rounded-2xl border p-4 mb-6 flex items-center justify-between gap-4 ${
            allGreen
              ? 'border-green-500/40 bg-green-500/10'
              : 'border-amber-500/40 bg-amber-500/10'
          }`}
        >
          <div>
            <p className="font-semibold text-lg">
              {loading
                ? 'Analyse en cours…'
                : allGreen
                  ? 'Tous les composants sont opérationnels'
                  : requiredReady
                    ? 'Composants requis OK — optionnels partiels'
                    : 'Certains composants requis sont en alerte — entrée autorisée en mode test'}
            </p>
            <p className="text-sm text-slate-300 mt-1">
              {loading
                ? 'Sonde des bridges, gateway, empreintes, iris, caméra et imprimante.'
                : 'Vous pouvez entrer et tester chaque brique à son étape (photo, empreintes, iris, etc.).'}
            </p>
          </div>
          {!loading && (
            <span
              className={`text-4xl ${allGreen ? 'text-green-400' : 'text-amber-400'}`}
            >
              {allGreen ? '✓' : '◐'}
            </span>
          )}
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          {components.map((c) => {
            const s = statusStyles(c.status);
            return (
              <div
                key={c.id}
                className={`rounded-xl border p-4 ${s.border} transition-colors`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className={`h-3 w-3 rounded-full shrink-0 ${s.dot}`} />
                    <div>
                      <h2 className="font-semibold text-slate-900">{c.label}</h2>
                      {!c.required && (
                        <span className="text-xs text-slate-500">(optionnel)</span>
                      )}
                    </div>
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${s.badge}`}>
                    {s.label}
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-1">{c.description}</p>
                <p className={`text-sm mt-2 ${s.text}`}>{c.message}</p>
                {c.endpoint && (
                  <p className="text-xs text-slate-500 mt-2 font-mono truncate">{c.endpoint}</p>
                )}
              </div>
            );
          })}
        </div>

        <div className="mt-8 flex flex-wrap gap-3 justify-end">
          <button
            type="button"
            onClick={runProbe}
            disabled={loading}
            className="px-5 py-3 rounded-lg border border-slate-600 text-slate-200 hover:bg-slate-800 disabled:opacity-50"
          >
            Relancer l’analyse
          </button>
          <button
            type="button"
            disabled={!canEnter}
            onClick={() => router.push('/auth')}
            className="px-8 py-3 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg"
            title={
              requiredReady
                ? 'Tous les composants requis sont joignables ou dégradés'
                : 'Mode test : continuer malgré des alertes sur la sonde'
            }
          >
            Entrer →
          </button>
        </div>

        <p className="text-xs text-slate-500 mt-4 text-center">
          {useMockProbe ? (
            <>
              Mode mock — <code className="text-slate-400">NEXT_PUBLIC_MOCK_HEALTH=true</code>
              {' · '}
              <code className="text-slate-400">NEXT_PUBLIC_MOCK_HEALTH_FAIL=true</code> pour simuler
              une panne iris.
            </>
          ) : (
            <>
              Sonde réelle (Device Bridge, gateway, modules). Mock :{' '}
              <code className="text-slate-400">NEXT_PUBLIC_MOCK_HEALTH=true</code>
            </>
          )}
        </p>
      </main>
    </div>
  );
}
