using System.Diagnostics;
using System.Net.Http;
using Fgp.DeviceBridge.Api.Modules;

namespace Fgp.DeviceBridge.Api.Hosting;

/// <summary>Démarre Fgp.CameraGp.Bridge.exe (x86) et attend /health sur le port sidecar.</summary>
public sealed class CameraGpSidecarHostedService : IHostedService, IDisposable
{
    private readonly CameraGpOptions _options;
    private readonly ILogger<CameraGpSidecarHostedService> _logger;
    private Process? _process;

    public CameraGpSidecarHostedService(CameraGpOptions options, ILogger<CameraGpSidecarHostedService> logger)
    {
        _options = options;
        _logger = logger;
    }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        if (!_options.AutoStartSidecar || !OperatingSystem.IsWindows())
            return;

        var sidecarBase = (_options.SidecarUrl ?? "http://127.0.0.1:8766").TrimEnd('/');
        if (await SidecarHealthyAsync(sidecarBase, cancellationToken))
        {
            _logger.LogInformation("Sidecar CameraGP déjà actif: {Url}", sidecarBase);
            return;
        }

        var exe = ResolveSidecarExe();
        if (exe is null)
        {
            _logger.LogWarning(
                "Fgp.CameraGp.Bridge.exe introuvable — build: dotnet build device-bridge/Fgp.DeviceBridge.sln");
            return;
        }

        try
        {
            var psi = new ProcessStartInfo(exe)
            {
                UseShellExecute = false,
                CreateNoWindow = true,
                WorkingDirectory = Path.GetDirectoryName(exe)!,
            };
            psi.Environment["ASPNETCORE_URLS"] = sidecarBase;

            _process = Process.Start(psi);
            _logger.LogInformation("Sidecar CameraGP démarré: {Exe} → {Url} (PID {Pid})", exe, sidecarBase, _process?.Id);

            var deadline = DateTime.UtcNow.AddSeconds(Math.Clamp(_options.SidecarStartupWaitSeconds, 5, 120));
            while (DateTime.UtcNow < deadline && !cancellationToken.IsCancellationRequested)
            {
                if (await SidecarHealthyAsync(sidecarBase, cancellationToken))
                {
                    _logger.LogInformation("Sidecar CameraGP HTTP prêt");
                    return;
                }

                if (_process is { HasExited: true })
                {
                    _logger.LogError("Sidecar arrêté (code {Code}) — installer CameraGPSDKsetup.exe ?", _process.ExitCode);
                    return;
                }

                await Task.Delay(500, cancellationToken);
            }

            _logger.LogWarning("Timeout sidecar — vérifier OCX GPY et caméra USB branchée");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Impossible de démarrer le sidecar CameraGP");
        }
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        if (_process is { HasExited: false })
        {
            try
            {
                _process.Kill(entireProcessTree: true);
                _logger.LogInformation("Sidecar CameraGP arrêté");
            }
            catch (Exception ex)
            {
                _logger.LogDebug(ex, "Arrêt sidecar");
            }
        }

        return Task.CompletedTask;
    }

    private static async Task<bool> SidecarHealthyAsync(string sidecarBase, CancellationToken ct)
    {
        try
        {
            using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(3) };
            var json = await http.GetStringAsync($"{sidecarBase}/health", ct);
            return json.Contains("ok", StringComparison.OrdinalIgnoreCase) ||
                   json.Contains("healthy", StringComparison.OrdinalIgnoreCase) ||
                   json.Contains("device_count", StringComparison.OrdinalIgnoreCase);
        }
        catch
        {
            return false;
        }
    }

    private string? ResolveSidecarExe()
    {
        if (!string.IsNullOrWhiteSpace(_options.SidecarExePath) && File.Exists(_options.SidecarExePath))
            return Path.GetFullPath(_options.SidecarExePath);

        var baseDir = AppContext.BaseDirectory;
        var candidates = new[]
        {
            Path.Combine(baseDir, "Fgp.CameraGp.Bridge.exe"),
            Path.Combine(baseDir, "..", "Fgp.CameraGp.Bridge", "Fgp.CameraGp.Bridge.exe"),
            Path.Combine(baseDir, "..", "..", "..", "Fgp.CameraGp.Bridge", "bin", "Debug", "net8.0-windows", "Fgp.CameraGp.Bridge.exe"),
            Path.Combine(baseDir, "..", "..", "..", "..", "Fgp.CameraGp.Bridge", "bin", "Debug", "net8.0-windows", "Fgp.CameraGp.Bridge.exe"),
            Path.Combine(baseDir, "..", "..", "..", "..", "..", "Fgp.CameraGp.Bridge", "bin", "Debug", "net8.0-windows", "Fgp.CameraGp.Bridge.exe"),
        };

        foreach (var c in candidates)
        {
            var full = Path.GetFullPath(c);
            if (File.Exists(full))
                return full;
        }

        return null;
    }

    public void Dispose() => _process?.Dispose();
}
