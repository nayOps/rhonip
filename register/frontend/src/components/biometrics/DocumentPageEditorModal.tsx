import React, { useEffect } from 'react';
import { DocumentPage } from '@/types';
import { sideLabel } from '@/lib/document-scan-utils';

export interface DocumentPageEditorModalProps {
  page: DocumentPage;
  draft?: boolean;
  documentLabel?: string;
  zoom: number;
  rotation: number;
  cropScale: number;
  isApplying: boolean;
  onZoomChange: (zoom: number) => void;
  onRotationChange: (rotation: number) => void;
  onCropScaleChange: (scale: number) => void;
  onReset: () => void;
  onApply: () => void;
  onClose: () => void;
}

export default function DocumentPageEditorModal({
  page,
  draft = false,
  documentLabel,
  zoom,
  rotation,
  cropScale,
  isApplying,
  onZoomChange,
  onRotationChange,
  onCropScaleChange,
  onReset,
  onApply,
  onClose,
}: DocumentPageEditorModalProps) {
  const isImage = page.mimeType.startsWith('image/');

  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener('keydown', onKey);
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-3 md:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="doc-editor-title"
      onClick={onClose}
    >
      <div
        className="flex flex-col w-full max-w-5xl max-h-[92vh] bg-white rounded-xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="shrink-0 flex items-start justify-between gap-3 px-4 py-3 border-b bg-gray-50">
          <div className="min-w-0">
            <h3 id="doc-editor-title" className="text-base font-semibold text-gray-900">
              Édition du document scanné
            </h3>
            <p className="text-sm text-gray-600 mt-0.5">
              {documentLabel ? `${documentLabel} — ` : ''}
              {sideLabel(page.side)} · page {page.pageNumber}
              {draft ? ' (brouillon)' : ''}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 w-9 h-9 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100 text-lg leading-none"
            aria-label="Fermer"
          >
            ×
          </button>
        </div>

        {!isImage ? (
          <div className="p-8 text-center text-gray-600">
            <p className="font-medium">Édition disponible uniquement pour les images.</p>
            <p className="text-sm mt-2">Ce fichier n&apos;est pas une image scannée.</p>
            <button
              type="button"
              onClick={onClose}
              className="mt-4 px-4 py-2 border border-gray-300 rounded-lg text-sm"
            >
              Fermer
            </button>
          </div>
        ) : (
          <>
            <div className="flex-1 min-h-[50vh] md:min-h-[55vh] bg-neutral-900 relative overflow-hidden">
              <img
                src={page.image}
                alt={`Document ${sideLabel(page.side)}`}
                className="absolute inset-0 w-full h-full object-contain transition-transform duration-150"
                style={{ transform: `scale(${zoom}) rotate(${rotation}deg)` }}
              />
              <div
                className="absolute border-2 border-emerald-400 shadow-[0_0_0_9999px_rgba(0,0,0,0.35)] pointer-events-none"
                style={{
                  width: `${cropScale * 100}%`,
                  height: `${cropScale * 100}%`,
                  left: `${(100 - cropScale * 100) / 2}%`,
                  top: `${(100 - cropScale * 100) / 2}%`,
                }}
              />
              <p className="absolute bottom-3 left-3 right-3 text-center text-xs text-white/80 bg-black/40 rounded px-2 py-1">
                Cadre vert = zone conservée après rognage
              </p>
            </div>

            <div className="shrink-0 border-t bg-white px-4 py-3 space-y-3">
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => onZoomChange(Math.max(0.5, zoom - 0.1))}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
                >
                  Zoom −
                </button>
                <button
                  type="button"
                  onClick={() => onZoomChange(Math.min(3, zoom + 0.1))}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
                >
                  Zoom +
                </button>
                <button
                  type="button"
                  onClick={() => onRotationChange(rotation - 90)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
                >
                  Rotation −90°
                </button>
                <button
                  type="button"
                  onClick={() => onRotationChange(rotation + 90)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
                >
                  Rotation +90°
                </button>
                <button
                  type="button"
                  onClick={onReset}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
                >
                  Réinitialiser
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Taille du cadre de rognage : {Math.round(cropScale * 100)} %
                </label>
                <input
                  type="range"
                  min={0.5}
                  max={1}
                  step={0.02}
                  value={cropScale}
                  onChange={(e) => onCropScaleChange(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="flex flex-wrap justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="button"
                  disabled={isApplying}
                  onClick={onApply}
                  className="px-5 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50"
                >
                  {isApplying ? 'Enregistrement…' : 'Appliquer et fermer'}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
