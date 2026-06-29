using System.Text.Json;
using Fgp.CameraGp.Bridge.Camera;

file sealed class CaptureDocumentRequest
{
    public bool AutoCut { get; set; } = true;
}

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureHttpJsonOptions(o =>
{
    o.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
    o.SerializerOptions.PropertyNameCaseInsensitive = true;
});

builder.Services.AddSingleton<CameraGpOcxHost>();
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod()));

var app = builder.Build();
app.UseCors();

var preferredW = app.Configuration.GetValue("Camera:PreferredWidth", 1920);
var preferredH = app.Configuration.GetValue("Camera:PreferredHeight", 1080);
var captureTimeoutMs = app.Configuration.GetValue("Camera:CaptureTimeoutMs", 30_000);

app.MapGet("/health", async (CameraGpOcxHost host, CancellationToken ct) =>
{
    try
    {
        var count = await host.InvokeAsync(f => f.DeviceCount, ct);
        var status = count > 0 ? "ok" : "degraded";
        return Results.Ok(new
        {
            status,
            version = "0.1.0",
            mode = "camera-gp-com",
            device_count = count,
            message = count > 0 ? $"{count} caméra(s) détectée(s)" : "Aucune caméra — branchez l'appareil GPY",
        });
    }
    catch (Exception ex)
    {
        return Results.Ok(new { status = "down", message = ex.Message, mode = "camera-gp-com" });
    }
});

app.MapGet("/api/v1/devices/camera/devices", async (CameraGpOcxHost host, CancellationToken ct) =>
{
    var devices = await host.InvokeAsync(f => f.ListDevices(), ct);
    return Results.Ok(new
    {
        devices = devices.Select(d => new { id = d.Id, name = d.Name }).ToList(),
    });
});

app.MapPost("/api/v1/devices/camera/open", async (CameraGpOcxHost host, CancellationToken ct) =>
{
    var result = await host.InvokeAsync(f => f.Open(preferredW, preferredH), ct);
    return result.Success
        ? Results.Ok(new { success = true, message = result.Message })
        : Results.BadRequest(new { success = false, message = result.Message });
});

app.MapPost("/api/v1/devices/camera/close", async (CameraGpOcxHost host, CancellationToken ct) =>
{
    await host.InvokeAsync(f =>
    {
        f.CloseCamera();
        return true;
    }, ct);
    return Results.Ok(new { success = true, message = "Caméra fermée" });
});

app.MapGet("/api/v1/devices/camera/preview", async (CameraGpOcxHost host, CancellationToken ct) =>
{
    var b64 = await host.InvokeAsync(f => f.GetPreviewJpegBase64(), ct);
    if (string.IsNullOrEmpty(b64))
        return Results.Ok(new { success = false, message = "Pas de frame", image_base64 = (string?)null });
    return Results.Ok(new { success = true, message = "OK", image_base64 = b64, mime = "image/jpeg" });
});

app.MapPost("/api/v1/devices/camera/capture-document", async (
    CameraGpOcxHost host,
    CaptureDocumentRequest? body,
    CancellationToken ct) =>
{
    var autoCut = body?.AutoCut ?? true;
    var (ok, msg, b64) = await host.InvokeAsync(form =>
    {
        if (!form.IsOpen)
        {
            var opened = form.Open(preferredW, preferredH);
            if (!opened.Success)
                return (false, opened.Message, (string?)null);
        }

        return form.CaptureImageAsync(autoCut, captureTimeoutMs, ct).GetAwaiter().GetResult();
    }, ct);
    if (!ok || string.IsNullOrEmpty(b64))
        return Results.BadRequest(new { success = false, message = msg, image_base64 = (string?)null });

    return Results.Ok(new
    {
        success = true,
        message = msg,
        image_base64 = b64,
        mime = "image/jpeg",
        auto_cut = autoCut,
    });
});

app.MapPost("/api/v1/devices/camera/capture", async (CameraGpOcxHost host, CancellationToken ct) =>
{
    var (ok, msg, b64) = await host.InvokeAsync(form =>
    {
        if (!form.IsOpen)
        {
            var opened = form.Open(preferredW, preferredH);
            if (!opened.Success)
                return (false, opened.Message, (string?)null);
        }

        return form.CaptureFaceAsync(captureTimeoutMs, ct).GetAwaiter().GetResult();
    }, ct);
    if (!ok || string.IsNullOrEmpty(b64))
        return Results.BadRequest(new { success = false, message = msg, image_base64 = (string?)null });

    return Results.Ok(new
    {
        success = true,
        message = msg,
        image_base64 = b64,
        mime = "image/jpeg",
        face_detected = true,
    });
});

app.Lifetime.ApplicationStopping.Register(() =>
{
    var host = app.Services.GetService<CameraGpOcxHost>();
    host?.Dispose();
});

app.Run();
