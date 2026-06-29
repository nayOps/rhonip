using System.Text;
using Fgp.DeviceBridge.Api.Models;

namespace Fgp.DeviceBridge.Api.Modules;

public sealed class MockIrisModule : IIrisModule
{
    public string ModuleName => "iris";

    public ModuleHealth GetHealth() => new("ok", "Mode simulation (mock)", "mock");

    public Task<IrisStatusResponse> GetStatusAsync(CancellationToken ct = default) =>
        Task.FromResult(new IrisStatusResponse(true, "mock", "Iris simulé — pas de matériel"));

    public Task<IrisPreviewResponse> GetLivePreviewAsync(CancellationToken ct = default)
    {
        const string tiny =
            "Qk02AAAAAAAAADYAAAAoAAAAAQAAAAEAAAABABgAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAA";
        return Task.FromResult(new IrisPreviewResponse(true, "Preview simulé", tiny, tiny));
    }

    public async Task<IrisCaptureResponse> CaptureAsync(IrisCaptureRequest request, CancellationToken ct = default)
    {
        await Task.Delay(1500, ct);
        var eye = (request.Eye ?? "both").ToLowerInvariant();
        var eyes = new List<IrisEyeResult>();
        if (eye is "right" or "both")
            eyes.Add(new("right", true, SimulatedBmpBase64(), "image/bmp", 82, null));
        if (eye is "left" or "both")
            eyes.Add(new("left", true, SimulatedBmpBase64(), "image/bmp", 85, null));
        return new(true, "Capture simulée", eyes);
    }

    public Task<DeviceOperationResponse> OpenAsync(CancellationToken ct = default) =>
        Task.FromResult(new DeviceOperationResponse(true, "Open simulé"));

    public Task<DeviceOperationResponse> StopAsync(CancellationToken ct = default) =>
        Task.FromResult(new DeviceOperationResponse(true, "Stop simulé"));

    public Task<DeviceOperationResponse> CloseAsync(CancellationToken ct = default) =>
        Task.FromResult(new DeviceOperationResponse(true, "Close simulé"));

    private static string SimulatedBmpBase64() =>
        Convert.ToBase64String(Encoding.UTF8.GetBytes("MOCK_IRIS_BMP"));
}
