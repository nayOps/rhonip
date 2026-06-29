using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public interface IFingerprintModule
{
    string ModuleName { get; }
    ModuleHealth GetHealth();
    Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default);
    Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default);
    Task<FingerprintCaptureResponse> CaptureAsync(FingerprintCaptureRequest request, CancellationToken ct = default);
}
