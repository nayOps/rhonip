using System.Net.Http.Json;
using System.Text.Json;
using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

/// <summary>Proxy HTTP vers le sidecar x86 Fgp.CameraGp.Bridge (OCX COM).</summary>
public sealed class CameraGpProxyModule : ICameraModule
{
    private readonly HttpClient _http;
    private readonly string _sidecarUrl;

    public CameraGpProxyModule(HttpClient http, CameraGpOptions options)
    {
        _http = http;
        _sidecarUrl = (options.SidecarUrl ?? "http://127.0.0.1:8766").TrimEnd('/');
        _http.BaseAddress = new Uri(_sidecarUrl + "/");
        _http.Timeout = TimeSpan.FromSeconds(60);
    }

    public string ModuleName => "camera";

    public ModuleHealth GetHealth()
    {
        try
        {
            var resp = _http.GetAsync("health").GetAwaiter().GetResult();
            if (!resp.IsSuccessStatusCode)
                return new("degraded", $"Sidecar injoignable ({_sidecarUrl})", "gpy-com");

            var json = resp.Content.ReadFromJsonAsync<JsonElement>().GetAwaiter().GetResult();
            var status = json.TryGetProperty("status", out var s) ? s.GetString() : "unknown";
            var msg = json.TryGetProperty("message", out var m) ? m.GetString() : null;
            return new(status ?? "unknown", msg ?? "CameraGP COM", "gpy-com");
        }
        catch (Exception ex)
        {
            return new("down", $"Sidecar x86 absent — {ex.Message}", "gpy-com");
        }
    }

    public async Task<CameraStatusResponse> GetStatusAsync(CancellationToken ct = default)
    {
        try
        {
            var health = await _http.GetFromJsonAsync<JsonElement>("health", ct);
            var status = health.TryGetProperty("status", out var s) ? s.GetString() : "unknown";
            var count = health.TryGetProperty("device_count", out var c) && c.TryGetInt32(out var n) ? n : (int?)null;
            var msg = health.TryGetProperty("message", out var m) ? m.GetString() ?? "" : "";
            var available = status is "ok" or "healthy";
            return new(available, "gpy-com", msg, count);
        }
        catch (Exception ex)
        {
            return new(false, "gpy-com", $"Sidecar CameraGP non démarré ({_sidecarUrl}): {ex.Message}");
        }
    }

    public async Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default)
    {
        var raw = await PostJsonAsync("/api/v1/devices/camera/open", null, ct);
        return ToDeviceOp(raw);
    }

    public async Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default)
    {
        var raw = await PostJsonAsync("/api/v1/devices/camera/close", null, ct);
        return ToDeviceOp(raw);
    }

    public async Task<CameraPreviewResponse> GetPreviewAsync(CancellationToken ct = default)
    {
        try
        {
            var raw = await _http.GetFromJsonAsync<JsonElement>("api/v1/devices/camera/preview", ct);
            var b64 = GetStr(raw, "image_base64", "imageBase64");
            var ok = raw.TryGetProperty("success", out var s) && s.GetBoolean();
            var msg = GetStr(raw, "message", "Message") ?? (ok ? "OK" : "Pas de frame");
            return new(ok && !string.IsNullOrEmpty(b64), msg, b64);
        }
        catch (Exception ex)
        {
            return new(false, ex.Message);
        }
    }

    public async Task<CameraCaptureResponse> CaptureAsync(bool useFaceDetection = true, CancellationToken ct = default)
    {
        var raw = await PostJsonAsync("/api/v1/devices/camera/capture", null, ct);
        var success = raw.TryGetProperty("success", out var s) && s.GetBoolean();
        var msg = GetStr(raw, "message", "Message") ?? "Capture";
        var b64 = GetStr(raw, "image_base64", "imageBase64");
        var face = raw.TryGetProperty("face_detected", out var f) && f.GetBoolean();
        return new(success, msg, b64, FaceDetected: face);
    }

    public async Task<CameraCaptureResponse> CaptureDocumentAsync(bool autoCut = true, CancellationToken ct = default)
    {
        var raw = await PostJsonAsync("/api/v1/devices/camera/capture-document", new { auto_cut = autoCut }, ct);
        var success = raw.TryGetProperty("success", out var s) && s.GetBoolean();
        var msg = GetStr(raw, "message", "Message") ?? "Scan document";
        var b64 = GetStr(raw, "image_base64", "imageBase64");
        return new(success, msg, b64, FaceDetected: false);
    }

    private async Task<JsonElement> PostJsonAsync(string path, object? body, CancellationToken ct)
    {
        using var resp = await _http.PostAsJsonAsync(path.TrimStart('/'), body ?? new { }, ct);
        var json = await resp.Content.ReadFromJsonAsync<JsonElement>(ct);
        if (!resp.IsSuccessStatusCode && json.ValueKind == JsonValueKind.Undefined)
            throw new HttpRequestException($"Sidecar {path} HTTP {(int)resp.StatusCode}");
        return json;
    }

    private static DeviceOperationResponse ToDeviceOp(JsonElement raw)
    {
        var ok = raw.TryGetProperty("success", out var s) && s.GetBoolean();
        var msg = GetStr(raw, "message", "Message") ?? (ok ? "OK" : "Erreur");
        return new(ok, msg);
    }

    private static string? GetStr(JsonElement el, params string[] names)
    {
        foreach (var n in names)
        {
            if (el.TryGetProperty(n, out var p) && p.ValueKind == JsonValueKind.String)
                return p.GetString();
        }
        return null;
    }
}
