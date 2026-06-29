using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public interface ICameraModule
{
    string ModuleName { get; }
    ModuleHealth GetHealth();
    Task<CameraStatusResponse> GetStatusAsync(CancellationToken ct = default);
    Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default);
    Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default);
    Task<CameraPreviewResponse> GetPreviewAsync(CancellationToken ct = default);
    Task<CameraCaptureResponse> CaptureAsync(bool useFaceDetection = true, CancellationToken ct = default);
    Task<CameraCaptureResponse> CaptureDocumentAsync(bool autoCut = true, CancellationToken ct = default);
}
