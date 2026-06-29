using System.Text.Json;

namespace Fgp.DeviceBridge.Api.Modules.Iris;

public sealed class IrisDeviceOptions
{
    /// <summary>mock | device (alias: iris, real, jd5, jd7)</summary>
    public string? Mode { get; set; }

    /// <summary>URL HTTP du Iris Device Server (ex. http://127.0.0.1:50218).</summary>
    public string? BaseUrl { get; set; } = "http://127.0.0.1:50218";

    /// <summary>Dossier SDK iris (IrisDeviceServer.exe, DLL, device_server.json).</summary>
    public string? BinPath { get; set; }

    /// <summary>Chemin explicite vers IrisDeviceServer.exe (sinon BinPath\IrisDeviceServer.exe).</summary>
    public string? ServerExePath { get; set; }

    /// <summary>Démarre IrisDeviceServer.exe au lancement du bridge si le port est fermé.</summary>
    public bool AutoStartServer { get; set; } = true;

    /// <summary>Attente max (s) que le port HTTP réponde après démarrage du processus.</summary>
    public int ServerStartupWaitSeconds { get; set; } = 25;

    public int PreviewWidth { get; set; } = 320;
    public int PreviewHeight { get; set; } = 240;
    public int DefaultTimeoutSeconds { get; set; } = 30;
    public int DefaultQuality { get; set; } = 60;

    public static bool IsDeviceMode(string? mode)
    {
        if (string.IsNullOrWhiteSpace(mode)) return false;
        return mode.Equals("device", StringComparison.OrdinalIgnoreCase)
            || mode.Equals("iris", StringComparison.OrdinalIgnoreCase)
            || mode.Equals("real", StringComparison.OrdinalIgnoreCase)
            || mode.Equals("jd5", StringComparison.OrdinalIgnoreCase)
            || mode.Equals("jd7", StringComparison.OrdinalIgnoreCase);
    }

    public string? ResolveServerExe()
    {
        if (!string.IsNullOrWhiteSpace(ServerExePath) && File.Exists(ServerExePath))
            return Path.GetFullPath(ServerExePath);

        if (string.IsNullOrWhiteSpace(BinPath))
            return null;

        var candidate = Path.Combine(BinPath, "IrisDeviceServer.exe");
        return File.Exists(candidate) ? Path.GetFullPath(candidate) : null;
    }

    public string? ResolveWorkingDirectory()
    {
        var exe = ResolveServerExe();
        if (exe is not null)
            return Path.GetDirectoryName(exe);

        if (!string.IsNullOrWhiteSpace(BinPath) && Directory.Exists(BinPath))
            return Path.GetFullPath(BinPath);

        return null;
    }

    /// <summary>Lit ServerPort depuis device_server.json (défaut 50218).</summary>
    public int ReadServerPortFromConfig()
    {
        var dir = ResolveWorkingDirectory();
        if (dir is null)
            return 50218;

        var jsonPath = Path.Combine(dir, "device_server.json");
        if (!File.Exists(jsonPath))
            return 50218;

        try
        {
            using var doc = JsonDocument.Parse(File.ReadAllText(jsonPath));
            if (doc.RootElement.TryGetProperty("ServerPort", out var port) && port.TryGetInt32(out var p) && p > 0)
                return p;
        }
        catch
        {
            /* ignore */
        }

        return 50218;
    }
}
