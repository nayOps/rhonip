'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/context/AuthContext';
import HandFingerprint, { type HandSide } from '@/components/auth/HandFingerprint';

export default function GuichetAuth() {
  const router = useRouter();
  const { loginOpsFingerprint, loginAdmin } = useAuth();
  const [mode, setMode] = useState<'ops' | 'admin'>('ops');
  const [hand, setHand] = useState<HandSide>('right');
  const [email, setEmail] = useState('admin@fgp.local');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'idle' | 'scanning' | 'done'>('idle');

  const handleOpsAuth = async () => {
    setError(null);
    setStep('scanning');
    setLoading(true);
    try {
      await loginOpsFingerprint(hand);
      setStep('done');
      await new Promise((r) => setTimeout(r, 450));
      router.replace('/agents');
    } catch (err) {
      setStep('idle');
      setError(err instanceof Error ? err.message : 'Authentification échouée');
    } finally {
      setLoading(false);
    }
  };

  const handleAdminAuth = async () => {
    setError(null);
    setLoading(true);
    try {
      await loginAdmin(email, password);
      router.replace('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentification admin échouée');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex flex-col">
      <header className="px-6 py-5 border-b border-slate-700/60">
        <div className="max-w-3xl mx-auto flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400">Guichet FGP</p>
            <h1 className="text-xl font-bold mt-0.5">Authentification opérateur</h1>
          </div>
          <button
            type="button"
            onClick={() => router.push('/analyse')}
            className="text-sm text-slate-400 hover:text-white shrink-0"
          >
            ← Retour
          </button>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg">
          <div className="rounded-3xl border border-slate-700 bg-slate-900/70 backdrop-blur p-8 shadow-2xl">
            <div className="mb-6 flex gap-2 bg-slate-800 rounded-xl p-1">
              <button
                type="button"
                onClick={() => setMode('ops')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'ops' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:text-white'}`}
              >
                Opérateur (FAP60)
              </button>
              <button
                type="button"
                onClick={() => setMode('admin')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'admin' ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:text-white'}`}
              >
                Admin (Dashboard)
              </button>
            </div>

            {mode === 'ops' ? (
              <>
                <div className="text-center mb-8">
                  <p className="text-emerald-400 text-sm font-medium uppercase tracking-wider">
                    Empreinte digitale
                  </p>
                  <h2 className="text-2xl font-bold mt-2">Choisissez votre main</h2>
                  <p className="text-slate-400 text-sm mt-2">
                    Placez l&apos;index de la main sélectionnée sur le lecteur FAP60
                  </p>
                </div>

                <div className="flex justify-center gap-6 sm:gap-10 mb-8">
                  <HandFingerprint
                    side="left"
                    selected={hand === 'left'}
                    scanning={step === 'scanning'}
                    onSelect={() => setHand('left')}
                  />
                  <HandFingerprint
                    side="right"
                    selected={hand === 'right'}
                    scanning={step === 'scanning'}
                    onSelect={() => setHand('right')}
                  />
                </div>

                <div
                  className={`rounded-xl border px-4 py-4 text-center text-sm transition-colors ${
                    step === 'done'
                      ? 'border-green-500/50 bg-green-500/10 text-green-300'
                      : step === 'scanning'
                        ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
                        : 'border-slate-700 bg-slate-800/50 text-slate-400'
                  }`}
                >
                  {step === 'scanning' && (
                    <>
                      <div className="inline-block h-8 w-8 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin mb-2" />
                      <p>Lecture en cours — main {hand === 'left' ? 'gauche' : 'droite'}…</p>
                    </>
                  )}
                  {step === 'done' && <p>Empreinte reconnue — ouverture de l&apos;enrôlement</p>}
                  {step === 'idle' && (
                    <p>
                      Main {hand === 'left' ? 'gauche' : 'droite'} sélectionnée · lecteur prêt (mock)
                    </p>
                  )}
                </div>
              </>
            ) : (
              <div className="space-y-4">
                <div className="text-center mb-2">
                  <p className="text-indigo-400 text-sm font-medium uppercase tracking-wider">Accès administration</p>
                  <h2 className="text-2xl font-bold mt-2">Connexion admin</h2>
                  <p className="text-slate-400 text-sm mt-2">Utilisez le compte admin local pour le tableau de bord</p>
                </div>
                <div>
                  <label className="text-sm text-slate-300 block mb-1">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                  />
                </div>
                <div>
                  <label className="text-sm text-slate-300 block mb-1">Mot de passe</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                  />
                </div>
                <p className="text-xs text-slate-400">
                  Identifiants par défaut: <span className="font-mono">admin@fgp.local / admin123</span>
                </p>
              </div>
            )}

            {error && (
              <p className="mt-4 text-sm text-red-300 bg-red-950/50 border border-red-800 rounded-lg p-3">
                {error}
              </p>
            )}

            <button
              type="button"
              onClick={mode === 'ops' ? handleOpsAuth : handleAdminAuth}
              disabled={loading}
              className={`mt-6 w-full py-3.5 rounded-xl text-white font-semibold disabled:opacity-50 shadow-lg transition-colors ${mode === 'ops' ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-900/30' : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-900/30'}`}
            >
              {loading ? 'Vérification…' : mode === 'ops' ? "S'authentifier" : 'Se connecter (admin)'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
