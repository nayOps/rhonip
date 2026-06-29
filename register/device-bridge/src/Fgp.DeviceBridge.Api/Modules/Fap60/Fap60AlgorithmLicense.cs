namespace Fgp.DeviceBridge.Api.Modules.Fap60;

internal static class Fap60AlgorithmLicense
{
    public const int AuthInfoMaxBytes = 1080;
    private const string CachedLicenseFileName = "fingerprint.license";

    private static readonly string[] DefaultLicenseNames =
    [
        "license.dat",
        "License.dat",
        "auth.dat",
        "fingerprint.license",
        "fingerprint.dat",
        CachedLicenseFileName,
    ];

    public sealed record InitResult(bool Success, bool AlgorithmActive, string Message);

    public static InitResult Initialize(string sdkPath, Fap60FingerprintOptions options)
    {
        Fap60Native.SetDllDirectory(sdkPath);
        string? lastLicenseError = null;

        foreach (var path in ResolveLicensePaths(sdkPath, options.LicenseFilePath))
        {
            if (!File.Exists(path))
                continue;

            var data = File.ReadAllBytes(path);
            if (data.Length == 0)
                continue;

            var rc = Fap60Native.zzInit(data, data.Length);
            if (rc == 0)
                return new(true, true, $"Licence algorithme OK — {Path.GetFileName(path)} ({data.Length} octets)");

            lastLicenseError = $"Fichier {Path.GetFileName(path)} : {Fap60AlgorithmErrors.Describe(rc)}";
        }

        if (options.TryLicenseServerOnMissingFile &&
            options.LicenseServer is { UserId: { Length: > 0 } userId, Password: { Length: > 0 } pwd })
        {
            var auth = FetchFromServer(options.LicenseServer, userId, pwd);
            if (auth.Success)
            {
                var rc = Fap60Native.zzInit(auth.LicenseData!, auth.LicenseData!.Length);
                if (rc == 0)
                {
                    if (options.CacheLicenseFromServer)
                    {
                        try { File.WriteAllBytes(Path.Combine(sdkPath, CachedLicenseFileName), auth.LicenseData!); }
                        catch { /* cache optionnel */ }
                    }
                    return new(true, true, "Licence algorithme OK — zzAuth serveur");
                }
                lastLicenseError = $"zzAuth+zzInit : {Fap60AlgorithmErrors.Describe(rc)}";
            }
            else
            {
                lastLicenseError = auth.Message;
            }
        }

        // Toujours comme FAP60Demo (OpenDevice appelle zzInit(null, 0) avant capture).
        var demoRc = Fap60Native.zzInit(IntPtr.Zero, 0);
        if (demoRc == 0)
            return new(true, true, "Algorithme initialisé — zzInit (comme FAP60Demo)");

        var demoMsg = Fap60AlgorithmErrors.Describe(demoRc);
        if (!options.RequireAlgorithmLicense)
        {
            return new(true, false,
                $"Mode dégradé — zzInit échoué ({demoMsg}). {lastLicenseError ?? "Pas de license.dat valide."}");
        }

        return new(false, false,
            $"{demoMsg}. {lastLicenseError ?? ""} Copiez license.dat dans {sdkPath} ou configurez LicenseServer.");
    }

    private static IEnumerable<string> ResolveLicensePaths(string sdkPath, string? configured)
    {
        var paths = new List<string>();

        void TryAdd(string? p)
        {
            if (string.IsNullOrWhiteSpace(p))
                return;
            var full = Path.IsPathRooted(p)
                ? Path.GetFullPath(p)
                : Path.GetFullPath(Path.Combine(sdkPath, p));
            if (!paths.Contains(full, StringComparer.OrdinalIgnoreCase))
                paths.Add(full);
        }

        TryAdd(configured);
        foreach (var name in DefaultLicenseNames)
            TryAdd(name);

        return paths;
    }

    private sealed record AuthResult(bool Success, byte[]? LicenseData, string Message);

    private static AuthResult FetchFromServer(Fap60LicenseServerOptions server, string userId, string password)
    {
        var authInfo = new byte[AuthInfoMaxBytes];
        var errInfo = new byte[256];
        var len = new int[1];

        var rc = Fap60Native.zzAuth(
            server.Ip,
            server.Port,
            userId,
            password,
            authInfo,
            len,
            errInfo);

        if (rc != 0)
        {
            var err = Fap60ImageHelper.TrimCString(errInfo);
            if (string.IsNullOrWhiteSpace(err))
                err = Fap60AlgorithmErrors.Describe(rc);
            return new(false, null, $"zzAuth ({rc}): {err}");
        }

        var size = len[0];
        if (size <= 0 || size > authInfo.Length)
            return new(false, null, $"zzAuth : longueur licence invalide ({size})");

        var blob = new byte[size];
        Array.Copy(authInfo, blob, size);
        return new(true, blob, "zzAuth OK");
    }
}
