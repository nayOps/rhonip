namespace Fgp.DeviceBridge.Api.Modules.Fap60;

/// <summary>Alignement doigts / buffer FAP60 (d'après FAP60Demo).</summary>
internal static class Fap60FingerLayout
{
    // g_CaptureType index par position logique
    private static readonly Dictionary<string, int> FlagIndex = new(StringComparer.OrdinalIgnoreCase)
    {
        ["left_index"] = 0,
        ["left_middle"] = 1,
        ["left_ring"] = 2,
        ["left_little"] = 3,
        ["left_thumb"] = 4,
        ["right_thumb"] = 5,
        ["right_index"] = 6,
        ["right_middle"] = 7,
        ["right_ring"] = 8,
        ["right_little"] = 9,
    };

    private static readonly Dictionary<string, string[]> CaptureFingerOrder = new(StringComparer.OrdinalIgnoreCase)
    {
        ["left_four"] = ["left_little", "left_ring", "left_middle", "left_index"],
        ["right_four"] = ["right_index", "right_middle", "right_ring", "right_little"],
        ["both_thumbs"] = ["left_thumb", "right_thumb"],
        ["single"] = ["right_index"],
    };

    public static int CaptureTypeToInt(string captureType) => captureType.ToLowerInvariant() switch
    {
        "right_four" => 1,
        "both_thumbs" => 3,
        "single" => 4,
        "roll" => 5,
        _ => 0,
    };

    public static string[] GetOrderedFingers(string captureType, string? singleFinger = null)
    {
        if (captureType.Equals("single", StringComparison.OrdinalIgnoreCase) && !string.IsNullOrWhiteSpace(singleFinger))
            return new[] { singleFinger.Trim().ToLowerInvariant() };
        return CaptureFingerOrder.TryGetValue(captureType, out var fingers)
            ? fingers
            : CaptureFingerOrder["left_four"];
    }

    public static int[] BuildFingerFlags(IEnumerable<string> presentFingers)
    {
        var flags = new int[10];
        foreach (var finger in presentFingers)
        {
            if (FlagIndex.TryGetValue(finger, out var idx))
                flags[idx] = 1;
        }
        return flags;
    }

    public static int CountMissing(string captureType, IEnumerable<string> presentFingers)
    {
        var expected = GetOrderedFingers(captureType);
        var presentSet = new HashSet<string>(presentFingers, StringComparer.OrdinalIgnoreCase);
        return expected.Count(f => !presentSet.Contains(f));
    }

    public static List<(string Position, byte[] Gray)> ExtractSmallImages(
        string captureType,
        byte[] smallBuffer,
        IEnumerable<string> presentFingers)
    {
        var ordered = GetOrderedFingers(captureType);
        var presentSet = new HashSet<string>(presentFingers, StringComparer.OrdinalIgnoreCase);
        var result = new List<(string, byte[])>();
        var offset = 0;

        foreach (var finger in ordered)
        {
            if (!presentSet.Contains(finger))
                continue;
            var chunk = new byte[Fap60Native.SmallFingerBytes];
            Array.Copy(smallBuffer, offset, chunk, 0, Fap60Native.SmallFingerBytes);
            offset += Fap60Native.SmallFingerBytes;
            result.Add((finger, chunk));
        }

        return result;
    }
}
