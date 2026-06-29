/**
 * Client WebSocket CameraGP (GPY / XHY-D500) — port 9002.
 * Protocole dérivé de gpy/SDK/_extracted/Sample/html/js/WsUtil.js
 */

import { fetchBridgeJson } from '@/lib/bridge-fetch';
import { pickGuichetCameraIdByName, scoreGuichetCameraName } from '@/lib/guichet-camera-devices';

const DEFAULT_HOST = process.env.NEXT_PUBLIC_GPY_WS_HOST || 'localhost';
const DEFAULT_PORT = Number(process.env.NEXT_PUBLIC_GPY_WS_PORT || '9002');

export interface GpyResolution {
  width: number;
  height: number;
}

export interface GpyCameraDevice {
  id: number;
  name: string;
}

export class GpyCameraClient {
  private ws: WebSocket | null = null;
  private canvas: HTMLCanvasElement | null = null;
  private ctx: CanvasRenderingContext2D | null = null;
  private canvasW = 640;
  private canvasH = 480;
  private canvasX = 0;
  private canvasY = 0;
  private camId = 0;
  private streamW = 1920;
  private streamH = 1080;
  private devices: GpyCameraDevice[] = [];
  private faceCheckEnabled = false;
  private liveFrameCount = 0;
  private lastEmptyPreviewLogAt = 0;
  private refreshTimer: ReturnType<typeof setInterval> | null = null;
  private captureWaiter: { resolve: (b64: string) => void; reject: (e: Error) => void } | null = null;

  onLog?: (line: string) => void;
  onDevices?: (devices: GpyCameraDevice[]) => void;
  onReady?: (resolution: GpyResolution) => void;
  onError?: (message: string) => void;

  get connected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get deviceList(): GpyCameraDevice[] {
    return this.devices;
  }

  private log(msg: string) {
    this.onLog?.(msg);
  }

  private send(bytes: Uint8Array) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(bytes.buffer);
    }
  }

  private cmd3(b1: number, b2: number) {
    this.send(new Uint8Array([0xef, b1, b2]));
  }

  private cmd4(b1: number, b2: number, b3: number) {
    this.send(new Uint8Array([0xef, b1, b2, b3]));
  }

  private initParameters() {
    this.canvasX = 0;
    this.canvasY = 0;
    this.cmd4(0x0d, 0x01, 2);
    this.cmd4(0x0e, 0x01, 0);
    this.cmd4(0x20, 0x01, 0);
    this.cmd4(0x07, 0x01, 0);
    this.cmd4(0x21, 0x01, 0);
    this.cmd4(0x06, 0x01, 0);
    const ww = this.canvasW;
    const hh = this.canvasH;
    this.send(
      new Uint8Array([
        0xef, 0x15, 0x04,
        Math.floor(ww / 256), ww % 256,
        Math.floor(hh / 256), hh % 256,
      ])
    );
    this.cmd4(0x49, 0x01, 80);
    this.cmd4(0x42, 0x01, 1);
  }

  private sendRefreshDev() {
    this.cmd3(0x00, 0x00);
  }

  private sendGetMainCameraId() {
    this.cmd4(0x3a, 0x01, 0x01);
  }

  private sendEnableBase64Output() {
    this.cmd4(0xb2, 0x01, 0x01);
  }

  private sendStartVideo(camId: number, width: number, height: number) {
    this.streamW = width;
    this.streamH = height;
    this.send(
      new Uint8Array([
        0xef, 0x02, 0x05, camId,
        Math.floor(width / 256), width % 256,
        Math.floor(height / 256), height % 256,
      ])
    );
  }

  private sendCloseVideo() {
    this.cmd3(0x08, 0x00);
    if (this.ctx && this.canvas) {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
  }

  private sendRefreshFrame() {
    this.cmd3(0x04, 0x00);
  }

  private sendCapture() {
    this.send(new Uint8Array([0xef, 0x0a, 0x01, 0x00]));
  }

  /** Découpage automatique de document (équivalent SetAutoCut / sendMsgSetCutType). */
  sendSetAutoCut(on: boolean) {
    this.cmd4(0x0e, 0x01, on ? 1 : 0);
  }

  private initDocumentParameters() {
    this.canvasX = 0;
    this.canvasY = 0;
    this.cmd4(0x0d, 0x01, 2);
    this.sendSetAutoCut(true);
    this.cmd4(0x20, 0x01, 0);
    this.cmd4(0x07, 0x01, 0);
    this.cmd4(0x21, 0x01, 0);
    this.cmd4(0x06, 0x01, 0);
    const ww = this.canvasW;
    const hh = this.canvasH;
    this.send(
      new Uint8Array([
        0xef, 0x15, 0x04,
        Math.floor(ww / 256), ww % 256,
        Math.floor(hh / 256), hh % 256,
      ])
    );
    this.cmd4(0x49, 0x01, 80);
    this.cmd4(0x42, 0x01, 1);
  }

  private async warmPreviewFrames(count = 4) {
    for (let i = 0; i < count; i++) {
      this.sendRefreshFrame();
      await new Promise((r) => window.setTimeout(r, 120));
    }
  }

  private captureFromCanvas(options?: { silent?: boolean }): string | null {
    if (!this.canvas) return null;
    if (this.liveFrameCount < 1) {
      if (!options?.silent) {
        const now = Date.now();
        if (now - this.lastEmptyPreviewLogAt > 4000) {
          this.lastEmptyPreviewLogAt = now;
          this.log(`Aperçu sans frame (${this.liveFrameCount})`);
        }
      }
      return null;
    }
    try {
      const w = this.canvas.width;
      const h = this.canvas.height;
      if (w < 32 || h < 32) {
        this.log(`Canvas trop petit (${w}×${h})`);
        return null;
      }
      const url = this.canvas.toDataURL('image/jpeg', 0.92);
      if (url.length > 500) return url;
      this.log('Capture canvas : image vide');
      return null;
    } catch (e) {
      this.log(`Capture canvas : ${e instanceof Error ? e.message : 'erreur'}`);
      return null;
    }
  }

  /** Frame JPEG courante pour l’assistant ICAO (flux GPYScan / canvas). */
  getLivePreviewDataUrl(options?: { silent?: boolean }): string | null {
    return this.captureFromCanvas(options);
  }

  get hasLiveFrames(): boolean {
    return this.liveFrameCount > 0;
  }

  /** Photo depuis le flux affiché — fonctionne avec Logitech/HP via GPYScan sans matériel XHY. */
  async captureSnapshotFromPreview(): Promise<string> {
    // Certains postes mettent quelques secondes à démarrer le flux live.
    for (let attempt = 1; attempt <= 3; attempt++) {
      const ready = await this.waitForLivePreview(2, 4500 + attempt * 1200);
      if (!ready) {
        this.log(`Aperçu live lent (essai ${attempt}) : ${this.liveFrameCount} frame(s)`);
      }
      const fromCanvas = this.captureFromCanvas();
      if (fromCanvas) return fromCanvas;
      await this.warmPreviewFrames(6);
      await new Promise((r) => window.setTimeout(r, 250));
    }

    // Fallback: tenter une capture GPY directe, puis re-tenter le canvas.
    try {
      this.log('Aperçu vide — tentative CaptureImage GPY de secours…');
      return await this.snapOnce(false, 7_000);
    } catch {
      const fromCanvas = this.captureFromCanvas();
      if (fromCanvas) return fromCanvas;
      throw new Error(
        'Aperçu vide — le flux caméra tarde à démarrer. Attendez 3–5 s puis réessayez.'
      );
    }
  }

  private sendFaceCheck(enable: number) {
    this.send(new Uint8Array([0xef, 0x78, 0x01, enable]));
  }

  private sendCaptureFace() {
    this.cmd3(0x79, 0x00);
  }

  private pickCameraId(): number {
    if (this.devices.length === 0) return 0;
    const picked = pickGuichetCameraIdByName(this.devices);
    const pickedName = this.devices.find((d) => d.id === picked)?.name ?? '';
    if (scoreGuichetCameraName(pickedName) >= 0) return picked;

    // Dernier recours : première entrée nommée (éviter slot vide id=0)
    const named = this.devices.find((d) => (d.name || '').trim().length > 0);
    return named?.id ?? picked;
  }

  private isGenericWebcamName(name: string): boolean {
    const n = name.toLowerCase().replace(/\s+/g, '');
    if (!n) return true;
    return /logitech|罗技|c930|c920|brio|hp5mp|hp\d|webcam|integrated|ircamera|usbvideo|camera0/.test(n);
  }

  private hasCertifiedGpyCamera(): boolean {
    return this.devices.some((d) => {
      const n = d.name.toLowerCase();
      if (!n || this.isGenericWebcamName(d.name)) return false;
      return /xhy|d500|cameragp/.test(n) || /^gpy[\s_-]/.test(n);
    });
  }

  private pickResolution(pairs: number[]): GpyResolution {
    let best: GpyResolution = { width: 640, height: 480 };
    let bestArea = 0;
    let prefer: GpyResolution | null = null;
    for (let i = 0; i + 1 < pairs.length; i += 2) {
      const width = pairs[i];
      const height = pairs[i + 1];
      if (!width || !height) continue;
      const area = width * height;
      if (width === 1920 && height === 1080) prefer = { width, height };
      if (area > bestArea && width <= 4000 && height <= 3000) {
        bestArea = area;
        best = { width, height };
      }
    }
    if (prefer) return prefer;
    if (best.width > 1600 || best.height > 1200) {
      return { width: 1280, height: 960 };
    }
    return best;
  }

  private decodeDeviceNames(data: Uint8Array, offset: number, numCam: number): GpyCameraDevice[] {
    const list: GpyCameraDevice[] = [];
    let tmp = offset;
    for (let i = 0; i < numCam; i++) {
      const tmpLen = data[tmp];
      tmp++;
      const slice = data.slice(tmp, tmp + tmpLen);
      tmp += tmpLen;
      let name = '';
      try {
        name = decodeURIComponent(String.fromCharCode(...Array.from(slice)));
      } catch {
        try {
          name = new TextDecoder('utf-8').decode(slice);
        } catch {
          name = String.fromCharCode(...Array.from(slice));
        }
      }
      list.push({ id: i, name: name.trim() || `Caméra ${i}` });
    }
    return list;
  }

  private normalizeBase64(raw: unknown): string {
    let text = String(raw ?? '').trim();
    const last = text.charAt(text.length - 1);
    const last2 = text.charAt(text.length - 2);
    if (last === '=' && last2 !== '=') {
      text = `${text.substring(0, text.length - 1)}=`;
    }
    return text;
  }

  private deliverCapture(base64: string) {
    const waiter = this.captureWaiter;
    this.captureWaiter = null;
    if (!waiter) return;
    const norm = this.normalizeBase64(base64);
    waiter.resolve(norm.startsWith('data:') ? norm : `data:image/jpeg;base64,${norm}`);
  }

  private drawBase64Preview(dataUrl: string) {
    if (!this.ctx || !this.canvas) return;
    const img = new Image();
    img.onload = () => {
      if (!this.ctx || !this.canvas) return;
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
      this.liveFrameCount++;
    };
    img.onerror = () => {
      this.onError?.('Décodage aperçu GPY échoué');
    };
    img.src = dataUrl;
  }

  private drawRgbFrame(data: Uint8Array, ww: number, hh: number) {
    if (!this.ctx || !this.canvas) return;
    const imgData = this.ctx.createImageData(ww, hh);
    let dataNum = 7;

    for (let i = 0; i < imgData.data.length; i += 4) {
      imgData.data[i] = data[dataNum];
      imgData.data[i + 1] = data[dataNum + 1];
      imgData.data[i + 2] = data[dataNum + 2];
      imgData.data[i + 3] = 255;
      dataNum += 3;
    }

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    const x = this.canvas.width / 2 - ww / 2 + this.canvasX;
    const y = this.canvas.height / 2 - hh / 2 + this.canvasY;
    this.ctx.putImageData(imgData, x, y);
    this.liveFrameCount++;
  }

  /** Attend que l'aperçu live ait reçu au moins une frame (scan document / webcam GPY). */
  async waitForLivePreview(minFrames = 2, timeoutMs = 6000): Promise<boolean> {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      if (this.liveFrameCount >= minFrames) return true;
      this.sendRefreshFrame();
      await new Promise((r) => window.setTimeout(r, 150));
    }
    return this.liveFrameCount >= minFrames;
  }

  private handleBinary(data: Uint8Array) {
    if (data.length < 3 || data[0] !== 0xef) return;
    const op = data[1];

    if (op === 0x01) {
      const numCam = data[3];
      const len = data[4];
      const pairs: number[] = [];
      let tmp = 5;
      for (let i = 0; i < len; i++) {
        pairs.push(data[tmp] * 256 + data[tmp + 1], data[tmp + 2] * 256 + data[tmp + 3]);
        tmp += 4;
      }
      const res = this.pickResolution(pairs);
      this.devices = this.decodeDeviceNames(data, tmp, numCam);
      this.onDevices?.(this.devices);
      this.camId = this.pickCameraId();
      this.log(
        `GPY : ${this.devices.length} caméra(s), id=${this.camId} «${this.devices[this.camId]?.name || '?'}», flux ${res.width}×${res.height}`
      );
      this.sendStartVideo(this.camId, res.width, res.height);
      this.onReady?.(res);
      return;
    }

    if (op === 0x3b && data.length >= 4) {
      this.camId = data[3];
      return;
    }

    if (op === 0x14 && data.length >= 4) {
      const tmp = data[3];
      if (tmp === 0x46 || tmp === 0x5f) {
        this.faceCheckEnabled = true;
      }
      return;
    }

    if ((op === 0x05 || op === 0x0c) && data.length >= 7) {
      const ww = data[3] * 256 + data[4];
      const hh = data[5] * 256 + data[6];
      this.drawRgbFrame(data, ww, hh);
      return;
    }

    if (op === 0x36 && data.length >= 6) {
      const len = data[3] * 65536 + data[4] * 256 + data[5];
      const slice = data.slice(6, 6 + len);
      try {
        const str = decodeURIComponent(String.fromCharCode(...Array.from(slice)));
        this.deliverCapture(str);
      } catch {
        this.onError?.('Décodage image GPY échoué');
      }
      return;
    }

    if ((op === 0x3e || op === 0x43) && data.length >= 6) {
      const len = data[3] * 65536 + data[4] * 256 + data[5];
      const slice = data.slice(6, 6 + len);
      try {
        const str = decodeURIComponent(String.fromCharCode(...Array.from(slice)));
        this.deliverCapture(str);
      } catch {
        this.onError?.('Décodage visage GPY échoué');
      }
      return;
    }

    if (this.captureWaiter) {
      this.log(`GPY capture en attente, opcode 0x${op.toString(16)}`);
    }
  }

  private handleMessage(event: MessageEvent) {
    if (typeof event.data === 'string') {
      if (event.data.includes('GetPicBase64:')) {
        this.deliverCapture(event.data.substring(13));
        return;
      }
      const b64Match = event.data.match(/data:image\/[^;]+;base64,([A-Za-z0-9+/=]+)/);
      if (b64Match?.[1]) {
        if (this.captureWaiter) {
          this.deliverCapture(b64Match[1]);
        } else {
          this.drawBase64Preview(b64Match[0]);
        }
        return;
      }
      const rawB64 = event.data.match(/^([A-Za-z0-9+/]{200,}={0,2})$/);
      if (rawB64?.[1] && !this.captureWaiter) {
        this.drawBase64Preview(`data:image/jpeg;base64,${rawB64[1]}`);
      }
      return;
    }
    if (event.data instanceof ArrayBuffer) {
      this.handleBinary(new Uint8Array(event.data));
    }
  }

  connect(
    canvas: HTMLCanvasElement,
    options?: { host?: string; port?: number; documentMode?: boolean }
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      if (typeof WebSocket === 'undefined') {
        reject(new Error('WebSocket indisponible'));
        return;
      }

      this.disconnect();
      this.canvas = canvas;
      this.canvasW = Math.max(canvas.clientWidth || 640, 320);
      this.canvasH = Math.max(canvas.clientHeight || 480, 240);
      canvas.width = this.canvasW;
      canvas.height = this.canvasH;
      this.liveFrameCount = 0;
      this.ctx = canvas.getContext('2d');
      if (!this.ctx) {
        reject(new Error('Canvas 2D requis'));
        return;
      }

      const host = options?.host ?? DEFAULT_HOST;
      const port = options?.port ?? DEFAULT_PORT;
      const documentMode = options?.documentMode === true;
      const url = `ws://${host}:${port}`;
      this.log(`Connexion GPY ${url}${documentMode ? ' (scan document)' : ''}…`);

      const ws = new WebSocket(url);
      ws.binaryType = 'arraybuffer';
      this.ws = ws;

      const failTimer = window.setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) {
          ws.close();
          reject(new Error('Service CameraGP injoignable (port 9002). Installez CameraGPSDKsetup.exe.'));
        }
      }, 8000);

      ws.onopen = () => {
        window.clearTimeout(failTimer);
        this.sendEnableBase64Output();
        this.sendGetMainCameraId();
        if (documentMode) this.initDocumentParameters();
        else this.initParameters();
        this.sendRefreshDev();
        this.refreshTimer = window.setInterval(() => {
          if (this.ws?.readyState === WebSocket.OPEN) this.sendRefreshFrame();
        }, 80);
        resolve();
      };

      ws.onmessage = (e) => this.handleMessage(e);
      ws.onerror = () => {
        window.clearTimeout(failTimer);
        this.onError?.('WebSocket GPY erreur');
        reject(new Error('WebSocket GPY erreur'));
      };
      ws.onclose = () => {
        this.onError?.('Connexion GPY fermée');
      };
    });
  }

  /** Scan document : XHY → CaptureImage WS ; HP/Logitech → image live canvas uniquement. */
  async captureDocument(autoCut = true): Promise<string> {
    if (!this.connected) throw new Error('Scanner GPY non connecté');
    this.sendSetAutoCut(autoCut);
    await this.warmPreviewFrames(12);
    const liveReady = await this.waitForLivePreview(2, 8000);
    if (!liveReady) {
      this.log(`Scan : flux live lent (${this.liveFrameCount} frame)`);
    }

    const camName = this.devices[this.camId]?.name ?? '';
    const useCanvasOnly = this.isGenericWebcamName(camName) || !this.hasCertifiedGpyCamera();

    if (useCanvasOnly) {
      this.log(`Scan aperçu live («${camName || '?'}» — pas de CaptureImage WS)`);
      const snap = this.captureFromCanvas();
      if (snap) return snap;
      throw new Error(
        'Aperçu vide — attendez 2–3 s que le flux s\'affiche dans le cadre, puis réessayez.'
      );
    }

    try {
      return await this.snapOnce(false, 8_000);
    } catch (e) {
      const snap = this.captureFromCanvas();
      if (snap) {
        this.log('Scan document — fallback aperçu live');
        return snap;
      }
      throw e instanceof Error ? e : new Error('Timeout scan GPY — réessayez ou importez un fichier.');
    }
  }

  disconnect() {
    this.liveFrameCount = 0;
    if (this.refreshTimer) {
      window.clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
    this.sendCloseVideo();
    this.sendFaceCheck(0);
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
    this.captureWaiter?.reject(new Error('Caméra GPY déconnectée'));
    this.captureWaiter = null;
  }

  waitForCapture(timeoutMs = 20000): Promise<string> {
    return new Promise((resolve, reject) => {
      this.captureWaiter = { resolve, reject };
      window.setTimeout(() => {
        if (this.captureWaiter) {
          this.captureWaiter = null;
          reject(new Error('Timeout capture GPY'));
        }
      }, timeoutMs);
    });
  }

  private async snapOnce(face: boolean, timeoutMs: number): Promise<string> {
    try {
      await this.warmPreviewFrames();
      const capturePromise = this.waitForCapture(timeoutMs);
      if (face) {
        this.sendFaceCheck(1);
        await new Promise((r) => window.setTimeout(r, 900));
        this.log('GPY : détection visage activée');
        this.sendCaptureFace();
      } else {
        this.log('GPY : CaptureImage…');
        this.sendCapture();
      }
      return await capturePromise;
    } finally {
      this.sendFaceCheck(0);
    }
  }

  async capturePhoto(useFace = true): Promise<string> {
    if (!this.connected) throw new Error('GPY non connecté');
    if (this.captureWaiter) throw new Error('Capture déjà en cours');

    const certified = this.hasCertifiedGpyCamera();
    const tryFace = useFace && certified;

    if (!certified) {
      await this.warmPreviewFrames(6);
      const snap = this.captureFromCanvas();
      if (snap) {
        this.log('Photo depuis aperçu live (webcam via GPYScan — sans XHY)');
        return snap;
      }
      this.log('Aperçu GPY — tentative CaptureImage serveur…');
    } else if (useFace && !tryFace) {
      this.log('Photo simple (aperçu live)');
    }

    const camIds =
      this.devices.length > 1
        ? [this.camId, ...this.devices.map((d) => d.id).filter((id) => id !== this.camId)]
        : [this.camId];

    let lastErr: Error | null = null;
    for (const camId of camIds) {
      if (camId !== this.camId) {
        this.log(`Essai caméra id=${camId} «${this.devices[camId]?.name || '?'}»`);
        this.sendCloseVideo();
        await new Promise((r) => window.setTimeout(r, 200));
        this.camId = camId;
        this.sendStartVideo(camId, this.streamW, this.streamH);
        await new Promise((r) => window.setTimeout(r, 600));
      }

      try {
        if (tryFace) {
          try {
            return await this.snapOnce(true, 12_000);
          } catch {
            this.sendFaceCheck(0);
            return await this.snapOnce(false, 8_000);
          }
        }
        const timeout = certified ? 15_000 : 5_000;
        return await this.snapOnce(false, timeout);
      } catch (e) {
        lastErr = e instanceof Error ? e : new Error('Capture GPY échouée');
        const fromCanvas = this.captureFromCanvas();
        if (fromCanvas) {
          this.log('Photo depuis aperçu live (fallback canvas)');
          return fromCanvas;
        }
      }
    }

    const fromCanvas = this.captureFromCanvas();
    if (fromCanvas) {
      this.log('Photo prise depuis l\'aperçu live (fallback canvas)');
      return fromCanvas;
    }

    throw lastErr ?? new Error('Timeout capture GPY — utilisez « Webcam navigateur » ou importez une image.');
  }
}

/** Vérifie le port 9002 via Device Bridge (TCP) — évite les erreurs WebSocket dans la console. */
export async function checkGpyServiceViaBridge(): Promise<{
  available: boolean;
  message?: string;
}> {
  try {
    const { ok, data } = await fetchBridgeJson<{ available?: boolean; message?: string }>(
      '/api/v1/devices/camera/gpy-status',
      undefined,
      4000
    );
    if (!ok || !data) return { available: false, message: 'Device Bridge injoignable (8765)' };
    return { available: Boolean(data.available), message: data.message };
  } catch {
    return { available: false, message: 'Device Bridge injoignable — démarrez dotnet run sur le bridge' };
  }
}

/** Vérifie si le service CameraGP écoute (WebSocket direct — préférer checkGpyServiceViaBridge). */
export function probeGpyCameraService(
  host = DEFAULT_HOST,
  port = DEFAULT_PORT,
  timeoutMs = 4000
): Promise<boolean> {
  return new Promise((resolve) => {
    if (typeof WebSocket === 'undefined') {
      resolve(false);
      return;
    }

    let settled = false;
    const settle = (ok: boolean) => {
      if (settled) return;
      settled = true;
      window.clearTimeout(timer);
      resolve(ok);
    };

    let ws: WebSocket;
    try {
      ws = new WebSocket(`ws://${host}:${port}`);
    } catch {
      settle(false);
      return;
    }

    const timer = window.setTimeout(() => settle(false), timeoutMs);

    ws.onopen = () => {
      settle(true);
      window.setTimeout(() => {
        try {
          if (ws.readyState === WebSocket.OPEN) ws.close();
        } catch {
          /* ignore */
        }
      }, 80);
    };

    ws.onerror = () => settle(false);
  });
}

export const GPY_SERVICE_HELP =
  'Le service CameraGP (WebSocket port 9002) n\'est pas démarré. ' +
  'Installez CameraGPSDKsetup.exe, lancez l\'application GPYScan / CameraGP (icône barre des tâches), ' +
  'puis vérifiez avec: scripts/check-gpy-ws.ps1';
