using System.Text;
using System.Text.Json;
using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules.Iris;

/// <summary>Proxy HTTP vers Iris Device Server (port 50218 par défaut).</summary>
public sealed class IrisDeviceModule : IIrisModule
{
    private readonly HttpClient _http;
    private readonly IrisDeviceOptions _options;
    private Uri _baseUri;

    public IrisDeviceModule(HttpClient http, IrisDeviceOptions options)
    {
        _http = http;
        _options = options;
        var port = options.ReadServerPortFromConfig();
        _baseUri = new Uri($"http://127.0.0.1:{port}/");
        _http.Timeout = TimeSpan.FromSeconds(Math.Max(90, options.DefaultTimeoutSeconds + 60));
    }

    private Uri ResolveUri(string relativePath)
    {
        var path = relativePath.TrimStart('/');
        return new Uri(_baseUri, path);
    }

    private async Task<(bool HttpOk, int Port)> EnsureHttpAsync(CancellationToken ct)
    {
        var resolved = await IrisDeviceHttpProbe.ResolveBaseUrlAsync(_options.BaseUrl, ct);
        if (resolved is null)
            return (false, _options.ReadServerPortFromConfig());

        _baseUri = new Uri(resolved.TrimEnd('/') + "/");
        var (host, port) = ParseEndpoint(_baseUri);
        var (httpOk, _) = await IrisDeviceHttpProbe.TryStatusAsync(host, port, ct);
        return (httpOk, port);
    }

    private static string HttpDownMessage(int port) =>
        $"IrisDeviceServer arrêté — aucun HTTP sur 50218/50219 (config: {port}). " +
        "POST /api/v1/devices/iris/start-server, ou lancez iris\\bin\\IrisDeviceServer.exe + 启用HTTP服务.bat (admin).";

    public string ModuleName => "iris";

    private (string Host, int Port) Endpoint => ParseEndpoint(_baseUri);

    public ModuleHealth GetHealth()
    {
        var port = _options.ReadServerPortFromConfig();
        if (!IrisServerStarter.IsHttpAvailableAsync(_options).GetAwaiter().GetResult())
            return new("down", HttpDownMessage(port), "device");

        try
        {
            var st = GetStatusAsync(CancellationToken.None).GetAwaiter().GetResult();
            if (st.Available)
                return new("ok", st.Message, "device");

            var httpNote = st.ServerPort.HasValue
                ? $"HTTP actif (port {st.ServerPort}) — "
                : "HTTP actif — ";
            return new("degraded", $"{httpNote}{st.Message}", "device");
        }
        catch
        {
            return new(
                "degraded",
                $"Iris HTTP (ports {string.Join("/", IrisDeviceHttpProbe.DefaultPorts)}) — statut lecteur non lu",
                "device");
        }
    }

    public async Task<IrisStatusResponse> GetStatusAsync(CancellationToken ct = default)
    {
        var (httpOk, port) = await EnsureHttpAsync(ct);
        if (!httpOk)
            return new(false, "device", HttpDownMessage(port), port);

        try
        {
            var model = await PostDeviceAsync("Model", "{}", ct);
            var status = await PostDeviceAsync("Status", "{}", ct);
            ParseDevicePayload(model.Raw, out var deviceModel, out _, out var modelErr);
            ParseDevicePayload(status.Raw, out _, out var deviceStatus, out var statusErr);
            var errcode = modelErr ?? statusErr;

            // Ne pas appeler Open ici : chaque sonde déclenchait bip/LED sans garantir DEV_OPENED.
            var ready = deviceStatus is 2 or 3;
            if (!ready && string.IsNullOrWhiteSpace(deviceModel))
            {
                var wake = await WakeDeviceAsync(ct);
                if (wake.Success)
                {
                    model = await PostDeviceAsync("Model", "{}", ct);
                    status = await PostDeviceAsync("Status", "{}", ct);
                    ParseDevicePayload(model.Raw, out deviceModel, out _, out modelErr);
                    ParseDevicePayload(status.Raw, out _, out deviceStatus, out statusErr);
                    ready = deviceStatus is 2 or 3 || !string.IsNullOrWhiteSpace(deviceModel);
                }
            }

            if (!ready && string.IsNullOrWhiteSpace(deviceModel))
            {
                return new(
                    false,
                    "device",
                    "HTTP actif — JD5 non prêt. Fermez DeviceUI, start-iris-server-admin.bat (UAC), puis Ouvrir lecteur.",
                    port,
                    deviceModel,
                    deviceStatus ?? 1,
                    errcode);
            }

            if (!ready && deviceStatus == 1)
            {
                return new(
                    false,
                    "device",
                    string.IsNullOrWhiteSpace(deviceModel)
                        ? "Lecteur JD5 non détecté — USB + serveur admin."
                        : $"Iris {deviceModel.Trim()} — fermé, cliquez Ouvrir lecteur.",
                    port,
                    deviceModel,
                    deviceStatus,
                    errcode);
            }

            ready = deviceStatus is 2 or 3 || !string.IsNullOrWhiteSpace(deviceModel);
            var msg = status.Success
                ? BuildStatusMessage(deviceModel, deviceStatus, _baseUri.ToString())
                : status.Message;
            return new(ready, "device", msg, port, deviceModel, deviceStatus, errcode);
        }
        catch (Exception ex)
        {
            return new(false, "device", ex.Message, port);
        }
    }

    public async Task<IrisPreviewResponse> GetLivePreviewAsync(CancellationToken ct = default)
    {
        var w = _options.PreviewWidth;
        var h = _options.PreviewHeight;
        var left = await FetchImageBase64Async($"image/living/left.bmp?width={w}&height={h}", ct);
        var right = await FetchImageBase64Async($"image/living/right.bmp?width={w}&height={h}", ct);
        var ok = !string.IsNullOrEmpty(left) || !string.IsNullOrEmpty(right);
        return new(ok, ok ? "Preview live" : "Pas de frame live — démarrer une capture", left, right);
    }

    public async Task<IrisCaptureResponse> CaptureAsync(IrisCaptureRequest request, CancellationToken ct = default)
    {
        var prep = await EnsureDeviceReadyForCaptureAsync(ct);
        if (!prep.Success)
            return new(false, prep.Message, RawResponse: prep.Raw);

        var eyeCode = MapEye(request.Eye);
        var body = JsonSerializer.Serialize(new
        {
            mode = 1,
            eye = eyeCode,
            timeout_seconds = request.TimeoutSeconds > 0 ? request.TimeoutSeconds : _options.DefaultTimeoutSeconds,
            exposure = 0,
            quality = request.Quality > 0 ? request.Quality : _options.DefaultQuality,
            fake_eye_enable = 0,
            lens_eye_enable = 0,
        });

        var capture = await PostDeviceAsync("Capture", body, ct);
        if (!capture.Success)
            return new(false, capture.Message, RawResponse: capture.Raw);

        var eyes = new List<IrisEyeResult>();
        var w = _options.PreviewWidth;
        var h = _options.PreviewHeight;

        if (eyeCode is 1 or 3)
        {
            var img = await FetchImageBase64Async($"image/captured/right.bmp?width={w}&height={h}", ct);
            eyes.Add(new("right", !string.IsNullOrEmpty(img), img, "image/bmp",
                ExtractQuality(capture.Raw, "right"), string.IsNullOrEmpty(img) ? "Image œil droit absente" : null));
        }

        if (eyeCode is 2 or 3)
        {
            var img = await FetchImageBase64Async($"image/captured/left.bmp?width={w}&height={h}", ct);
            eyes.Add(new("left", !string.IsNullOrEmpty(img), img, "image/bmp",
                ExtractQuality(capture.Raw, "left"), string.IsNullOrEmpty(img) ? "Image œil gauche absente" : null));
        }

        var success = eyes.Count > 0 && eyes.All(e => e.Success);
        return new(success,
            success ? "Capture iris terminée" : "Capture terminée mais image(s) manquante(s)",
            eyes,
            capture.Raw);
    }

    public async Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default)
    {
        var (httpOk, port) = await EnsureHttpAsync(ct);
        if (!httpOk)
            return new(false, HttpDownMessage(port));

        var wake = await WakeDeviceAsync(ct);
        if (!wake.Success)
            return new(false, wake.Message);

        return new(true, wake.Message);
    }

    public async Task<DeviceOperationResponse> StopAsync(CancellationToken ct = default)
    {
        var r = await PostDeviceAsync("Stop", "", ct);
        return new(r.Success, r.Message);
    }

    public async Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default)
    {
        var r = await PostDeviceAsync("Close", "{}", ct);
        return new(r.Success, r.Message);
    }

    private async Task<(bool Success, string Message, string? Raw)> PostDeviceAsync(
        string path,
        string jsonBody,
        CancellationToken ct)
    {
        try
        {
            using var content = new StringContent(jsonBody ?? "", Encoding.UTF8, "text/plain");
            var resp = await _http.PostAsync(ResolveUri($"device/{path}"), content, ct);
            var text = await resp.Content.ReadAsStringAsync(ct);
            if (!resp.IsSuccessStatusCode)
                return (false, $"HTTP {(int)resp.StatusCode}: {text}", text);

            if (TryParseError(text, out var err))
                return (false, err, text);

            return (true, "OK", text);
        }
        catch (HttpRequestException ex)
        {
            return (false,
                $"Connexion HTTP iris échouée ({_baseUri}) — port 50219 actif ? Réponse vide sur 50218. {ex.Message}",
                null);
        }
        catch (Exception ex)
        {
            return (false, ex.Message, null);
        }
    }

    private async Task<string?> FetchImageBase64Async(string relativePath, CancellationToken ct)
    {
        try
        {
            var bytes = await _http.GetByteArrayAsync(ResolveUri(relativePath), ct);
            return bytes.Length > 0 ? Convert.ToBase64String(bytes) : null;
        }
        catch
        {
            return null;
        }
    }

    private static int MapEye(string? eye) => (eye ?? "both").Trim().ToLowerInvariant() switch
    {
        "right" => 1,
        "left" => 2,
        "both" => 3,
        _ => 3,
    };

    private async Task<(bool Success, string Message, string? Raw)> EnsureDeviceReadyForCaptureAsync(CancellationToken ct)
    {
        await PostDeviceAsync("Stop", "", ct);

        var model = await PostDeviceAsync("Model", "{}", ct);
        ParseDevicePayload(model.Raw, out var deviceModel, out _, out var modelErr);
        if (modelErr is > 0)
            return (false, IrisErrorCatalog.Describe(modelErr), model.Raw);

        if (string.IsNullOrWhiteSpace(deviceModel))
        {
            return (false,
                "Aucun lecteur iris détecté (model vide) — branchez le JD5 USB, un seul IrisDeviceServer.exe, puis Ouvrir lecteur.",
                model.Raw);
        }

        var status = await PostDeviceAsync("Status", "{}", ct);
        ParseDevicePayload(status.Raw, out _, out var deviceStatus, out var statusErr);
        if (statusErr is > 0)
            return (false, IrisErrorCatalog.Describe(statusErr), status.Raw);

        if (deviceStatus == 3)
        {
            await PostDeviceAsync("Stop", "", ct);
            deviceStatus = 2;
        }

        if (deviceStatus == 1)
        {
            var wake = await WakeDeviceAsync(ct);
            if (!wake.Success)
                return (false, wake.Message, status.Raw);

            status = await PostDeviceAsync("Status", "{}", ct);
            ParseDevicePayload(status.Raw, out _, out deviceStatus, out statusErr);
            model = await PostDeviceAsync("Model", "{}", ct);
            ParseDevicePayload(model.Raw, out deviceModel, out _, out _);
            if (statusErr is > 0)
                return (false, IrisErrorCatalog.Describe(statusErr), status.Raw);
            if (deviceStatus == 1 && string.IsNullOrWhiteSpace(deviceModel))
            {
                return (false,
                    $"Lecteur toujours fermé ({IrisErrorCatalog.StatusLabel(1)}) — {IrisErrorCatalog.Describe(IrisErrorCatalog.ErrDeviceClosedCapture)}",
                    status.Raw);
            }
        }

        return (true, $"Prêt — {deviceModel ?? "JD5"}", status.Raw);
    }

    /// <summary>
    /// Pas d'API device/Open (参数错误). Comme device_server.html : lancer Capture puis flux live.
    /// </summary>
    private async Task<(bool Success, string Message)> WakeDeviceAsync(CancellationToken ct)
    {
        await PostDeviceAsync("Stop", "", ct);
        await PostDeviceAsync("OperationMode", "{\"mode\":1}", ct);

        var (ready, model, status, msg) = await ReadDeviceStateAsync(ct);
        if (ready)
            return (true, msg);

        _ = TriggerCaptureSessionAsync(ct);

        var w = _options.PreviewWidth;
        var h = _options.PreviewHeight;
        var deadline = DateTime.UtcNow.AddSeconds(20);
        while (DateTime.UtcNow < deadline && !ct.IsCancellationRequested)
        {
            await Task.Delay(400, ct);
            var left = await FetchImageBase64Async($"image/living/left.bmp?width={w}&height={h}", ct);
            var right = await FetchImageBase64Async($"image/living/right.bmp?width={w}&height={h}", ct);
            if (!string.IsNullOrEmpty(left) || !string.IsNullOrEmpty(right))
            {
                (ready, model, status, msg) = await ReadDeviceStateAsync(ct);
                var label = string.IsNullOrWhiteSpace(model) ? "JD5" : model.Trim();
                return (true, $"Lecteur actif — {label} (aperçu live, placez les yeux devant le capteur)");
            }

            (ready, model, _, msg) = await ReadDeviceStateAsync(ct);
            if (ready)
                return (true, msg);
        }

        await PostDeviceAsync("Stop", "", ct);

        if (!string.IsNullOrWhiteSpace(model))
            return (false, $"Iris {model.Trim()} détecté — placez-vous devant le lecteur puis réessayez Ouvrir lecteur.");

        return (false,
            "JD5 non actif — fermez DeviceUI, lancez start-iris-server-admin-console.bat (fenêtre admin), " +
            "branchez le USB, puis Ouvrir lecteur (le bip/LED = essai d’ouverture).");
    }

    private async Task<(bool Ready, string? Model, int? Status, string Message)> ReadDeviceStateAsync(CancellationToken ct)
    {
        var modelResp = await PostDeviceAsync("Model", "{}", ct);
        ParseDevicePayload(modelResp.Raw, out var deviceModel, out _, out var modelErr);
        if (modelErr is > 0)
            return (false, deviceModel, null, IrisErrorCatalog.Describe(modelErr));

        var statusResp = await PostDeviceAsync("Status", "{}", ct);
        ParseDevicePayload(statusResp.Raw, out _, out var deviceStatus, out var statusErr);
        if (statusErr is > 0)
            return (false, deviceModel, deviceStatus, IrisErrorCatalog.Describe(statusErr));

        if (deviceStatus is 2 or 3)
        {
            var label = string.IsNullOrWhiteSpace(deviceModel) ? "JD5" : deviceModel.Trim();
            return (true, deviceModel, deviceStatus,
                $"Lecteur prêt — {label} ({IrisErrorCatalog.StatusLabel(deviceStatus.Value)})");
        }

        if (!string.IsNullOrWhiteSpace(deviceModel))
        {
            return (false, deviceModel, deviceStatus,
                $"Iris {deviceModel.Trim()} — {IrisErrorCatalog.StatusLabel(deviceStatus ?? 1)}");
        }

        return (false, deviceModel, deviceStatus, "model vide");
    }

    private Task TriggerCaptureSessionAsync(CancellationToken ct)
    {
        var body = JsonSerializer.Serialize(new
        {
            mode = 1,
            eye = 3,
            timeout_seconds = Math.Clamp(_options.DefaultTimeoutSeconds, 8, 30),
            exposure = 0,
            quality = _options.DefaultQuality,
            fake_eye_enable = 0,
            lens_eye_enable = 0,
        });

        return Task.Run(async () =>
        {
            try
            {
                using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                cts.CancelAfter(TimeSpan.FromSeconds(3));
                await PostDeviceAsync("Capture", body, cts.Token);
            }
            catch
            {
                /* le serveur peut continuer la capture après timeout client */
            }
        }, ct);
    }

    private static string BuildStatusMessage(string? model, int? status, string baseUri)
    {
        if (string.IsNullOrWhiteSpace(model))
            return $"Serveur HTTP actif ({baseUri}) mais aucun lecteur iris détecté (model vide) — JD5 attendu.";

        var st = status.HasValue ? IrisErrorCatalog.StatusLabel(status.Value) : "inconnu";
        return string.IsNullOrWhiteSpace(model)
            ? $"Iris ({baseUri})"
            : $"Iris {model.Trim()} — {st}";
    }

    private static void ParseDevicePayload(string? raw, out string? model, out int? status, out int? errcode)
    {
        model = null;
        status = null;
        errcode = null;
        if (string.IsNullOrWhiteSpace(raw)) return;

        try
        {
            using var doc = JsonDocument.Parse(raw);
            var root = doc.RootElement;
            if (root.TryGetProperty("model", out var m) && m.ValueKind == JsonValueKind.String)
                model = m.GetString();
            if (root.TryGetProperty("status", out var s) && s.TryGetInt32(out var sv))
                status = sv;
            if (root.TryGetProperty("errcode", out var e) && e.TryGetInt32(out var ev))
                errcode = ev;
        }
        catch
        {
            /* ignore */
        }
    }

    private static bool TryParseError(string text, out string message)
    {
        message = "";
        if (string.IsNullOrWhiteSpace(text)) return false;
        try
        {
            using var doc = JsonDocument.Parse(text);
            var root = doc.RootElement;
            if (root.TryGetProperty("errcode", out var ec) && ec.TryGetInt32(out var errcode) && errcode != 0)
            {
                var vendor = ExtractVendorMessage(root);
                message = IrisErrorCatalog.Describe(errcode, vendor);
                return true;
            }

            foreach (var key in new[] { "result", "error", "code" })
            {
                if (!root.TryGetProperty(key, out var prop) || prop.ValueKind != JsonValueKind.Number)
                    continue;
                var code = prop.GetInt32();
                if (code == 0)
                    return false;
                message = IrisErrorCatalog.Describe(code, ExtractVendorMessage(root));
                return true;
            }
        }
        catch
        {
            /* réponse non-JSON */
        }

        return false;
    }

    private static string? ExtractVendorMessage(JsonElement root)
    {
        foreach (var key in new[] { "message", "errmsg", "error_msg" })
        {
            if (!root.TryGetProperty(key, out var m) || m.ValueKind != JsonValueKind.String)
                continue;
            var s = m.GetString();
            if (string.IsNullOrWhiteSpace(s) || s.Any(c => c == '\uFFFD'))
                continue;
            return s;
        }

        return null;
    }

    private static int? ExtractQuality(string? raw, string side)
    {
        if (string.IsNullOrWhiteSpace(raw)) return null;
        try
        {
            using var doc = JsonDocument.Parse(raw);
            var root = doc.RootElement;
            foreach (var key in new[] { $"{side}_quality", $"{side}Quality", "quality" })
            {
                if (root.TryGetProperty(key, out var q) && q.TryGetInt32(out var v))
                    return Math.Clamp(v, 0, 100);
            }
        }
        catch { /* ignore */ }

        return null;
    }

    private static (string Host, int Port) ParseEndpoint(Uri uri)
    {
        var port = uri.Port;
        if (uri.IsDefaultPort)
            port = uri.Scheme.Equals("https", StringComparison.OrdinalIgnoreCase) ? 443 : 80;
        return (uri.Host, port);
    }

}
