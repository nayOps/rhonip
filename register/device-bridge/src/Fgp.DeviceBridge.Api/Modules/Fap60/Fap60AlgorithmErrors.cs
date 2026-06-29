namespace Fgp.DeviceBridge.Api.Modules.Fap60;

internal static class Fap60AlgorithmErrors
{
    public static string Describe(int code)
    {
        var doc = code switch
        {
            -100000 => "Échec initialisation algorithme (-100000)",
            -100001 => "Bibliothèque algorithme non initialisée (-100001)",
            -100002 => "Autorisation expirée (-100002)",
            -100003 => "Longueur code autorisation incorrecte (-100003)",
            -100004 => "Fichier d'autorisation introuvable (-100004) — placez license.dat dans SdkPath ou configurez LicenseFilePath / LicenseServer",
            -100005 => "Vérification code autorisation échouée (-100005)",
            _ => null,
        };

        if (doc != null)
            return doc;

        var sdk = Fap60ImageHelper.GetSdkErrorMessage(code);
        if (string.IsNullOrWhiteSpace(sdk) ||
            sdk.Contains("unknown", StringComparison.OrdinalIgnoreCase))
            return $"Erreur algorithme ({code})";

        return sdk;
    }
}
