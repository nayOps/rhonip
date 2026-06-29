namespace Fgp.DeviceBridge.Api.Models;

public record IrisStatusResponse(
    bool Available,
    string Mode,
    string Message,
    int? ServerPort = null,
    string? DeviceModel = null,
    int? DeviceStatus = null,
    int? Errcode = null);

public record IrisCaptureRequest(
    string Eye = "both",
    int TimeoutSeconds = 30,
    int Quality = 60);

public record IrisEyeResult(
    string Eye,
    bool Success,
    string? ImageBase64,
    string? Mime,
    int? Quality,
    string? Message);

public record IrisCaptureResponse(
    bool Success,
    string Message,
    List<IrisEyeResult>? Eyes = null,
    string? RawResponse = null);

public record IrisPreviewResponse(
    bool Success,
    string Message,
    string? LeftImageBase64 = null,
    string? RightImageBase64 = null,
    string Mime = "image/bmp");
