import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { FingerprintCapture as FingerprintData, FingerPosition, FingerStatus } from '@/types';
import { isWorkflowSkipEnabled } from '@/lib/workflow-test-mode';
import { buildFakeFingerprints } from '@/lib/fake-fingerprint-data';
import { isFakeFingerprintAllowed } from '@/lib/fingerprint-fake-mode';
import {
  CAPTURE_HAND_HINT,
  CAPTURE_TYPE_FINGERS,
  CAPTURE_TYPE_LABELS,
  CaptureType,
  captureFingerprints,
  closeFingerprintDevice,
  fetchFingerprintPreview,
  getFingerprintHealth,
  mapPreviewToFinger,
  openFingerprintDevice,
  saveFingerprintBiometrics,
} from '@/services/fingerprint-api';

interface FingerprintCaptureProps {
  onComplete: (fingerprints: FingerprintData[]) => void;
  onBack: () => void;
  sessionId?: string;
  /** Crée la session gateway si absente (guichet). */
  onEnsureSession?: () => Promise<string>;
  /** Message si la session n'a pas pu être créée au chargement (gateway arrêté). */
  gatewayInitWarning?: string | null;
  initialFingerprints?: FingerprintData[];
}

const ALL_FINGERS: FingerPosition[] = [
  'LEFT_LITTLE', 'LEFT_RING', 'LEFT_MIDDLE', 'LEFT_INDEX', 'LEFT_THUMB',
  'RIGHT_THUMB', 'RIGHT_INDEX', 'RIGHT_MIDDLE', 'RIGHT_RING', 'RIGHT_LITTLE',
];

const FINGER_SHORT: Record<FingerPosition, string> = {
  LEFT_LITTLE: 'L', LEFT_RING: 'R', LEFT_MIDDLE: 'M', LEFT_INDEX: 'I', LEFT_THUMB: 'T',
  RIGHT_THUMB: 'T', RIGHT_INDEX: 'I', RIGHT_MIDDLE: 'M', RIGHT_RING: 'R', RIGHT_LITTLE: 'L',
};

const NFIQ_OPTIONS = [
  { value: 1, label: '1 — Excellente' },
  { value: 2, label: '2 — Très bonne' },
  { value: 3, label: '3 — Bonne (défaut)' },
  { value: 4, label: '4 — Moyenne' },
  { value: 5, label: '5 — Faible max' },
];

const LEFT_HAND = CAPTURE_TYPE_FINGERS.left_four;
const RIGHT_HAND = CAPTURE_TYPE_FINGERS.right_four;
const BOTH_THUMBS = CAPTURE_TYPE_FINGERS.both_thumbs;

type EnrollmentPhase = 'left' | 'right' | 'thumbs';

function phaseToCaptureType(phase: EnrollmentPhase): CaptureType {
  if (phase === 'right') return 'right_four';
  if (phase === 'thumbs') return 'both_thumbs';
  return 'left_four';
}

function emptyFingerprints(): FingerprintData[] {
  return ALL_FINGERS.map((position) => ({ position, status: 'PENDING' as FingerStatus }));
}

function mergeFingerprints(initial?: FingerprintData[]): FingerprintData[] {
  const base = emptyFingerprints();
  if (!initial?.length) return base;
  return base.map((fp) => initial.find((i) => i.position === fp.position) ?? fp);
}

function handIsComplete(fingerprints: FingerprintData[], positions: FingerPosition[]): boolean {
  return positions.every((pos) => {
    const fp = fingerprints.find((f) => f.position === pos);
    return fp != null && fp.status !== 'PENDING';
  });
}

export default function FingerprintCapture({
  onComplete,
  onBack,
  sessionId,
  onEnsureSession,
  gatewayInitWarning,
  initialFingerprints,
}: FingerprintCaptureProps) {
  const [fingerprints, setFingerprints] = useState<FingerprintData[]>(() =>
    mergeFingerprints(initialFingerprints)
  );

  useEffect(() => {
    if (initialFingerprints?.length) {
      setFingerprints(mergeFingerprints(initialFingerprints));
    }
  }, [initialFingerprints]);
  const [phase, setPhase] = useState<EnrollmentPhase>('left');
  const captureType = phaseToCaptureType(phase);
  const [nfiqThreshold, setNfiqThreshold] = useState(3);
  const [presentFingers, setPresentFingers] = useState<Set<FingerPosition>>(
    () => new Set(LEFT_HAND)
  );
  const [deviceOpen, setDeviceOpen] = useState(false);
  const [bridgeOk, setBridgeOk] = useState<boolean | null>(null);
  const [bridgeMode, setBridgeMode] = useState<string>('');
  const [platePreview, setPlatePreview] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [usingFakeFingerprints, setUsingFakeFingerprints] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const previewInFlight = useRef(false);
  const activeFingers = useMemo(() => CAPTURE_TYPE_FINGERS[captureType], [captureType]);
  const leftComplete = useMemo(() => handIsComplete(fingerprints, LEFT_HAND), [fingerprints]);
  const rightComplete = useMemo(() => handIsComplete(fingerprints, RIGHT_HAND), [fingerprints]);
  const thumbsComplete = useMemo(() => handIsComplete(fingerprints, BOTH_THUMBS), [fingerprints]);
  const enrollmentReady = leftComplete && rightComplete && thumbsComplete;
  const enrollmentStep = !leftComplete ? 1 : !rightComplete ? 2 : !thumbsComplete ? 3 : 4;

  const prevComplete = useRef({ left: false, right: false });
  const [previewEpoch, setPreviewEpoch] = useState(0);

  const appendLog = useCallback((line: string) => {
    setLogs((prev) => [...prev.slice(-40), `${new Date().toLocaleTimeString()} — ${line}`]);
  }, []);

  const bumpPreview = useCallback(() => {
    setPlatePreview(null);
    setPreviewEpoch((n) => n + 1);
  }, []);

  useEffect(() => {
    if (leftComplete && !prevComplete.current.left && phase === 'left') {
      setPhase('right');
      bumpPreview();
      appendLog('✓ Main gauche (4) — posez la MAIN DROITE au centre du plateau.');
    }
    if (rightComplete && !prevComplete.current.right && phase === 'right') {
      setPhase('thumbs');
      bumpPreview();
      appendLog('✓ Main droite (4) — posez les DEUX POUCES au centre du plateau.');
    }
    prevComplete.current = { left: leftComplete, right: rightComplete };
  }, [leftComplete, rightComplete, phase, bumpPreview, appendLog]);

  useEffect(() => {
    getFingerprintHealth().then((h) => {
      setBridgeOk(h.ok);
      setBridgeMode(
        [h.mode || h.bridge?.modules?.fingerprint?.mode, h.via ? `via ${h.via}` : '']
          .filter(Boolean)
          .join(' — ')
      );
    });
  }, []);

  useEffect(() => {
    setPresentFingers(new Set(activeFingers));
  }, [captureType, activeFingers]);

  /** Aperçu live — pause uniquement pendant capture finale (pas Open/Close). */
  useEffect(() => {
    if (!deviceOpen || capturing) return;
    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval> | undefined;

    const tick = async () => {
      if (previewInFlight.current) return;
      previewInFlight.current = true;
      try {
        const url = await fetchFingerprintPreview(captureType);
        if (!cancelled) {
          // IMPORTANT: vider l'aperçu quand le plateau est vide
          // (sinon la dernière main capturée reste affichée et induit en erreur).
          setPlatePreview(url ?? null);
        }
      } finally {
        previewInFlight.current = false;
      }
    };

    const startId = window.setTimeout(() => {
      void tick();
      intervalId = window.setInterval(() => void tick(), 700);
    }, previewEpoch > 0 ? 400 : 900);

    return () => {
      cancelled = true;
      window.clearTimeout(startId);
      if (intervalId) window.clearInterval(intervalId);
    };
  }, [deviceOpen, captureType, capturing, previewEpoch]);

  const toggleFinger = (pos: FingerPosition) => {
    if (!activeFingers.includes(pos)) return;
    setPresentFingers((prev) => {
      const next = new Set(prev);
      if (next.has(pos)) {
        if (next.size <= 1) return prev;
        next.delete(pos);
      } else {
        next.add(pos);
      }
      return next;
    });
  };

  const handleOpenDevice = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await openFingerprintDevice();
      setDeviceOpen(res.success);
      appendLog(res.message);
      if (!res.success) setError(res.message);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'OpenDevice échoué';
      setError(msg);
      appendLog(msg);
    } finally {
      setBusy(false);
    }
  };

  const handleCloseDevice = async () => {
    setBusy(true);
    try {
      const res = await closeFingerprintDevice();
      setDeviceOpen(false);
      appendLog(res.message);
    } catch (e) {
      appendLog(e instanceof Error ? e.message : 'CloseDevice échoué');
    } finally {
      setBusy(false);
    }
  };

  const applyCaptureResult = (result: Awaited<ReturnType<typeof captureFingerprints>>) => {
    setUsingFakeFingerprints(false);
    const previews = result.previews;
    const templates = result.templates;
    setFingerprints((prev) =>
      prev.map((fp) => {
        const preview = previews?.find((p) => mapPreviewToFinger(p.position) === fp.position);
        const template = templates?.find((t) => mapPreviewToFinger(t.position) === fp.position);
        if (!preview && !template) return fp;
        const passes = preview ? preview.passes_nfiq !== false : true;
        const nfiq = preview?.nfiq ?? template?.nfiq;
        const status = preview
          ? passes
            ? 'CAPTURED'
            : 'DAMAGED'
          : template?.data_base64
            ? 'CAPTURED'
            : fp.status;
        return {
          ...fp,
          status,
          quality:
            preview?.quality ??
            template?.quality ??
            (nfiq ? (6 - nfiq) * 20 : fp.quality),
          nfiq,
          image: preview
            ? `data:${preview.mime || 'image/png'};base64,${preview.image_base64}`
            : fp.image,
          templateBase64: template?.data_base64 || fp.templateBase64,
          formatId: template?.format_id ?? fp.formatId,
          reason: preview && !passes ? `NFIQ ${preview.nfiq} > seuil ${nfiqThreshold}` : fp.reason,
          timestamp: new Date().toISOString(),
        };
      })
    );
  };

  const handleCapture = async () => {
    if (!deviceOpen) {
      setError('Cliquez d\'abord sur « Ouvrir le lecteur » (OpenDevice).');
      return;
    }
    const present = activeFingers.filter((f) => presentFingers.has(f));
    if (present.length === 0) {
      setError('Sélectionnez au moins un doigt à capturer.');
      return;
    }

    setBusy(true);
    setCapturing(true);
    setError(null);
    appendLog(`Capture démarrée — ${CAPTURE_TYPE_LABELS[captureType]}`);
    const timeoutMs = captureType === 'both_thumbs' ? 45_000 : 38_000;
    appendLog(
      captureType === 'both_thumbs'
        ? 'Posez les DEUX POUCES au centre du plateau (côte à côte), bien à plat — max ~45 s (repli single auto rapide).'
        : 'Posez les 4 doigts AU CENTRE du plateau (pas sur le bord), bien à plat — max ~35 s.'
    );

    const progressId = window.setInterval(() => {
      appendLog('Capture en cours… maintenez les doigts sur le plateau.');
    }, captureType === 'both_thumbs' ? 8000 : 10_000);

    try {
      const result = await captureFingerprints({
        captureType,
        presentFingers: present,
        nfiqThreshold,
        timeoutMs,
      });

      result.logs?.forEach(appendLog);
      appendLog(result.message);

      if (result.previews?.length || result.templates?.length) {
        applyCaptureResult(result);
      }

      bumpPreview();

      if (phase === 'thumbs') {
        appendLog('✓ Pouces (2) — vérifiez les 10 doigts puis « Suivant ».');
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Capture échouée';
      setError(msg);
      appendLog(msg);
    } finally {
      window.clearInterval(progressId);
      setCapturing(false);
      setBusy(false);
    }
  };

  const applyFakeFingerprints = () => {
    const fake = buildFakeFingerprints();
    setFingerprints(fake);
    setUsingFakeFingerprints(true);
    setPresentFingers(new Set(ALL_FINGERS));
    setPhase('thumbs');
    appendLog(
      '✓ Empreintes de démonstration 4+4+2 (sans lecteur). Au bureau : branchez le FAP60 et recapturez pour remplacer.'
    );
  };

  const markMissing = (position: FingerPosition, status: FingerStatus, reason: string) => {
    setFingerprints((prev) =>
      prev.map((fp) =>
        fp.position === position ? { ...fp, status, reason, timestamp: new Date().toISOString() } : fp
      )
    );
    setPresentFingers((prev) => {
      const next = new Set(prev);
      next.delete(position);
      return next;
    });
  };

  const capturedCount = fingerprints.filter((f) => f.status === 'CAPTURED').length;
  const leftCaptured = LEFT_HAND.filter((p) => fingerprints.find((f) => f.position === p)?.status === 'CAPTURED').length;
  const rightCaptured = RIGHT_HAND.filter((p) => fingerprints.find((f) => f.position === p)?.status === 'CAPTURED').length;
  const thumbsCaptured = BOTH_THUMBS.filter((p) => fingerprints.find((f) => f.position === p)?.status === 'CAPTURED').length;

  const handleSubmit = async () => {
    if (!enrollmentReady) {
      if (isWorkflowSkipEnabled()) onComplete([]);
      return;
    }
    setBusy(true);
    setError(null);
    let gatewaySaved = false;
    try {
      let sid = sessionId;
      if (!sid && onEnsureSession) {
        try {
          sid = await onEnsureSession();
          appendLog(`Session gateway : ${sid}`);
        } catch (e) {
          const msg = e instanceof Error ? e.message : 'Gateway indisponible';
          appendLog(`⚠ ${msg}`);
          setError(
            `${msg} — démarrez enrollment_gateway (port 8001). Les empreintes restent en mémoire ; vous pouvez continuer le parcours.`
          );
        }
      }
      if (sid) {
        try {
          await saveFingerprintBiometrics(sid, fingerprints);
          gatewaySaved = true;
          appendLog(
            usingFakeFingerprints
              ? `Empreintes factices enregistrées (${capturedCount}/10) — session ${sid}`
              : `Empreintes enregistrées (${capturedCount} gabarit(s)) — session ${sid}`
          );
        } catch (e) {
          const msg = e instanceof Error ? e.message : 'Sauvegarde gateway échouée';
          appendLog(`⚠ ${msg}`);
          setError(`${msg} — vous pouvez continuer ; relancez le gateway puis refaites l'enrôlement si besoin.`);
        }
      } else {
        appendLog('Aucune session gateway — données conservées localement uniquement.');
      }
      onComplete(fingerprints);
      if (gatewaySaved) setError(null);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Erreur inattendue';
      setError(msg);
      appendLog(msg);
      onComplete(fingerprints);
    } finally {
      setBusy(false);
    }
  };

  const renderFingerCell = (pos: FingerPosition) => {
    const fp = fingerprints.find((f) => f.position === pos);
    if (!fp) return null;
    const inScope = activeFingers.includes(pos);
    const checked = presentFingers.has(pos);
    const nfiq = fp.quality !== undefined ? Math.ceil(6 - fp.quality / 20) : null;

    return (
      <div
        key={pos}
        className={`rounded-lg border p-1.5 text-center transition ${
          inScope ? 'border-blue-300 bg-white' : 'border-gray-200 bg-gray-50 opacity-40'
        } ${fp.status === 'CAPTURED' ? 'ring-2 ring-green-400' : ''}`}
      >
        {inScope && (
          <label className="flex items-center justify-center gap-1 text-xs mb-1 cursor-pointer">
            <input
              type="checkbox"
              checked={checked}
              onChange={() => toggleFinger(pos)}
              disabled={busy}
            />
            <span>{FINGER_SHORT[pos]}</span>
          </label>
        )}
        <div className="h-16 md:h-[4.5rem] flex items-center justify-center bg-gray-100 rounded overflow-hidden">
          {fp.image ? (
            <img src={fp.image} alt={pos} className="max-h-full max-w-full object-contain" />
          ) : (
            <span className="text-gray-400 text-xs">{inScope ? '—' : ''}</span>
          )}
        </div>
        {fp.quality !== undefined && (
          <p className={`text-xs mt-1 font-semibold ${fp.status === 'CAPTURED' ? 'text-green-700' : 'text-amber-700'}`}>
            NFIQ ~{nfiq} · {fp.quality}%
          </p>
        )}
        {fp.reason && <p className="text-xs text-amber-600 mt-0.5">{fp.reason}</p>}
        {inScope && fp.status === 'PENDING' && (
          <button
            type="button"
            onClick={() => markMissing(pos, 'AMPUTATED', 'Doigt absent')}
            className="mt-1 text-xs text-gray-500 underline"
          >
            Absent
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 h-full w-full overflow-hidden bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="shrink-0 px-3 py-2 border-b bg-gradient-to-r from-slate-50 to-blue-50">
        <h2 className="text-base md:text-lg font-bold text-gray-900">Empreintes digitales — FAP60</h2>
        <p className="text-xs text-gray-600 mt-0.5 line-clamp-1">
          {usingFakeFingerprints
            ? 'Mode démonstration — empreintes factices enregistrées (remplaçables par capture FAP60).'
            : bridgeOk === false
              ? 'Lecteur non détecté — utilisez les empreintes de démonstration ou branchez le FAP60 au bureau.'
              : bridgeOk
                ? `Lecteur prêt (mode: ${bridgeMode || 'fap60'}) — enrôlement 4 · 4 · 2 (gauche, droite, pouces)`
                : 'Vérification du service…'}
        </p>
        {isFakeFingerprintAllowed() && !usingFakeFingerprints && (
          <button
            type="button"
            onClick={applyFakeFingerprints}
            disabled={busy}
            className="mt-2 w-full sm:w-auto px-3 py-1.5 rounded-lg text-xs font-medium border border-amber-400 bg-amber-50 text-amber-900 hover:bg-amber-100 disabled:opacity-50"
          >
            Empreintes de démonstration (sans lecteur FAP60)
          </button>
        )}
        <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-xs">
          <span
            className={`px-2 py-0.5 rounded-full font-medium ${
              enrollmentStep === 1 ? 'bg-blue-600 text-white' : leftComplete ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}
          >
            1. Gauche ×4 {leftComplete ? '✓' : ''}
          </span>
          <span className="text-gray-400">→</span>
          <span
            className={`px-2 py-0.5 rounded-full font-medium ${
              enrollmentStep === 2 ? 'bg-blue-600 text-white' : rightComplete ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}
          >
            2. Droite ×4 {rightComplete ? '✓' : ''}
          </span>
          <span className="text-gray-400">→</span>
          <span
            className={`px-2 py-0.5 rounded-full font-medium ${
              enrollmentStep === 3 ? 'bg-blue-600 text-white' : thumbsComplete ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}
          >
            3. Pouces ×2 {thumbsComplete ? '✓' : ''}
          </span>
        </div>
      </div>

      <div className="flex flex-1 min-h-0 overflow-hidden px-1 md:px-2 py-2 gap-2 md:gap-3">
        {/* Settings + contrôles — marge gauche étroite */}
        <div className="w-[172px] md:w-[188px] shrink-0 flex flex-col gap-2 min-h-0 overflow-y-auto">
          <div className="border rounded-lg p-2 bg-gray-50 shrink-0">
            <h3 className="font-semibold text-xs text-gray-800 mb-1.5">Settings</h3>
            <p className="text-xs text-gray-600 mb-1">Étape en cours</p>
            <p className="text-sm font-semibold text-gray-900 mb-2">{CAPTURE_TYPE_LABELS[captureType]}</p>
            <p className="text-[10px] text-blue-800 bg-blue-50 border border-blue-100 rounded px-1.5 py-1 mb-2 line-clamp-3">
              {CAPTURE_HAND_HINT[captureType]}
            </p>
            {phase !== 'left' && (
              <div className="flex flex-wrap gap-x-3 gap-y-1 mb-3">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => {
                    setPhase('left');
                    bumpPreview();
                  }}
                  className="text-xs text-blue-700 underline"
                >
                  Recapturer gauche (4)
                </button>
                {phase === 'thumbs' && (
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => {
                      setPhase('right');
                      bumpPreview();
                    }}
                    className="text-xs text-blue-700 underline"
                  >
                    Recapturer droite (4)
                  </button>
                )}
              </div>
            )}
            <label className="block text-xs text-gray-600 mb-1">NFIQ (max accepté)</label>
            <select
              value={nfiqThreshold}
              onChange={(e) => setNfiqThreshold(Number(e.target.value))}
              disabled={busy}
              className="w-full border rounded px-2 py-1.5 text-sm"
            >
              {NFIQ_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <div className="border rounded-lg p-2 shrink-0">
            <h3 className="font-semibold text-xs text-gray-800 mb-1.5">Fingerprint functions</h3>
            <div className="grid grid-cols-2 gap-1.5">
              <button
                type="button"
                onClick={handleOpenDevice}
                disabled={busy || deviceOpen}
                className="px-2 py-1.5 bg-green-600 text-white rounded text-xs font-medium disabled:opacity-50"
              >
                OpenDevice
              </button>
              <button
                type="button"
                onClick={handleCloseDevice}
                disabled={busy || !deviceOpen}
                className="px-2 py-1.5 bg-gray-600 text-white rounded text-xs font-medium disabled:opacity-50"
              >
                CloseDevice
              </button>
              <button
                type="button"
                onClick={handleCapture}
                disabled={busy || !deviceOpen}
                className="col-span-2 px-2 py-2 bg-blue-600 text-white rounded text-xs font-bold disabled:opacity-50"
              >
                {busy ? 'Capture…' : 'Capture'}
              </button>
            </div>
            {deviceOpen && (
              <p className="text-[10px] text-green-700 mt-1">● Lecteur ouvert</p>
            )}
          </div>
        </div>

        {/* Aperçu plateau — largeur plafonnée pour libérer la colonne doigts */}
        <div className="shrink-0 w-[min(42%,520px)] min-w-[240px] max-w-[520px] min-h-0 flex flex-col">
          <div className="border rounded-lg p-2 flex-1 min-h-0 flex flex-col h-full">
            <h3 className="shrink-0 font-semibold text-xs text-gray-800 mb-1">Aperçu plateau</h3>
            <div className="flex-1 min-h-0 bg-gray-900 rounded flex items-center justify-center overflow-hidden relative">
              {capturing && deviceOpen ? (
                <div className="text-center px-3">
                  <p className="text-amber-300 text-xs font-medium animate-pulse">Capture en cours…</p>
                  <p className="text-gray-400 text-[10px] mt-1">Centre du plateau — évitez le bord</p>
                </div>
              ) : platePreview ? (
                <img src={platePreview} alt="Plateau" className="max-w-full max-h-full object-contain" />
              ) : (
                <p className="text-gray-500 text-xs text-center px-3">
                  Ouvrez le lecteur, posez les doigts au <strong>centre</strong>, puis Capture
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Doigts — occupe toute la marge droite + espace libéré au centre */}
        <div className="flex-1 min-w-[300px] min-h-0 flex flex-col border-l border-gray-200 pl-2 md:pl-4">
          <div className="border rounded-lg p-2 md:p-3 flex-1 min-h-0 overflow-y-auto">
            <h3 className="font-semibold text-sm text-gray-800 mb-2">Doigts — présents</h3>
            <p className="text-xs text-gray-500 mb-1.5">Main gauche</p>
            <div className="grid grid-cols-4 gap-2 mb-2">
              {(['LEFT_LITTLE', 'LEFT_RING', 'LEFT_MIDDLE', 'LEFT_INDEX'] as FingerPosition[]).map(renderFingerCell)}
            </div>
            <div className="grid grid-cols-4 gap-2 mb-3">
              <div className="col-span-2 col-start-2">{renderFingerCell('LEFT_THUMB')}</div>
            </div>
            <p className="text-xs text-gray-500 mb-1.5">Main droite</p>
            <div className="grid grid-cols-4 gap-2 mb-2">
              <div className="col-span-2 col-start-2">{renderFingerCell('RIGHT_THUMB')}</div>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {(['RIGHT_INDEX', 'RIGHT_MIDDLE', 'RIGHT_RING', 'RIGHT_LITTLE'] as FingerPosition[]).map(renderFingerCell)}
            </div>
          </div>
        </div>
      </div>

      {gatewayInitWarning && !sessionId && (
        <div className="shrink-0 mx-2 mb-1 p-2 bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded line-clamp-2">
          {gatewayInitWarning} — lancez <code className="text-[10px]">docker compose up -d enrollment_gateway</code>{' '}
          (port 8001) avant « Suivant », ou continuez sans persistance serveur.
        </div>
      )}

      {error && (
        <div className="shrink-0 mx-2 mb-1 p-2 bg-red-50 border border-red-200 text-red-800 text-xs rounded line-clamp-2">
          {error}
        </div>
      )}

      <div className="shrink-0 mx-2 mb-1 border rounded-lg bg-black text-green-400 font-mono text-[10px] p-2 max-h-16 overflow-y-auto min-h-[2.5rem]">
        {logs.length === 0 ? (
          <span className="text-gray-500">Journal capture…</span>
        ) : (
          logs.map((l, i) => <div key={i}>{l}</div>)
        )}
      </div>

      <div className="shrink-0 px-3 py-2 border-t bg-gray-50 flex justify-between items-center gap-2">
        <button
          type="button"
          onClick={onBack}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 text-sm"
        >
          ← Précédent
        </button>
        <span className="text-xs text-gray-600 text-center hidden sm:block">
          4+4+2 : G {leftCaptured}/4 · D {rightCaptured}/4 · P {thumbsCaptured}/2
          {enrollmentReady ? ` — ${capturedCount}/10 OK` : ' — 3 étapes'}
        </span>
        <div className="flex gap-2 shrink-0">
          {isWorkflowSkipEnabled() && !enrollmentReady && (
            <button
              type="button"
              onClick={() => onComplete([])}
              className="px-3 py-2 rounded-lg text-sm font-medium bg-amber-500 text-white hover:bg-amber-600"
            >
              Passer (test) →
            </button>
          )}
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!enrollmentReady && !isWorkflowSkipEnabled()}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              enrollmentReady
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : isWorkflowSkipEnabled()
                  ? 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Suivant →
          </button>
        </div>
      </div>
    </div>
  );
}
