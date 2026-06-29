import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  DocumentPageSide,
  DocumentStructure,
  DocumentType,
  ScannedDocument,
} from '@/types';
import { isWorkflowSkipEnabled } from '@/lib/workflow-test-mode';
import {
  canFinalizeDraft,
  createEmptyDraft,
  dataUrlByteLength,
  DOCUMENT_STRUCTURES,
  formatDocumentSummary,
  nextPageSide,
  normalizeScannedDocument,
  shouldAutoFinalize,
  sideLabel,
  structureConfig,
  totalPagesInBundle,
} from '@/lib/document-scan-utils';
import {
  captureDocumentScan,
  closeCameraDevice,
  fetchCameraPreview,
  getCameraStatus,
  openCameraDevice,
} from '@/services/camera-api';
import { GpyCameraClient, GPY_SERVICE_HELP, probeGpyCameraService } from '@/lib/gpy-camera-client';
import DocumentPageEditorModal from '@/components/biometrics/DocumentPageEditorModal';

interface DocumentScanProps {
  onComplete: (documents: ScannedDocument[]) => void;
  onBack: () => void;
  initialDocuments?: ScannedDocument[];
}

const DOCUMENT_TYPES: { value: DocumentType; label: string; required?: boolean }[] = [
  { value: 'FICHE_IDENTIFICATION', label: 'Fiche d\'identification physique', required: true },
  { value: 'ACTE_NAISSANCE', label: 'Acte de naissance' },
  { value: 'JUGEMENT_SUPPLETIF', label: 'Jugement supplétif' },
  { value: 'CARTE_ELECTEUR', label: 'Carte d\'électeur' },
  { value: 'CERTIFICAT_NATIONALITE', label: 'Certificat de nationalité' },
  { value: 'PASSEPORT', label: 'Passeport' },
  { value: 'CARTE_ETUDIANT', label: 'Carte d\'étudiant/élève' },
  { value: 'PERMIS_CONDUIRE', label: 'Permis de conduire' },
  { value: 'AUTRE', label: 'Autre document' },
];

type ScannerBackend = 'none' | 'gpy-ws' | 'bridge';

function loadImage(dataUrl: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('Image document illisible'));
    img.src = dataUrl;
  });
}

export default function DocumentScan({
  onComplete,
  onBack,
  initialDocuments,
}: DocumentScanProps) {
  const [documents, setDocuments] = useState<ScannedDocument[]>(() => initialDocuments ?? []);

  useEffect(() => {
    if (initialDocuments?.length) setDocuments(initialDocuments);
  }, [initialDocuments]);
  const [draft, setDraft] = useState<ScannedDocument | null>(null);
  const [selectedType, setSelectedType] = useState<DocumentType>('FICHE_IDENTIFICATION');
  const [structure, setStructure] = useState<DocumentStructure>('SINGLE');
  const [manualSide, setManualSide] = useState<DocumentPageSide | 'AUTO'>('AUTO');
  const [autoCut, setAutoCut] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [scannerReady, setScannerReady] = useState(false);
  const [backend, setBackend] = useState<ScannerBackend>('none');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [bridgeAvailable, setBridgeAvailable] = useState<boolean | null>(null);
  const [wsAvailable, setWsAvailable] = useState(false);
  const [editorPageId, setEditorPageId] = useState<string | null>(null);
  const [editorZoom, setEditorZoom] = useState(1);
  const [editorRotation, setEditorRotation] = useState(0);
  const [editorCropScale, setEditorCropScale] = useState(0.9);
  const [isApplyingEdit, setIsApplyingEdit] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const previewTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const gpyClientRef = useRef<GpyCameraClient | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const appendLog = useCallback((line: string) => {
    setLogs((prev) => [...prev.slice(-24), `${new Date().toLocaleTimeString()} — ${line}`]);
  }, []);

  const normalizedDocs = documents.map(normalizeScannedDocument);
  const hasRequiredDocuments = normalizedDocs.some((d) => d.type === 'FICHE_IDENTIFICATION' && d.pages.length > 0);
  const canProceed = hasRequiredDocuments || isWorkflowSkipEnabled();
  const pageTotal = totalPagesInBundle(normalizedDocs) + (draft?.pages.length ?? 0);

  const allPages = [
    ...(draft?.pages ?? []).map((p) => ({ page: p, draft: true })),
    ...normalizedDocs.flatMap((doc) => doc.pages.map((p) => ({ page: p, draft: false }))),
  ];
  const editorPageEntry = allPages.find((e) => e.page.id === editorPageId) ?? null;

  const openPageEditor = useCallback((pageId: string) => {
    setEditorPageId(pageId);
    setEditorZoom(1);
    setEditorRotation(0);
    setEditorCropScale(0.9);
  }, []);

  const closePageEditor = useCallback(() => {
    setEditorPageId(null);
  }, []);

  const stopScanner = useCallback(() => {
    if (previewTimerRef.current) {
      clearInterval(previewTimerRef.current);
      previewTimerRef.current = null;
    }
    gpyClientRef.current?.disconnect();
    gpyClientRef.current = null;
    void closeCameraDevice().catch(() => {});
    setScannerReady(false);
    setBackend('none');
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [status, ws] = await Promise.all([
        getCameraStatus().catch(() => ({ available: false, message: '' })),
        probeGpyCameraService(),
      ]);
      if (cancelled) return;
      setBridgeAvailable(status.available);
      setWsAvailable(ws);
    })();
    return () => {
      cancelled = true;
      stopScanner();
    };
  }, [stopScanner]);

  const getDocumentTypeLabel = (type: DocumentType): string =>
    DOCUMENT_TYPES.find((dt) => dt.value === type)?.label || type;

  const ensureDraft = useCallback((): ScannedDocument => {
    if (draft) return draft;
    const d = createEmptyDraft(selectedType, structure, notes || undefined);
    setDraft(d);
    return d;
  }, [draft, selectedType, structure, notes]);

  const finalizeDraft = useCallback(
    (docToFinalize: ScannedDocument) => {
      const doc = normalizeScannedDocument(docToFinalize);
      if (!canFinalizeDraft(doc)) {
        const cfg = structureConfig(doc.structure);
        setError(`Ce document nécessite au moins ${cfg.minPages} page(s) (${cfg.label}).`);
        return;
      }
      setDocuments((prev) => [...prev, doc]);
      setDraft(null);
      setNotes('');
      appendLog(`Document terminé : ${getDocumentTypeLabel(doc.type)} — ${formatDocumentSummary(doc)}`);
    },
    [appendLog]
  );

  const addPage = useCallback(
    (imageData: string, filename: string, mimeType: string) => {
      const current = ensureDraft();
      const side = nextPageSide(current, manualSide === 'AUTO' ? undefined : manualSide);
      const pageNumber = current.pages.length + 1;
      const page = {
        id: `page_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
        side,
        pageNumber,
        image: imageData,
        filename,
        size: dataUrlByteLength(imageData),
        mimeType,
        scannedAt: new Date().toISOString(),
      };
      const updated: ScannedDocument = {
        ...current,
        type: selectedType,
        structure,
        notes: notes || current.notes,
        pages: [...current.pages, page],
      };
      setDraft(updated);
      openPageEditor(page.id);
      appendLog(`Page ${pageNumber} (${sideLabel(side)}) — ${getDocumentTypeLabel(selectedType)}`);

      if (shouldAutoFinalize(updated)) {
        finalizeDraft(updated);
      }
    },
    [ensureDraft, manualSide, selectedType, structure, notes, appendLog, finalizeDraft, openPageEditor]
  );

  const startNewDocument = () => {
    if (draft && draft.pages.length > 0) {
      const ok = window.confirm(
        'Un document est en cours. Abandonner les pages non terminées et en commencer un nouveau ?'
      );
      if (!ok) return;
    }
    setDraft(createEmptyDraft(selectedType, structure, notes || undefined));
    setError(null);
    appendLog(`Nouveau document : ${structureConfig(structure).label}`);
  };

  const cancelDraft = () => {
    setDraft(null);
    closePageEditor();
    appendLog('Brouillon annulé');
  };

  const applyEditToPage = useCallback(
    async (pageId: string) => {
      const entry = allPages.find((p) => p.page.id === pageId);
      if (!entry) return;
      setIsApplyingEdit(true);
      setError(null);
      try {
        const img = await loadImage(entry.page.image);
        const work = document.createElement('canvas');
        work.width = img.naturalWidth || img.width;
        work.height = img.naturalHeight || img.height;
        const wctx = work.getContext('2d');
        if (!wctx) throw new Error('Canvas édition indisponible');

        wctx.fillStyle = '#ffffff';
        wctx.fillRect(0, 0, work.width, work.height);
        wctx.save();
        wctx.translate(work.width / 2, work.height / 2);
        wctx.rotate((editorRotation * Math.PI) / 180);
        wctx.scale(editorZoom, editorZoom);
        wctx.drawImage(img, -img.width / 2, -img.height / 2);
        wctx.restore();

        const cropScale = Math.min(Math.max(editorCropScale, 0.4), 1);
        const cw = Math.max(32, Math.floor(work.width * cropScale));
        const ch = Math.max(32, Math.floor(work.height * cropScale));
        const sx = Math.max(0, Math.floor((work.width - cw) / 2));
        const sy = Math.max(0, Math.floor((work.height - ch) / 2));

        const out = document.createElement('canvas');
        out.width = cw;
        out.height = ch;
        const octx = out.getContext('2d');
        if (!octx) throw new Error('Canvas sortie indisponible');
        octx.fillStyle = '#ffffff';
        octx.fillRect(0, 0, out.width, out.height);
        octx.drawImage(work, sx, sy, cw, ch, 0, 0, cw, ch);

        const editedData = out.toDataURL('image/jpeg', 0.92);
        const editedSize = dataUrlByteLength(editedData);
        const editedAt = new Date().toISOString();

        setDraft((prev) =>
          prev
            ? {
                ...prev,
                pages: prev.pages.map((p) =>
                  p.id === pageId
                    ? {
                        ...p,
                        image: editedData,
                        size: editedSize,
                        scannedAt: editedAt,
                        filename: p.filename.replace(/(\.[a-z0-9]+)?$/i, '_edited.jpg'),
                        mimeType: 'image/jpeg',
                      }
                    : p
                ),
              }
            : prev
        );
        setDocuments((prev) =>
          prev.map((doc) => ({
            ...doc,
            pages: doc.pages.map((p) =>
              p.id === pageId
                ? {
                    ...p,
                    image: editedData,
                    size: editedSize,
                    scannedAt: editedAt,
                    filename: p.filename.replace(/(\.[a-z0-9]+)?$/i, '_edited.jpg'),
                    mimeType: 'image/jpeg',
                  }
                : p
            ),
          }))
        );
        appendLog(`Page modifiée: rognage/rotation appliqués (${cw}x${ch})`);
        closePageEditor();
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Édition du document échouée');
      } finally {
        setIsApplyingEdit(false);
      }
    },
    [allPages, appendLog, closePageEditor, editorCropScale, editorRotation, editorZoom]
  );

  const drawPreview = (dataUrl: string) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const img = new Image();
    img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    img.src = dataUrl;
  };

  const startScanner = async () => {
    setError(null);
    stopScanner();
    const canvas = canvasRef.current;
    if (!canvas) {
      setError('Canvas scanner non prêt');
      return;
    }
    canvas.width = 800;
    canvas.height = 600;
    if (!draft) {
      setDraft(createEmptyDraft(selectedType, structure, notes || undefined));
    }

    const wsUp = await probeGpyCameraService();
    if (wsUp) {
      try {
        const client = new GpyCameraClient();
        client.onLog = appendLog;
        client.onError = (m) => appendLog(`ERR ${m}`);
        await client.connect(canvas, { documentMode: true });
        gpyClientRef.current = client;
        setBackend('gpy-ws');
        setScannerReady(true);
        appendLog('Scanner GPY — WebSocket 9002 (mode document)');
        return;
      } catch (e) {
        appendLog(`WS : ${e instanceof Error ? e.message : 'échec'}`);
      }
    }

    const status = await getCameraStatus();
    setBridgeAvailable(status.available);
    if (status.available) {
      try {
        const opened = await openCameraDevice();
        if (!opened.success) throw new Error(opened.message);
        appendLog(opened.message);
        setBackend('bridge');
        setScannerReady(true);
        previewTimerRef.current = setInterval(async () => {
          const frame = await fetchCameraPreview();
          if (frame) drawPreview(frame);
        }, 200);
        return;
      } catch (e) {
        setError(
          `${e instanceof Error ? e.message : 'Bridge'}\n\nLancez start-device-bridge.cmd ou GPYScan (9002).`
        );
        return;
      }
    }

    setError(
      `Aucun scanner GPY disponible.\n\n${GPY_SERVICE_HELP}\n\nOu importez un fichier image/PDF.`
    );
  };

  const capturePage = async () => {
    if (!scannerReady || isScanning) return;
    setIsScanning(true);
    setError(null);
    try {
      let dataUrl: string;
      if (backend === 'gpy-ws' && gpyClientRef.current) {
        const client = gpyClientRef.current;
        try {
          dataUrl = await client.captureSnapshotFromPreview();
        } catch {
          dataUrl = await client.captureDocument(autoCut);
        }
      } else if (backend === 'bridge') {
        dataUrl = await captureDocumentScan(autoCut);
      } else {
        throw new Error('Démarrez le scanner avant de capturer');
      }
      const side = draft ? nextPageSide(draft, manualSide === 'AUTO' ? undefined : manualSide) : 'PAGE';
      const name = `scan_${selectedType}_${side}_${Date.now()}.jpg`;
      addPage(dataUrl, name, 'image/jpeg');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Scan échoué');
    } finally {
      setIsScanning(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files?.length) return;
    if (!draft) startNewDocument();

    Array.from(files).forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        addPage(result, file.name, file.type || 'application/octet-stream');
        if (index === files.length - 1 && structure === 'SINGLE' && files.length === 1) {
          /* auto-finalize via addPage */
        }
      };
      reader.readAsDataURL(file);
    });
    event.target.value = '';
  };

  const removeDocument = (id: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  };

  const removePageFromDraft = (pageId: string) => {
    if (!draft) return;
    setDraft({ ...draft, pages: draft.pages.filter((p) => p.id !== pageId) });
    if (editorPageId === pageId) closePageEditor();
  };

  const handleSubmit = () => {
    if (draft && draft.pages.length > 0) {
      const ok = window.confirm(
        'Un document n’est pas terminé. Terminer l’enrôlement sans l’ajouter ?'
      );
      if (!ok) return;
    }
    if (canProceed) onComplete(normalizedDocs);
  };

  const nextSideHint =
    draft && structure !== 'SINGLE'
      ? sideLabel(nextPageSide(draft, manualSide === 'AUTO' ? undefined : manualSide))
      : null;

  const showSidePicker =
    structure === 'RECTO_VERSO' ||
    structure === 'MULTI_PAGE_RECTO_VERSO' ||
    structure === 'MULTI_PAGE';

  return (
    <div className="flex flex-col flex-1 min-h-0 h-full w-full overflow-hidden bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="shrink-0 px-3 py-2 border-b bg-gradient-to-r from-green-50 to-teal-50">
        <h2 className="text-base md:text-lg font-bold text-gray-900">Numérisation des documents</h2>
        <p className="text-xs text-gray-600 mt-0.5 line-clamp-1">
          Page unique, recto/verso ou dossier multipages.
        </p>
        <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
          <span>
            <strong>{normalizedDocs.length}</strong> doc. · <strong>{pageTotal}</strong> p.
          </span>
          {draft && (
            <span className="bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-medium">
              Brouillon : {draft.pages.length} p.
              {nextSideHint ? ` — ${nextSideHint}` : ''}
            </span>
          )}
          {hasRequiredDocuments && (
            <span className="text-green-700 font-semibold">Fiche ID OK</span>
          )}
        </div>
      </div>

      {error && (
        <div className="shrink-0 mx-2 mt-1 p-2 bg-red-50 border border-red-200 text-red-800 text-xs rounded whitespace-pre-wrap line-clamp-3">
          {error}
        </div>
      )}

      <div className="flex flex-1 min-h-0 overflow-hidden px-1 md:px-2 py-2 gap-2 md:gap-3">
        {/* Gauche — configuration & actions */}
        <div className="w-[200px] md:w-[220px] shrink-0 flex flex-col gap-2 min-h-0 overflow-y-auto">
          <div className="border rounded-lg p-2 shrink-0">
            <h3 className="text-xs font-semibold text-gray-900 mb-1.5">Configuration</h3>
            <label className="block text-[10px] font-medium text-gray-700 mb-0.5">Type de pièce</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as DocumentType)}
              disabled={Boolean(draft?.pages.length)}
              className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs disabled:bg-gray-100"
            >
              {DOCUMENT_TYPES.map((docType) => (
                <option key={docType.value} value={docType.value}>
                  {docType.label} {docType.required ? '*' : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="border rounded-lg p-2 shrink-0">
            <label className="block text-[10px] font-medium text-gray-700 mb-1">Structure</label>
            <div className="space-y-1">
              {DOCUMENT_STRUCTURES.map((s) => (
                <label
                  key={s.value}
                  className={`flex items-start gap-1.5 p-1.5 border rounded cursor-pointer text-[10px] ${
                    structure === s.value ? 'border-teal-500 bg-teal-50' : 'border-gray-200'
                  } ${draft?.pages.length ? 'opacity-60 pointer-events-none' : ''}`}
                >
                  <input
                    type="radio"
                    name="docStructure"
                    value={s.value}
                    checked={structure === s.value}
                    onChange={() => setStructure(s.value)}
                    className="mt-0.5 shrink-0"
                  />
                  <span>
                    <span className="font-medium text-gray-900 block leading-tight">{s.label}</span>
                    <span className="text-gray-600 line-clamp-2">{s.hint}</span>
                  </span>
                </label>
              ))}
            </div>
          </div>

          {showSidePicker && (
            <div className="shrink-0">
              <label className="block text-[10px] font-medium text-gray-700 mb-0.5">Prochaine capture</label>
              <select
                value={manualSide}
                onChange={(e) => setManualSide(e.target.value as DocumentPageSide | 'AUTO')}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs"
              >
                <option value="AUTO">Automatique</option>
                <option value="RECTO">Recto</option>
                <option value="VERSO">Verso</option>
                <option value="PAGE">Page</option>
              </select>
            </div>
          )}

          <div className="flex flex-col gap-1.5 shrink-0">
            {!scannerReady ? (
              <button
                type="button"
                onClick={() => void startScanner()}
                className="w-full px-2 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-xs font-medium"
              >
                Démarrer scanner
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => void capturePage()}
                  disabled={isScanning}
                  className="w-full px-2 py-2 bg-secondary-600 text-white rounded-lg hover:bg-blue-700 text-xs font-bold disabled:opacity-50"
                >
                  {isScanning ? 'Capture…' : nextSideHint ? `Scanner ${nextSideHint}` : 'Scanner page'}
                </button>
                <button
                  type="button"
                  onClick={stopScanner}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-xs"
                >
                  Arrêter scanner
                </button>
              </>
            )}
          </div>

          <div className="flex flex-col gap-1 shrink-0">
            {!draft ? (
              <button
                type="button"
                onClick={startNewDocument}
                className="w-full px-2 py-1.5 bg-gray-800 text-white rounded-lg text-xs font-medium"
              >
                Nouveau document
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => finalizeDraft(draft)}
                  disabled={!canFinalizeDraft(draft)}
                  className="w-full px-2 py-1.5 bg-green-600 text-white rounded-lg text-xs font-medium disabled:opacity-40"
                >
                  Terminer document
                </button>
                <button
                  type="button"
                  onClick={cancelDraft}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-xs"
                >
                  Annuler brouillon
                </button>
              </>
            )}
          </div>

          <label className="flex items-center gap-1.5 text-[10px] text-gray-700 shrink-0">
            <input type="checkbox" checked={autoCut} onChange={(e) => setAutoCut(e.target.checked)} />
            Découpage auto (GPY)
          </label>

          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            placeholder="Notes…"
            className="w-full px-2 py-1.5 border border-gray-300 rounded text-xs resize-none shrink-0"
          />

          <input ref={fileInputRef} type="file" accept="image/*,.pdf" multiple onChange={handleFileSelect} className="hidden" />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="w-full px-2 py-1.5 border border-dashed border-gray-300 rounded-lg text-xs text-gray-700 hover:border-teal-500 shrink-0"
          >
            Importer fichier
          </button>

          {logs.length > 0 && (
            <div className="p-1.5 bg-gray-900 text-green-400 font-mono text-[10px] rounded max-h-16 overflow-y-auto shrink-0">
              {logs.map((l, i) => (
                <div key={i}>{l}</div>
              ))}
            </div>
          )}
        </div>

        {/* Centre — aperçu scanner */}
        <div className="shrink-0 w-[min(38%,480px)] min-w-[220px] max-w-[480px] min-h-0 flex flex-col">
          <div className="border rounded-lg p-2 flex-1 min-h-0 flex flex-col h-full">
            <h3 className="shrink-0 text-xs font-semibold text-gray-800 mb-1">Aperçu scanner</h3>
            <div className="relative flex-1 min-h-0 bg-gray-900 border-2 border-gray-300 rounded-lg overflow-hidden">
              <canvas ref={canvasRef} width={800} height={600} className="absolute inset-0 w-full h-full object-contain" />
              {!scannerReady && (
                <div className="absolute inset-0 flex items-center justify-center text-gray-400 text-xs p-3 text-center">
                  Démarrez le scanner
                </div>
              )}
              {isScanning && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-gray-900/80 text-white">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2" />
                  <span className="text-xs">Capture…</span>
                </div>
              )}
            </div>
            <p className="shrink-0 text-[10px] text-gray-500 mt-1.5 px-0.5">
              Cliquez sur une vignette à droite pour afficher le document en grand et l&apos;éditer.
            </p>
          </div>
        </div>

        {/* Droite — brouillon + documents terminés */}
        <div className="flex-1 min-w-[280px] min-h-0 flex flex-col border-l border-gray-200 pl-2 md:pl-4">
          <div className="flex-1 min-h-0 overflow-y-auto space-y-3">
            <h3 className="text-sm font-semibold text-gray-900 sticky top-0 bg-white py-1 z-10">
              Documents — brouillon & terminés
            </h3>

            {draft && draft.pages.length > 0 && (
              <div className="p-2 bg-amber-50 border border-amber-200 rounded-lg">
                <h4 className="font-semibold text-xs text-amber-900 mb-1">En cours</h4>
                <p className="text-[10px] text-amber-800 mb-2">
                  {getDocumentTypeLabel(draft.type)} — {structureConfig(draft.structure).label}
                </p>
                <div className="flex flex-wrap gap-2">
                  {draft.pages.map((p) => (
                    <div
                      key={p.id}
                      className={`relative w-16 md:w-20 cursor-pointer hover:ring-2 hover:ring-emerald-300 rounded ${
                        editorPageId === p.id ? 'ring-2 ring-emerald-500 rounded' : ''
                      }`}
                      onClick={() => openPageEditor(p.id)}
                      title="Ouvrir l'éditeur"
                    >
                      <img
                        src={p.image}
                        alt=""
                        className="w-16 md:w-20 h-20 md:h-24 object-cover border rounded"
                      />
                      <span className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-[9px] text-center py-0.5">
                        {sideLabel(p.side)} {p.pageNumber}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          removePageFromDraft(p.id);
                        }}
                        className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full text-[10px] leading-none"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {normalizedDocs.length === 0 ? (
              <p className="text-xs text-gray-500 py-6 text-center border border-dashed rounded-lg">
                Aucun document terminé
              </p>
            ) : (
              <div className="space-y-2">
                {normalizedDocs.map((doc) => (
                  <div key={doc.id} className="p-2 bg-gray-50 border border-gray-200 rounded-lg">
                    <div className="flex justify-between items-start gap-2 mb-1.5">
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-gray-900 truncate">
                          {getDocumentTypeLabel(doc.type)}
                        </p>
                        <p className="text-[10px] text-gray-600">{formatDocumentSummary(doc)}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeDocument(doc.id)}
                        className="text-red-500 text-[10px] shrink-0"
                      >
                        Suppr.
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {doc.pages.map((p) => (
                        <div
                          key={p.id}
                          className={`w-12 h-14 md:w-14 md:h-16 border rounded overflow-hidden bg-white shrink-0 cursor-pointer hover:ring-2 hover:ring-emerald-300 ${
                            editorPageId === p.id ? 'ring-2 ring-emerald-500' : ''
                          }`}
                          onClick={() => openPageEditor(p.id)}
                          title="Ouvrir l'éditeur"
                        >
                          {p.mimeType.startsWith('image/') ? (
                            <img src={p.image} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <span className="text-[9px] p-0.5">PDF</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {editorPageEntry && (
        <DocumentPageEditorModal
          page={editorPageEntry.page}
          draft={editorPageEntry.draft}
          documentLabel={
            editorPageEntry.draft && draft
              ? getDocumentTypeLabel(draft.type)
              : (() => {
                  const doc = normalizedDocs.find((d) => d.pages.some((pg) => pg.id === editorPageId));
                  return doc ? getDocumentTypeLabel(doc.type) : undefined;
                })()
          }
          zoom={editorZoom}
          rotation={editorRotation}
          cropScale={editorCropScale}
          isApplying={isApplyingEdit}
          onZoomChange={setEditorZoom}
          onRotationChange={setEditorRotation}
          onCropScaleChange={setEditorCropScale}
          onReset={() => {
            setEditorZoom(1);
            setEditorRotation(0);
            setEditorCropScale(0.9);
          }}
          onApply={() => void applyEditToPage(editorPageEntry.page.id)}
          onClose={closePageEditor}
        />
      )}

      <div className="shrink-0 px-3 py-2 border-t border-gray-200 bg-gray-50 flex justify-between items-center gap-2">
        <button
          type="button"
          onClick={onBack}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100"
        >
          ← Précédent
        </button>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!canProceed}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            canProceed ? 'bg-secondary-600 text-white hover:bg-blue-700' : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Suivant →
        </button>
      </div>
    </div>
  );
}
