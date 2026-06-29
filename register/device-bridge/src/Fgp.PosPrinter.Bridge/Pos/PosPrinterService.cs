using System.Text;

namespace Fgp.PosPrinter.Bridge.Pos;

public sealed class PosPrinterService
{
    private int _printerId = -1;
    private readonly string? _sdkPath;
    private bool _dllReady;

    public PosPrinterService(IConfiguration config)
    {
        _sdkPath = config["Printer:SdkPath"] ?? config["POS:SdkPath"];
        TryInitDll();
    }

    public bool IsOpen => _printerId > 0;

    private void TryInitDll()
    {
        if (_dllReady) return;
        var dir = ResolveSdkDir();
        if (dir is not null && Directory.Exists(dir))
            PosSdkNative.SetDllDirectory(dir);
        _dllReady = true;
    }

    private string? ResolveSdkDir()
    {
        if (!string.IsNullOrWhiteSpace(_sdkPath) && Directory.Exists(_sdkPath))
            return Path.GetFullPath(_sdkPath);

        var baseDir = AppContext.BaseDirectory;
        foreach (var rel in new[] { "sdk\\pos-x86", "..\\..\\..\\sdk\\pos-x86", "..\\sdk\\pos-x86" })
        {
            var p = Path.GetFullPath(Path.Combine(baseDir, rel));
            if (File.Exists(Path.Combine(p, "POS_SDK.dll")))
                return p;
        }

        var vendor = @"C:\Users\HYF\Documents\sdk\POS-SDK\SDK";
        if (File.Exists(Path.Combine(vendor, "POS_SDK.dll")))
            return vendor;

        return File.Exists(Path.Combine(baseDir, "POS_SDK.dll")) ? baseDir : null;
    }

    public (bool Success, string Message, int? PrinterId) Open(string connection, string portType)
    {
        TryInitDll();
        if (IsOpen)
            Close();

        var name = string.IsNullOrWhiteSpace(connection) ? "SP-USB1" : connection.Trim();
        var pt = PosSdkNative.MapPortType(portType);
        var id = PosSdkNative.POS_Port_OpenA(name, pt, false, "");
        if (id <= 0)
            return (false, $"Ouverture imprimante échouée ({name}, type {portType})", null);

        _printerId = id;
        return (true, $"Imprimante ouverte — {name}", id);
    }

    public void Close()
    {
        if (_printerId > 0)
        {
            try { PosSdkNative.POS_Port_Close(_printerId); } catch { /* ignore */ }
        }
        _printerId = -1;
    }

    public (bool Success, string Message) PrintReceipt(ReceiptPrintRequest req)
    {
        if (!IsOpen)
        {
            var opened = Open(req.Connection ?? "SP-USB1", req.PortType ?? "usb");
            if (!opened.Success)
                return (false, opened.Message);
        }

        try
        {
            var lines = req.Lines is { Count: > 0 } list ? list : new List<ReceiptLine>();
            foreach (var line in lines)
            {
                var align = line.Align?.ToLowerInvariant() switch
                {
                    "center" => 1,
                    "right" => 2,
                    _ => 0,
                };
                PosSdkNative.POS_Control_AlignType(_printerId, align);

                string text = (line.Text ?? string.Empty).Replace("\n", "\r\n", StringComparison.Ordinal);
                if (!text.EndsWith("\r\n", StringComparison.Ordinal))
                    text += "\r\n";

                if (line.Bold == true)
                {
                    PosSdkNative.POS_Output_PrintFontStringA(
                        _printerId, 0, 1, line.DoubleWidth == true ? 1 : 0, line.DoubleHeight == true ? 1 : 0, 0, text);
                }
                else
                {
                    PosSdkNative.POS_Output_PrintStringA(_printerId, text);
                }
            }

            if (!string.IsNullOrWhiteSpace(req.QrContent))
            {
                PosSdkNative.POS_Control_AlignType(_printerId, 1);
                PosSdkNative.POS_Output_PrintTwoDimensionalBarcodeA(
                    _printerId, PosSdkNative.PosBtQrcode, 4, 2, 0, req.QrContent.Trim());
                PosSdkNative.POS_Output_PrintStringA(_printerId, "\r\n");
            }

            if (req.Cut != false)
                PosSdkNative.POS_Control_CutPaper(_printerId, 1, 3);

            return (true, "Impression envoyée");
        }
        catch (Exception ex)
        {
            return (false, ex.Message);
        }
    }

    public (bool Success, string Message) PrintTestPage()
    {
        if (!IsOpen)
            return (false, "Imprimante non ouverte");

        var r = PosSdkNative.POS_Output_PrintStringA(_printerId, "Test FGP Device Bridge\r\n\r\n");
        PosSdkNative.POS_Control_CutPaper(_printerId, 1, 3);
        return r >= 0 ? (true, "Page test imprimée") : (false, $"Erreur impression ({r})");
    }

    public (bool Success, string Message, int StatusCode) QueryStatus()
    {
        if (!IsOpen)
            return (false, "Imprimante non ouverte", -1);

        var code = PosSdkNative.POS_Status_QueryStatus(_printerId);
        return (true, PosSdkNative.DescribeStatus(code), code);
    }
}

public sealed class ReceiptPrintRequest
{
    public string? Connection { get; set; }
    public string? PortType { get; set; }
    public List<ReceiptLine>? Lines { get; set; }
    public string? QrContent { get; set; }
    public bool? Cut { get; set; } = true;
}

public sealed class ReceiptLine
{
    public string? Text { get; set; }
    public string? Align { get; set; }
    public bool? Bold { get; set; }
    public bool? DoubleWidth { get; set; }
    public bool? DoubleHeight { get; set; }
}

public sealed class PrinterOpenRequest
{
    public string Connection { get; set; } = "SP-USB1";
    public string PortType { get; set; } = "usb";
}
