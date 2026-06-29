using System.Diagnostics;

namespace Fgp.DeviceBridge.Api.Modules.Iris;

public sealed record IrisServerStartResult(
    bool Success,
    string Message,
    string? BaseUrl,
    int? Pid);

/// <summary>Démarre IrisDeviceServer.exe si aucun port HTTP iris ne répond.</summary>
public static class IrisServerStarter
{
    public static async Task<IrisServerStartResult> TryStartAsync(
        IrisDeviceOptions options,
        ILogger? logger,
        CancellationToken ct = default)
    {
        if (!IrisDeviceOptions.IsDeviceMode(options.Mode))
            return new(false, "Module iris en mode mock", null, null);

        if (!OperatingSystem.IsWindows())
            return new(false, "Démarrage iris : Windows uniquement", null, null);

        var existing = await IrisDeviceHttpProbe.ResolveBaseUrlAsync(options.BaseUrl, ct);
        if (existing is not null)
            return new(true, $"Iris Device Server déjà actif ({existing})", existing, null);

        TryStopStaleServers();

        var exe = options.ResolveServerExe();
        if (exe is null)
        {
            var bin = options.BinPath ?? "(Iris:BinPath non configuré)";
            return new(false, $"IrisDeviceServer.exe introuvable dans {bin}", null, null);
        }

        try
        {
            var psi = new ProcessStartInfo(exe)
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                WorkingDirectory = options.ResolveWorkingDirectory() ?? Path.GetDirectoryName(exe)!,
            };

            var process = Process.Start(psi);
            if (process is null)
                return new(false, "Process.Start a retourné null", null, null);

            logger?.LogInformation("IrisDeviceServer démarré: {Exe} PID {Pid}", exe, process.Id);

            var deadline = DateTime.UtcNow.AddSeconds(Math.Clamp(options.ServerStartupWaitSeconds, 5, 120));
            while (DateTime.UtcNow < deadline && !ct.IsCancellationRequested)
            {
                if (process.HasExited)
                    return new(false, $"IrisDeviceServer arrêté (code {process.ExitCode})", null, process.Id);

                var url = await IrisDeviceHttpProbe.ResolveBaseUrlAsync(options.BaseUrl, ct);
                if (url is not null)
                    return new(true, $"Iris HTTP prêt ({url})", url, process.Id);

                await Task.Delay(500, ct);
            }

            return new(
                false,
                "Timeout HTTP — lancez device-bridge\\scripts\\start-iris-server-admin.bat (admin + UAC), branchez le JD5 USB",
                null,
                process.Id);
        }
        catch (Exception ex)
        {
            logger?.LogError(ex, "Démarrage IrisDeviceServer");
            return new(false, ex.Message, null, null);
        }
    }

    /// <summary>True si un port répond à POST /device/Status (pas seulement TCP ouvert).</summary>
    public static async Task<bool> IsHttpAvailableAsync(IrisDeviceOptions options, CancellationToken ct = default)
    {
        var url = await IrisDeviceHttpProbe.ResolveBaseUrlAsync(options.BaseUrl, ct);
        return url is not null;
    }

    public static bool IsAnyPortListening(IrisDeviceOptions options) =>
        IsHttpAvailableAsync(options).GetAwaiter().GetResult();

    private static void TryStopStaleServers()
    {
        foreach (var proc in Process.GetProcessesByName("IrisDeviceServer"))
        {
            try
            {
                proc.Kill(entireProcessTree: true);
                proc.WaitForExit(3000);
            }
            catch
            {
                /* ignore */
            }
        }
    }
}
