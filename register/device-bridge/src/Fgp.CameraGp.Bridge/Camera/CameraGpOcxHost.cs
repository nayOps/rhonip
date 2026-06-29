namespace Fgp.CameraGp.Bridge.Camera;

/// <summary>Thread STA dédié pour l'OCX ActiveX (obligatoire COM).</summary>
public sealed class CameraGpOcxHost : IDisposable
{
    private readonly Thread _thread;
    private readonly ManualResetEventSlim _ready = new(false);
    private CameraGpHostForm? _form;
    private bool _disposed;

    public CameraGpOcxHost()
    {
        _thread = new Thread(RunStaMessageLoop)
        {
            IsBackground = true,
            Name = "CameraGp-STA",
        };
        _thread.SetApartmentState(ApartmentState.STA);
        _thread.Start();
        _ready.Wait();
    }

    public Task<T> InvokeAsync<T>(Func<CameraGpHostForm, T> action, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (_form is null || _form.IsDisposed)
            throw new InvalidOperationException("Hôte OCX arrêté");

        var tcs = new TaskCompletionSource<T>(TaskCreationOptions.RunContinuationsAsynchronously);
        ct.Register(() => tcs.TrySetCanceled(ct));

        void Run()
        {
            try
            {
                var result = action(_form!);
                tcs.TrySetResult(result);
            }
            catch (Exception ex)
            {
                tcs.TrySetException(ex);
            }
        }

        if (_form.InvokeRequired)
            _form.BeginInvoke(Run);
        else
            Run();

        return tcs.Task;
    }

    private void RunStaMessageLoop()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.SetHighDpiMode(HighDpiMode.SystemAware);
        _form = new CameraGpHostForm();
        _ready.Set();
        Application.Run(_form);
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        if (_form is { IsDisposed: false })
        {
            try
            {
                _form.Invoke(() =>
                {
                    _form.CloseCamera();
                    _form.Close();
                });
            }
            catch { /* ignore */ }
        }

        try { Application.ExitThread(); } catch { /* ignore */ }
        _ready.Dispose();
    }
}
