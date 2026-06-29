import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  captureCameraPhoto,
  closeCameraDevice,
  fetchCameraPreview,
  getCameraStatus,
  openCameraDevice,
  probeCameraBridge,
  type CameraProbeResult,
  type CameraStatus,
} from '@/services/camera-api';
import {
  analyzeIdentityPhoto,
  cameraErrorMessage,
  captureFrameFromVideo,
  formatWebcamPermissionHelp,
  isPreferredGuichetWebcam,
  listVideoInputDevices,
  openCameraStream,
  openPreferredGuichetWebcam,
  pickPreferredWebcamDevice,
  queryCameraPermission,
  stopMediaStream,
} from '@/lib/photo-capture-utils';
import {
  captureFrameForIcaoStream,
  createIcaoFaceStream,
  fetchIcaoServiceConfig,
  ICAO_DEFAULTS,
  ICAO_FACE_SERVICE_HELP,
  mapIcaoProcessToPhotoData,
  processFaceCapture,
  probeIcaoFaceService,
  type IcaoCropInfo,
  type IcaoFinalStatus,
  type IcaoRealtimeResult,
  type IcaoServiceConfig,
} from '@/services/icao-face-api';
import {
  bridgeComOnlyBuiltinCameras,
  GUICHET_CAMERA_HINT,
  isBuiltinCameraLabel,
  isGuichetCameraLabel,
} from '@/lib/guichet-camera-devices';
import { drawIcaoLiveOverlay } from '@/lib/icao-live-overlay';
import { saveFaceBiometrics } from '@/services/enrollment-session-api';
import { GpyCameraClient, GPY_SERVICE_HELP, probeGpyCameraService } from '@/lib/gpy-camera-client';
import type { IcaoCaptureMeta } from '@/services/enrollment-session-api';

interface PhotoCaptureProps {
  onComplete: (photoData: PhotoData) => void;
  onBack: () => void;
  /** Passer l'étape photo sans capture (tests scan / imprimante). */
  onSkip?: () => void;
  allowSkipWithoutPhoto?: boolean;
  sessionId?: string;
  onEnsureSession?: () => Promise<string>;
  initialPhoto?: PhotoData | null;
  onDataChange?: (photo: PhotoData | null) => void;
}

export interface PhotoData {
  image: string;
  quality: number;
  icaoCompliant: boolean;
  checks: {
    faceDetected: boolean;
    eyesOpen: boolean;
    lookingStraight: boolean;
    neutralExpression: boolean;
    noGlasses: boolean;
    goodLighting: boolean;
    noShadows: boolean;
    sharpness: boolean;
    resolution: boolean;
    background: boolean;
  };
  timestamp: string;
  /** Image brute capturée (audit). */
  rawImage?: string;
  /** Image recadrée ICAO 7:9. */
  icaoImage?: string;
  captureMeta?: IcaoCaptureMeta;
  cropInfo?: IcaoCropInfo;
}

type ViewMode = 'idle' | 'live' | 'analyzing' | 'preview';
type PhotoSource = 'gpy' | 'webcam';

const GPY_BRIDGE_HELP =
  'Mode optionnel — caméra GPY via Device Bridge (8765) ou GPYScan (9002).\n' +
  'Pour le guichet standard, utilisez « Assistant ICAO (webcam) ».';

const WEBCAM_ICAO_HELP =
  'Webcam + assistant ICAO (service local port 50270) : guidage temps réel, recadrage 7:9 et validation photo.';

export default function PhotoCapture({
  onComplete,
  onBack,
  onSkip,
  allowSkipWithoutPhoto = false,
  sessionId,
  onEnsureSession,
  initialPhoto,
}: PhotoCaptureProps) {
  const [photoData, setPhotoData] = useState<PhotoData | null>(() => initialPhoto ?? null);

  useEffect(() => {
    if (initialPhoto) setPhotoData(initialPhoto);
  }, [initialPhoto]);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [mode, setMode] = useState<ViewMode>('idle');
  const [error, setError] = useState<string | null>(null);
  const [gpyAvailable, setGpyAvailable] = useState<boolean | null>(null);
  const [gpyWsAvailable, setGpyWsAvailable] = useState(false);
  const [bridgeCameraStatus, setBridgeCameraStatus] = useState<CameraStatus | null>(null);
  const [bridgeProbe, setBridgeProbe] = useState<CameraProbeResult | null>(null);
  const [bridgeProbeBusy, setBridgeProbeBusy] = useState(false);
  const [source, setSource] = useState<PhotoSource>('webcam');
  const [gpyLogs, setGpyLogs] = useState<string[]>([]);
  const [activityLogs, setActivityLogs] = useState<string[]>([]);
  const lastGuidanceMessageRef = useRef<string | null>(null);
  const [webcamDevices, setWebcamDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');
  const [cameraPermission, setCameraPermission] = useState<PermissionState | 'unknown'>('unknown');
  /** Aperçu ICAO via Device Bridge (contourne getUserMedia navigateur). */
  const [icaoBridgePreview, setIcaoBridgePreview] = useState(false);
  /** true = flux GPYScan WS (9002), false = preview COM bridge */
  const [icaoBridgeUsesWs, setIcaoBridgeUsesWs] = useState(false);
  const [icaoAvailable, setIcaoAvailable] = useState<boolean | null>(null);
  const [icaoConfig, setIcaoConfig] = useState<IcaoServiceConfig>({ ...ICAO_DEFAULTS });
  const [liveGuidance, setLiveGuidance] = useState<IcaoRealtimeResult | null>(null);
  const [icaoRecommendation, setIcaoRecommendation] = useState<string | null>(null);
  const [icaoFinalStatus, setIcaoFinalStatus] = useState<IcaoFinalStatus | null>(null);
  const [icaoAnalysisUsed, setIcaoAnalysisUsed] = useState(false);
  const [autoCaptureEnabled, setAutoCaptureEnabled] = useState(true);
  const [stableReadyCount, setStableReadyCount] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const previewBoxRef = useRef<HTMLDivElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const gpyCanvasRef = useRef<HTMLCanvasElement>(null);
  const previewTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const gpyWsClientRef = useRef<GpyCameraClient | null>(null);
  const icaoStreamRef = useRef<ReturnType<typeof createIcaoFaceStream> | null>(null);
  const icaoFrameTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stableReadyCountRef = useRef(0);
  const autoCaptureDoneRef = useRef(false);
  const handleCaptureRef = useRef<() => Promise<void>>(async () => {});

  const resetIcaoCaptureProgress = useCallback(() => {
    stableReadyCountRef.current = 0;
    autoCaptureDoneRef.current = false;
    setStableReadyCount(0);
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [status, wsUp, inputs, icaoUp, camPerm] = await Promise.all([
        getCameraStatus().catch(() => ({ available: false, message: 'Device Bridge injoignable' })),
        probeGpyCameraService(),
        listVideoInputDevices().catch(() => [] as MediaDeviceInfo[]),
        probeIcaoFaceService(),
        queryCameraPermission(),
      ]);
      if (cancelled) return;
      setGpyAvailable(status.available);
      setGpyWsAvailable(wsUp);
      setBridgeCameraStatus(status);
      setIcaoAvailable(icaoUp);
      setCameraPermission(camPerm);
      if (icaoUp) {
        const cfg = await fetchIcaoServiceConfig();
        if (!cancelled && cfg) setIcaoConfig(cfg);
      }
      setWebcamDevices(inputs);
      const preferred = pickPreferredWebcamDevice(inputs);
      if (preferred?.deviceId && (preferred.label || '').length > 0) {
        setSelectedDeviceId(preferred.deviceId);
      }

      setSource('webcam');
      if (!icaoUp) {
        setError(`Assistant ICAO requis pour la photo d'identité.\n\n${ICAO_FACE_SERVICE_HELP}`);
      } else {
        setError(null);
      }
      if (!status.available && wsUp) {
        appendGpyLogStatic(
          setGpyLogs,
          'GPYScan (9002) détecté — aperçu possible ; COM/XHY non requis pour tester.'
        );
      }
    })();
    return () => {
      cancelled = true;
      if (previewTimerRef.current) clearInterval(previewTimerRef.current);
    };
  }, []);

  useEffect(() => {
    return () => {
      if (previewTimerRef.current) clearInterval(previewTimerRef.current);
      if (icaoFrameTimerRef.current) clearInterval(icaoFrameTimerRef.current);
      icaoStreamRef.current?.close();
      icaoStreamRef.current = null;
      stopMediaStream(streamRef.current);
      gpyWsClientRef.current?.disconnect();
      gpyWsClientRef.current = null;
    };
  }, []);

  const stopIcaoStream = useCallback(() => {
    if (icaoFrameTimerRef.current) {
      clearInterval(icaoFrameTimerRef.current);
      icaoFrameTimerRef.current = null;
    }
    icaoStreamRef.current?.close();
    icaoStreamRef.current = null;
    setLiveGuidance(null);
    resetIcaoCaptureProgress();
  }, [resetIcaoCaptureProgress]);

  const appendGpyLog = useCallback((line: string) => {
    setGpyLogs((prev) => [...prev.slice(-20), `${new Date().toLocaleTimeString()} — ${line}`]);
  }, []);

  const appendActivityLog = useCallback((line: string) => {
    setActivityLogs((prev) => [...prev.slice(-30), `${new Date().toLocaleTimeString()} — ${line}`]);
  }, []);

  useEffect(() => {
    if (!liveGuidance?.message || mode !== 'live') return;
    if (liveGuidance.message === lastGuidanceMessageRef.current) return;
    lastGuidanceMessageRef.current = liveGuidance.message;
    appendActivityLog(liveGuidance.message);
  }, [appendActivityLog, liveGuidance?.message, mode]);

  const attachStreamToVideo = useCallback((stream: MediaStream) => {
    const video = videoRef.current;
    if (!video) return;
    video.srcObject = stream;
    video.play().catch(() => {});
  }, []);

  const stopWebcam = useCallback(() => {
    stopIcaoStream();
    if (previewTimerRef.current) {
      clearInterval(previewTimerRef.current);
      previewTimerRef.current = null;
    }
    if (icaoBridgePreview) {
      if (gpyWsClientRef.current) {
        gpyWsClientRef.current.disconnect();
        gpyWsClientRef.current = null;
      } else {
        void closeCameraDevice().catch(() => {});
      }
      setIcaoBridgePreview(false);
      setIcaoBridgeUsesWs(false);
    }
    stopMediaStream(streamRef.current);
    streamRef.current = null;
    const video = videoRef.current;
    if (video) video.srcObject = null;
  }, [icaoBridgePreview, stopIcaoStream]);

  const stopGpyPreview = useCallback(() => {
    if (previewTimerRef.current) {
      clearInterval(previewTimerRef.current);
      previewTimerRef.current = null;
    }
    gpyWsClientRef.current?.disconnect();
    gpyWsClientRef.current = null;
    void closeCameraDevice().catch(() => {});
  }, []);

  /** Arrête webcam / GPY sans changer l'écran (utilisé après capture → preview). */
  const stopCaptureDevices = useCallback(() => {
    if (source === 'gpy') stopGpyPreview();
    else stopWebcam();
  }, [source, stopGpyPreview, stopWebcam]);

  const stopLive = useCallback(() => {
    stopCaptureDevices();
    setMode('idle');
  }, [stopCaptureDevices]);

  const drawPreviewOnCanvas = (dataUrl: string) => {
    const canvas = gpyCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = dataUrl;
  };

  const runAnalysis = useCallback(
    async (dataUrl: string) => {
      setMode('analyzing');
      setError(null);
      setIcaoRecommendation(null);
      setIcaoFinalStatus(null);
      setIcaoAnalysisUsed(false);
      try {
        if (source === 'webcam') {
          if (!icaoAvailable) {
            throw new Error(`Assistant ICAO requis.\n\n${ICAO_FACE_SERVICE_HELP}`);
          }
          const cameraLabel =
            webcamDevices.find((d) => d.deviceId === selectedDeviceId)?.label || 'Webcam';
          const processed = await processFaceCapture(dataUrl, {
            camera: cameraLabel,
            deviceId: 'KIT-ONIP-WEBCAM',
            enrollmentId: sessionId,
          });
          const mapped = mapIcaoProcessToPhotoData(processed);
          setIcaoRecommendation(processed.recommendation || processed.quality.recommendation);
          setIcaoFinalStatus(processed.quality.status);
          setIcaoAnalysisUsed(true);
          setPhotoData({
            image: mapped.image,
            rawImage: mapped.rawImage,
            icaoImage: mapped.icaoImage,
            quality: mapped.quality,
            icaoCompliant: mapped.icaoCompliant,
            checks: mapped.checks,
            timestamp: mapped.timestamp,
            captureMeta: mapped.captureMeta,
            cropInfo: mapped.cropInfo,
          });
          const final = processed.quality;
          if (final.status !== 'ACCEPTED' && final.errors.length > 0) {
            setError(final.errors.slice(0, 3).join(' · '));
          } else if (final.status === 'REVIEW') {
            setError(
              `Score ${final.qualityScore}% — révision requise (seuil acceptation : ${icaoConfig.scoreAccepted}%). Reprenez la photo ou ajustez l'éclairage.`
            );
          } else if (!processed.capture.icaoImageSaved) {
            setError(processed.crop.error || 'Recadrage ICAO non généré — photo brute conservée.');
          }
        } else {
          const { quality, checks, icaoCompliant } = await analyzeIdentityPhoto(dataUrl);
          setPhotoData({
            image: dataUrl,
            quality: Math.max(quality, 80),
            icaoCompliant: true,
            checks: {
              ...checks,
              faceDetected: true,
            },
            timestamp: new Date().toISOString(),
          });
        }
        stopCaptureDevices();
        setMode('preview');
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Analyse échouée');
        setMode('idle');
      }
    },
    [
      icaoAvailable,
      icaoConfig.scoreAccepted,
      selectedDeviceId,
      sessionId,
      source,
      stopCaptureDevices,
      webcamDevices,
    ]
  );

  const paintLiveOverlay = useCallback(() => {
    const box = previewBoxRef.current;
    const canvas = overlayCanvasRef.current;
    if (!box || !canvas) return;
    const w = box.clientWidth;
    const h = box.clientHeight;
    if (w < 2 || h < 2) return;
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    drawIcaoLiveOverlay(ctx, liveGuidance?.overlay, w, h);
  }, [liveGuidance?.overlay]);

  useEffect(() => {
    paintLiveOverlay();
  }, [paintLiveOverlay, mode]);

  useEffect(() => {
    const box = previewBoxRef.current;
    if (!box) return;
    const ro = new ResizeObserver(() => paintLiveOverlay());
    ro.observe(box);
    return () => ro.disconnect();
  }, [paintLiveOverlay]);

  const startGpyWebSocket = useCallback(async () => {
    const canvas = gpyCanvasRef.current;
    if (!canvas) throw new Error('Canvas GPY non prêt');

    const client = new GpyCameraClient();
    client.onLog = (line) => appendGpyLog(line);
    client.onError = (line) => appendGpyLog(`ERR ${line}`);
    client.onDevices = (devices) => {
      const certified = devices.some((d) => {
        const n = d.name.toLowerCase();
        return /xhy|d500|cameragp/.test(n) && !/logitech|hp |^hp|webcam/i.test(n);
      });
      if (!certified) {
        appendGpyLog(
          'Pas de XHY-D500 — capture depuis l\'aperçu live (Logitech/HP OK). Webcam navigateur aussi possible.'
        );
      }
    };
    await client.connect(canvas);
    gpyWsClientRef.current = client;
    appendGpyLog('Connecté via WebSocket 9002 (GPYScan / CameraGPSDK)');
    setMode('live');
  }, [appendGpyLog]);

  const startGpy = useCallback(async () => {
    setError(null);
    setPhotoData(null);
    stopGpyPreview();
    stopWebcam();

    const wsUp = await probeGpyCameraService();
    if (wsUp) {
      try {
        appendGpyLog('Mode WebSocket 9002 (GPYScan / CameraGPSDK)');
        await startGpyWebSocket();
        setGpyAvailable(true);
        return;
      } catch (e) {
        setError(`${e instanceof Error ? e.message : 'GPY WS'}\n\n${GPY_SERVICE_HELP}`);
        setMode('idle');
        return;
      }
    }

    const status = await getCameraStatus();
    setGpyAvailable(status.available);
    setBridgeCameraStatus(status);
    if (!status.available) {
      setError(`${status.message}\n\n${GPY_BRIDGE_HELP}`);
      return;
    }

    try {
      const opened = await openCameraDevice();
      if (!opened.success) {
        throw new Error(opened.message || 'Ouverture caméra GPY échouée');
      }
      appendGpyLog(opened.message);
      setMode('live');

      previewTimerRef.current = setInterval(async () => {
        const frame = await fetchCameraPreview();
        if (frame) drawPreviewOnCanvas(frame);
      }, 200);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Ouverture caméra GPY échouée';
      const isHardware =
        /non certifié|GPY\/XHY|code -1|HP 5MP|Aucune caméra GPY/i.test(msg);
      if (isHardware) {
        const wsUp = await probeGpyCameraService();
        if (wsUp) {
          try {
            appendGpyLog('COM refusé — bascule WebSocket 9002…');
            await startGpyWebSocket();
            return;
          } catch (wsErr) {
            setError(
              `${msg}\n\n${wsErr instanceof Error ? wsErr.message : ''}\n\n${GPY_BRIDGE_HELP}`
            );
            setMode('idle');
            return;
          }
        }
      }
      setError(`${msg}\n\n${GPY_BRIDGE_HELP}`);
      setGpyAvailable(false);
      setMode('idle');
    }
  }, [appendGpyLog, startGpyWebSocket, stopGpyPreview, stopWebcam]);

  const startIcaoLiveStream = useCallback(async (): Promise<boolean> => {
    const cfg = await fetchIcaoServiceConfig();
    const up = cfg !== null;
    setIcaoAvailable(up);
    if (cfg) setIcaoConfig(cfg);
    if (!up) return false;

    resetIcaoCaptureProgress();
    stopIcaoStream();
    const stream = createIcaoFaceStream(
      (result) => setLiveGuidance(result),
      () => {}
    );
    icaoStreamRef.current = stream;
    try {
      await stream.connect();
      icaoFrameTimerRef.current = setInterval(() => {
        const video = videoRef.current;
        if (!video) return;
        const frame = captureFrameForIcaoStream(video);
        if (frame) stream.sendFrame(frame);
      }, 280);
      return true;
    } catch (e) {
      stopIcaoStream();
      setIcaoAvailable(false);
      const msg = e instanceof Error ? e.message : 'Assistant ICAO indisponible';
      setError(`${msg}\n\n${ICAO_FACE_SERVICE_HELP}`);
      return false;
    }
  }, [resetIcaoCaptureProgress, stopIcaoStream]);

  const startBridgeIcaoPreview = useCallback(async () => {
    try {
    setError(null);
    setPhotoData(null);
    setLiveGuidance(null);
    resetIcaoCaptureProgress();
    stopGpyPreview();
    stopWebcam();

    const icaoStreamUp = await startIcaoLiveStream();
    if (!icaoStreamUp) {
      setMode('idle');
      return;
    }

    const wsUp = await probeGpyCameraService();
    if (wsUp) {
      const canvas = gpyCanvasRef.current;
      if (!canvas) throw new Error('Canvas aperçu non prêt');

      const client = new GpyCameraClient();
      client.onLog = (line) => appendActivityLog(line);
      client.onDevices = (devices) => {
        if (devices.length === 0) {
          appendActivityLog('GPYScan : aucune caméra détectée — ouvrez CameraGPSDK / GPYScan');
          return;
        }
        const c930 = devices.find((d) => /罗技|c930|logitech/i.test(d.name));
        appendActivityLog(
          c930
            ? `Caméra détectée : ${c930.name}`
            : `Caméra GPY : ${devices.map((d) => d.name).join(', ')}`
        );
      };
      await client.connect(canvas);
      gpyWsClientRef.current = client;

      const liveReady = await client.waitForLivePreview(1, 8000);
      if (!liveReady) {
        appendActivityLog('GPYScan connecté mais sans image — bascule Device Bridge COM…');
        client.disconnect();
        gpyWsClientRef.current = null;
      } else {
        setIcaoBridgePreview(true);
        setIcaoBridgeUsesWs(true);
        setMode('live');

        let emptyPolls = 0;
        icaoFrameTimerRef.current = setInterval(() => {
          const frame = client.getLivePreviewDataUrl({ silent: true });
          if (frame) {
            emptyPolls = 0;
            icaoStreamRef.current?.sendFrame(frame);
            return;
          }
          emptyPolls += 1;
          if (emptyPolls >= 20) {
            appendActivityLog(
              'Aperçu GPY vide — ouvrez GPYScan (icône barre des tâches) ou autorisez la webcam dans Chrome (localhost:3000).'
            );
            emptyPolls = 0;
          }
        }, 280);

        appendActivityLog('ICAO + GPYScan (9002) — aperçu actif');
        return;
      }
    }

    const status = await getCameraStatus();
    setBridgeCameraStatus(status);
    if (bridgeComOnlyBuiltinCameras(status.message)) {
      throw new Error(
        `${status.message}\n\n` +
          `${GUICHET_CAMERA_HINT}\n` +
          'Le Device Bridge COM ne peut pas ouvrir la HP intégrée.\n' +
          '→ Autorisez la webcam Chrome (localhost:3000) pour utiliser la 罗技 C930c.\n' +
          '→ Ou lancez GPYScan (port 9002) puis « ICAO via GPYScan ».'
      );
    }
    if (!status.available) {
      throw new Error(
        `${status.message}\n\nLancez GPYScan (9002) ou start-device-bridge.cmd (8765).`
      );
    }

    const opened = await openCameraDevice();
    if (!opened.success) {
      throw new Error(opened.message || 'Ouverture caméra bridge échouée');
    }

    setIcaoBridgePreview(true);
    setIcaoBridgeUsesWs(false);
    setMode('live');
    appendActivityLog(`ICAO + Device Bridge COM — ${opened.message}`);

    let emptyFrames = 0;
    previewTimerRef.current = setInterval(async () => {
      const frame = await fetchCameraPreview();
      if (!frame) {
        emptyFrames += 1;
        if (emptyFrames >= 15) {
          appendActivityLog(
            'Aperçu COM vide/bruité — lancez GPYScan (CameraGPSDK, port 9002) pour la Logitech C930c'
          );
          emptyFrames = 0;
        }
        return;
      }
      emptyFrames = 0;
      drawPreviewOnCanvas(frame);
      icaoStreamRef.current?.sendFrame(frame);
    }, 280);

    appendActivityLog('Assistant ICAO actif (aperçu COM — préférez GPYScan si image bruitée)');
    } catch (e) {
      stopGpyPreview();
      stopWebcam();
      setIcaoBridgePreview(false);
      setIcaoBridgeUsesWs(false);
      setMode('idle');
      setError(e instanceof Error ? e.message : 'Aperçu bridge échoué');
    }
  }, [
    appendActivityLog,
    resetIcaoCaptureProgress,
    startIcaoLiveStream,
    stopGpyPreview,
    stopWebcam,
  ]);

  const startWebcam = useCallback(async () => {
    setError(null);
    setPhotoData(null);
    setLiveGuidance(null);
    setIcaoFinalStatus(null);
    setIcaoAnalysisUsed(false);
    setIcaoRecommendation(null);
    resetIcaoCaptureProgress();
    stopGpyPreview();
    stopWebcam();

    const icaoUp = await probeIcaoFaceService();
    setIcaoAvailable(icaoUp);
    if (icaoUp) {
      const cfg = await fetchIcaoServiceConfig();
      if (cfg) setIcaoConfig(cfg);
    }
    if (!icaoUp) {
      setError(`Assistant ICAO requis pour la photo d'identité.\n\n${ICAO_FACE_SERVICE_HELP}`);
      setMode('idle');
      return;
    }

    try {
      const { stream, devices, selected } = await openPreferredGuichetWebcam();
      setWebcamDevices(devices);
      if (selected?.deviceId) {
        setSelectedDeviceId(selected.deviceId);
        appendActivityLog(`Webcam : ${selected.label || selected.deviceId.slice(0, 12)}`);
      }
      setCameraPermission('granted');
      streamRef.current = stream;
      setMode('live');
      attachStreamToVideo(stream);
      lastGuidanceMessageRef.current = null;
      const icaoStreamUp = await startIcaoLiveStream();
      if (!icaoStreamUp) {
        stopWebcam();
        setMode('idle');
        return;
      }
      appendActivityLog('Assistant ICAO actif — cadrez le visage dans le cadre vert');
    } catch (e) {
      stopWebcam();
      const perm = await queryCameraPermission();
      setCameraPermission(perm);
      const denied = e instanceof DOMException && e.name === 'NotAllowedError';
      if (denied) {
        const status = await getCameraStatus();
        setBridgeCameraStatus(status);
        setError(
          `${cameraErrorMessage(e, perm)}\n\n` +
            'Solution recommandée : autorisez la webcam pour http://localhost:3000 dans Chrome.\n' +
            'Alternative : bouton « Démarrer ICAO via Device Bridge » (GPYScan / Device Bridge requis).'
        );
        setMode('idle');
        return;
      }
      if (
        e instanceof Error &&
        /localhost:3000|contexte sécurisé|secure/i.test(e.message)
      ) {
        setError(
          `${e.message}\n\nOuvrez le guichet via http://localhost:3000 (pas une adresse IP) pour utiliser la webcam.`
        );
        setMode('idle');
        return;
      }
      setError(cameraErrorMessage(e, perm));
      setMode('idle');
    }
  }, [
    appendActivityLog,
    attachStreamToVideo,
    resetIcaoCaptureProgress,
    startBridgeIcaoPreview,
    startIcaoLiveStream,
    stopGpyPreview,
    stopWebcam,
  ]);

  const startLive = () => {
    if (source === 'gpy') void startGpy();
    else void startWebcam();
  };

  const handleCapture = useCallback(async () => {
    if (mode !== 'live' || isCapturing) return;
    setError(null);
    setIsCapturing(true);
    try {
      let dataUrl: string;
      if (source === 'gpy') {
        if (previewTimerRef.current) {
          clearInterval(previewTimerRef.current);
          previewTimerRef.current = null;
        }
        if (gpyWsClientRef.current) {
          appendGpyLog('Capture photo (aperçu live ou GPYScan)…');
          try {
            dataUrl = await gpyWsClientRef.current.captureSnapshotFromPreview();
            appendGpyLog('OK — image depuis aperçu canvas');
          } catch {
            dataUrl = await gpyWsClientRef.current.capturePhoto(false);
          }
        } else {
          appendGpyLog('Capture visage (Device Bridge COM)…');
          dataUrl = await captureCameraPhoto();
        }
      } else if (icaoBridgePreview) {
        if (!icaoAvailable) {
          throw new Error(`Assistant ICAO requis.\n\n${ICAO_FACE_SERVICE_HELP}`);
        }
        if (icaoBridgeUsesWs && gpyWsClientRef.current) {
          dataUrl = await gpyWsClientRef.current.captureSnapshotFromPreview();
        } else {
          try {
            dataUrl = await captureCameraPhoto();
          } catch {
            const canvas = gpyCanvasRef.current;
            if (!canvas) throw new Error('Aperçu bridge non prêt');
            dataUrl = canvas.toDataURL('image/jpeg', 0.92);
          }
        }
      } else {
        if (!icaoAvailable) {
          throw new Error(`Assistant ICAO requis.\n\n${ICAO_FACE_SERVICE_HELP}`);
        }
        const video = videoRef.current;
        if (!video) throw new Error('Vidéo non prête');
        dataUrl = captureFrameFromVideo(video);
      }
      await runAnalysis(dataUrl);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Capture échouée');
      autoCaptureDoneRef.current = false;
    } finally {
      setIsCapturing(false);
    }
  }, [appendGpyLog, icaoAvailable, icaoBridgePreview, icaoBridgeUsesWs, isCapturing, mode, runAnalysis, source]);

  useEffect(() => {
    handleCaptureRef.current = handleCapture;
  }, [handleCapture]);

  useEffect(() => {
    const framesNeeded = icaoConfig.autoCaptureStableFrames;
    if (
      mode !== 'live' ||
      source !== 'webcam' ||
      !icaoAvailable ||
      !autoCaptureEnabled ||
      isCapturing ||
      autoCaptureDoneRef.current
    ) {
      if (liveGuidance?.status !== 'READY') {
        stableReadyCountRef.current = 0;
        setStableReadyCount(0);
      }
      return;
    }

    if (liveGuidance?.status === 'READY') {
      const next = stableReadyCountRef.current + 1;
      stableReadyCountRef.current = next;
      setStableReadyCount(next);
      if (next >= framesNeeded) {
        autoCaptureDoneRef.current = true;
        void handleCaptureRef.current();
      }
    } else {
      stableReadyCountRef.current = 0;
      setStableReadyCount(0);
    }
  }, [
    autoCaptureEnabled,
    icaoAvailable,
    icaoConfig.autoCaptureStableFrames,
    isCapturing,
    liveGuidance,
    mode,
    source,
  ]);

  const handleRetake = () => {
    setPhotoData(null);
    setError(null);
    setIcaoRecommendation(null);
    setIcaoFinalStatus(null);
    setIcaoAnalysisUsed(false);
    resetIcaoCaptureProgress();
    lastGuidanceMessageRef.current = null;
    setActivityLogs([]);
    setMode('idle');
    stopLive();
  };

  const webcamCaptureReady =
    source !== 'webcam' ||
    !icaoAvailable ||
    liveGuidance?.status === 'READY' ||
    (liveGuidance?.qualityScore ?? 0) >= icaoConfig.realtimeReadyScore;

  const canProceedWithPhoto =
    !photoData ||
    !icaoAnalysisUsed ||
    icaoFinalStatus === 'ACCEPTED' ||
    icaoFinalStatus === 'REVIEW';

  const autoCaptureProgress =
    icaoConfig.autoCaptureStableFrames > 0
      ? Math.min(100, Math.round((stableReadyCount / icaoConfig.autoCaptureStableFrames) * 100))
      : 0;

  const handleSkipStep = async () => {
    setSaveError(null);
    stopLive();
    const skippedPhoto: PhotoData = {
      image: '',
      quality: 0,
      icaoCompliant: false,
      checks: {
        faceDetected: false,
        eyesOpen: false,
        lookingStraight: false,
        neutralExpression: false,
        noGlasses: false,
        goodLighting: false,
        noShadows: false,
        sharpness: false,
        resolution: false,
        background: false,
      },
      timestamp: new Date().toISOString(),
    };
    try {
      let sid = sessionId;
      if (!sid && onEnsureSession) {
        sid = await onEnsureSession();
      }
      if (sid) {
        await saveFaceBiometrics(sid, skippedPhoto, 'skipped');
      }
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Enregistrement étape photo ignorée échoué');
      return;
    }
    if (onSkip) onSkip();
    else onComplete(skippedPhoto);
  };

  const handleSubmit = async () => {
    if (!photoData) {
      if (allowSkipWithoutPhoto) handleSkipStep();
      return;
    }
    setSaveError(null);
    try {
      let sid = sessionId;
      if (!sid && onEnsureSession) {
        sid = await onEnsureSession();
      }
      if (sid) {
        await saveFaceBiometrics(sid, photoData);
      }
      onComplete(photoData);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Sauvegarde photo échouée');
    }
  };

  const handleDeviceChange = async (deviceId: string) => {
    setSelectedDeviceId(deviceId);
    if (mode === 'live' && source === 'webcam') {
      stopWebcam();
      try {
        const stream = await openCameraStream(deviceId);
        streamRef.current = stream;
        attachStreamToVideo(stream);
        setCameraPermission('granted');
      } catch (e) {
        const perm = await queryCameraPermission();
        setCameraPermission(perm);
        setError(cameraErrorMessage(e, perm));
        setMode('idle');
      }
    }
  };

  const runBridgeCameraProbe = useCallback(async () => {
    setBridgeProbeBusy(true);
    setBridgeProbe(null);
    try {
      const [status, probe] = await Promise.all([getCameraStatus(), probeCameraBridge()]);
      setBridgeCameraStatus(status);
      setGpyAvailable(status.available);
      setBridgeProbe(probe);
      if (status.available) {
        appendGpyLog(`Bridge OK — ${status.message}`);
      } else {
        appendGpyLog(`Bridge : ${status.message || 'caméra indisponible'}`);
      }
      if (probe?.open) {
        appendGpyLog(
          probe.open.success
            ? `Probe open : ${probe.open.message}`
            : `Probe open échoué : ${probe.open.message}`
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Inspection bridge échouée');
    } finally {
      setBridgeProbeBusy(false);
    }
  }, [appendGpyLog]);

  const switchSource = async (next: PhotoSource) => {
    if (next === source) return;
    stopLive();
    if (next === 'webcam') {
      setSource('webcam');
      const icaoUp = await probeIcaoFaceService();
      setIcaoAvailable(icaoUp);
      if (!icaoUp) {
        setError(`Assistant ICAO requis pour la photo d'identité.\n\n${ICAO_FACE_SERVICE_HELP}`);
      } else {
        setError(null);
      }
      return;
    }
    setError(null);
    const status = await getCameraStatus();
    const wsUp = await probeGpyCameraService();
    setGpyAvailable(status.available);
    setGpyWsAvailable(wsUp);
    setBridgeCameraStatus(status);
    if (!status.available && !wsUp) {
      setError(`${status.message}\n\n${GPY_BRIDGE_HELP}`);
      return;
    }
    setSource('gpy');
  };

  const showLive = mode === 'live';
  const showAnalyzing = mode === 'analyzing';
  const showPreview = mode === 'preview' && photoData;
  const useGpyPreview =
    (source === 'gpy' && (showLive || (mode === 'idle' && !showPreview))) ||
    (source === 'webcam' && icaoBridgePreview && showLive);

  const checkLabels: Record<keyof PhotoData['checks'], string> = {
    faceDetected: 'Visage détecté',
    eyesOpen: 'Contraste visage',
    lookingStraight: 'Visage centré',
    neutralExpression: 'Expression',
    noGlasses: 'Sans lunettes (serveur)',
    goodLighting: 'Éclairage',
    noShadows: 'Luminosité homogène',
    sharpness: 'Netteté',
    resolution: 'Résolution',
    background: 'Fond clair',
  };

  const icaoLevelBadge = (level: 'OK' | 'WARN' | 'FAIL') => {
    if (level === 'OK') return <span className="text-green-700 font-medium">OK</span>;
    if (level === 'WARN') return <span className="text-amber-700 font-medium">Attention</span>;
    return <span className="text-red-700 font-medium">À corriger</span>;
  };

  const journalLines = source === 'gpy' ? gpyLogs : activityLogs;

  const getCheckIcon = (passed: boolean) =>
    passed ? (
      <svg className="w-5 h-5 shrink-0 text-green-500" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
          clipRule="evenodd"
        />
      </svg>
    ) : (
      <svg className="w-5 h-5 shrink-0 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
          clipRule="evenodd"
        />
      </svg>
    );

  return (
    <div className="flex flex-col flex-1 min-h-0 h-full w-full overflow-hidden bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="shrink-0 px-3 py-2 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-blue-50">
        <div className="flex flex-wrap items-center justify-between gap-1.5">
          <h2 className="text-base md:text-lg font-bold text-gray-900">Photo d&apos;identité</h2>
          <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={showAnalyzing}
            onClick={() => void switchSource('webcam')}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              source === 'webcam' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
            }`}
          >
            Assistant ICAO (webcam) {source === 'webcam' ? '★' : ''}
          </button>
          <button
            type="button"
            disabled={(!gpyAvailable && !gpyWsAvailable) || showAnalyzing}
            onClick={() => void switchSource('gpy')}
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              source === 'gpy' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
            }`}
          >
            GPY (optionnel) {gpyAvailable ? 'COM ✓' : gpyWsAvailable ? 'WS ✓' : '—'}
          </button>
          </div>
        </div>
        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
          {icaoAvailable === null && 'Détection assistant ICAO…'}
          {icaoAvailable === true &&
            `${WEBCAM_ICAO_HELP} Acceptation ≥ ${icaoConfig.scoreAccepted}%.`}
          {icaoAvailable === false &&
            'Assistant ICAO arrêté — lancez start-icao-face-service.cmd (port 50270).'}
        </p>
      </div>

      {source === 'gpy' && (
        <div className="shrink-0 mx-3 mt-2 p-2 bg-slate-50 border border-slate-200 rounded text-xs text-slate-800">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-medium">Device Bridge — caméra</span>
            <button
              type="button"
              disabled={bridgeProbeBusy || showAnalyzing}
              onClick={() => void runBridgeCameraProbe()}
              className="px-2 py-0.5 rounded bg-slate-200 hover:bg-slate-300 text-slate-800 disabled:opacity-50"
            >
              {bridgeProbeBusy ? 'Inspection…' : 'Inspecter'}
            </button>
          </div>
          <p className="mt-1">
            {bridgeCameraStatus
              ? bridgeCameraStatus.available
                ? `✓ ${bridgeCameraStatus.message || 'Caméra disponible'}${
                    bridgeCameraStatus.device_count != null
                      ? ` (${bridgeCameraStatus.device_count} détectée(s))`
                      : ''
                  }`
                : `✗ ${bridgeCameraStatus.message || 'Bridge injoignable'}`
              : 'Statut en cours…'}
          </p>
          {bridgeProbe?.open && (
            <p className="mt-0.5 text-slate-600">
              Test open/close :{' '}
              {bridgeProbe.open.success ? 'OK' : `échec — ${bridgeProbe.open.message}`}
            </p>
          )}
        </div>
      )}

      {error && (
        <div className="shrink-0 mx-3 mt-2 p-2 bg-red-50 border border-red-200 text-red-800 text-xs rounded whitespace-pre-wrap">
          {error}
        </div>
      )}

      {source === 'webcam' && cameraPermission === 'denied' && mode === 'idle' && (
          <div className="shrink-0 mx-3 mt-2 p-2 bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded space-y-2">
            <p className="font-medium">Caméra navigateur bloquée</p>
            <p>{GUICHET_CAMERA_HINT}</p>
            <p className="whitespace-pre-wrap">{formatWebcamPermissionHelp('denied')}</p>
            {gpyWsAvailable && (
              <button
                type="button"
                onClick={() => void startBridgeIcaoPreview()}
                className="px-3 py-1.5 rounded bg-amber-600 text-white hover:bg-amber-700 text-sm font-medium"
              >
                ICAO via GPYScan (罗技 C930c, sans Chrome)
              </button>
            )}
            {bridgeCameraStatus?.available &&
              !bridgeComOnlyBuiltinCameras(bridgeCameraStatus.message) && (
                <p className="text-amber-800">
                  Device Bridge COM : réservé à la caméra XHY-D500 certifiée.
                </p>
              )}
            {bridgeCameraStatus?.message &&
              bridgeComOnlyBuiltinCameras(bridgeCameraStatus.message) && (
                <p className="text-amber-800">
                  La HP intégrée du PC n&apos;est pas utilisable ici — branchez la 罗技 C930c en USB
                  et autorisez Chrome.
                </p>
              )}
          </div>
        )}

      <div className="flex flex-row flex-1 min-h-0 overflow-hidden p-2 md:p-4 gap-3 md:gap-4">
        <div className="flex flex-col shrink-0 min-h-0 gap-2 w-fit max-w-[48%]">
          {source === 'webcam' && (mode === 'idle' || mode === 'live') && (
            <label className="shrink-0 block text-xs text-gray-600 w-full">
              Webcam
              {webcamDevices.length > 0 ? (
                <select
                  className="mt-0.5 w-full border rounded px-2 py-1 text-sm"
                  value={selectedDeviceId}
                  onChange={(e) => void handleDeviceChange(e.target.value)}
                  disabled={mode === 'live' && cameraPermission !== 'granted'}
                >
                  {webcamDevices
                    .slice()
                    .sort((a, b) => {
                      const aG = isGuichetCameraLabel(a.label || '') ? 1 : 0;
                      const bG = isGuichetCameraLabel(b.label || '') ? 1 : 0;
                      if (aG !== bG) return bG - aG;
                      const aB = isBuiltinCameraLabel(a.label || '') ? 1 : 0;
                      const bB = isBuiltinCameraLabel(b.label || '') ? 1 : 0;
                      return aB - bB;
                    })
                    .map((d) => (
                    <option key={d.deviceId} value={d.deviceId}>
                      {isGuichetCameraLabel(d.label || '') ? '★ 罗技 ' : ''}
                      {isBuiltinCameraLabel(d.label || '') ? '(PC) ' : ''}
                      {d.label || `Caméra ${d.deviceId.slice(0, 8)}…`}
                    </option>
                  ))}
                </select>
              ) : (
                <p className="mt-1 text-amber-700 text-xs whitespace-pre-wrap">
                  {formatWebcamPermissionHelp(cameraPermission)}
                </p>
              )}
            </label>
          )}

          <div className="flex-1 min-h-0 flex items-start justify-start">
            <div
              ref={previewBoxRef}
              className="relative h-full max-h-full aspect-square w-auto max-w-full min-w-0 bg-gray-900 border-2 border-gray-300 rounded-lg overflow-hidden shadow-md"
            >
              <canvas
                ref={gpyCanvasRef}
                width={640}
                height={853}
                className={`absolute inset-0 w-full h-full object-contain ${useGpyPreview ? 'block' : 'hidden'}`}
              />
              <video
                ref={videoRef}
                className={`absolute inset-0 w-full h-full object-cover ${
                  showLive && source === 'webcam' && !icaoBridgePreview ? 'block' : 'hidden'
                }`}
                style={{ transform: 'scaleX(-1)' }}
                playsInline
                muted
                autoPlay
              />
              <canvas
                ref={overlayCanvasRef}
                className={`pointer-events-none absolute inset-0 z-[15] w-full h-full ${
                  showLive && source === 'webcam' && liveGuidance?.overlay ? 'block' : 'hidden'
                }`}
                aria-hidden
              />
              {showPreview && photoData && (
                <img
                  src={photoData.image}
                  alt="Photo capturée"
                  className="absolute inset-0 w-full h-full object-cover z-10"
                  style={{ transform: 'scaleX(-1)' }}
                />
              )}
              {mode === 'idle' && !showPreview && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 p-4 text-center z-0">
                  <p className="text-sm">
                    {source === 'gpy'
                      ? 'Démarrez la caméra GPY'
                      : 'Démarrez l\'assistant ICAO (webcam)'}
                  </p>
                </div>
              )}
              {showAnalyzing && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-gray-900/90 text-white">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2" />
                  <p className="text-xs font-medium">Analyse…</p>
                </div>
              )}
              {(showLive || mode === 'idle') && !showPreview && (
                <div
                  className="pointer-events-none absolute inset-4 border-[3px] border-blue-400/60 rounded-[45%] opacity-80 z-10"
                  aria-hidden
                />
              )}
              {showLive && source === 'webcam' && liveGuidance && (
                <div
                  className={`absolute bottom-0 left-0 right-0 z-20 px-2 py-1.5 text-center text-xs font-medium ${
                    liveGuidance.status === 'READY'
                      ? 'bg-green-600/90 text-white'
                      : 'bg-amber-600/90 text-white'
                  }`}
                >
                  {autoCaptureEnabled &&
                  liveGuidance.status === 'READY' &&
                  stableReadyCount > 0 &&
                  stableReadyCount < icaoConfig.autoCaptureStableFrames
                    ? `Capture automatique… ${stableReadyCount}/${icaoConfig.autoCaptureStableFrames}`
                    : liveGuidance.message}
                  <span className="ml-2 opacity-90">({liveGuidance.qualityScore}%)</span>
                </div>
              )}
              {showPreview && photoData && (
                <div className="absolute top-3 right-3 z-20">
                  <span
                    className={`px-3 py-1 text-white text-xs font-bold rounded-full ${
                      icaoFinalStatus === 'REJECTED'
                        ? 'bg-red-500'
                        : icaoFinalStatus === 'REVIEW'
                          ? 'bg-amber-500'
                          : photoData.icaoCompliant
                            ? 'bg-green-500'
                            : 'bg-amber-500'
                    }`}
                  >
                    {icaoFinalStatus === 'REJECTED'
                      ? 'Refusée'
                      : icaoFinalStatus === 'REVIEW'
                        ? 'Révision'
                        : photoData.icaoCompliant
                          ? 'ICAO OK'
                          : 'À revoir'}
                  </span>
                </div>
              )}
            </div>
          </div>

            <div className="shrink-0 w-full space-y-2">
              {mode === 'idle' && (
                <button
                  type="button"
                  onClick={startLive}
                  disabled={source === 'webcam' && icaoAvailable === false}
                  className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium"
                >
                  {source === 'gpy'
                    ? 'Démarrer caméra GPY'
                    : cameraPermission === 'denied' && bridgeCameraStatus?.available
                      ? 'Démarrer ICAO (Device Bridge)'
                      : 'Démarrer assistant ICAO'}
                </button>
              )}
              {icaoBridgePreview && showLive && (
                <p className="text-xs text-green-800 px-1">
                  ICAO actif —{' '}
                  {icaoBridgeUsesWs
                    ? 'GPYScan (9002) · 罗技 C930c'
                    : 'Device Bridge COM (si image bruitée → lancer GPYScan)'}
                </p>
              )}
              {showLive && source === 'webcam' && icaoAvailable && (
                <label className="flex items-center gap-2 text-xs text-gray-700 px-1">
                  <input
                    type="checkbox"
                    checked={autoCaptureEnabled}
                    onChange={(e) => {
                      setAutoCaptureEnabled(e.target.checked);
                      resetIcaoCaptureProgress();
                    }}
                    className="rounded border-gray-300"
                  />
                  Capture automatique quand la pose est conforme
                </label>
              )}
              {showLive && source === 'webcam' && icaoAvailable && autoCaptureEnabled && (
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 transition-all duration-200"
                    style={{ width: `${autoCaptureProgress}%` }}
                  />
                </div>
              )}
              {showLive && (
                <>
                  <button
                    type="button"
                    onClick={() => void handleCapture()}
                    disabled={isCapturing || !webcamCaptureReady}
                    className={`w-full px-3 py-2 rounded-lg text-sm font-bold ${
                      isCapturing || !webcamCaptureReady
                        ? 'bg-gray-400 text-white cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {isCapturing
                      ? 'Capture en cours…'
                      : source === 'gpy'
                        ? 'Capturer (GPY)'
                        : !webcamCaptureReady
                          ? 'Ajustez la pose (assistant ICAO)'
                          : 'Prendre la photo'}
                  </button>
                  <button
                    type="button"
                    onClick={stopLive}
                    className="w-full px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm"
                  >
                    Arrêter
                  </button>
                </>
              )}
              {showPreview && photoData && (
                <>
                  {icaoRecommendation && (
                    <p
                      className={`text-xs p-2 rounded border ${
                        photoData.icaoCompliant
                          ? 'bg-green-50 border-green-200 text-green-900'
                          : 'bg-amber-50 border-amber-200 text-amber-900'
                      }`}
                    >
                      {icaoRecommendation}
                    </p>
                  )}
                  <div className="p-2 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex justify-between text-xs font-medium text-gray-700 mb-1">
                      <span>Qualité</span>
                      <span className="text-green-600">{photoData.quality}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: `${photoData.quality}%` }} />
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleRetake}
                    className="w-full px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm"
                  >
                    Reprendre la photo
                  </button>
                </>
              )}
            </div>

            {(showLive || mode === 'idle' || journalLines.length > 0) && (
              <div className="shrink-0 w-full flex flex-col min-h-0">
                <p className="text-xs font-semibold text-gray-700 mb-1">Journal</p>
                <div className="p-2 bg-gray-900 text-green-400 font-mono text-[10px] rounded max-h-24 overflow-y-auto min-h-[3rem]">
                  {journalLines.length === 0 ? (
                    <span className="text-gray-500">En attente d&apos;événements…</span>
                  ) : (
                    journalLines.map((l, i) => <div key={i}>{l}</div>)
                  )}
                </div>
              </div>
            )}
        </div>

        <div className="flex-1 min-w-0 min-h-0 flex flex-col overflow-y-auto border-l border-gray-200 pl-3 md:pl-4">
          <h3 className="shrink-0 text-base font-semibold text-gray-900 mb-3">Contrôles</h3>

          {!photoData && source === 'webcam' && liveGuidance && (
            <div className="shrink-0 mb-3 p-3 rounded-lg border text-sm space-y-2 bg-gray-50 border-gray-200">
              <p className="font-semibold text-gray-900">Assistant ICAO (temps réel)</p>
              <p
                className={`text-base font-medium ${
                  liveGuidance.status === 'READY' ? 'text-green-800' : 'text-amber-800'
                }`}
              >
                {liveGuidance.message}
              </p>
              <div className="flex justify-between text-xs text-gray-600">
                <span>Score qualité</span>
                <span className="font-semibold">{liveGuidance.qualityScore}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    liveGuidance.status === 'READY' ? 'bg-green-500' : 'bg-amber-500'
                  }`}
                  style={{ width: `${liveGuidance.qualityScore}%` }}
                />
              </div>
              <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-xs text-gray-700">
                <span>Visage : {liveGuidance.checks.faceDetected ? '✓' : '—'}</span>
                <span>Centré : {liveGuidance.checks.faceCentered ? '✓' : '—'}</span>
                <span>Yeux : {liveGuidance.checks.eyesOpen ? '✓' : '—'}</span>
                <span>Bouche : {liveGuidance.checks.mouthClosed ? '✓' : '—'}</span>
                <span>Tête : {icaoLevelBadge(liveGuidance.checks.headPose)}</span>
                <span>Éclairage : {icaoLevelBadge(liveGuidance.checks.lighting)}</span>
                <span>Fond : {icaoLevelBadge(liveGuidance.checks.background)}</span>
                <span>Netteté : {icaoLevelBadge(liveGuidance.checks.sharpness)}</span>
              </div>
            </div>
          )}

          {!photoData && (
            <div className="shrink-0 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-900 space-y-2 mb-3">
              <p className="font-semibold">Assistant ICAO — photo d&apos;identité</p>
              {icaoAvailable === true && (
                <p className="text-green-800 text-xs">
                  Service ICAO actif — cadre vert 7:9 (35×45 mm), tête + haut des épaules, visage
                  70–80 % de la hauteur. Acceptation ≥ {icaoConfig.scoreAccepted}%, auto-capture
                  après {icaoConfig.autoCaptureStableFrames} frames stables.
                </p>
              )}
              {icaoAvailable === false && (
                <p className="text-amber-800 text-xs whitespace-pre-wrap">{ICAO_FACE_SERVICE_HELP}</p>
              )}
              <ul className="list-disc list-inside space-y-1 text-blue-800 text-xs">
                <li>
                  <strong>Étape 1</strong> : lancer{' '}
                  <code className="text-[11px]">start-icao-face-service.cmd</code> (port 50270)
                </li>
                <li>
                  <strong>Étape 2</strong> : lancer GPYScan / CameraGPSDK (port 9002) pour la Logitech
                  C930c si la webcam navigateur est bloquée
                </li>
                <li>
                  <strong>Étape 3</strong> : autoriser la webcam dans Chrome (icône cadenas) ou utiliser
                  « Démarrer ICAO via Device Bridge »
                </li>
                <li>
                  <strong>Étape 4</strong> : aligner tête + épaules dans le cadre vert jusqu&apos;au score
                  ≥ {icaoConfig.scoreAccepted}%
                </li>
              </ul>
              {(gpyAvailable || gpyWsAvailable) && (
                <p className="text-gray-600 text-xs mt-1 whitespace-pre-wrap">{GPY_BRIDGE_HELP}</p>
              )}
            </div>
          )}

          {photoData && (
            <div className="space-y-2 shrink-0">
              {(Object.keys(photoData.checks) as Array<keyof PhotoData['checks']>).map((check) => (
                <div
                  key={check}
                  className={`flex items-center justify-between p-2.5 rounded-lg border ${
                    photoData.checks[check] ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                  }`}
                >
                  <span
                    className={`text-sm font-medium ${
                      photoData.checks[check] ? 'text-green-900' : 'text-red-900'
                    }`}
                  >
                    {checkLabels[check]}
                  </span>
                  {getCheckIcon(photoData.checks[check])}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {saveError && (
        <div className="shrink-0 mx-3 mb-1 p-2 bg-red-50 border border-red-200 text-red-800 text-xs rounded">
          {saveError}
        </div>
      )}

      <div className="shrink-0 px-3 py-2 border-t border-gray-200 bg-gray-50 flex justify-between gap-2">
        <button
          type="button"
          onClick={onBack}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 text-sm font-medium"
        >
          ← Précédent
        </button>
        <button
          type="button"
          onClick={() => void handleSubmit()}
          title={
            photoData && !canProceedWithPhoto
              ? 'Photo non conforme ICAO — reprenez la capture'
              : undefined
          }
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            photoData && !canProceedWithPhoto
              ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
              : photoData
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : allowSkipWithoutPhoto
                  ? 'bg-amber-500 text-white hover:bg-amber-600'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
          disabled={(!photoData && !allowSkipWithoutPhoto) || (!!photoData && !canProceedWithPhoto)}
        >
          {photoData && !canProceedWithPhoto
            ? icaoFinalStatus === 'REVIEW'
              ? 'Suivant bloqué — révision ICAO'
              : 'Suivant bloqué — reprendre la photo'
            : photoData
              ? 'Suivant →'
              : 'Suivant — passer la photo (test) →'}
        </button>
      </div>
    </div>
  );
}

function appendGpyLogStatic(
  setLogs: React.Dispatch<React.SetStateAction<string[]>>,
  line: string
) {
  setLogs((prev) => [...prev.slice(-20), `${new Date().toLocaleTimeString()} — ${line}`]);
}
