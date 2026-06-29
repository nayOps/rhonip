# Redemarre IrisDeviceServer proprement (HTTP sur 50219).
$ErrorActionPreference = "Stop"
$bin = "C:\Users\HYF\Documents\sdk\iris\bin"
if (-not (Test-Path $bin)) {
    Write-Host "KO  Dossier introuvable: $bin" -ForegroundColor Red
    exit 1
}

Write-Host "Arret des instances IrisDeviceServer..." -ForegroundColor Cyan
Get-Process IrisDeviceServer -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

$exe = Join-Path $bin "IrisDeviceServer.exe"
if (-not (Test-Path $exe)) {
    Write-Host "KO  $exe manquant" -ForegroundColor Red
    exit 1
}

Write-Host "Demarrage $exe ..." -ForegroundColor Cyan
Start-Process -FilePath $exe -WorkingDirectory $bin | Out-Null

$deadline = (Get-Date).AddSeconds(25)
$ok = $false
while ((Get-Date) -lt $deadline) {
    foreach ($port in @(50219, 50218)) {
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:$port/device/Status" -Method POST -Body "{}" `
                -ContentType "text/plain" -TimeoutSec 5 -UseBasicParsing
            if ($r.Content -match "errcode") {
                Write-Host "OK  HTTP iris sur port $port" -ForegroundColor Green
                Write-Host "    $($r.Content.Trim())" -ForegroundColor DarkGray
                $ok = $true
                break
            }
        } catch {
            /* retry */
        }
    }
    if ($ok) { break }
    Start-Sleep -Milliseconds 500
}

if (-not $ok) {
    Write-Host "KO  Pas de HTTP sur 50219 — verifiez le pare-feu ou lancez 启用HTTP服务.bat (admin) une fois." -ForegroundColor Red
    exit 1
}

Write-Host "Si Ouvrir lecteur echoue: utilisez start-iris-server-admin.bat (admin + UAC)." -ForegroundColor Yellow
Write-Host "Puis: Device Bridge (8765), Analyse -> Relancer, etape iris -> Ouvrir lecteur." -ForegroundColor Green
