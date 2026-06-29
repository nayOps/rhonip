using System.Net.Sockets;
using System.Text;

namespace Fgp.DeviceBridge.Api.Modules.Iris;

internal static class IrisDeviceHttpProbe
{
    /// <summary>Ports courants : HTTP actif souvent sur 50219 (Postman), 50218 = TCP parfois sans HTTP.</summary>
    public static readonly int[] DefaultPorts = [50219, 50218];

    private static readonly TimeSpan TcpProbeTimeout = TimeSpan.FromMilliseconds(600);
    private static readonly TimeSpan HttpProbeTimeout = TimeSpan.FromSeconds(8);

    public static bool IsTcpOpen(string host, int port)
    {
        try
        {
            using var client = new TcpClient();
            var connect = client.ConnectAsync(host, port);
            if (!connect.Wait(TcpProbeTimeout))
                return false;
            return client.Connected;
        }
        catch
        {
            return false;
        }
    }

    public static async Task<(bool Ok, string? Body)> TryStatusAsync(string host, int port, CancellationToken ct = default)
    {
        if (!IsTcpOpen(host, port))
            return (false, null);

        try
        {
            using var handler = new SocketsHttpHandler
            {
                ConnectTimeout = TimeSpan.FromSeconds(1),
                PooledConnectionLifetime = TimeSpan.Zero,
            };
            using var http = new HttpClient(handler) { Timeout = HttpProbeTimeout };
            using var content = new StringContent("{}", Encoding.UTF8, "text/plain");
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            cts.CancelAfter(HttpProbeTimeout);
            var resp = await http.PostAsync($"http://{host}:{port}/device/Status", content, cts.Token);
            var text = await resp.Content.ReadAsStringAsync(cts.Token);
            if (!resp.IsSuccessStatusCode || string.IsNullOrWhiteSpace(text))
                return (false, text);

            return text.Contains("errcode", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("status", StringComparison.OrdinalIgnoreCase)
                ? (true, text)
                : (false, text);
        }
        catch
        {
            return (false, null);
        }
    }

    /// <summary>Retourne l'URL de base si un port répond à /device/Status, sinon null.</summary>
    public static async Task<string?> ResolveBaseUrlAsync(string? configuredBaseUrl, CancellationToken ct = default)
    {
        var host = "127.0.0.1";
        var portsToTry = new List<int>();

        if (Uri.TryCreate(configuredBaseUrl, UriKind.Absolute, out var uri))
        {
            host = uri.Host;
            if (!uri.IsDefaultPort)
                portsToTry.Add(uri.Port);
        }

        foreach (var p in DefaultPorts)
        {
            if (!portsToTry.Contains(p))
                portsToTry.Add(p);
        }

        var probes = portsToTry
            .Select(async port =>
            {
                var (ok, _) = await TryStatusAsync(host, port, ct);
                return ok ? $"http://{host}:{port}" : null;
            })
            .ToArray();

        var results = await Task.WhenAll(probes);
        return results.FirstOrDefault(r => r is not null);
    }
}
