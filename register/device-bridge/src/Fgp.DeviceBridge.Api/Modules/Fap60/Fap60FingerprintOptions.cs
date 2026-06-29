namespace Fgp.DeviceBridge.Api.Modules.Fap60;

public sealed record Fap60FingerprintOptions
{
    public string? SdkPath { get; init; }
    public string Mode { get; init; } = "mock";

    /// <summary>Fichier licence algorithme (binaire ou texte). Relatif à SdkPath si chemin relatif.</summary>
    public string? LicenseFilePath { get; init; }

    /// <summary>Si false : ouverture device sans zzInit ; capture OK, NFIQ non calculé.</summary>
    public bool RequireAlgorithmLicense { get; init; } = true;

    /// <summary>Appeler zzAuth si aucun fichier licence local.</summary>
    public bool TryLicenseServerOnMissingFile { get; init; }

    /// <summary>Enregistrer le blob zzAuth dans SdkPath/fingerprint.license (hors git).</summary>
    public bool CacheLicenseFromServer { get; init; } = true;

    public Fap60LicenseServerOptions? LicenseServer { get; init; }
}

public sealed class Fap60LicenseServerOptions
{
    public string Ip { get; init; } = "183.129.171.153";
    public int Port { get; init; } = 1902;
    public string? UserId { get; init; }
    public string? Password { get; init; }
}
