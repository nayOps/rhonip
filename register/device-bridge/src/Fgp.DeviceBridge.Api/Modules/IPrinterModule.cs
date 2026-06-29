using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public interface IPrinterModule
{
    string ModuleName { get; }
    ModuleHealth GetHealth();
    Task<PrinterStatusResponse> GetStatusAsync(CancellationToken ct = default);
    Task<PrinterOperationResponse> OpenAsync(PrinterOpenRequest? request, CancellationToken ct = default);
    Task<PrinterOperationResponse> CloseAsync(CancellationToken ct = default);
    Task<PrinterOperationResponse> PrintReceiptAsync(PrintReceiptRequest request, CancellationToken ct = default);
    Task<PrinterOperationResponse> PrintTestAsync(CancellationToken ct = default);
}
