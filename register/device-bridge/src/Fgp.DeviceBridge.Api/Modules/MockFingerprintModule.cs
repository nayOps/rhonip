using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public sealed class MockFingerprintModule : IFingerprintModule
{
    private bool _open;

    public string ModuleName => "fingerprint";

    public ModuleHealth GetHealth() => new(
        Status: "ok",
        Message: "Mode simulation (mock)",
        Mode: "mock");

    public Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default)
    {
        _open = true;
        return Task.FromResult(new DeviceOperationResponse(true, "Mock fingerprint device opened", 0));
    }

    public Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default)
    {
        _open = false;
        return Task.FromResult(new DeviceOperationResponse(true, "Mock fingerprint device closed"));
    }

    public async Task<FingerprintCaptureResponse> CaptureAsync(
        FingerprintCaptureRequest request,
        CancellationToken ct = default)
    {
        if (!_open)
            return new FingerprintCaptureResponse(false, "Device not open. Call /open first.");

        await Task.Delay(800, ct);

        var positions = request.PresentFingers?.Count > 0
            ? request.PresentFingers.Select(p => p.ToLowerInvariant()).ToArray()
            : (!string.IsNullOrWhiteSpace(request.FingerPosition)
                ? new[] { request.FingerPosition.Trim().ToLowerInvariant() }
                : request.CaptureType switch
                {
                    "right_four" => new[] { "right_index", "right_middle", "right_ring", "right_little" },
                    "both_thumbs" => new[] { "left_thumb", "right_thumb" },
                    "single" => new[] { "right_index" },
                    _ => new[] { "left_index", "left_middle", "left_ring", "left_little" },
                });

        var threshold = Math.Clamp(request.NfiqThreshold, 1, 5);
        var templates = new List<FingerTemplate>();
        var previews = new List<FingerPreview>();
        var logs = new List<string> { $"[MOCK] Capture {request.CaptureType}, seuil NFIQ {threshold}" };

        foreach (var p in positions)
        {
            var nfiq = 2;
            var label = "Très bonne (2)";
            var quality = 80;
            templates.Add(new FingerTemplate(p, request.TemplateFormat, Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes($"MOCK-{p}")), quality, nfiq, label));
            previews.Add(new FingerPreview(p, MinimalPngBase64(), "image/png", nfiq, label, quality, nfiq <= threshold));
            logs.Add($"{p}: NFIQ={nfiq} (mock)");
        }

        return new FingerprintCaptureResponse(
            true,
            $"Mock capture ({request.CaptureType}) — {positions.Length} doigt(s)",
            templates,
            previews,
            MinimalPngBase64(),
            logs);
    }

    private static string MinimalPngBase64()
    {
        // 1x1 transparent PNG
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
    }
}
