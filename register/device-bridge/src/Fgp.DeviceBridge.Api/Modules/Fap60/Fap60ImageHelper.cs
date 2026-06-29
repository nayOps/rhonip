using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Text;

namespace Fgp.DeviceBridge.Api.Modules.Fap60;

internal static class Fap60ImageHelper
{
    public static string ToPngBase64(byte[] gray, int width, int height)
    {
        if (width <= 0 || height <= 0 || gray.Length < width * height)
            return string.Empty;

        return InvokeSta(() =>
        {
            using var bmp = CreateGrayBitmap(gray, width, height);
            using var ms = new MemoryStream();
            bmp.Save(ms, ImageFormat.Png);
            return Convert.ToBase64String(ms.ToArray());
        });
    }

    /// <summary>GDI+ requiert un thread STA (comme WinForms FAP60Demo).</summary>
    private static T InvokeSta<T>(Func<T> func)
    {
        T? result = default;
        Exception? error = null;
        var thread = new Thread(() =>
        {
            try { result = func(); }
            catch (Exception ex) { error = ex; }
        });
        thread.SetApartmentState(ApartmentState.STA);
        thread.IsBackground = true;
        thread.Start();
        thread.Join(TimeSpan.FromSeconds(30));
        if (error != null)
            throw error;
        return result!;
    }

    public static int GetNfiq(byte[] fingerGray, int width, int height)
    {
        var score = new int[1] { 5 };
        Fap60Native.zzGetQualityNFIQScore(fingerGray, width, height, score);
        return score[0];
    }

    public static string NfiqLabel(int nfiq) => nfiq switch
    {
        1 => "Excellente (1)",
        2 => "Très bonne (2)",
        3 => "Bonne (3)",
        4 => "Moyenne (4)",
        5 => "Faible (5)",
        _ => "Inconnue",
    };

    public static int NfiqToQualityPercent(int nfiq) =>
        Math.Clamp((6 - nfiq) * 20, 0, 100);

    /// <summary>Message d'erreur driver/SDK uniquement (sans appeler Describe — évite récursion).</summary>
    public static string GetSdkErrorMessage(int code)
    {
        var msg = new byte[256];
        var sdk = Fap60Native.mxGetMessageText(code, msg) == 0 ? TrimCString(msg) : "";
        if (!string.IsNullOrWhiteSpace(sdk) &&
            !sdk.Contains("unknown", StringComparison.OrdinalIgnoreCase))
            return sdk;

        return string.IsNullOrWhiteSpace(sdk) ? $"erreur driver ({code})" : sdk;
    }

    public static string GetErrorMessage(int code)
    {
        if (code <= -100000)
            return Fap60AlgorithmErrors.Describe(code);

        return GetSdkErrorMessage(code);
    }

    public static string TrimCString(byte[] bytes)
    {
        var len = Array.IndexOf(bytes, (byte)0);
        if (len < 0) len = bytes.Length;
        return Encoding.ASCII.GetString(bytes, 0, len).Trim();
    }

    private static Bitmap CreateGrayBitmap(byte[] gray, int width, int height)
    {
        var bmp = new Bitmap(width, height, PixelFormat.Format8bppIndexed);
        var palette = bmp.Palette;
        for (var i = 0; i < 256; i++)
            palette.Entries[i] = Color.FromArgb(255, i, i, i);
        bmp.Palette = palette;

        var bmpData = bmp.LockBits(
            new Rectangle(0, 0, width, height),
            ImageLockMode.WriteOnly,
            PixelFormat.Format8bppIndexed);

        try
        {
            var stride = bmpData.Stride;
            for (var y = 0; y < height; y++)
            {
                var srcRow = (height - 1 - y) * width;
                var dstRow = bmpData.Scan0 + y * stride;
                Marshal.Copy(gray, srcRow, dstRow, width);
            }
        }
        finally
        {
            bmp.UnlockBits(bmpData);
        }

        return bmp;
    }
}
