using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using AxCameraGPOcxLib;

namespace Fgp.CameraGp.Bridge.Camera;

/// <summary>Formulaire caché hébergeant l'OCX CameraGP sur thread STA (comme testOcx).</summary>
public sealed class CameraGpHostForm : Form
{
    private readonly AxCameraGPOcx _ocx;
    private int _camId;
    private int _openFormat = 1;
    private int _supportFormat = 1;
    private int _width;
    private int _height;
    private bool _isOpen;

    public CameraGpHostForm()
    {
        Text = "FGP CameraGP Host";
        ShowInTaskbar = false;
        WindowState = FormWindowState.Minimized;
        Opacity = 0;
        Width = 1;
        Height = 1;

        _ocx = new AxCameraGPOcx();
        ((System.ComponentModel.ISupportInitialize)_ocx).BeginInit();
        _ocx.Dock = DockStyle.Fill;
        _ocx.Enabled = true;
        Controls.Add(_ocx);
        ((System.ComponentModel.ISupportInitialize)_ocx).EndInit();

        _ocx.MessageCallback += OnMessageCallback;
    }

    public bool IsOpen => _isOpen;
    public int DeviceCount => Safe(() => _ocx.GetDevCount());

    public IReadOnlyList<(int Id, string Name)> ListDevices()
    {
        var count = _ocx.GetDevCount();
        var list = new List<(int, string)>(count);
        for (var i = 0; i < count; i++)
            list.Add((i, _ocx.GetDevFriendName(i) ?? $"Camera {i}"));
        return list;
    }

    public (bool Success, string Message) Open(int? preferredWidth = 1920, int? preferredHeight = 1080)
    {
        if (_isOpen)
            return (true, $"Déjà ouvert — {_width}×{_height}");

        var count = _ocx.GetDevCount();
        if (count <= 0)
            return (false, "Aucune caméra USB — branchez la XHY-D500 (GPY) et relancez.");

        var tried = new List<string>();
        foreach (var camId in RankCameraIds(count))
        {
            ConfigureFormatForDevice(camId);
            var name = Safe(() => _ocx.GetDevFriendName(camId)) ?? $"#{camId}";
            foreach (var (w, h, resLabel) in ListResolutions(camId, preferredWidth, preferredHeight))
            {
                var code = _ocx.CAM_Open(camId, _openFormat, w, h);
                if (code == 0)
                {
                    _camId = camId;
                    _isOpen = true;
                    _width = w;
                    _height = h;
                    _ocx.SetFileType(0);
                    _ocx.IsImageBase64(1);
                    var label = string.IsNullOrWhiteSpace(name) ? $"caméra {camId}" : name;
                    return (true, $"Caméra ouverte — {label}, {resLabel}");
                }

                tried.Add($"{name} ({camId}) {resLabel} → {DescribeOpenCode(code)}");
            }
        }

        var deviceList = string.Join(", ", ListDevices().Select(d => $"{d.Id}:{d.Name}"));
        return (false,
            "Aucune caméra GPY/XHY ouverte (code -1 = modèle non certifié par l'OCX). " +
            $"Périphériques vus : [{deviceList}]. " +
            "Branchez la XHY-D500, débranchez les webcams (HP, etc.), fermez GPYScan. " +
            $"Essais : {string.Join("; ", tried.Take(6))}");
    }

    public void CloseCamera()
    {
        if (!_isOpen) return;
        try { _ocx.CAM_Close(); } catch { /* ignore */ }
        _isOpen = false;
        _width = 0;
        _height = 0;
    }

    public string? GetPreviewJpegBase64()
    {
        if (!_isOpen || _width == 0 || _height == 0)
            return null;

        var ptr = _ocx.GetRGBData();
        if (ptr == 0) return null;

        unsafe
        {
            var len = _width * _height * 3;
            var rgb = new byte[len];
            var src = (byte*)ptr;
            for (var i = 0; i < len; i++)
                rgb[i] = src[i];

            using var bmp = new Bitmap(_width, _height, PixelFormat.Format24bppRgb);
            var data = bmp.LockBits(new Rectangle(0, 0, _width, _height), ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
            Marshal.Copy(rgb, 0, data.Scan0, len);
            bmp.UnlockBits(data);

            using var ms = new MemoryStream();
            bmp.Save(ms, ImageFormat.Jpeg);
            return Convert.ToBase64String(ms.ToArray());
        }
    }

    public async Task<(bool Success, string Message, string? ImageBase64)> CaptureImageAsync(
        bool autoCut,
        int timeoutMs,
        CancellationToken ct)
    {
        if (!_isOpen)
            return (false, "Caméra non ouverte", null);

        var tcs = new TaskCompletionSource<string?>(TaskCreationOptions.RunContinuationsAsynchronously);

        void Handler(object? s, _DCameraGPOcxEvents_MessageCallbackEvent e)
        {
            if (e.type == 8 && !string.IsNullOrWhiteSpace(e.str))
                tcs.TrySetResult(e.str);
            else if (e.type == 1 && !string.IsNullOrWhiteSpace(e.str))
            {
                try
                {
                    if (File.Exists(e.str))
                    {
                        var bytes = File.ReadAllBytes(e.str);
                        tcs.TrySetResult(Convert.ToBase64String(bytes));
                    }
                }
                catch
                {
                    /* attendre éventuel callback base64 (type 8) */
                }
            }
        }

        _ocx.MessageCallback += Handler;
        try
        {
            _ocx.SetAutoCut(autoCut ? 1 : 0);
            _ocx.IsImageBase64(1);
            _ocx.SetFileType(1);
            _ocx.CaptureImage();

            using var linked = CancellationTokenSource.CreateLinkedTokenSource(ct);
            linked.CancelAfter(timeoutMs);
            await using var reg = linked.Token.Register(() => tcs.TrySetCanceled(linked.Token));

            var b64 = await tcs.Task.ConfigureAwait(true);
            if (string.IsNullOrWhiteSpace(b64))
                return (false, "Capture document sans image", null);

            return (true, autoCut ? "Scan document (découpage auto)" : "Scan document", b64);
        }
        catch (OperationCanceledException)
        {
            return (false, "Délai scan document dépassé", null);
        }
        catch (Exception ex)
        {
            return (false, ex.Message, null);
        }
        finally
        {
            _ocx.MessageCallback -= Handler;
        }
    }

    public async Task<(bool Success, string Message, string? ImageBase64)> CaptureFaceAsync(int timeoutMs, CancellationToken ct)
    {
        if (!_isOpen)
            return (false, "Caméra non ouverte", null);

        var tcs = new TaskCompletionSource<string?>(TaskCreationOptions.RunContinuationsAsynchronously);

        void Handler(object? s, _DCameraGPOcxEvents_MessageCallbackEvent e)
        {
            if (e.type == 8 && !string.IsNullOrWhiteSpace(e.str))
                tcs.TrySetResult(e.str);
            else if (e.type == 5)
                tcs.TrySetException(new InvalidOperationException($"Capture échouée: {e.str}"));
            else if (e.type == 50)
                tcs.TrySetException(new InvalidOperationException("Recadrage automatique hors limites"));
        }

        _ocx.MessageCallback += Handler;
        try
        {
            var faceOk = _ocx.InitFaceCheck();
            if (faceOk != 1)
                return (false, "InitFaceCheck refusé — visage non détecté ou SDK indisponible", null);

            _ocx.CaptureFace();

            using var linked = CancellationTokenSource.CreateLinkedTokenSource(ct);
            linked.CancelAfter(timeoutMs);
            await using var reg = linked.Token.Register(() => tcs.TrySetCanceled(linked.Token));

            var b64 = await tcs.Task.ConfigureAwait(true);
            if (string.IsNullOrWhiteSpace(b64))
                return (false, "Capture sans image", null);

            return (true, "Capture visage OK", b64);
        }
        catch (OperationCanceledException)
        {
            return (false, "Délai capture dépassé", null);
        }
        catch (Exception ex)
        {
            return (false, ex.Message, null);
        }
        finally
        {
            _ocx.MessageCallback -= Handler;
            try { _ocx.DeInitFaceCheck(); } catch { /* ignore */ }
        }
    }

    private IEnumerable<int> RankCameraIds(int count)
    {
        var ids = Enumerable.Range(0, count).Select(id =>
        {
            var name = (Safe(() => _ocx.GetDevFriendName(id)) ?? "").ToLowerInvariant();
            var score = 0;
            if (name.Contains("xhy") || name.Contains("gpy") || name.Contains("d500") || name.Contains("cameragp"))
                score += 100;
            if (name.Contains("罗技") || name.Contains("logitech") || name.Contains("c930") || name.Contains("高清网络摄像机"))
                score += 90;
            if (string.IsNullOrWhiteSpace(name))
                score += 40;
            if (name.Contains("hp") || name.Contains("webcam") || name.Contains("integrated") || name.Contains("usb video"))
                score -= 80;
            return (id, score);
        }).OrderByDescending(x => x.score).Select(x => x.id).ToList();

        if (count > 1)
        {
            try
            {
                var main = _ocx.GetMainCameraID(1);
                if (!ids.Contains(main))
                    ids.Insert(0, main);
                else
                {
                    ids.Remove(main);
                    ids.Insert(0, main);
                }
            }
            catch { /* ignore */ }
        }

        return ids;
    }

    private void ConfigureFormatForDevice(int camId)
    {
        _camId = camId;
        var formatSum = _ocx.GetFormatCount(camId);
        switch (formatSum)
        {
            case 1:
                _openFormat = 1;
                _supportFormat = 1;
                break;
            case 2:
                _openFormat = 0;
                _supportFormat = 2;
                break;
            case 3:
                _openFormat = 1;
                _supportFormat = 1;
                break;
            default:
                _openFormat = 1;
                _supportFormat = 1;
                break;
        }
    }

    private List<(int W, int H, string Label)> ListResolutions(int camId, int? prefW, int? prefH)
    {
        var list = new List<(int W, int H, string Label)>();
        var n = _ocx.GetResolutionCount(camId, _supportFormat);
        for (var j = 0; j < n; j++)
        {
            var s = _ocx.GetResolution(j) ?? "";
            if (TryParseResolution(s, out var w, out var h))
                list.Add((W: w, H: h, Label: s));
        }

        if (list.Count == 0)
            return list;

        return list
            .OrderByDescending(r =>
            {
                var score = r.W * r.H / 1000;
                if (prefW.HasValue && r.W == prefW.Value) score += 1000;
                if (prefH.HasValue && r.H == prefH.Value) score += 1000;
                return score;
            })
            .ToList();
    }

    private static string DescribeOpenCode(int code) => code switch
    {
        -1 => "non reconnu (pas GPY)",
        -2 => "échec ouverture",
        _ => $"code {code}",
    };

    private static bool TryParseResolution(string sizeStr, out int width, out int height)
    {
        width = 0;
        height = 0;
        var pos = sizeStr.LastIndexOf('*');
        if (pos < 0) pos = sizeStr.LastIndexOf('x');
        if (pos < 0) return false;
        if (!int.TryParse(sizeStr[..pos].Trim(), out width)) return false;
        if (!int.TryParse(sizeStr[(pos + 1)..].Trim(), out height)) return false;
        return width > 0 && height > 0;
    }

    private void OnMessageCallback(object? sender, _DCameraGPOcxEvents_MessageCallbackEvent e)
    {
        // réservé — handlers par capture
    }

    private T Safe<T>(Func<T> fn)
    {
        try { return fn(); }
        catch { return default!; }
    }
}
