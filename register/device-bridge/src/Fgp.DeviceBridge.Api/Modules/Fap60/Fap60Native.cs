using System.Runtime.InteropServices;

namespace Fgp.DeviceBridge.Api.Modules.Fap60;

internal static class Fap60Native
{
    public const int BigWidth = 1600;
    public const int BigHeight = 1500;
    public const int SmallWidth = 300;
    public const int SmallHeight = 400;
    public const int SmallFingerBytes = SmallWidth * SmallHeight;

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool SetDllDirectory(string lpPathName);

    [DllImport("FAP60-02.dll", EntryPoint = "mxOpenDevice", CallingConvention = CallingConvention.StdCall)]
    public static extern IntPtr mxOpenDevice(int[] errCode);

    [DllImport("FAP60-02.dll", EntryPoint = "closeDevice", CallingConvention = CallingConvention.StdCall)]
    public static extern int closeDevice(IntPtr ptr);

    [DllImport("FAP60-02.dll", EntryPoint = "getDeviceSN", CallingConvention = CallingConvention.StdCall)]
    public static extern int getDeviceSN(IntPtr ptr, byte[] sn);

    [DllImport("FAP60-02.dll", EntryPoint = "getFirmwareVersion", CallingConvention = CallingConvention.StdCall)]
    public static extern int getFirmwareVersion(IntPtr ptr, byte[] info);

    [DllImport("FAP60-02.dll", EntryPoint = "getSdkVersion", CallingConvention = CallingConvention.StdCall)]
    public static extern int getSdkVersion(IntPtr ptr, byte[] version, int[] length);

    [DllImport("FAP60-02.dll", EntryPoint = "mxGetMessageText", CallingConvention = CallingConvention.StdCall)]
    public static extern int mxGetMessageText(int nErrorCode, byte[] msg);

    [DllImport("FAP60-02.dll", EntryPoint = "captureImage_old", CallingConvention = CallingConvention.StdCall)]
    public static extern int captureImage_old(
        IntPtr ptr,
        int captureType,
        int nMissNum,
        int unTimeOutMs,
        byte[] save_ori_img_buf,
        byte[] save_enh_img_buf,
        byte[] save_small_image_buf,
        int[] fingerFlags);

    [DllImport("fingerprint.dll", EntryPoint = "zzInit", CallingConvention = CallingConvention.StdCall)]
    public static extern int zzInit(IntPtr szLicenseData, int iLicenseDataLen);

    [DllImport("fingerprint.dll", EntryPoint = "zzInit", CallingConvention = CallingConvention.StdCall)]
    public static extern int zzInit(byte[] szLicenseData, int iLicenseDataLen);

    [DllImport("fingerprint.dll", EntryPoint = "zzFree", CallingConvention = CallingConvention.StdCall)]
    public static extern int zzFree();

    [DllImport("fingerprint.dll", EntryPoint = "zzAuth", CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Ansi)]
    public static extern int zzAuth(
        string szIp,
        int nPort,
        string szUserId,
        string szPwd,
        byte[] szAuthInfo,
        int[] iAuthInfoLen,
        byte[] szErrInfo);

    [DllImport("fingerprint.dll", EntryPoint = "zzFingerSegment", CallingConvention = CallingConvention.StdCall)]
    public static extern int zzFingerSegment(
        byte[] pImage,
        int nImgWidth,
        int nImgHeight,
        int dFingerNum,
        int[] dstLeftOrRightHand,
        byte[] dstpImage);

    [DllImport("fingerprint.dll", EntryPoint = "zzGetQualityNFIQScore", CallingConvention = CallingConvention.StdCall)]
    public static extern int zzGetQualityNFIQScore(byte[] pFingerImgBuf, int x, int y, int[] pQScore);

    [DllImport("FAP60-02.dll", EntryPoint = "captureVideo", CallingConvention = CallingConvention.StdCall)]
    public static extern int captureVideo(IntPtr ptr, int captureType, byte[] save_enh_img_buf);

    [DllImport("FAP60-02.dll", EntryPoint = "mxCancleCapture", CallingConvention = CallingConvention.StdCall)]
    public static extern int mxCancleCapture(IntPtr ptr);

    [DllImport("FAP60-02.dll", EntryPoint = "cancleCapture", CallingConvention = CallingConvention.StdCall)]
    public static extern int cancleCapture();
}
