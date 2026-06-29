using System.Text.Json;
using Fgp.DeviceBridge.Api.Hosting;
using Fgp.DeviceBridge.Api.Models;
using Fgp.DeviceBridge.Api.Modules;
using Fgp.DeviceBridge.Api.Modules.Fap60;
using Fgp.DeviceBridge.Api.Modules.Iris;

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
    options.SerializerOptions.PropertyNameCaseInsensitive = true;
});

builder.Services.AddCors(o =>
{
    var origins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()
        ?? new[]
        {
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:80",
            "http://127.0.0.1:80",
        };
    o.AddDefaultPolicy(p => p.WithOrigins(origins).AllowAnyHeader().AllowAnyMethod());
});

var fpOptions = builder.Configuration.GetSection("Fingerprint").Get<Fap60FingerprintOptions>()
    ?? new Fap60FingerprintOptions();
var fpMode = fpOptions.Mode ?? builder.Configuration["Fingerprint:Mode"] ?? "mock";
var fpSdkPathConfigured = fpOptions.SdkPath ?? builder.Configuration["Fingerprint:SdkPath"];
var fpSdkPath = Fap60SdkPathResolver.Resolve(fpSdkPathConfigured, builder.Environment.ContentRootPath);

IFingerprintModule fingerprint = fpMode.Equals("fap60", StringComparison.OrdinalIgnoreCase)
    ? new Fap60FingerprintModule(fpSdkPath, fpOptions)
    : new MockFingerprintModule();

builder.Services.AddSingleton(fingerprint);
if (fpMode.Equals("fap60", StringComparison.OrdinalIgnoreCase))
{
    var sdkHint = fpSdkPath ?? "(non résolu)";
    Console.WriteLine($"[FAP60] SdkPath = {sdkHint}");
    if (!Fap60SdkPathResolver.IsValidSdkDirectory(fpSdkPath))
        Console.WriteLine("[FAP60] SDK incomplet — lancez scripts\\copy-fap60-sdk.ps1 puis redémarrez le bridge.");
}

var cameraOptions = builder.Configuration.GetSection("Camera").Get<CameraGpOptions>() ?? new CameraGpOptions();
var cameraMode = cameraOptions.Mode ?? builder.Configuration["Camera:Mode"] ?? "mock";
builder.Services.AddSingleton(cameraOptions);

ICameraModule camera = cameraMode.Equals("gpy", StringComparison.OrdinalIgnoreCase)
    || cameraMode.Equals("gpy-com", StringComparison.OrdinalIgnoreCase)
    ? new CameraGpProxyModule(new HttpClient(), cameraOptions)
    : new CameraMockModule();

builder.Services.AddSingleton(camera);

if (camera is CameraGpProxyModule && cameraOptions.AutoStartSidecar)
    builder.Services.AddHostedService<CameraGpSidecarHostedService>();

var irisOptions = builder.Configuration.GetSection("Iris").Get<IrisDeviceOptions>() ?? new IrisDeviceOptions();
irisOptions.Mode ??= builder.Configuration["Iris:Mode"];
irisOptions.BinPath ??= builder.Configuration["Iris:BinPath"];
irisOptions.BaseUrl ??= builder.Configuration["Iris:BaseUrl"];
builder.Services.AddSingleton(irisOptions);

builder.Services.AddHttpClient(nameof(IrisDeviceModule), client =>
{
    client.Timeout = TimeSpan.FromSeconds(Math.Max(90, irisOptions.DefaultTimeoutSeconds + 60));
});

var useIrisDevice = IrisDeviceOptions.IsDeviceMode(irisOptions.Mode);
builder.Services.AddSingleton<IIrisModule>(sp =>
{
    if (!useIrisDevice)
        return new MockIrisModule();

    var http = sp.GetRequiredService<IHttpClientFactory>().CreateClient(nameof(IrisDeviceModule));
    return new IrisDeviceModule(http, irisOptions);
});

if (useIrisDevice && irisOptions.AutoStartServer)
    builder.Services.AddHostedService<IrisDeviceServerHostedService>();

var printerOptions = builder.Configuration.GetSection("Printer").Get<PosPrinterOptions>() ?? new PosPrinterOptions();
var printerMode = printerOptions.Mode ?? builder.Configuration["Printer:Mode"] ?? "mock";
builder.Services.AddSingleton(printerOptions);

IPrinterModule printer = printerMode.Equals("pos", StringComparison.OrdinalIgnoreCase)
    ? new PosPrinterProxyModule(new HttpClient(), printerOptions)
    : new PosPrinterMockModule();

builder.Services.AddSingleton(printer);

if (printer is PosPrinterProxyModule && printerOptions.AutoStartSidecar)
    builder.Services.AddHostedService<PosPrinterSidecarHostedService>();

var app = builder.Build();
app.UseCors();

app.MapGet("/health", (IFingerprintModule fp, ICameraModule cam, IIrisModule irisMod, IPrinterModule prn) =>
{
    var modules = new Dictionary<string, ModuleHealth>
    {
        [fp.ModuleName] = fp.GetHealth(),
        [cam.ModuleName] = cam.GetHealth(),
        [irisMod.ModuleName] = irisMod.GetHealth(),
        [prn.ModuleName] = prn.GetHealth(),
        ["document"] = new("unknown", "Scanner via CameraGP"),
        ["signature"] = new("unknown", "Not implemented"),
    };

    var overall = modules.Values.Any(m => m.Status == "down")
        ? "unhealthy"
        : modules.Values.Any(m => m.Status is "degraded" or "unknown")
            ? "degraded"
            : "healthy";

    return Results.Ok(new HealthResponse(overall, "0.1.0", modules));
});

app.MapPost("/api/v1/devices/fingerprint/open", async (IFingerprintModule fp, CancellationToken ct) =>
    Results.Ok(await fp.OpenAsync(ct)));

app.MapPost("/api/v1/devices/fingerprint/close", async (IFingerprintModule fp, CancellationToken ct) =>
    Results.Ok(await fp.CloseAsync(ct)));

app.MapPost("/api/v1/devices/fingerprint/preview", async (
    IFingerprintModule fp,
    FingerprintCaptureRequest request,
    CancellationToken ct) =>
{
    if (fp is not Fap60FingerprintModule fap60)
        return Results.BadRequest(new { success = false, message = "Preview disponible uniquement en mode fap60" });

    var result = await fap60.GetPreviewFrameAsync(request.CaptureType, ct);
    return Results.Ok(result);
});

app.MapPost("/api/v1/devices/fingerprint/capture", async (
    IFingerprintModule fp,
    FingerprintCaptureRequest request,
    CancellationToken ct) =>
{
    try
    {
        var result = await fp.CaptureAsync(request, ct);
        return result.Success ? Results.Ok(result) : Results.BadRequest(result);
    }
    catch (Exception ex)
    {
        return Results.Json(
            new FingerprintCaptureResponse(false, ex.Message, Logs: new List<string> { ex.ToString() }),
            statusCode: StatusCodes.Status400BadRequest);
    }
});

app.MapGet("/api/v1/devices/camera/status", async (ICameraModule cam, CancellationToken ct) =>
{
    var status = await cam.GetStatusAsync(ct);
    return Results.Ok(status);
});

app.MapGet("/api/v1/devices/camera/gpy-status", async (ICameraModule cam, CancellationToken ct) =>
{
    var status = await cam.GetStatusAsync(ct);
    return Results.Ok(new
    {
        available = status.Available,
        mode = status.Mode,
        device_count = status.DeviceCount,
        message = status.Message,
        integration = "device-bridge-com",
    });
});

app.MapPost("/api/v1/devices/camera/open", async (ICameraModule cam, CancellationToken ct) =>
{
    var result = await cam.OpenAsync(ct);
    return result.Success ? Results.Ok(result) : Results.BadRequest(result);
});

app.MapPost("/api/v1/devices/camera/close", async (ICameraModule cam, CancellationToken ct) =>
    Results.Ok(await cam.CloseAsync(ct)));

app.MapGet("/api/v1/devices/camera/preview", async (ICameraModule cam, CancellationToken ct) =>
    Results.Ok(await cam.GetPreviewAsync(ct)));

app.MapPost("/api/v1/devices/camera/capture", async (ICameraModule cam, CancellationToken ct) =>
{
    var result = await cam.CaptureAsync(useFaceDetection: true, ct);
    return result.Success ? Results.Ok(result) : Results.BadRequest(result);
});

app.MapPost("/api/v1/devices/camera/capture-document", async (ICameraModule cam, CaptureDocumentBody? body, CancellationToken ct) =>
{
    var result = await cam.CaptureDocumentAsync(body?.AutoCut ?? true, ct);
    return result.Success ? Results.Ok(result) : Results.BadRequest(result);
});

app.MapPost("/api/v1/devices/camera/probe", async (ICameraModule cam, CancellationToken ct) =>
{
    var health = cam.GetHealth();
    var status = await cam.GetStatusAsync(ct);
    DeviceOperationResponse? open = null;
    DeviceOperationResponse? close = null;
    if (status.Available)
    {
        open = await cam.OpenAsync(ct);
        if (open.Success)
            close = await cam.CloseAsync(ct);
    }

    return Results.Ok(new
    {
        health,
        status,
        open,
        close,
        probed_at = DateTime.UtcNow,
    });
});

app.MapGet("/api/v1/devices/iris/status", async (IIrisModule irisMod, CancellationToken ct) =>
    Results.Ok(await irisMod.GetStatusAsync(ct)));

app.MapGet("/api/v1/devices/iris/preview/live", async (IIrisModule irisMod, CancellationToken ct) =>
    Results.Ok(await irisMod.GetLivePreviewAsync(ct)));

app.MapPost("/api/v1/devices/iris/capture", async (
    IIrisModule irisMod,
    IrisCaptureRequest request,
    CancellationToken ct) =>
{
    var result = await irisMod.CaptureAsync(request, ct);
    return result.Success ? Results.Ok(result) : Results.BadRequest(result);
});

app.MapPost("/api/v1/devices/iris/start-server", async (
    IrisDeviceOptions irisOpts,
    ILogger<IrisDeviceServerHostedService> log,
    CancellationToken ct) =>
{
    var result = await IrisServerStarter.TryStartAsync(irisOpts, log, ct);
    return Results.Ok(new
    {
        success = result.Success,
        message = result.Message,
        base_url = result.BaseUrl,
        pid = result.Pid,
    });
});

app.MapPost("/api/v1/devices/iris/open", async (IIrisModule irisMod, CancellationToken ct) =>
{
    var result = await irisMod.OpenAsync(ct);
    return Results.Ok(result);
});

app.MapPost("/api/v1/devices/iris/stop", async (IIrisModule irisMod, CancellationToken ct) =>
    Results.Ok(await irisMod.StopAsync(ct)));

app.MapPost("/api/v1/devices/iris/close", async (IIrisModule irisMod, CancellationToken ct) =>
    Results.Ok(await irisMod.CloseAsync(ct)));

app.MapPost("/api/v1/devices/iris/probe", async (IIrisModule irisMod, CancellationToken ct) =>
{
    var health = irisMod.GetHealth();
    var status = await irisMod.GetStatusAsync(ct);
    DeviceOperationResponse? open = null;
    DeviceOperationResponse? stop = null;
    if (!status.Available)
        open = await irisMod.OpenAsync(ct);
    if (status.Available || open?.Success == true)
        stop = await irisMod.StopAsync(ct);

    var statusAfter = open?.Success == true
        ? await irisMod.GetStatusAsync(ct)
        : status;

    return Results.Ok(new
    {
        health,
        status = statusAfter,
        open,
        stop,
        probed_at = DateTime.UtcNow,
    });
});

app.MapPost("/api/v1/devices/fingerprint/probe", async (IFingerprintModule fp, CancellationToken ct) =>
{
    var health = fp.GetHealth();
    var open = await fp.OpenAsync(ct);
    DeviceOperationResponse? close = null;
    if (open.Success)
        close = await fp.CloseAsync(ct);

    return Results.Ok(new
    {
        health,
        open,
        close,
        probed_at = DateTime.UtcNow,
    });
});

app.MapGet("/api/v1/devices/printer/status", async (IPrinterModule prn, CancellationToken ct) =>
    Results.Ok(await prn.GetStatusAsync(ct)));

app.MapPost("/api/v1/devices/printer/open", async (IPrinterModule prn, PrinterOpenRequest? body, CancellationToken ct) =>
{
    var result = await prn.OpenAsync(body, ct);
    return result.Success ? Results.Ok(result) : Results.BadRequest(result);
});

app.MapPost("/api/v1/devices/printer/close", async (IPrinterModule prn, CancellationToken ct) =>
    Results.Ok(await prn.CloseAsync(ct)));

app.MapPost("/api/v1/devices/printer/print-receipt", async (IPrinterModule prn, PrintReceiptRequest body, CancellationToken ct) =>
{
    var result = await prn.PrintReceiptAsync(body, ct);
    return result.Success ? Results.Ok(result) : Results.BadRequest(result);
});

app.MapPost("/api/v1/devices/printer/test", async (IPrinterModule prn, CancellationToken ct) =>
{
    var result = await prn.PrintTestAsync(ct);
    return result.Success ? Results.Ok(result) : Results.BadRequest(result);
});

app.Run();
