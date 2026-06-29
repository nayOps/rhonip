using System.Diagnostics;
using System.Net.Sockets;
using Fgp.DeviceBridge.Api.Modules.Iris;

namespace Fgp.DeviceBridge.Api.Hosting;

/// <summary>Démarre IrisDeviceServer.exe si AutoStartServer et port HTTP fermé.</summary>
public sealed class IrisDeviceServerHostedService : IHostedService, IDisposable
{
    private readonly IrisDeviceOptions _options;
    private readonly ILogger<IrisDeviceServerHostedService> _logger;
    private Process? _process;
    private bool _startedByBridge;

    public IrisDeviceServerHostedService(
        IrisDeviceOptions options,
        ILogger<IrisDeviceServerHostedService> logger)
    {
        _options = options;
        _logger = logger;
    }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        if (!_options.AutoStartServer || !IrisDeviceOptions.IsDeviceMode(_options.Mode))
            return;

        if (!OperatingSystem.IsWindows())
        {
            _logger.LogWarning("Iris Device Server auto-start : Windows uniquement");
            return;
        }

        var result = await IrisServerStarter.TryStartAsync(_options, _logger, cancellationToken);
        if (result.Success)
            _logger.LogInformation("Iris auto-start: {Message}", result.Message);
        else if (!string.IsNullOrWhiteSpace(result.Message))
            _logger.LogWarning("Iris auto-start: {Message}", result.Message);
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        if (_startedByBridge && _process is { HasExited: false })
        {
            try
            {
                _process.Kill(entireProcessTree: true);
                _logger.LogInformation("Iris Device Server arrêté (démarré par le bridge)");
            }
            catch (Exception ex)
            {
                _logger.LogDebug(ex, "Arrêt IrisDeviceServer");
            }
        }

        return Task.CompletedTask;
    }

    public void Dispose() => _process?.Dispose();
}
