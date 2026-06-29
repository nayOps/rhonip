import type { IcaoLiveOverlay } from '@/services/icao-face-api';

export type OverlayDrawOptions = {
  showLandmarks?: boolean;
  showMesh?: boolean;
  showBoundingBox?: boolean;
  showEyeLine?: boolean;
  showFaceAxis?: boolean;
  showCropFrame?: boolean;
};

const DEFAULT_OPTS: OverlayDrawOptions = {
  showLandmarks: true,
  showMesh: true,
  showBoundingBox: true,
  showEyeLine: true,
  showFaceAxis: true,
  showCropFrame: true,
};

/** Dessine landmarks / mesh / bbox / lignes / cadre ICAO sur un canvas superposé à la vidéo. */
export function drawIcaoLiveOverlay(
  ctx: CanvasRenderingContext2D,
  overlay: IcaoLiveOverlay | null | undefined,
  width: number,
  height: number,
  options: OverlayDrawOptions = DEFAULT_OPTS
) {
  ctx.clearRect(0, 0, width, height);
  if (!overlay || width < 1 || height < 1) return;

  const opts = { ...DEFAULT_OPTS, ...options };

  if (opts.showBoundingBox && overlay.boundingBox) {
    const b = overlay.boundingBox;
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.85)';
    ctx.lineWidth = 2;
    ctx.strokeRect(b.xMin * width, b.yMin * height, (b.xMax - b.xMin) * width, (b.yMax - b.yMin) * height);
  }

  if (opts.showCropFrame && overlay.cropFrame) {
    const c = overlay.cropFrame;
    ctx.strokeStyle = 'rgba(34, 197, 94, 0.9)';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.strokeRect(c.x * width, c.y * height, c.width * width, c.height * height);
    ctx.setLineDash([]);
    const pct = c.faceHeightPercent;
    const min = c.faceHeightTargetMin ?? 70;
    const max = c.faceHeightTargetMax ?? 80;
    if (typeof pct === 'number') {
      const inBand = pct >= min && pct <= max;
      ctx.fillStyle = inBand ? 'rgba(34, 197, 94, 0.95)' : 'rgba(245, 158, 11, 0.95)';
      ctx.font = '12px system-ui, sans-serif';
      ctx.fillText(
        `Visage ${pct.toFixed(0)} % (ICAO ${min}–${max} %)`,
        c.x * width + 4,
        Math.max(14, c.y * height - 6)
      );
    }
  }

  if (opts.showMesh && overlay.connections?.length && overlay.facialLandmarks?.length) {
    ctx.strokeStyle = 'rgba(96, 165, 250, 0.55)';
    ctx.lineWidth = 1;
    for (const [i, j] of overlay.connections) {
      const a = overlay.facialLandmarks[i];
      const b = overlay.facialLandmarks[j];
      if (!a || !b) continue;
      ctx.beginPath();
      ctx.moveTo(a.x * width, a.y * height);
      ctx.lineTo(b.x * width, b.y * height);
      ctx.stroke();
    }
  }

  if (opts.showLandmarks && overlay.facialLandmarks?.length) {
    ctx.fillStyle = 'rgba(250, 204, 21, 0.9)';
    for (const p of overlay.facialLandmarks) {
      ctx.beginPath();
      ctx.arc(p.x * width, p.y * height, 1.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  if (opts.showEyeLine && overlay.eyeLine) {
    const le = overlay.eyeLine.left;
    const re = overlay.eyeLine.right;
    ctx.strokeStyle = 'rgba(34, 197, 94, 1)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(le.x * width, le.y * height);
    ctx.lineTo(re.x * width, re.y * height);
    ctx.stroke();
  }

  if (opts.showFaceAxis && overlay.faceAxis) {
    const top = overlay.faceAxis.top;
    const bottom = overlay.faceAxis.bottom;
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.9)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(top.x * width, top.y * height);
    ctx.lineTo(bottom.x * width, bottom.y * height);
    ctx.stroke();
    if (overlay.faceAxis.nose) {
      const n = overlay.faceAxis.nose;
      ctx.fillStyle = 'rgba(239, 68, 68, 0.8)';
      ctx.beginPath();
      ctx.arc(n.x * width, n.y * height, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}
