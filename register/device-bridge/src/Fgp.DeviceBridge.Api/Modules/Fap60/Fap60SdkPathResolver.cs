namespace Fgp.DeviceBridge.Api.Modules.Fap60;

/// <summary>
/// Résout le dossier SDK FAP60 (Bin64) — évite le chemin obsolète fgp\fgp\device-bridge.
/// </summary>
internal static class Fap60SdkPathResolver
{
    private static readonly string[] RequiredDlls = ["FAP60-02.dll", "fingerprint.dll", "Driver.dll"];

    public static string? Resolve(string? configured, string contentRoot)
    {
        var candidates = new List<string>();

        void Add(string? path)
        {
            if (string.IsNullOrWhiteSpace(path)) return;
            try
            {
                candidates.Add(Path.GetFullPath(path));
            }
            catch
            {
                /* chemin invalide */
            }
        }

        Add(Environment.GetEnvironmentVariable("FGP_FAP60_SDK_PATH"));
        Add(configured);

        // device-bridge/sdk/fap60-x64 (depuis src/Fgp.DeviceBridge.Api)
        Add(Path.Combine(contentRoot, "..", "..", "sdk", "fap60-x64"));

        // Référence guichet FGP + monorepo ONIP
        Add(@"C:\Users\HYF\Documents\sdk\fgp\register\device-bridge\sdk\fap60-x64");
        Add(@"C:\Users\HYF\Documents\rh-onip\register\device-bridge\sdk\fap60-x64");

        // Bin64 FAP60Demo (même runtime que la démo constructeur)
        Add(
            @"C:\Users\HYF\Documents\sdk\FAP60 Windows CSharp SDKV2.0.14C-2025091817\FAP60 Windows CSharp SDKV2.0.14C-2025091817\samplecode\FAP60Demo\Bin64");
        Add(
            @"C:\Users\HYF\Documents\sdk\FAP60 Windows CSharp SDKV2.0.14C-2025091817\FAP60 Windows CSharp SDKV2.0.14C-2025091817\bin\Bin64");

        foreach (var dir in candidates.Distinct(StringComparer.OrdinalIgnoreCase))
        {
            if (IsValidSdkDirectory(dir))
                return dir;
        }

        return string.IsNullOrWhiteSpace(configured) ? null : configured;
    }

    public static bool IsValidSdkDirectory(string? dir)
    {
        if (string.IsNullOrWhiteSpace(dir) || !Directory.Exists(dir))
            return false;
        return RequiredDlls.All(f => File.Exists(Path.Combine(dir, f)));
    }
}
