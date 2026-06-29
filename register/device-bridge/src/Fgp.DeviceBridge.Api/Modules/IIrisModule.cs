using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public interface IIrisModule
{
    string ModuleName { get; }
    ModuleHealth GetHealth();
    Task<IrisStatusResponse> GetStatusAsync(CancellationToken ct = default);
    Task<IrisPreviewResponse> GetLivePreviewAsync(CancellationToken ct = default);
    Task<IrisCaptureResponse> CaptureAsync(IrisCaptureRequest request, CancellationToken ct = default);
    Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default);
    Task<DeviceOperationResponse> StopAsync(CancellationToken ct = default);
    Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default);
}
