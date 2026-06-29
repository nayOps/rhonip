import { jsPDF } from 'jspdf';
import {
  CompletedEnrollmentReportRow,
  getCompletedEnrollmentReport,
  mediaProxyUrl,
} from '@/services/enrollment-session-api';

const FOOTER_LINES = [
  'Administrateur — ALEMA OLAMBA NATHAN',
  'Superviseur — SILVA KALADNULAS',
  'OPS — BAKOLE JACQUE',
  'OPS — GEORDY MULIMBLA',
];

/** Même palette que le récépissé (étape 8) — bleu institutionnel */
const COLORS = {
  blue900: [30, 58, 138] as [number, number, number],
  blue800: [30, 64, 175] as [number, number, number],
  blue700: [29, 78, 216] as [number, number, number],
  headerText: [255, 255, 255] as [number, number, number],
  rowAlt: [239, 246, 255] as [number, number, number],
  border: [191, 219, 254] as [number, number, number],
  muted: [100, 116, 139] as [number, number, number],
  success: [22, 163, 74] as [number, number, number],
};

const HEADER_HEIGHT_MM = 46;

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

function truncate(text: string, max: number): string {
  const t = text.trim();
  if (t.length <= max) return t || '—';
  return `${t.slice(0, max - 1)}…`;
}

async function loadImageDataUrl(uri: string | null | undefined): Promise<string | null> {
  if (!uri) return null;
  try {
    const url = mediaProxyUrl(uri);
    const res = await fetch(url);
    if (!res.ok) return null;
    const blob = await res.blob();
    return await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(typeof reader.result === 'string' ? reader.result : null);
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(blob);
    });
  } catch {
    return null;
  }
}

function drawPageHeader(doc: jsPDF, pageW: number, subtitle: string) {
  const h = HEADER_HEIGHT_MM;
  const cx = pageW / 2;

  doc.setFillColor(...COLORS.blue900);
  doc.rect(0, 0, pageW, h, 'F');
  doc.setFillColor(...COLORS.blue800);
  doc.rect(0, h - 5, pageW, 5, 'F');

  doc.setTextColor(...COLORS.headerText);

  // 1. République Démocratique du Congo
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9);
  doc.text('République Démocratique du Congo', cx, 9, { align: 'center' });

  // 2. Office National d'Identification de la Population
  doc.setFontSize(10);
  doc.text("OFFICE NATIONAL D'IDENTIFICATION DE LA POPULATION", cx, 15.5, { align: 'center' });

  // 3. Identification biométrique du personnel
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8.5);
  doc.text('Identification biométrique du personnel', cx, 21, { align: 'center' });

  // 4. Recherche et développement (à la place de « Fichier Général… »)
  doc.setFontSize(8);
  doc.text('Recherche et développement', cx, 26.5, { align: 'center' });

  doc.setDrawColor(255, 255, 255);
  doc.setLineWidth(0.25);
  doc.line(cx - 42, 30, cx + 42, 30);

  // 5. Titre du document
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text('RAPPORT', cx, 37, { align: 'center' });

  // Métadonnées (droite)
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7);
  doc.text(subtitle, pageW - 14, 11, { align: 'right' });
  doc.setFontSize(6);
  doc.text('Document officiel — usage interne', pageW - 14, 16, { align: 'right' });
}

function drawPageFooter(doc: jsPDF, pageW: number, pageH: number, pageNum: number, totalPages: number) {
  const footerTop = pageH - 22;
  doc.setDrawColor(...COLORS.border);
  doc.setLineWidth(0.3);
  doc.line(14, footerTop, pageW - 14, footerTop);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7);
  doc.setTextColor(...COLORS.muted);
  const colW = (pageW - 28) / 2;
  FOOTER_LINES.forEach((line, i) => {
    const x = i % 2 === 0 ? 14 : 14 + colW;
    const y = footerTop + 4 + Math.floor(i / 2) * 4.5;
    doc.text(line, x, y);
  });

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.text(`Page ${pageNum} / ${totalPages}`, pageW - 14, pageH - 6, { align: 'right' });
}

export async function generateCompletedEnrollmentsPdf(): Promise<void> {
  const report = await getCompletedEnrollmentReport();
  const rows = report.rows;

  const images = await Promise.all(
    rows.map((r) => loadImageDataUrl(r.photo_uri))
  );

  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const margin = 14;
  const tableTop = HEADER_HEIGHT_MM + 4;
  const rowH = 20;
  const footerReserve = 26;
  const usableBottom = pageH - footerReserve;

  const colPhoto = 18;
  const colNom = 42;
  const colPostnom = 42;
  const colStatut = 28;
  const colMatricule = 52;
  const colCreated = 44;
  const cols = [
    { label: 'Photo', w: colPhoto },
    { label: 'Nom', w: colNom },
    { label: 'Postnom', w: colPostnom },
    { label: 'Statut', w: colStatut },
    { label: 'Matricule', w: colMatricule },
    { label: 'Créée le', w: colCreated },
  ];

  const subtitle = `Généré le ${formatDate(report.generated_at)} · ${report.count} enregistrement(s)`;

  const drawTableHeader = (y: number) => {
    let x = margin;
    doc.setFillColor(...COLORS.blue800);
    doc.rect(margin, y, pageW - margin * 2, 9, 'F');
    doc.setTextColor(...COLORS.headerText);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8);
    cols.forEach((c) => {
      doc.text(c.label, x + 2, y + 6);
      x += c.w;
    });
    return y + 9;
  };

  let y = tableTop;
  let pageNum = 1;
  const pageStarts: number[] = [1];

  drawPageHeader(doc, pageW, subtitle);
  y = drawTableHeader(y);

  rows.forEach((row, idx) => {
    if (y + rowH > usableBottom) {
      doc.addPage();
      pageNum += 1;
      pageStarts.push(pageNum);
      drawPageHeader(doc, pageW, subtitle);
      y = tableTop;
      y = drawTableHeader(y);
    }

    if (idx % 2 === 1) {
      doc.setFillColor(...COLORS.rowAlt);
      doc.rect(margin, y, pageW - margin * 2, rowH, 'F');
    }

    doc.setDrawColor(...COLORS.border);
    doc.rect(margin, y, pageW - margin * 2, rowH);

    let x = margin;
    const img = images[idx];
    if (img) {
      try {
        doc.addImage(img, 'JPEG', x + 2, y + 2, colPhoto - 4, rowH - 4);
      } catch {
        doc.setFontSize(7);
        doc.setTextColor(...COLORS.muted);
        doc.text('—', x + 6, y + rowH / 2);
      }
    } else {
      doc.setFontSize(7);
      doc.setTextColor(...COLORS.muted);
      doc.text('N/A', x + 5, y + rowH / 2);
    }
    x += colPhoto;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(30, 41, 59);
    doc.text(truncate(row.nom, 28), x + 2, y + 8);
    x += colNom;
    doc.text(truncate(row.postnom, 28), x + 2, y + 8);
    x += colPostnom;

    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.success);
    doc.setFontSize(7);
    doc.text(row.statut || 'COMPLETED', x + 2, y + 8);
    x += colStatut;

    doc.setFont('courier', 'normal');
    doc.setTextColor(30, 41, 59);
    doc.setFontSize(7);
    doc.text(truncate(row.registration_number || '—', 32), x + 2, y + 8);
    x += colMatricule;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.text(formatDate(row.created_at), x + 2, y + 8);

    y += rowH;
  });

  const totalPages = doc.getNumberOfPages();
  for (let p = 1; p <= totalPages; p += 1) {
    doc.setPage(p);
    drawPageFooter(doc, pageW, pageH, p, totalPages);
  }

  const stamp = new Date().toISOString().slice(0, 10);
  doc.save(`rapport-enrolements-completes-${stamp}.pdf`);
}

export type { CompletedEnrollmentReportRow };
