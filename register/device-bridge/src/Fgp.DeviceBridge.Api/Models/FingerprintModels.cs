namespace Fgp.DeviceBridge.Api.Models;

public record FingerprintCaptureRequest(
    string CaptureType = "left_four",
    string? FingerPosition = null,
    List<string>? PresentFingers = null,
    int MissingFingers = 0,
    int TimeoutMs = 30000,
    int TemplateFormat = 4,
    int NfiqThreshold = 3);

public record FingerTemplate(
    string Position,
    int FormatId,
    string DataBase64,
    int Quality,
    int? Nfiq = null,
    string? NfiqLabel = null);

public record FingerPreview(
    string Position,
    string ImageBase64,
    string Mime = "image/png",
    int? Nfiq = null,
    string? NfiqLabel = null,
    int? Quality = null,
    bool? PassesNfiq = null);

public record FingerprintCaptureResponse(
    bool Success,
    string Message,
    List<FingerTemplate>? Templates = null,
    List<FingerPreview>? Previews = null,
    string? PreviewPlateBase64 = null,
    List<string>? Logs = null);

public record DeviceOperationResponse(bool Success, string Message, int? PrinterId = null);

public record ModuleHealth(string Status, string? Message = null, string? Mode = null);

public record HealthResponse(string Status, string Version, Dictionary<string, ModuleHealth> Modules);
