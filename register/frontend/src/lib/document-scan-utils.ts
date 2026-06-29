import type { DocumentPageSide, DocumentStructure, DocumentType, ScannedDocument } from '@/types';

export const DOCUMENT_STRUCTURES: {
  value: DocumentStructure;
  label: string;
  hint: string;
  minPages: number;
  maxPages: number | null;
}[] = [
  {
    value: 'SINGLE',
    label: 'Page unique',
    hint: 'Une seule face ou page = un document complet',
    minPages: 1,
    maxPages: 1,
  },
  {
    value: 'RECTO_VERSO',
    label: 'Recto + verso',
    hint: 'Deux faces (ex. carte, fiche pliée) = un seul document',
    minPages: 2,
    maxPages: 2,
  },
  {
    value: 'MULTI_PAGE',
    label: 'Plusieurs pages',
    hint: 'Pile de pages (acte, dossier) = un document',
    minPages: 1,
    maxPages: null,
  },
  {
    value: 'MULTI_PAGE_RECTO_VERSO',
    label: 'Multipages recto / verso',
    hint: 'Feuillets recto puis verso (ou l’inverse) dans le même document',
    minPages: 2,
    maxPages: null,
  },
];

export function structureConfig(structure: DocumentStructure) {
  return DOCUMENT_STRUCTURES.find((s) => s.value === structure) ?? DOCUMENT_STRUCTURES[0];
}

export function createEmptyDraft(type: DocumentType, structure: DocumentStructure, notes?: string): ScannedDocument {
  return {
    id: `doc_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
    type,
    structure,
    pages: [],
    notes,
    createdAt: new Date().toISOString(),
  };
}

export function nextPageSide(doc: ScannedDocument, manualSide?: DocumentPageSide): DocumentPageSide {
  if (manualSide) return manualSide;
  const n = doc.pages.length;
  switch (doc.structure) {
    case 'SINGLE':
      return 'PAGE';
    case 'RECTO_VERSO':
      return n === 0 ? 'RECTO' : 'VERSO';
    case 'MULTI_PAGE':
      return 'PAGE';
    case 'MULTI_PAGE_RECTO_VERSO': {
      if (n === 0) return 'RECTO';
      const last = doc.pages[n - 1]?.side;
      return last === 'RECTO' ? 'VERSO' : 'RECTO';
    }
    default:
      return 'PAGE';
  }
}

export function sideLabel(side: DocumentPageSide): string {
  switch (side) {
    case 'RECTO':
      return 'Recto';
    case 'VERSO':
      return 'Verso';
    default:
      return 'Page';
  }
}

export function canFinalizeDraft(doc: ScannedDocument): boolean {
  const cfg = structureConfig(doc.structure);
  return doc.pages.length >= cfg.minPages;
}

export function shouldAutoFinalize(doc: ScannedDocument): boolean {
  const cfg = structureConfig(doc.structure);
  return cfg.maxPages !== null && doc.pages.length >= cfg.maxPages;
}

export function documentPageCount(doc: ScannedDocument): number {
  return doc.pages.length;
}

export function totalPagesInBundle(docs: ScannedDocument[]): number {
  return docs.reduce((sum, d) => sum + d.pages.length, 0);
}

export function getDocumentThumbnail(doc: ScannedDocument): string | undefined {
  return doc.pages[0]?.image;
}

/** Compatibilité si d’anciennes données n’avaient qu’une image à la racine. */
export function normalizeScannedDocument(raw: ScannedDocument): ScannedDocument {
  if (raw.pages?.length) return raw;
  const legacy = raw as ScannedDocument & { image?: string; filename?: string; mimeType?: string; size?: number };
  if (!legacy.image) return { ...raw, pages: [] };
  return {
    ...raw,
    structure: raw.structure ?? 'SINGLE',
    pages: [
      {
        id: `page_${raw.id}_1`,
        side: 'PAGE',
        pageNumber: 1,
        image: legacy.image,
        filename: legacy.filename ?? 'scan.jpg',
        size: legacy.size ?? 0,
        mimeType: legacy.mimeType ?? 'image/jpeg',
        scannedAt: raw.createdAt ?? new Date().toISOString(),
      },
    ],
    createdAt: raw.createdAt ?? new Date().toISOString(),
  };
}

export function formatDocumentSummary(doc: ScannedDocument): string {
  const cfg = structureConfig(doc.structure);
  const n = doc.pages.length;
  if (doc.structure === 'RECTO_VERSO') {
    return n >= 2 ? 'Recto + verso' : n === 1 ? 'Recto seul' : 'Vide';
  }
  if (doc.structure === 'MULTI_PAGE_RECTO_VERSO') {
    const r = doc.pages.filter((p) => p.side === 'RECTO').length;
    const v = doc.pages.filter((p) => p.side === 'VERSO').length;
    return `${n} page(s) — ${r} recto, ${v} verso`;
  }
  if (doc.structure === 'MULTI_PAGE') {
    return `${n} page(s)`;
  }
  return cfg.label;
}

export function dataUrlByteLength(dataUrl: string): number {
  const i = dataUrl.indexOf(',');
  const b64 = i >= 0 ? dataUrl.slice(i + 1) : dataUrl;
  return Math.floor((b64.length * 3) / 4);
}
