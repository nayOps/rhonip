using System.Diagnostics;
using Fgp.DeviceBridge.Api.Modules;

namespace Fgp.DeviceBridge.Api.Hosting;

public sealed class PosPrinterSidecarHostedService : IHostedService, IDisposable
{
    private readonly PosPrinterOptions _options;
    private readonly ILogger<PosPrinterSidecarHostedService> _logger;
    private Process? _process;

    public PosPrinterSidecarHostedService(PosPrinterOptions options, ILogger<PosPrinterSidecarHostedService> logger)
    {
        _options = options;
        _logger = logger;
    }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        if (!_options.AutoStartSidecar || !OperatingSystem.IsWindows())
            return;

        var sidecarBase = (_options.SidecarUrl ?? "http://127.0.0.1:8767").TrimEnd('/');
        if (await SidecarHealthyAsync(sidecarBase, cancellationToken))
        {
            _logger.LogInformation("Sidecar POS déjà actif: {Url}", sidecarBase);
            return;
        }

        var exe = ResolveSidecarExe();
        if (exe is null)
        {
            _logger.LogWarning("Fgp.PosPrinter.Bridge.exe introuvable — build-pos-sidecar.cmd");
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
            psi.ArgumentList.Add("--urls");
            psi.ArgumentList.Add(sidecarBase);
            psi.Environment["ASPNETCORE_URLS"] = sidecarBase;

            _process = Process.Start(psi);
            _logger.LogInformation("Sidecar POS démarré: {Exe} → {Url}", exe, sidecarBase);

            var deadline = DateTime.UtcNow.AddSeconds(Math.Clamp(_options.SidecarStartupWaitSeconds, 5, 120));
            while (DateTime.UtcNow < deadline && !cancellationToken.IsCancellationRequested)
            {
                if (await SidecarHealthyAsync(sidecarBase, cancellationToken))
                {
                    _logger.LogInformation("Sidecar POS HTTP prêt");
                    return;
                }

                if (_process is { HasExited: true })
                {
                    _logger.LogError("Sidecar POS arrêté (code {Code})", _process.ExitCode);
                    return;
                }

                await Task.Delay(500, cancellationToken);
            }

            _logger.LogWarning("Timeout sidecar POS — vérifiez POS_SDK.dll et imprimante USB");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Impossible de démarrer le sidecar POS");
        }
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        if (_process is { HasExited: false })
        {
            try { _process.Kill(entireProcessTree: true); }
            catch { /* ignore */ }
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
                   json.Contains("pos-sdk", StringComparison.OrdinalIgnoreCase);
        }
        catch
        {
            return false;
        }
    }

    private string? ResolveSidecarExe()
    {
        var baseDir = AppContext.BaseDirectory;
        var candidates = new[]
        {
            Path.Combine(baseDir, "pos-sidecar", "Fgp.PosPrinter.Bridge.exe"),
            Path.Combine(baseDir, "Fgp.PosPrinter.Bridge.exe"),
            Path.Combine(baseDir, "..", "..", "..", "Fgp.PosPrinter.Bridge", "bin", "Debug", "net8.0", "Fgp.PosPrinter.Bridge.exe"),
            Path.Combine(baseDir, "..", "..", "..", "..", "Fgp.PosPrinter.Bridge", "bin", "Debug", "net8.0", "Fgp.PosPrinter.Bridge.exe"),
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
