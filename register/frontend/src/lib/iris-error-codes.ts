/** Codes errcode Iris Device Server — alignés sur device-bridge IrisErrorCatalog.cs */
export const IRIS_ERR_DEVICE_OPEN_FAILED = 16777219; // 0x01000003
export const IRIS_ERR_DEVICE_CLOSED_CAPTURE = 16777231; // 0x0100000F

const KNOWN: Record<number, string> = {
  [IRIS_ERR_DEVICE_OPEN_FAILED]:
    'Ouverture JD5 impossible — exécutez device-bridge\\scripts\\start-iris-server-admin.bat (admin), puis Ouvrir lecteur.',
  [IRIS_ERR_DEVICE_CLOSED_CAPTURE]:
    'Lecteur iris fermé ou occupé — fermez DeviceUI si ouvert, puis Ouvrir lecteur ou redémarrez IrisDeviceServer.exe.',
};

export function describeIrisErrcode(code: number, vendorMessage?: string): string {
  const core = KNOWN[code];
  if (core) {
    return vendorMessage?.trim() ? `${core} — ${vendorMessage.trim()}` : core;
  }
  const layer = (code >> 24) & 0xff;
  const sub = code & 0xffffff;
  if (layer === 1) {
    return `Erreur système iris (${sub}) — vérifiez USB, un seul processus sur le lecteur JD5.`;
  }
  return vendorMessage?.trim()
    ? `Erreur iris (${code}) — ${vendorMessage.trim()}`
    : `Erreur iris (errcode=${code})`;
}
