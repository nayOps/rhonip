using System.Diagnostics;
using System.Text;
using Fgp.DeviceBridge.Api.Models;
using Fgp.DeviceBridge.Api.Modules.Fap60;

namespace Fgp.DeviceBridge.Api.Modules;

public sealed class Fap60FingerprintModule : IFingerprintModule
{
    private const int CaptureTimeoutError = -26;
    private const int ImageMissingError = -30;
    private const int CaptureRetryDelayMs = 400;
    /// <summary>Comme FAP60Demo : timeout par appel SDK, pas la durée totale.</summary>
    private const int SdkAttemptTimeoutMs = 15_000;
    /// <summary>Garde-fou si captureImage_old ne respecte pas unTimeOutMs.</summary>
    private const int SdkCallWatchdogMs = SdkAttemptTimeoutMs + 3_000;
    private const int PostCancelJoinMs = 3_000;
    private const int MaxCaptureAttempts = 8;
    private const int SdkStuckError = -9_001;
    private readonly string? _sdkPath;
    private readonly Fap60FingerprintOptions _options;
    private IntPtr _deviceHandle = IntPtr.Zero;
    private bool _open;
    private bool _algoActive;
    private string? _licenseMessage;
    private string? _lastDeviceSn;
    private string? _firmware;
    private readonly SemaphoreSlim _deviceGate = new(1, 1);
    private volatile bool _captureInProgress;

    public Fap60FingerprintModule(string? sdkPath, Fap60FingerprintOptions? options = null)
    {
        _sdkPath = sdkPath;
        _options = options ?? new Fap60FingerprintOptions { SdkPath = sdkPath };
    }

    public string ModuleName => "fingerprint";

    public ModuleHealth GetHealth()
    {
        if (!OperatingSystem.IsWindows())
            return new("down", "FAP60 requires Windows", "fap60");

        if (string.IsNullOrWhiteSpace(_sdkPath) || !Directory.Exists(_sdkPath))
            return new("degraded", "SdkPath manquant — lancez copy-fap60-sdk.ps1 (sdk/fap60-x64)", "fap60");

        var required = new[] { "FAP60-02.dll", "fingerprint.dll", "Driver.dll" };
        var missing = required.Where(f => !File.Exists(Path.Combine(_sdkPath!, f))).ToList();
        if (missing.Count > 0)
            return new("degraded", $"DLL manquantes: {string.Join(", ", missing)}", "fap60");

        var licenseHint = _licenseMessage ?? "Licence algo : non chargée";
        if (_open)
            return new("ok", $"Lecteur ouvert — SN: {_lastDeviceSn ?? "n/a"} — {licenseHint}", "fap60");

        return new("ok", $"SDK FAP60 prêt — {licenseHint}", "fap60");
    }

    public Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default)
    {
        if (!OperatingSystem.IsWindows())
            return Task.FromResult(new DeviceOperationResponse(false, "Windows only"));

        if (_open && _deviceHandle != IntPtr.Zero)
            return Task.FromResult(new DeviceOperationResponse(true, $"Déjà ouvert — SN: {_lastDeviceSn}", 0));

        try
        {
            Fap60Native.SetDllDirectory(_sdkPath!);

            // Comme FAP60Demo : zzInit à chaque OpenDevice (après zzFree au CloseDevice).
            var lic = Fap60AlgorithmLicense.Initialize(_sdkPath!, _options);
            _licenseMessage = lic.Message;
            if (!lic.Success)
                return Task.FromResult(new DeviceOperationResponse(false, lic.Message));
            _algoActive = lic.AlgorithmActive;

            var errCode = new int[1];
            var handle = Fap60Native.mxOpenDevice(errCode);
            if (handle == IntPtr.Zero)
            {
                var msg = Fap60ImageHelper.GetErrorMessage(errCode[0]);
                return Task.FromResult(new DeviceOperationResponse(false, $"mxOpenDevice ({errCode[0]}): {msg}"));
            }

            _deviceHandle = handle;
            _open = true;
            _lastDeviceSn = ReadSerial(handle);
            _firmware = ReadFirmware(handle);
            WarmUpDevice(captureType: 0);

            var message = new StringBuilder($"FAP60 ouvert — SN: {_lastDeviceSn ?? "n/a"}");
            if (!string.IsNullOrEmpty(_firmware))
                message.Append($", firmware: {_firmware}");
            if (!string.IsNullOrEmpty(_licenseMessage))
                message.Append($" — {_licenseMessage}");

            return Task.FromResult(new DeviceOperationResponse(true, message.ToString(), 0));
        }
        catch (DllNotFoundException ex)
        {
            return Task.FromResult(new DeviceOperationResponse(false, $"DLL: {ex.Message}"));
        }
        catch (Exception ex)
        {
            return Task.FromResult(new DeviceOperationResponse(false, ex.Message));
        }
    }

    public Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default)
    {
        if (_open && _deviceHandle != IntPtr.Zero)
        {
            try { CancelCapture(); } catch { /* ignore */ }
            try { Fap60Native.closeDevice(_deviceHandle); } catch { /* ignore */ }
        }
        if (_algoActive)
        {
            try { Fap60Native.zzFree(); } catch { /* ignore */ }
            _algoActive = false;
        }
        _deviceHandle = IntPtr.Zero;
        _open = false;
        return Task.FromResult(new DeviceOperationResponse(true, "FAP60 fermé"));
    }

    public async Task<FingerprintCaptureResponse> CaptureAsync(
        FingerprintCaptureRequest request,
        CancellationToken ct = default)
    {
        if (!_open || _deviceHandle == IntPtr.Zero)
        {
            var open = await OpenAsync(ct);
            if (!open.Success)
                return new FingerprintCaptureResponse(false, open.Message);
        }

        try
        {
            await _deviceGate.WaitAsync(ct);
            _captureInProgress = true;
            try
            {
                // Pas de token sur Task.Run : CancelAfter provoquait HTTP 500 (OperationCanceledException).
                return await Task.Run(() => CaptureCore(request, allowThumbsFallback: true));
            }
            finally
            {
                _captureInProgress = false;
                _deviceGate.Release();
            }
        }
        catch (OperationCanceledException)
        {
            return new FingerprintCaptureResponse(
                false,
                "Capture annulée ou délai dépassé",
                Logs: new List<string> { "Délai client ou serveur — repositionnez les doigts au centre du plateau et réessayez." });
        }
        catch (Exception ex)
        {
            return new FingerprintCaptureResponse(false, $"Erreur capture: {ex.Message}", Logs: new List<string> { ex.ToString() });
        }
    }

    private FingerprintCaptureResponse CaptureCore(FingerprintCaptureRequest request, bool allowThumbsFallback)
    {
        try
        {
            Fap60Native.SetDllDirectory(_sdkPath!);

            var captureType = request.CaptureType;
            if (!string.IsNullOrWhiteSpace(request.FingerPosition))
                captureType = "single";

            var present = request.PresentFingers?.Count > 0
                ? request.PresentFingers.Select(f => f.ToLowerInvariant()).ToList()
                : Fap60FingerLayout.GetOrderedFingers(captureType, request.FingerPosition).ToList();

            var captureTypeInt = Fap60FingerLayout.CaptureTypeToInt(captureType);
            var baseMissNum = request.MissingFingers > 0
                ? request.MissingFingers
                : Fap60FingerLayout.CountMissing(captureType, present);

            var isThumbs = captureType.Equals("both_thumbs", StringComparison.OrdinalIgnoreCase);
            var sdkTimeoutMs = isThumbs ? 6_000 : SdkAttemptTimeoutMs;
            var sdkWatchdogMs = sdkTimeoutMs + 3_000;
            var maxAttempts = isThumbs ? 2 : MaxCaptureAttempts;
            var retryDelayMs = isThumbs ? 250 : CaptureRetryDelayMs;
            var thumbsHardBudgetMs = isThumbs ? 12_000 : request.TimeoutMs;

            var saveOri = new byte[Fap60Native.BigWidth * Fap60Native.BigHeight];
            var saveEnh = new byte[Fap60Native.BigWidth * Fap60Native.BigHeight];
            var saveSmall = new byte[4 * Fap60Native.SmallFingerBytes];

            var logs = new List<string>
            {
                $"Capture type={captureType} (mode {captureTypeInt}), doigts présents={present.Count}, absents={baseMissNum}",
                $"Seuil NFIQ max accepté: {request.NfiqThreshold}",
                "Placez les doigts sur le plateau — la capture peut prendre plusieurs secondes…",
            };

            if (isThumbs)
            {
                CancelCapture();
                Thread.Sleep(300);
                WarmUpDevice(3);
                logs.Add("Pouces : reset SDK + warm-up mode 3 (après capture 4+4)");
            }

            // o_CaptureStatus : buffer de SORTIE SDK (FAP60Demo initialise g_CaptureType à 0).
            var captureStatus = new int[10];
            var deadline = DateTime.UtcNow.AddMilliseconds(request.TimeoutMs);
            var rc = -1;
            var attempts = 0;
            var timeoutAttempts = 0;
            var thumbsTimeoutStreak = 0;
            var totalSw = Stopwatch.StartNew();

            logs.Add(
                $"Max {maxAttempts} tentatives, {sdkTimeoutMs / 1000}s SDK / {sdkWatchdogMs / 1000}s watchdog, budget {request.TimeoutMs / 1000}s");

            while (DateTime.UtcNow < deadline && attempts < maxAttempts)
            {
                if (isThumbs && totalSw.ElapsedMilliseconds >= thumbsHardBudgetMs)
                {
                    logs.Add("Pouces: budget direct dépassé — passage au repli single.");
                    rc = CaptureTimeoutError;
                    break;
                }

                attempts++;
                Array.Clear(captureStatus, 0, captureStatus.Length);

                var nMissThisAttempt = baseMissNum;
                if (isThumbs && present.Count == 2)
                    nMissThisAttempt = attempts <= 2 ? 0 : 8;

                var attemptSw = Stopwatch.StartNew();
                rc = CaptureImageOnceWithWatchdog(
                    captureTypeInt,
                    nMissThisAttempt,
                    saveOri,
                    saveEnh,
                    saveSmall,
                    captureStatus,
                    sdkTimeoutMs,
                    sdkWatchdogMs);

                logs.Add(
                    $"Tentative {attempts} — nMiss={nMissThisAttempt}, rc={rc}, {attemptSw.ElapsedMilliseconds} ms");

                if (rc == SdkStuckError)
                {
                    logs.Add("SDK bloqué après annulation — fermez puis rouvrez le lecteur (CloseDevice / OpenDevice).");
                    break;
                }

                if (rc == 0)
                {
                    if (_algoActive && !isThumbs)
                    {
                        var fingerNum = present.Count;
                        var handSide = new int[1];
                        var edgeRc = Fap60EdgeCheck.CheckEdge(saveEnh, fingerNum, handSide);
                        if (edgeRc != 0)
                        {
                            rc = edgeRc;
                            LogPlacementRetry(logs, edgeRc, isThumbs);
                            Thread.Sleep(retryDelayMs);
                            continue;
                        }

                        var handRc = Fap60EdgeCheck.ValidateHand(captureType, fingerNum, handSide);
                        if (handRc != 0)
                        {
                            rc = handRc;
                            LogPlacementRetry(logs, handRc, isThumbs);
                            Thread.Sleep(retryDelayMs);
                            continue;
                        }
                    }

                    break;
                }

                if (Fap60EdgeCheck.IsRetryablePlacementError(rc))
                {
                    if (rc == CaptureTimeoutError)
                        timeoutAttempts++;
                    if (isThumbs && rc == CaptureTimeoutError)
                    {
                        thumbsTimeoutStreak++;
                        if (thumbsTimeoutStreak >= 2)
                        {
                            logs.Add("Pouces: timeouts répétés — bascule anticipée vers repli single.");
                            break;
                        }
                    }
                    else if (isThumbs)
                    {
                        thumbsTimeoutStreak = 0;
                    }
                    LogPlacementRetry(logs, rc, isThumbs);
                    Thread.Sleep(retryDelayMs);
                    continue;
                }

                CancelCapture();
                logs.Add($"Tentative {attempts} — {Fap60ImageHelper.GetErrorMessage(rc)}");
                Thread.Sleep(retryDelayMs);
            }

            logs.Add($"Durée totale boucle capture : {totalSw.ElapsedMilliseconds} ms");

            if (rc != 0)
            {
                if (isThumbs && allowThumbsFallback)
                {
                    var fallback = CaptureThumbsSinglesFallback(request, logs);
                    if (fallback is not null)
                        return fallback;
                }

                var err = Fap60ImageHelper.GetErrorMessage(rc);
                logs.Add($"Échec capture après {attempts} tentative(s) ({timeoutAttempts} timeout(s)) ({rc}): {err}");
                logs.Add(isThumbs
                    ? "Pouces : posez les DEUX pouces côte à côte au CENTRE du plateau (verticalement, bien à plat)."
                    : "Comme FAP60Demo : posez les 4 doigts AU CENTRE du plateau (pas sur le bord).");
                return new FingerprintCaptureResponse(false, err, Logs: logs);
            }

            logs.Add($"Capture plate OK après {attempts} tentative(s)");

            logs.Add("Capture plate réussie — extraction des doigts…");

            var plateB64 = Fap60ImageHelper.ToPngBase64(saveEnh, Fap60Native.BigWidth, Fap60Native.BigHeight);
            var fingers = Fap60FingerLayout.ExtractSmallImages(captureType, saveSmall, present);

            var previews = new List<FingerPreview>();
            var templates = new List<FingerTemplate>();
            var threshold = Math.Clamp(request.NfiqThreshold, 1, 5);

            if (!_algoActive)
                logs.Add("NFIQ non calculé (licence algorithme absente — mode dégradé)");

            foreach (var (position, gray) in fingers)
            {
                int? nfiq = null;
                string? label = null;
                int quality = 80;
                bool? passes = true;

                if (_algoActive)
                {
                    var score = Fap60ImageHelper.GetNfiq(gray, Fap60Native.SmallWidth, Fap60Native.SmallHeight);
                    nfiq = score;
                    label = Fap60ImageHelper.NfiqLabel(score);
                    quality = Fap60ImageHelper.NfiqToQualityPercent(score);
                    passes = score <= threshold;
                }
                var imgB64 = Fap60ImageHelper.ToPngBase64(gray, Fap60Native.SmallWidth, Fap60Native.SmallHeight);

                previews.Add(new FingerPreview(position, imgB64, "image/png", nfiq, label, quality, passes));
                templates.Add(new FingerTemplate(
                    position,
                    request.TemplateFormat,
                    Convert.ToBase64String(gray),
                    quality,
                    nfiq,
                    label));

                if (nfiq.HasValue)
                    logs.Add($"{position}: NFIQ={nfiq} ({label}) — {(passes == true ? "OK" : "SOUS SEUIL")}");
                else
                    logs.Add($"{position}: image capturée (NFIQ non disponible)");
            }

            var allPass = !_algoActive || previews.All(p => p.PassesNfiq != false);
            var message = allPass
                ? $"Capture {captureType} réussie — {previews.Count} doigt(s)"
                : $"Capture terminée — certains doigts dépassent le seuil NFIQ ({threshold})";

            return new FingerprintCaptureResponse(
                true,
                message,
                templates,
                previews,
                plateB64,
                logs);
        }
        catch (Exception ex)
        {
            return new FingerprintCaptureResponse(false, ex.Message, Logs: new List<string> { ex.ToString() });
        }
    }

    /// <summary>Image live du plateau (captureVideo), pour aperçu avant capture finale.</summary>
    public async Task<FingerprintCaptureResponse> GetPreviewFrameAsync(
        string captureType = "left_four",
        CancellationToken ct = default)
    {
        if (!_open || _deviceHandle == IntPtr.Zero)
            return new FingerprintCaptureResponse(false, "Ouvrez le lecteur d'abord");

        if (_captureInProgress)
            return new FingerprintCaptureResponse(false, "Capture en cours", Logs: ["busy"]);

        if (!await _deviceGate.WaitAsync(0, ct))
            return new FingerprintCaptureResponse(false, "Lecteur occupé", Logs: ["busy"]);

        try
        {
            return await Task.Run(() =>
            {
                Fap60Native.SetDllDirectory(_sdkPath!);
                var buf = new byte[Fap60Native.BigWidth * Fap60Native.BigHeight];
                var typeInt = Fap60FingerLayout.CaptureTypeToInt(captureType);
                var rc = Fap60Native.captureVideo(_deviceHandle, typeInt, buf);
                if (rc == ImageMissingError)
                    return new FingerprintCaptureResponse(false, "Posez les doigts sur le plateau pour l'aperçu");

                if (rc != 0)
                    return new FingerprintCaptureResponse(false, Fap60ImageHelper.GetErrorMessage(rc));

                var plateB64 = Fap60ImageHelper.ToPngBase64(buf, Fap60Native.BigWidth, Fap60Native.BigHeight);
                return new FingerprintCaptureResponse(true, "Aperçu live", PreviewPlateBase64: plateB64);
            }, ct);
        }
        catch (Exception ex)
        {
            return new FingerprintCaptureResponse(false, ex.Message);
        }
        finally
        {
            _deviceGate.Release();
        }
    }

    private int CaptureImageOnceWithWatchdog(
        int captureTypeInt,
        int nMissNum,
        byte[] saveOri,
        byte[] saveEnh,
        byte[] saveSmall,
        int[] captureStatus,
        int sdkTimeoutMs = SdkAttemptTimeoutMs,
        int? sdkWatchdogMs = null)
    {
        var watchdogMs = sdkWatchdogMs ?? sdkTimeoutMs + 3_000;
        var rcBox = new int[1] { -1 };
        var work = Task.Run(() =>
        {
            rcBox[0] = Fap60Native.captureImage_old(
                _deviceHandle,
                captureTypeInt,
                nMissNum,
                sdkTimeoutMs,
                saveOri,
                saveEnh,
                saveSmall,
                captureStatus);
        });

        if (work.Wait(watchdogMs))
            return rcBox[0];

        CancelCapture();
        if (!work.Wait(PostCancelJoinMs))
            return SdkStuckError;

        return work.IsCompletedSuccessfully ? rcBox[0] : CaptureTimeoutError;
    }

    /// <summary>Repli : 2 captures mode single (pouce gauche puis droit) si both_thumbs échoue.</summary>
    private FingerprintCaptureResponse? CaptureThumbsSinglesFallback(
        FingerprintCaptureRequest request,
        List<string> logs)
    {
        logs.Add("Repli pouces : capture single (gauche puis droite), ~7 s max par pouce…");
        var previews = new List<FingerPreview>();
        var templates = new List<FingerTemplate>();
        string? plateB64 = null;

        foreach (var finger in Fap60FingerLayout.GetOrderedFingers("both_thumbs"))
        {
            CancelCapture();
            Thread.Sleep(250);
            WarmUpDevice(4);

            var sub = new FingerprintCaptureRequest(
                CaptureType: "single",
                FingerPosition: finger,
                PresentFingers: new List<string> { finger },
                MissingFingers: 0,
                TimeoutMs: Math.Min(request.TimeoutMs, 7_000),
                TemplateFormat: request.TemplateFormat,
                NfiqThreshold: request.NfiqThreshold);

            var subResult = CaptureCore(sub, allowThumbsFallback: false);
            subResult.Logs?.ForEach(logs.Add);

            if (!subResult.Success)
            {
                logs.Add($"Repli échoué sur {finger} : {subResult.Message}");
                return null;
            }

            if (subResult.Previews is not null)
                previews.AddRange(subResult.Previews);
            if (subResult.Templates is not null)
                templates.AddRange(subResult.Templates);
            plateB64 ??= subResult.PreviewPlateBase64;
        }

        if (previews.Count < 2 && templates.Count < 2)
            return null;

        logs.Add($"Repli pouces OK — {previews.Count} aperçu(s)");
        return new FingerprintCaptureResponse(
            true,
            "Capture both_thumbs réussie (repli single)",
            templates,
            previews,
            plateB64,
            logs);
    }

    private static void LogPlacementRetry(List<string> logs, int code, bool thumbs = false)
    {
        var msg = Fap60ImageHelper.GetErrorMessage(code);
        var hint = code switch
        {
            Fap60EdgeCheck.EdgeFingerError when thumbs =>
                "Pouces trop en bord — placez les deux pouces au CENTRE du plateau.",
            Fap60EdgeCheck.EdgeFingerError =>
                "Doigts en bord du capteur — avancez la main vers le CENTRE du plateau, doigts bien à plat.",
            Fap60EdgeCheck.WrongLeftHandError => "Main gauche attendue — placez bien la main gauche.",
            Fap60EdgeCheck.WrongRightHandError => "Main droite attendue — placez bien la main droite.",
            CaptureTimeoutError when thumbs =>
                "Timeout pouces — maintenez les deux pouces immobiles au centre (~10 s).",
            CaptureTimeoutError => "Timeout — maintenez les doigts au centre du plateau.",
            _ => msg,
        };
        logs.Add($"Reprise capture : {hint}");
    }

    private void WarmUpDevice(int captureType)
    {
        try
        {
            var buf = new byte[Fap60Native.BigWidth * Fap60Native.BigHeight];
            Fap60Native.captureVideo(_deviceHandle, captureType, buf);
        }
        catch
        {
            /* warm-up best-effort */
        }
    }

    private void CancelCapture()
    {
        if (_deviceHandle != IntPtr.Zero)
            try { Fap60Native.mxCancleCapture(_deviceHandle); } catch { /* ignore */ }
        try { Fap60Native.cancleCapture(); } catch { /* ignore */ }
    }

    private static string? ReadSerial(IntPtr handle)
    {
        var sn = new byte[64];
        return Fap60Native.getDeviceSN(handle, sn) == 0 ? Fap60ImageHelper.TrimCString(sn) : null;
    }

    private static string? ReadFirmware(IntPtr handle)
    {
        var info = new byte[128];
        return Fap60Native.getFirmwareVersion(handle, info) == 0 ? Fap60ImageHelper.TrimCString(info) : null;
    }
}
