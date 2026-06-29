# Verifie HTTP iris (50219 / 50218), le lecteur JD5 USB et le bridge.
param(
    [string]$IrisHost = "127.0.0.1",
    [string]$BridgeUrl = "http://127.0.0.1:8765",
    [string]$IrisBin = "C:\Users\HYF\Documents\sdk\iris\bin"
)

$httpPort = $null
Write-Host "=== Iris Device Server HTTP ===" -ForegroundColor Cyan
foreach ($port in @(50219, 50218)) {
    try {
        $r = Invoke-WebRequest -Uri "http://${IrisHost}:$port/device/Status" -Method POST -Body "{}" `
            -ContentType "text/plain" -TimeoutSec 5 -UseBasicParsing
        if ($r.Content -match "errcode") {
            Write-Host "OK  HTTP actif sur port $port" -ForegroundColor Green
            Write-Host "    $($r.Content.Trim())" -ForegroundColor DarkGray
            $httpPort = $port
            break
        }
    } catch {
        Write-Host "KO  Port $port : pas de reponse HTTP" -ForegroundColor Yellow
    }
}
if (-not $httpPort) {
    Write-Host "-> Lancer IrisDeviceServer.exe puis enable-http-service.bat (admin) dans $IrisBin" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Fichiers SDK ===" -ForegroundColor Cyan
$files = @(
    "IrisDeviceServer.exe",
    "DeviceUI.exe"
)
foreach ($rel in $files) {
    $p = Join-Path $IrisBin $rel
    if (Test-Path $p) {
        Write-Host "OK  $rel" -ForegroundColor Green
    } else {
        Write-Host "KO  $rel" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== USB (JD5 / Iris) ===" -ForegroundColor Cyan
$jd5Present = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object {
    $_.InstanceId -match 'VID_1234&PID_0101'
}
$jd7Present = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object {
    $_.InstanceId -match 'VID_2285&PID_2F11'
}
$otherIris = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object {
    $_.FriendlyName -match 'iris|JD7|Iris|Herrick|DM520|WLH|JD5'
}
if ($jd5Present) {
    Write-Host "OK  JD5 / IRIS-SCANNER (VID_1234 and PID_0101) :" -ForegroundColor Green
    $jd5Present | Format-Table FriendlyName, Status, Class, InstanceId -AutoSize
} elseif ($jd7Present) {
    Write-Host "OK  JD7 (VID_2285 and PID_2F11) — driver JD7Driver si besoin :" -ForegroundColor Green
    $jd7Present | Format-Table FriendlyName, Status, Class, InstanceId -AutoSize
} elseif ($otherIris) {
    Write-Host "Peripherique iris detecte :" -ForegroundColor Yellow
    $otherIris | Format-Table FriendlyName, Status, Class, InstanceId -AutoSize
} else {
    Write-Host "Aucun peripherique iris branche (PresentOnly)." -ForegroundColor Yellow
}

if ($httpPort) {
    Write-Host ""
    Write-Host "=== Iris HTTP Model / Open ===" -ForegroundColor Cyan
    foreach ($ep in @("Model", "Open")) {
        try {
            $r = Invoke-WebRequest -Uri "http://${IrisHost}:$httpPort/device/$ep" -Method POST -Body "{}" `
                -ContentType "text/plain" -TimeoutSec 15 -UseBasicParsing
            Write-Host "${ep}: $($r.Content.Trim())" -ForegroundColor DarkGray
        } catch {
            Write-Host "${ep}: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Device Bridge iris/status ===" -ForegroundColor Cyan
try {
    $status = Invoke-RestMethod -Uri "$BridgeUrl/api/v1/devices/iris/status" -Method Get -TimeoutSec 20
    if ($status.available) {
        $color = "Green"
    } else {
        $color = "Yellow"
    }
    Write-Host "available:     $($status.available)" -ForegroundColor $color
    Write-Host "server_port:   $($status.server_port)"
    Write-Host "device_model:  $($status.device_model)"
    Write-Host "device_status: $($status.device_status)"
    Write-Host "errcode:       $($status.errcode)"
    Write-Host "message:       $($status.message)"
    if (-not $status.available -and $httpPort) {
        Write-Host ""
        Write-Host "HTTP OK mais lecteur non ouvert — Ouvrir lecteur ou DeviceUI.exe." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Bridge injoignable ($BridgeUrl)" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

$instances = @(Get-Process IrisDeviceServer -ErrorAction SilentlyContinue)
if ($instances.Count -gt 1) {
    Write-Host ""
    Write-Host "ATTENTION: $($instances.Count) processus IrisDeviceServer — gardez-en un seul." -ForegroundColor Yellow
}
