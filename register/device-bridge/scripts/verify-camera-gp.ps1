# Verifie le sidecar CameraGP (COM GPY) pour le Device Bridge
$ErrorActionPreference = "Continue"

$bridgeUrl = "http://127.0.0.1:8765"
$sidecarUrl = "http://127.0.0.1:8766"

Write-Host "Device Bridge: $bridgeUrl" -ForegroundColor Cyan
Write-Host "Sidecar CameraGP: $sidecarUrl" -ForegroundColor Cyan

$baseDir = Join-Path $PSScriptRoot "..\src\Fgp.DeviceBridge.Api\bin\Debug\net8.0"
$sidecarExe = Join-Path $baseDir "Fgp.CameraGp.Bridge.exe"
if (Test-Path $sidecarExe) {
    Write-Host "OK  Fgp.CameraGp.Bridge.exe (sortie Api)" -ForegroundColor Green
} else {
    $alt = Join-Path $PSScriptRoot "..\src\Fgp.CameraGp.Bridge\bin\Debug\net8.0-windows\Fgp.CameraGp.Bridge.exe"
    if (Test-Path $alt) {
        Write-Host "OK  Fgp.CameraGp.Bridge.exe (projet, pas encore copie vers Api)" -ForegroundColor Yellow
    } else {
        Write-Host "KO  Fgp.CameraGp.Bridge.exe absent - build avec Visual Studio (projet x86 COM)" -ForegroundColor Red
        Write-Host "    ou: dotnet build device-bridge\Fgp.DeviceBridge.sln (Api seulement)" -ForegroundColor Red
    }
}

try {
    $health = Invoke-RestMethod -Uri "$bridgeUrl/health" -TimeoutSec 5
    Write-Host "OK  Bridge /health" -ForegroundColor Green
    $health | ConvertTo-Json -Depth 4
} catch {
    Write-Host "KO  Bridge injoignable - lancer .\start-device-bridge.cmd" -ForegroundColor Red
}

try {
    $side = Invoke-RestMethod -Uri "$sidecarUrl/health" -TimeoutSec 5
    Write-Host "OK  Sidecar /health" -ForegroundColor Green
    $side | ConvertTo-Json -Depth 4
} catch {
    Write-Host "INFO Sidecar 8766 ferme - AutoStartSidecar au demarrage du bridge" -ForegroundColor Yellow
}

try {
    $cam = Invoke-RestMethod -Uri "$bridgeUrl/api/v1/devices/camera/status" -TimeoutSec 10
    Write-Host 'Camera proxy status:' -ForegroundColor Cyan
    $cam | ConvertTo-Json -Depth 4
    if ($cam.available) {
        Write-Host "OK  Camera disponible" -ForegroundColor Green
    } else {
        Write-Host "INFO Camera indisponible - installer CameraGPSDKsetup.exe, brancher USB" -ForegroundColor Yellow
    }
} catch {
    Write-Host "KO  GET camera/status" -ForegroundColor Red
}
