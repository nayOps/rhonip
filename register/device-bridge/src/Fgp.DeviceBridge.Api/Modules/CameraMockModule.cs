using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public sealed class CameraMockModule : ICameraModule
{
    public string ModuleName => "camera";

    public ModuleHealth GetHealth() =>
        new("ok", "Mode mock — pas de caméra matérielle", "mock");

    public Task<CameraStatusResponse> GetStatusAsync(CancellationToken ct = default) =>
        Task.FromResult(new CameraStatusResponse(true, "mock", "Mode simulation"));

    public Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default) =>
        Task.FromResult(new DeviceOperationResponse(true, "Mock ouvert"));

    public Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default) =>
        Task.FromResult(new DeviceOperationResponse(true, "Mock fermé"));

    public Task<CameraPreviewResponse> GetPreviewAsync(CancellationToken ct = default) =>
        Task.FromResult(new CameraPreviewResponse(false, "Preview non disponible en mock"));

    public Task<CameraCaptureResponse> CaptureAsync(bool useFaceDetection = true, CancellationToken ct = default) =>
        Task.FromResult(new CameraCaptureResponse(false, "Utilisez la webcam navigateur en mode mock"));

    public Task<CameraCaptureResponse> CaptureDocumentAsync(bool autoCut = true, CancellationToken ct = default) =>
        Task.FromResult(new CameraCaptureResponse(false, "Scan document : mode mock — utilisez GPYScan ou import fichier"));
}
