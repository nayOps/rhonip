import React, { useCallback, useEffect, useRef, useState } from 'react';
import { IrisCapture as IrisData, EyePosition, EyeStatus } from '@/types';
import {
  bridgeEyeToPosition,
  captureIris,
  eyeResultToDataUrl,
  fetchIrisLivePreview,
  getIrisStatus,
  isIrisHttpServerDown,
  openIrisDevice,
  previewToDataUrls,
  startIrisServer,
  stopIrisCapture,
} from '@/services/iris-api';
import { saveIrisBiometrics } from '@/services/enrollment-session-api';
import { isWorkflowSkipEnabled } from '@/lib/workflow-test-mode';
import { describeIrisErrcode } from '@/lib/iris-error-codes';
import {
  EYE_STATUS_LABELS,
  EYE_UNAVAILABLE_OPTIONS,
  IRIS_ENROLLMENT_SCENARIOS,
  IRIS_MIN_QUALITY_WARN,
  detectIrisScenario,
  eyePositionLabel,
  isEyeUnavailable,
  isIrisEnrollmentComplete,
  irisProgressLabel,
  normalizeIrisEnrollmentState,
} from '@/lib/iris-enrollment-utils';

interface IrisCaptureProps {
  onComplete: (irisData: IrisData[]) => void;
  onBack: () => void;
  sessionId?: string;
  onEnsureSession?: () => Promise<string>;
  initialIris?: IrisData[];
}

export default function IrisCapture({
  onComplete,
  onBack,
  sessionId,
  onEnsureSession,
  initialIris,
}: IrisCaptureProps) {
  const [irisData, setIrisData] = useState<IrisData[]>(() =>
    normalizeIrisEnrollmentState(initialIris)
  );

  useEffect(() => {
    setIrisData(normalizeIrisEnrollmentState(initialIris));
  }, [initialIris]);
  const [deviceMessage, setDeviceMessage] = useState<string>('Vérification du lecteur iris…');
  const [deviceModel, setDeviceModel] = useState<string | undefined>();
  const [deviceAvailable, setDeviceAvailable] = useState<boolean | null>(null);
  const [deviceConnecting, setDeviceConnecting] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [liveLeft, setLiveLeft] = useState<string | undefined>();
  const [liveRight, setLiveRight] = useState<string | undefined>();
  const [saveError, setSaveError] = useState<string | null>(null);
  const [expandedEye, setExpandedEye] = useState<EyePosition | null>(null);
  const previewTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  const updateIris = useCallback((position: EyePosition, updates: Partial<IrisData>) => {
    setIrisData((prev) =>
      prev.map((iris) => {
        if (iris.position !== position) return iris;
        const next: IrisData = {
          ...iris,
          ...updates,
          timestamp: new Date().toISOString(),
        };
        if (updates.status === 'PENDING') {
          next.image = undefined;
          next.quality = undefined;
          next.reason = undefined;
        } else if (updates.status && isEyeUnavailable(updates.status)) {
          next.image = undefined;
          next.quality = undefined;
        }
        return next;
      })
    );
  }, []);

  const checkIrisReader = useCallback(async () => {
    setDeviceConnecting(true);
    setSaveError(null);
    try {
      const st = await getIrisStatus();
      if (isIrisHttpServerDown(st.message)) {
        setDeviceAvailable(false);
        setDeviceMessage(st.message);
        return;
      }
      setDeviceAvailable(st.available);
      setDeviceMessage(st.message);
      setDeviceModel(st.device_model?.trim() || undefined);
    } catch (e) {
      setDeviceAvailable(false);
      setDeviceMessage(e instanceof Error ? e.message : 'Bridge iris injoignable (8765)');
      setDeviceModel(undefined);
    } finally {
      setDeviceConnecting(false);
    }
  }, []);

  const openIrisReader = useCallback(async () => {
    setDeviceConnecting(true);
    setSaveError(null);
    try {
      const opened = await openIrisDevice();
      setDeviceMessage(opened.message);
      const st = await getIrisStatus();
      setDeviceAvailable(st.available);
      setDeviceModel(st.device_model?.trim() || undefined);
      if (st.available) setDeviceMessage(st.message);
    } catch (e) {
      setDeviceAvailable(false);
      setDeviceMessage(e instanceof Error ? e.message : 'Ouverture lecteur échouée');
    } finally {
      setDeviceConnecting(false);
    }
  }, []);

  const launchIrisServer = useCallback(async () => {
    setDeviceConnecting(true);
    setSaveError(null);
    try {
      const started = await startIrisServer();
      setDeviceMessage(started.message);
      if (started.success) {
        await checkIrisReader();
        return;
      }
      setDeviceAvailable(false);
    } catch (e) {
      setDeviceMessage(e instanceof Error ? e.message : 'Démarrage serveur iris échoué');
    } finally {
      setDeviceConnecting(false);
    }
  }, [checkIrisReader]);

  useEffect(() => {
    void checkIrisReader();
  }, [checkIrisReader]);

  const stopPreviewLoop = useCallback(() => {
    if (previewTimer.current) {
      clearInterval(previewTimer.current);
      previewTimer.current = null;
    }
  }, []);

  const pollPreview = useCallback(async () => {
    try {
      const preview = await fetchIrisLivePreview();
      const urls = previewToDataUrls(preview);
      if (urls.left) setLiveLeft(urls.left);
      if (urls.right) setLiveRight(urls.right);
    } catch {
      /* ignore */
    }
  }, []);

  const startPreviewLoop = useCallback(() => {
    stopPreviewLoop();
    void pollPreview();
    previewTimer.current = setInterval(() => void pollPreview(), 200);
  }, [stopPreviewLoop, pollPreview]);

  useEffect(() => {
    if (deviceAvailable && !isCapturing) {
      startPreviewLoop();
      return () => stopPreviewLoop();
    }
    stopPreviewLoop();
    return undefined;
  }, [deviceAvailable, isCapturing, startPreviewLoop, stopPreviewLoop]);

  useEffect(() => () => {
    stopPreviewLoop();
    stopIrisCapture().catch(() => undefined);
  }, [stopPreviewLoop]);

  const applyCaptureResults = (
    eyes: { eye: string; success: boolean; image?: string; quality?: number; message?: string }[]
  ) => {
    for (const e of eyes) {
      const pos = bridgeEyeToPosition(e.eye);
      if (!pos) continue;
      if (e.success && e.image) {
        updateIris(pos, { status: 'CAPTURED', quality: e.quality ?? 80, image: e.image, reason: undefined });
      } else {
        updateIris(pos, { status: 'FAILED', reason: e.message ?? 'Capture échouée', image: undefined, quality: undefined });
      }
    }
  };

  const runCapture = async (eye: 'left' | 'right' | 'both') => {
    setIsCapturing(true);
    setSaveError(null);
    startPreviewLoop();
    try {
      const result = await captureIris(eye, 30);
      stopPreviewLoop();
      await stopIrisCapture();

      if (!result.eyes?.length) {
        const msg = result.message || 'Capture sans résultat';
        setDeviceMessage(msg);
        setSaveError(msg);
        return;
      }

      const mapped = result.eyes.map((e) => ({
        eye: e.eye,
        success: e.success,
        image: eyeResultToDataUrl(e),
        quality: e.quality,
        message: e.message,
      }));
      applyCaptureResults(mapped);

      if (!result.success) {
        const hint = describeIrisErrcode(
          undefined,
          result.message
        );
        setDeviceMessage(hint);
        setSaveError(hint);
      } else {
        setDeviceMessage('Capture terminée');
        setLiveLeft(undefined);
        setLiveRight(undefined);
      }
    } catch (e) {
      stopPreviewLoop();
      setDeviceMessage(e instanceof Error ? e.message : 'Erreur capture');
    } finally {
      setIsCapturing(false);
    }
  };

  const markUnavailable = (
    position: EyePosition,
    status: EyeStatus,
    reason: string
  ) => {
    if (!isEyeUnavailable(status)) return;
    updateIris(position, { status, reason });
    setExpandedEye(null);
  };

  const markBothUnavailable = (
    status: EyeStatus,
    reason: string
  ) => {
    if (!isEyeUnavailable(status)) return;
    (['LEFT', 'RIGHT'] as EyePosition[]).forEach((pos) => {
      const eye = irisData.find((i) => i.position === pos);
      if (eye && (eye.status === 'PENDING' || eye.status === 'FAILED')) {
        markUnavailable(pos, status, reason);
      }
    });
  };

  const canProceed = isIrisEnrollmentComplete(irisData);
  const activeScenario = detectIrisScenario(irisData);
  const progressText = irisProgressLabel(irisData);

  const handleValidate = async () => {
    if (!canProceed) {
      if (isWorkflowSkipEnabled()) onComplete(irisData);
      return;
    }
    setSaveError(null);
    try {
      let sid = sessionId;
      if (!sid && onEnsureSession) {
        sid = await onEnsureSession();
      }
      if (sid) {
        await saveIrisBiometrics(sid, irisData);
      }
      onComplete(irisData);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Sauvegarde iris échouée');
    }
  };

  const getStatusColor = (status: EyeStatus) => {
    switch (status) {
      case 'PENDING':
        return 'text-gray-500 border-gray-200';
      case 'CAPTURED':
        return 'text-green-700 border-green-300 bg-green-50';
      case 'BLIND':
      case 'MISSING':
      case 'DAMAGED':
        return 'text-amber-800 border-amber-300 bg-amber-50';
      case 'FAILED':
        return 'text-red-700 border-red-300 bg-red-50';
      default:
        return 'text-gray-500 border-gray-200';
    }
  };

  const renderUnavailableActions = (position: EyePosition) => (
    <div className="flex flex-col gap-1 mt-2">
      <span className="text-xs text-gray-500">Non capturable :</span>
      <div className="flex flex-wrap gap-1">
        {EYE_UNAVAILABLE_OPTIONS.map((opt) => (
          <button
            key={opt.status}
            type="button"
            onClick={() => markUnavailable(position, opt.status, opt.reason)}
            disabled={isCapturing}
            className="px-2 py-1 text-xs rounded bg-amber-100 text-amber-900 hover:bg-amber-200 disabled:opacity-50"
          >
            {opt.shortLabel}
          </button>
        ))}
      </div>
    </div>
  );

  const renderEyeActions = (iris: IrisData) => {
    const pos = iris.position;
    const showUnavailable = expandedEye === pos || iris.status === 'PENDING' || iris.status === 'FAILED';

    if (iris.status === 'CAPTURED') {
      return (
        <div className="flex flex-wrap gap-2 mt-3">
          <button
            type="button"
            onClick={() => runCapture(pos === 'LEFT' ? 'left' : 'right')}
            disabled={isCapturing}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Recapturer
          </button>
          <button
            type="button"
            onClick={() => setExpandedEye(expandedEye === pos ? null : pos)}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Signaler non capturable
          </button>
          {expandedEye === pos && renderUnavailableActions(pos)}
        </div>
      );
    }

    if (isEyeUnavailable(iris.status)) {
      return (
        <div className="flex flex-wrap gap-2 mt-3">
          <button
            type="button"
            onClick={() => runCapture(pos === 'LEFT' ? 'left' : 'right')}
            disabled={isCapturing}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Capturer quand même
          </button>
          <button
            type="button"
            onClick={() => updateIris(pos, { status: 'PENDING', reason: undefined })}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded"
          >
            Modifier
          </button>
          {expandedEye === pos && renderUnavailableActions(pos)}
        </div>
      );
    }

    if (iris.status === 'FAILED') {
      return (
        <div className="mt-3 space-y-2">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => runCapture(pos === 'LEFT' ? 'left' : 'right')}
              disabled={isCapturing}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Réessayer
            </button>
            <button
              type="button"
              onClick={() => updateIris(pos, { status: 'PENDING', reason: undefined })}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded"
            >
              Réinitialiser
            </button>
          </div>
          {showUnavailable && renderUnavailableActions(pos)}
        </div>
      );
    }

    return (
      <div className="mt-3 space-y-2">
        <button
          type="button"
          onClick={() => runCapture(pos === 'LEFT' ? 'left' : 'right')}
          disabled={isCapturing || deviceAvailable === false}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Capturer
        </button>
        {showUnavailable && renderUnavailableActions(pos)}
      </div>
    );
  };

  const statusBanner =
    deviceAvailable === null
      ? 'bg-gray-50 border-gray-200 text-gray-700'
      : deviceAvailable
        ? 'bg-green-50 border-green-200 text-green-900'
        : 'bg-amber-50 border-amber-200 text-amber-900';

  const bothPending = irisData.every((i) => i.status === 'PENDING' || i.status === 'FAILED');

  return (
    <div className="flex flex-col flex-1 min-h-0 h-full w-full overflow-hidden bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="shrink-0 px-3 py-2 border-b bg-gradient-to-r from-indigo-50 to-violet-50">
        <h2 className="text-base md:text-lg font-bold text-gray-900">Capture d&apos;iris</h2>
        <p className="text-xs text-gray-600 mt-0.5">
          Lecteur iris {deviceModel ?? 'JD5'} — 30–50 cm, yeux ouverts
        </p>
        <p className="text-xs font-medium text-indigo-700 mt-1">{progressText}</p>
      </div>

      <div className={`shrink-0 mx-2 mt-2 p-2 border rounded-lg text-xs ${statusBanner}`}>
        <div className="flex flex-wrap items-start justify-between gap-2">
          <p className="flex-1 min-w-0">
            <strong>Lecteur :</strong> {deviceConnecting ? 'Connexion…' : deviceMessage}
          </p>
          <div className="flex flex-col gap-1 shrink-0">
            <button
              type="button"
              onClick={() => void launchIrisServer()}
              disabled={deviceConnecting || isCapturing}
              className="px-2 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 text-[10px] font-medium"
            >
              Démarrer serveur iris
            </button>
            <button
              type="button"
              onClick={() => void openIrisReader()}
              disabled={deviceConnecting || isCapturing}
              className="px-2 py-1 rounded border border-indigo-200 bg-white text-indigo-800 hover:bg-indigo-50 disabled:opacity-50 text-[10px] font-medium"
            >
              Ouvrir lecteur
            </button>
          </div>
        </div>
        {deviceAvailable === false && (
          <p className="mt-1 text-[10px] leading-snug">
            1) <strong>Admin</strong> :{' '}
            <code className="text-[9px]">device-bridge\scripts\start-iris-server-admin.bat</code>{' '}
            (acceptez UAC).
            2) Device Bridge sur le port <strong>8765</strong>.
            3) Brancher le <strong>JD5</strong> USB puis <strong>Ouvrir lecteur</strong> (pas DeviceUI en
            parallèle).
            4) Un seul <code className="text-[9px]">IrisDeviceServer.exe</code>.
            Signalement œil possible sans capture.
          </p>
        )}
      </div>

      {saveError && (
        <div className="shrink-0 mx-2 mt-1 p-2 bg-red-50 border border-red-200 text-red-800 text-xs rounded line-clamp-2">
          {saveError}
        </div>
      )}

      <div className="flex flex-1 min-h-0 overflow-hidden px-1 md:px-2 py-2 gap-2 md:gap-3">
        {/* Gauche — contrôles et scénarios */}
        <div className="w-[172px] md:w-[200px] shrink-0 flex flex-col gap-2 min-h-0 overflow-y-auto">
          <div className="border rounded-lg p-2 bg-slate-50 shrink-0">
            <h3 className="font-semibold text-xs text-slate-900 mb-1.5">Cas d&apos;enrôlement</h3>
            <div className="grid grid-cols-1 gap-1 text-[10px]">
              {IRIS_ENROLLMENT_SCENARIOS.map((s) => (
                <div
                  key={s.id}
                  className={`p-1.5 rounded border ${
                    activeScenario === s.id
                      ? 'border-indigo-400 bg-indigo-50 text-indigo-900'
                      : 'border-slate-200 text-slate-700'
                  }`}
                >
                  <span className="font-medium block">{s.title}</span>
                  <span className="text-slate-600 line-clamp-2">{s.hint}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="border rounded-lg p-2 bg-blue-50 shrink-0">
            <h3 className="font-semibold text-xs text-blue-900 mb-1">Instructions</h3>
            <ul className="text-[10px] text-blue-800 space-y-0.5 leading-snug">
              <li>• Standard : 2 yeux</li>
              <li>• Un œil + autre signalé</li>
              <li>• Les 2 signalés si impossible</li>
            </ul>
          </div>

          <button
            type="button"
            onClick={() => runCapture('both')}
            disabled={isCapturing || deviceAvailable === false}
            className="w-full px-2 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-xs font-bold shrink-0"
          >
            {isCapturing ? 'Capture…' : 'Capturer les 2 yeux'}
          </button>

          {bothPending && (
            <div className="p-2 border border-amber-200 bg-amber-50 rounded-lg text-[10px] shrink-0">
              <p className="font-medium text-amber-900 mb-1">2 yeux non capturables ?</p>
              <div className="flex flex-col gap-1">
                {EYE_UNAVAILABLE_OPTIONS.map((opt) => (
                  <button
                    key={opt.status}
                    type="button"
                    onClick={() => markBothUnavailable(opt.status, opt.reason)}
                    disabled={isCapturing}
                    className="px-2 py-1 rounded bg-white border border-amber-300 text-amber-900 hover:bg-amber-100 disabled:opacity-50"
                  >
                    Les 2 — {opt.shortLabel}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Centre — aperçu live (largeur limitée) */}
        <div className="shrink-0 w-[min(36%,440px)] min-w-[200px] max-w-[440px] min-h-0 flex flex-col">
          <div className="border rounded-lg p-2 flex-1 min-h-0 flex flex-col h-full">
            <h3 className="shrink-0 text-xs font-semibold text-gray-800 mb-1">Aperçu live</h3>
            <div className="flex-1 min-h-0 grid grid-rows-2 gap-2">
              <div className="min-h-0 flex flex-col">
                <p className="text-[10px] font-medium text-gray-700 mb-0.5 shrink-0">Œil droit</p>
                <div className="flex-1 min-h-0 bg-black border rounded flex items-center justify-center overflow-hidden">
                  {liveRight || irisData.find((i) => i.position === 'RIGHT')?.image ? (
                    <img
                      src={liveRight || irisData.find((i) => i.position === 'RIGHT')?.image}
                      alt="Œil droit"
                      className="max-w-full max-h-full object-contain"
                    />
                  ) : (
                    <span className="text-gray-500 text-xs">—</span>
                  )}
                </div>
              </div>
              <div className="min-h-0 flex flex-col">
                <p className="text-[10px] font-medium text-gray-700 mb-0.5 shrink-0">Œil gauche</p>
                <div className="flex-1 min-h-0 bg-black border rounded flex items-center justify-center overflow-hidden">
                  {liveLeft || irisData.find((i) => i.position === 'LEFT')?.image ? (
                    <img
                      src={liveLeft || irisData.find((i) => i.position === 'LEFT')?.image}
                      alt="Œil gauche"
                      className="max-w-full max-h-full object-contain"
                    />
                  ) : (
                    <span className="text-gray-500 text-xs">—</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Droite — fiches œil (marge droite + espace libéré) */}
        <div className="flex-1 min-w-[280px] min-h-0 flex flex-col border-l border-gray-200 pl-2 md:pl-4">
          <div className="flex-1 min-h-0 overflow-y-auto">
            <h3 className="font-semibold text-sm text-gray-900 mb-2 sticky top-0 bg-white py-1 z-10">
              Yeux — statut et actions
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {irisData.map((iris) => (
                <div
                  key={iris.position}
                  className={`p-3 border-2 rounded-lg ${getStatusColor(iris.status)}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-sm text-gray-900">{eyePositionLabel(iris.position)}</h3>
                    <span className="text-[10px] font-semibold uppercase tracking-wide">
                      {EYE_STATUS_LABELS[iris.status]}
                    </span>
                  </div>

                  {iris.image && (
                    <img
                      src={iris.image}
                      alt={iris.position}
                      className="w-full h-24 md:h-28 object-contain border rounded bg-black mb-2"
                    />
                  )}

                  <div className="space-y-1 text-xs text-gray-600">
                    {iris.quality != null && (
                      <div>
                        Qualité : {iris.quality}%
                        {iris.status === 'CAPTURED' && iris.quality < IRIS_MIN_QUALITY_WARN && (
                          <span className="text-amber-600 ml-1">(faible)</span>
                        )}
                      </div>
                    )}
                    {iris.reason && <div className="text-amber-800 line-clamp-2">{iris.reason}</div>}
                  </div>

                  {renderEyeActions(iris)}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="shrink-0 px-3 py-2 border-t bg-gray-50 flex justify-between items-center gap-2">
        <button
          type="button"
          onClick={onBack}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 text-sm"
        >
          ← Précédent
        </button>
        <div className="flex gap-2 shrink-0">
          {isWorkflowSkipEnabled() && !canProceed && (
            <button
              type="button"
              onClick={() => onComplete(irisData)}
              disabled={isCapturing}
              className="px-3 py-2 rounded-lg text-sm font-medium bg-amber-500 text-white hover:bg-amber-600 disabled:opacity-50"
            >
              Passer (test) →
            </button>
          )}
          <button
            type="button"
            onClick={handleValidate}
            disabled={(!canProceed && !isWorkflowSkipEnabled()) || isCapturing}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              (canProceed || isWorkflowSkipEnabled()) && !isCapturing
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Valider et continuer →
          </button>
        </div>
      </div>
    </div>
  );
}
