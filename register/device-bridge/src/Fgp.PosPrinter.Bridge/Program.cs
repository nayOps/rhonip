using System.Text.Json;
using Fgp.PosPrinter.Bridge.Pos;

var builder = WebApplication.CreateBuilder(new WebApplicationOptions
{
    Args = args,
    ContentRootPath = AppContext.BaseDirectory,
});

builder.Services.ConfigureHttpJsonOptions(o =>
{
    o.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
    o.SerializerOptions.PropertyNameCaseInsensitive = true;
});

builder.Services.AddSingleton<PosPrinterService>();
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod()));

var app = builder.Build();
app.UseCors();

var printer = app.Services.GetRequiredService<PosPrinterService>();

app.MapGet("/health", () =>
{
    var sdkDir = AppContext.BaseDirectory;
    var hasDll = File.Exists(Path.Combine(sdkDir, "POS_SDK.dll"))
        || File.Exists(@"C:\Users\HYF\Documents\sdk\POS-SDK\SDK\POS_SDK.dll");
    return Results.Ok(new
    {
        status = hasDll ? "ok" : "degraded",
        mode = "pos-sdk-x86",
        message = hasDll ? "POS_SDK.dll trouvé" : "POS_SDK.dll absent — copiez depuis POS-SDK\\SDK",
        printer_open = printer.IsOpen,
    });
});

app.MapPost("/api/v1/devices/printer/open", (PrinterOpenRequest? body, PosPrinterService svc) =>
{
    var result = svc.Open(body?.Connection ?? "SP-USB1", body?.PortType ?? "usb");
    return result.Success
        ? Results.Ok(new { success = true, message = result.Message, printer_id = result.PrinterId })
        : Results.BadRequest(new { success = false, message = result.Message });
});

app.MapPost("/api/v1/devices/printer/close", (PosPrinterService svc) =>
{
    svc.Close();
    return Results.Ok(new { success = true, message = "Imprimante fermée" });
});

app.MapGet("/api/v1/devices/printer/status", (PosPrinterService svc) =>
{
    var st = svc.QueryStatus();
    return Results.Ok(new
    {
        success = st.Success,
        message = st.Message,
        status_code = st.StatusCode,
        open = svc.IsOpen,
    });
});

app.MapPost("/api/v1/devices/printer/print-receipt", (ReceiptPrintRequest body, PosPrinterService svc) =>
{
    var result = svc.PrintReceipt(body);
    return result.Success
        ? Results.Ok(new { success = true, message = result.Message })
        : Results.BadRequest(new { success = false, message = result.Message });
});

app.MapPost("/api/v1/devices/printer/test", (PosPrinterService svc) =>
{
    if (!svc.IsOpen)
    {
        var o = svc.Open("SP-USB1", "usb");
        if (!o.Success)
            return Results.BadRequest(new { success = false, message = o.Message });
    }

    var result = svc.PrintTestPage();
    return result.Success
        ? Results.Ok(new { success = true, message = result.Message })
        : Results.BadRequest(new { success = false, message = result.Message });
});

app.Lifetime.ApplicationStopping.Register(() => printer.Close());

app.Run();
