namespace Fgp.DeviceBridge.Api.Modules.Fap60;

/// <summary>Vérifications post-capture comme FAP60Demo (AssistantFunc.checkEdgeFinger).</summary>
internal static class Fap60EdgeCheck
{
    public const int EdgeFingerError = -100032;
    public const int WrongLeftHandError = -600013;
    public const int WrongRightHandError = -600014;

    public static int CheckEdge(byte[] plateImage, int fingerCount, int[] handSideOut)
    {
        var segmentBuf = new byte[640 * 640 * 4];
        return Fap60Native.zzFingerSegment(
            plateImage,
            Fap60Native.BigWidth,
            Fap60Native.BigHeight,
            fingerCount,
            handSideOut,
            segmentBuf);
    }

    public static int ValidateHand(string captureType, int fingerCount, int[] handSide)
    {
        if (fingerCount != 4)
            return 0;

        return captureType.ToLowerInvariant() switch
        {
            "left_four" when handSide[0] != 1 => WrongLeftHandError,
            "right_four" when handSide[0] != 2 => WrongRightHandError,
            _ => 0,
        };
    }

    public static bool IsRetryablePlacementError(int code) =>
        code is CaptureTimeoutError or EdgeFingerError or WrongLeftHandError or WrongRightHandError;

    private const int CaptureTimeoutError = -26;
}
