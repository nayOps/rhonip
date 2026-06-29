namespace Fgp.DeviceBridge.Api.Modules.Iris;

/// <summary>Codes errcode renvoyés par Iris Device Server (souvent 0x01xxxxxx).</summary>
public static class IrisErrorCatalog
{
    public const int ErrDeviceClosedCapture = 16777231; // 0x0100000F — capture alors que DEV_CLOSED
    public const int ErrDeviceOpenFailed = 16777219;    // 0x01000003 — ouverture / périphérique absent

    private static readonly Dictionary<int, string> Known = new()
    {
        [0] = "OK",
        [ErrDeviceOpenFailed] =
            "Lecteur JD5 non prêt — start-iris-server-admin.bat (UAC), fermez DeviceUI, puis Ouvrir lecteur (pas d’API device/Open).",
        [ErrDeviceClosedCapture] =
            "Lecteur iris fermé ou occupé — fermez DeviceUI si besoin, puis Ouvrir lecteur (évitez plusieurs apps sur le scanner).",
    };

    public static string Describe(int? code, string? vendorMessage = null)
    {
        if (code is null or 0)
            return vendorMessage ?? "OK";
        return DescribeCode(code.Value, vendorMessage);
    }

    public static string DescribeCode(int code, string? vendorMessage = null)
    {
        string core;
        if (Known.TryGetValue(code, out var text))
            core = text;
        else
        {
            var layer = (code >> 24) & 0xFF;
            var sub = code & 0xFFFFFF;
            core = layer switch
            {
                1 => $"Erreur système iris ({sub}, 0x{code:X8})",
                _ => $"Erreur iris (errcode={code}, 0x{code:X8})",
            };
        }

        return !string.IsNullOrWhiteSpace(vendorMessage)
            ? $"{core} — {vendorMessage.Trim()}"
            : core;
    }

    public static string StatusLabel(int status) => status switch
    {
        1 => "fermé (DEV_CLOSED)",
        2 => "ouvert (DEV_OPENED)",
        3 => "capture en cours (DEV_CAPTURING)",
        _ => $"statut inconnu ({status})",
    };
}
