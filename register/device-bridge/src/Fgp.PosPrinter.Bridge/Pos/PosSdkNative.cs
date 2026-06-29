using System.Runtime.InteropServices;

namespace Fgp.PosPrinter.Bridge.Pos;

internal static class PosSdkNative
{
    public const int PosPtCom = 1000;
    public const int PosPtLpt = 1001;
    public const int PosPtUsb = 1002;
    public const int PosPtNet = 1003;

    public const int PosEsSuccess = 0;
    public const int PosBtQrcode = 4102;
    public const int PosHtDown = 4013;

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool SetDllDirectory(string lpPathName);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Port_OpenA")]
    public static extern int POS_Port_OpenA(string lpName, int iPort, bool bFile, string path);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Port_Close")]
    public static extern int POS_Port_Close(int printId);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Output_PrintStringA")]
    public static extern int POS_Output_PrintStringA(int printId, string strBuff);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Output_PrintFontStringA")]
    public static extern int POS_Output_PrintFontStringA(
        int printId, int iFont, int iThick, int iWidth, int iHeight, int iUnderLine, string lpString);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Control_AlignType")]
    public static extern int POS_Control_AlignType(int printId, int iAlignType);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Control_CutPaper")]
    public static extern int POS_Control_CutPaper(int printId, int type, int len);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Status_QueryStatus")]
    public static extern int POS_Status_QueryStatus(int printId);

    [DllImport("POS_SDK.dll", CharSet = CharSet.Ansi, EntryPoint = "POS_Output_PrintTwoDimensionalBarcodeA")]
    public static extern int POS_Output_PrintTwoDimensionalBarcodeA(
        int printId, int iType, int parameter1, int parameter2, int parameter3, string lpString);

    public static int MapPortType(string? type) => (type ?? "usb").ToLowerInvariant() switch
    {
        "com" => PosPtCom,
        "lpt" => PosPtLpt,
        "net" => PosPtNet,
        _ => PosPtUsb,
    };

    public static string DescribeStatus(int code) => code switch
    {
        3002 => "Papier épuisé",
        3003 => "Tête en surchauffe",
        3004 => "Capot ouvert",
        3005 => "Tampon plein",
        3006 => "Erreur coupe",
        3001 => "OK",
        _ => $"État imprimante ({code})",
    };
}
