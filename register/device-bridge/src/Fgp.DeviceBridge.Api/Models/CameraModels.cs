namespace Fgp.DeviceBridge.Api.Models;

public record CameraCaptureResponse(
    bool Success,
    string Message,
    string? ImageBase64 = null,
    string Mime = "image/jpeg",
    bool? FaceDetected = null,
    List<string>? Logs = null);

public record CameraPreviewResponse(
    bool Success,
    string Message,
    string? ImageBase64 = null,
    string Mime = "image/jpeg");

public record CameraStatusResponse(
    bool Available,
    string Mode,
    string Message,
    int? DeviceCount = null);

public record CaptureDocumentBody(bool AutoCut = true);
