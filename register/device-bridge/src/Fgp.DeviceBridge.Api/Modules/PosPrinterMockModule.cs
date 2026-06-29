using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public sealed class PosPrinterMockModule : IPrinterModule
{
    public string ModuleName => "print";

    public ModuleHealth GetHealth() => new("degraded", "Mode mock — utilisez Printer:Mode=pos", "mock");

    public Task<PrinterStatusResponse> GetStatusAsync(CancellationToken ct = default) =>
        Task.FromResult(new PrinterStatusResponse(false, "mock", "Imprimante POS non configurée (mode mock)"));

    public Task<PrinterOperationResponse> OpenAsync(PrinterOpenRequest? request, CancellationToken ct = default) =>
        Task.FromResult(new PrinterOperationResponse(false, "Mode mock — lancez le sidecar POS"));

    public Task<PrinterOperationResponse> CloseAsync(CancellationToken ct = default) =>
        Task.FromResult(new PrinterOperationResponse(true, "OK"));

    public Task<PrinterOperationResponse> PrintReceiptAsync(PrintReceiptRequest request, CancellationToken ct = default) =>
        Task.FromResult(new PrinterOperationResponse(false, "Mode mock — configurez Printer:Mode=pos dans appsettings"));

    public Task<PrinterOperationResponse> PrintTestAsync(CancellationToken ct = default) =>
        Task.FromResult(new PrinterOperationResponse(false, "Mode mock"));
}
