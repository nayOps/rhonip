using System.Net.Http.Json;
using System.Text.Json;
using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public sealed class PosPrinterProxyModule : IPrinterModule
{
    private readonly HttpClient _http;
    private readonly PosPrinterOptions _options;

    public PosPrinterProxyModule(HttpClient http, PosPrinterOptions options)
    {
        _http = http;
        _options = options;
        _http.BaseAddress = new Uri((_options.SidecarUrl ?? "http://127.0.0.1:8767").TrimEnd('/') + "/");
        _http.Timeout = TimeSpan.FromSeconds(60);
    }

    public string ModuleName => "print";

    public ModuleHealth GetHealth()
    {
        try
        {
            var resp = _http.GetAsync("health").GetAwaiter().GetResult();
            if (!resp.IsSuccessStatusCode)
                return new("down", $"Sidecar POS injoignable ({_options.SidecarUrl})", "pos-sdk");

            var json = resp.Content.ReadFromJsonAsync<JsonElement>().GetAwaiter().GetResult();
            var status = json.TryGetProperty("status", out var s) ? s.GetString() : "unknown";
            var msg = json.TryGetProperty("message", out var m) ? m.GetString() : "POS SDK";
            return new(status ?? "unknown", msg ?? "POS", "pos-sdk");
        }
        catch (Exception ex)
        {
            return new("down", $"Sidecar POS absent — {ex.Message}", "pos-sdk");
        }
    }

    public async Task<PrinterStatusResponse> GetStatusAsync(CancellationToken ct = default)
    {
        try
        {
            var health = await _http.GetFromJsonAsync<JsonElement>("health", ct);
            var ok = health.TryGetProperty("status", out var s) && s.GetString() is "ok" or "healthy";
            var msg = health.TryGetProperty("message", out var m) ? m.GetString() ?? "" : "";
            var open = health.TryGetProperty("printer_open", out var o) && o.GetBoolean();

            if (!ok)
                return new PrinterStatusResponse(false, "pos-sdk", msg, open);

            var st = await _http.GetFromJsonAsync<JsonElement>("api/v1/devices/printer/status", ct);
            var stMsg = GetStr(st, "message", "Message") ?? msg;
            var code = st.TryGetProperty("status_code", out var c) && c.TryGetInt32(out var n) ? n : (int?)null;
            var isOpen = st.TryGetProperty("open", out var op) && op.GetBoolean();
            return new PrinterStatusResponse(true, "pos-sdk", stMsg, isOpen || open, code);
        }
        catch (Exception ex)
        {
            return new PrinterStatusResponse(false, "pos-sdk", ex.Message);
        }
    }

    public async Task<PrinterOperationResponse> OpenAsync(PrinterOpenRequest? request, CancellationToken ct = default)
    {
        var body = request ?? new PrinterOpenRequest(_options.Connection, _options.PortType);
        var raw = await PostJsonAsync("api/v1/devices/printer/open", body, ct);
        return ToOp(raw);
    }

    public async Task<PrinterOperationResponse> CloseAsync(CancellationToken ct = default)
    {
        var raw = await PostJsonAsync("api/v1/devices/printer/close", new { }, ct);
        return ToOp(raw);
    }

    public async Task<PrinterOperationResponse> PrintReceiptAsync(PrintReceiptRequest request, CancellationToken ct = default)
    {
        request = request with
        {
            Connection = request.Connection ?? _options.Connection,
            PortType = request.PortType ?? _options.PortType,
        };
        var raw = await PostJsonAsync("api/v1/devices/printer/print-receipt", request, ct);
        return ToOp(raw);
    }

    public async Task<PrinterOperationResponse> PrintTestAsync(CancellationToken ct = default)
    {
        var raw = await PostJsonAsync("api/v1/devices/printer/test", new { }, ct);
        return ToOp(raw);
    }

    private async Task<JsonElement> PostJsonAsync(string path, object body, CancellationToken ct)
    {
        using var resp = await _http.PostAsJsonAsync(path.TrimStart('/'), body, ct);
        return await resp.Content.ReadFromJsonAsync<JsonElement>(ct);
    }

    private static PrinterOperationResponse ToOp(JsonElement raw)
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
