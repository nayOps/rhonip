namespace Fgp.DeviceBridge.Api.Models;

public record PrinterStatusResponse(
    bool Available,
    string Mode,
    string Message,
    bool Open = false,
    int? StatusCode = null);

public record PrinterOperationResponse(
    bool Success,
    string Message,
    List<string>? Logs = null);

public record PrinterOpenRequest(string Connection = "SP-USB1", string PortType = "usb");

public record ReceiptLineDto(
    string Text,
    string? Align = null,
    bool? Bold = null,
    bool? DoubleWidth = null,
    bool? DoubleHeight = null);

public record PrintReceiptRequest(
    string? Connection = null,
    string? PortType = null,
    List<ReceiptLineDto>? Lines = null,
    string? QrContent = null,
    bool? Cut = true);
