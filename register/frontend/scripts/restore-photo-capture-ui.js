const fs = require('fs');
const p = 'src/components/biometrics/PhotoCapture.tsx';
let s = fs.readFileSync(p, 'utf8');

s = s.replace(
  "import { getWorkflowStepIndex, WORKFLOW_STEP_ORDER } from '@/lib/enrollment-ui';\nimport PhotoCaptureOnipLayout from '@/components/biometrics/PhotoCaptureOnipLayout';\n",
  ''
);
s = s.replace(
  `  sessionId?: string;
  onEnsureSession?: () => Promise<string>;
  strataLabel?: string;
  enrollmentReference?: string;
}`,
  `  sessionId?: string;
  onEnsureSession?: () => Promise<string>;
}`
);
s = s.replace(
  `  sessionId,
  onEnsureSession,
  strataLabel,
  enrollmentReference,
}: PhotoCaptureProps) {`,
  `  sessionId,
  onEnsureSession,
}: PhotoCaptureProps) {`
);
s = s.replace(
  `  const handleCaptureRef = useRef<() => Promise<void>>(async () => {});
  const autoStartRef = useRef(false);`,
  `  const handleCaptureRef = useRef<() => Promise<void>>(async () => {});`
);
s = s.replace(
  `    resetIcaoCaptureProgress();
    autoStartRef.current = false;
    setMode('idle');
    stopLive();
    void startWebcam();
  };`,
  `    resetIcaoCaptureProgress();
    setMode('idle');
    stopLive();
  };`
);

const start = s.indexOf('  const showLive = mode === \'live\';');
const end = s.indexOf('function appendGpyLogStatic');
if (start < 0 || end < 0) {
  console.error('markers', start, end);
  process.exit(1);
}

const tail = `  const showLive = mode === 'live';
  const showAnalyzing = mode === 'analyzing';
  const showPreview = mode === 'preview' && photoData;
  const useGpyPreview = source === 'gpy' && (showLive || (mode === 'idle' && !showPreview));

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

  const getCheckIcon = (passed: boolean) =>
    passed ? (
      <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
          clipRule="evenodd"
        />
      </svg>
    ) : (
      <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
          clipRule="evenodd"
        />
      </svg>
    );

  return (
    <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-blue-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Photo d&apos;identité</h2>
        <p className="text-gray-600">
          {gpyAvailable === null && 'Détection des modes caméra…'}
          {gpyAvailable === true &&
            'XHY-D500 / COM disponible (Device Bridge 8765). Webcam navigateur toujours utilisable.'}
          {gpyAvailable === false && gpyWsAvailable &&
            'Sans XHY : utilisez Webcam navigateur ou GPYScan (9002) pour l\\'aperçu + capture.'}
          {gpyAvailable === false && !gpyWsAvailable && WEBCAM_DEFAULT_HELP}
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            disabled={(!gpyAvailable && !gpyWsAvailable) || showAnalyzing}
            onClick={() => void switchSource('gpy')}
            className={\`px-3 py-1 rounded-full text-sm font-medium \${
              source === 'gpy' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
            }\`}
          >
            GPY {gpyAvailable ? 'COM ✓' : gpyWsAvailable ? 'WS ✓' : '—'}
          </button>
          <button
            type="button"
            disabled={showAnalyzing}
            onClick={() => void switchSource('webcam')}
            className={\`px-3 py-1 rounded-full text-sm font-medium \${
              source === 'webcam' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
            }\`}
          >
            Webcam navigateur {source === 'webcam' ? '★' : ''}
          </button>
        </div>
      </div>

      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 text-red-800 text-sm rounded whitespace-pre-wrap">
          {error}
        </div>
      )}

      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Photo</h3>

            {source === 'webcam' && webcamDevices.length > 0 && mode === 'idle' && (
              <label className="block text-xs text-gray-600 mb-2">
                Webcam
                <select
                  className="mt-1 w-full border rounded px-2 py-1.5 text-sm"
                  value={selectedDeviceId}
                  onChange={(e) => setSelectedDeviceId(e.target.value)}
                >
                  {webcamDevices.map((d) => (
                    <option key={d.deviceId} value={d.deviceId}>
                      {d.label || d.deviceId.slice(0, 12)}
                    </option>
                  ))}
                </select>
              </label>
            )}

            <div className="relative w-full aspect-[3/4] bg-gray-900 border-2 border-gray-300 rounded-lg overflow-hidden">
              <canvas
                ref={gpyCanvasRef}
                width={640}
                height={853}
                className={\`absolute inset-0 w-full h-full object-contain \${useGpyPreview ? 'block' : 'hidden'}\`}
              />
              <video
                ref={videoRef}
                className={\`absolute inset-0 w-full h-full object-cover \${
                  showLive && source === 'webcam' ? 'block' : 'hidden'
                }\`}
                style={{ transform: 'scaleX(-1)' }}
                playsInline
                muted
                autoPlay
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
                      ? 'Démarrez la caméra GPY (Device Bridge)'
                      : 'Démarrez la webcam ou importez une image'}
                  </p>
                </div>
              )}
              {showAnalyzing && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-gray-900/90 text-white">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-white mb-3" />
                  <p className="text-sm font-medium">Analyse qualité…</p>
                </div>
              )}
              {(showLive || mode === 'idle') && !showPreview && (
                <div
                  className="pointer-events-none absolute inset-6 border-4 border-blue-400/60 rounded-[45%] opacity-80 z-10"
                  aria-hidden
                />
              )}
              {showLive && source === 'webcam' && liveGuidance && (
                <div
                  className={\`absolute bottom-0 left-0 right-0 z-20 px-3 py-2 text-center text-sm font-medium \${
                    liveGuidance.status === 'READY'
                      ? 'bg-green-600/90 text-white'
                      : 'bg-amber-600/90 text-white'
                  }\`}
                >
                  {autoCaptureEnabled &&
                  liveGuidance.status === 'READY' &&
                  stableReadyCount > 0 &&
                  stableReadyCount < icaoConfig.autoCaptureStableFrames
                    ? \`Capture automatique… \${stableReadyCount}/\${icaoConfig.autoCaptureStableFrames}\`
                    : liveGuidance.message}
                  <span className="ml-2 opacity-90">({liveGuidance.qualityScore}%)</span>
                </div>
              )}
              {showPreview && photoData && (
                <div className="absolute top-3 right-3 z-20">
                  <span
                    className={\`px-3 py-1 text-white text-xs font-bold rounded-full \${
                      icaoFinalStatus === 'REJECTED'
                        ? 'bg-red-500'
                        : icaoFinalStatus === 'REVIEW'
                          ? 'bg-amber-500'
                          : photoData.icaoCompliant
                            ? 'bg-green-500'
                            : 'bg-amber-500'
                    }\`}
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

            <div className="mt-4 space-y-2">
              {mode === 'idle' && (
                <>
                  <button
                    type="button"
                    onClick={startLive}
                    className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                  >
                    {source === 'gpy' ? 'Démarrer caméra GPY' : 'Démarrer webcam'}
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full px-4 py-3 border-2 border-dashed border-gray-300 text-gray-700 rounded-lg hover:border-blue-400 font-medium"
                  >
                    Importer une photo
                  </button>
                </>
              )}
              {showLive && source === 'webcam' && icaoAvailable && (
                <label className="flex items-center gap-2 text-sm text-gray-700 px-1">
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
                    style={{ width: \`\${autoCaptureProgress}%\` }}
                  />
                </div>
              )}
              {showLive && (
                <>
                  <button
                    type="button"
                    onClick={() => void handleCapture()}
                    disabled={isCapturing || !webcamCaptureReady}
                    className={\`w-full px-4 py-3 rounded-lg font-bold \${
                      isCapturing || !webcamCaptureReady
                        ? 'bg-gray-400 text-white cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }\`}
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
                    className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Arrêter
                  </button>
                </>
              )}
              {showPreview && photoData && (
                <>
                  {icaoRecommendation && (
                    <p
                      className={\`text-sm p-2 rounded border \${
                        photoData.icaoCompliant
                          ? 'bg-green-50 border-green-200 text-green-900'
                          : 'bg-amber-50 border-amber-200 text-amber-900'
                      }\`}
                    >
                      {icaoRecommendation}
                    </p>
                  )}
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex justify-between text-sm font-medium text-gray-700 mb-1">
                      <span>Qualité</span>
                      <span className="text-green-600">{photoData.quality}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500" style={{ width: \`\${photoData.quality}%\` }} />
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleRetake}
                    className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Reprendre la photo
                  </button>
                </>
              )}
            </div>

            {source === 'gpy' && gpyLogs.length > 0 && (
              <div className="mt-3 p-2 bg-gray-900 text-green-400 font-mono text-xs rounded max-h-24 overflow-y-auto">
                {gpyLogs.map((l, i) => (
                  <div key={i}>{l}</div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Contrôles</h3>
            {!photoData && source === 'webcam' && liveGuidance && (
              <div className="mb-4 p-3 rounded-lg border text-sm space-y-2 bg-gray-50 border-gray-200">
                <p className="font-semibold text-gray-900">Assistant ICAO (temps réel)</p>
                <p className="text-gray-700">{liveGuidance.message}</p>
                <div className="grid grid-cols-2 gap-1 text-xs text-gray-600">
                  <span>Visage : {liveGuidance.checks.faceDetected ? '✓' : '—'}</span>
                  <span>Centré : {liveGuidance.checks.faceCentered ? '✓' : '—'}</span>
                  <span>Yeux : {liveGuidance.checks.eyesOpen ? '✓' : '—'}</span>
                  <span>Bouche : {liveGuidance.checks.mouthClosed ? '✓' : '—'}</span>
                </div>
              </div>
            )}
            {!photoData && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-900 space-y-2">
                <p className="font-semibold">Guichet FGP — caméra intégrée</p>
                {icaoAvailable === true && (
                  <p className="text-green-800 text-xs">
                    Service ICAO actif — acceptation ≥ {icaoConfig.scoreAccepted}%, révision{' '}
                    {icaoConfig.scoreReview}–{icaoConfig.scoreAccepted - 1}%, auto-capture après{' '}
                    {icaoConfig.autoCaptureStableFrames} frames stables.
                  </p>
                )}
                {icaoAvailable === false && (
                  <p className="text-amber-800 text-xs whitespace-pre-wrap">{ICAO_FACE_SERVICE_HELP}</p>
                )}
                <ul className="list-disc list-inside space-y-1 text-blue-800">
                  <li>
                    <strong>Sans XHY-D500</strong> : Webcam + assistant ICAO → Démarrer → Prendre la photo
                  </li>
                  <li>
                    <strong>Avec GPYScan (9002)</strong> : mode GPY → capture depuis l&apos;aperçu live
                  </li>
                  <li>
                    <strong>Production</strong> : brancher XHY-D500 + Device Bridge (.\\start-device-bridge.cmd)
                  </li>
                </ul>
                {(gpyAvailable === false || gpyWsAvailable) && (
                  <p className="text-amber-800 text-xs mt-2 whitespace-pre-wrap">{GPY_BRIDGE_HELP}</p>
                )}
              </div>
            )}
            {photoData && (
              <div className="space-y-2">
                {(Object.keys(photoData.checks) as Array<keyof PhotoData['checks']>).map((check) => (
                  <div
                    key={check}
                    className={\`flex items-center justify-between p-3 rounded-lg border \${
                      photoData.checks[check] ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                    }\`}
                  >
                    <span
                      className={\`text-sm font-medium \${
                        photoData.checks[check] ? 'text-green-900' : 'text-red-900'
                      }\`}
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
      </div>

      {saveError && (
        <div className="mx-6 mb-2 p-3 bg-red-50 border border-red-200 text-red-800 text-sm rounded">
          {saveError}
        </div>
      )}

      <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-between">
        <button
          type="button"
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 font-medium"
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
          className={\`px-6 py-3 rounded-lg font-medium \${
            photoData && !canProceedWithPhoto
              ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
              : photoData
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : allowSkipWithoutPhoto
                  ? 'bg-amber-500 text-white hover:bg-amber-600'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }\`}
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

`;

s = s.slice(0, start) + tail + s.slice(end);
fs.writeFileSync(p, s);
console.log('restored classic photo UI');
