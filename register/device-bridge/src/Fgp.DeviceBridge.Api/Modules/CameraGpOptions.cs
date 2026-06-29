namespace Fgp.DeviceBridge.Api.Modules;

public sealed class CameraGpOptions
{
    public string? Mode { get; set; }
    public string SidecarUrl { get; set; } = "http://127.0.0.1:8766";
    public bool AutoStartSidecar { get; set; } = true;
    public string? SidecarExePath { get; set; }
    public int SidecarStartupWaitSeconds { get; set; } = 25;
}
