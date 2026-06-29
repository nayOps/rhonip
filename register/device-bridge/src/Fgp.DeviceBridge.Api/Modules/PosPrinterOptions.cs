namespace Fgp.DeviceBridge.Api.Modules;

public sealed class PosPrinterOptions
{
    public string? Mode { get; set; } = "pos";
    public string? SidecarUrl { get; set; } = "http://127.0.0.1:8767";
    public bool AutoStartSidecar { get; set; } = true;
    public int SidecarStartupWaitSeconds { get; set; } = 25;
    public string Connection { get; set; } = "SP-USB1";
    public string PortType { get; set; } = "usb";
    public string? SdkPath { get; set; }
}
