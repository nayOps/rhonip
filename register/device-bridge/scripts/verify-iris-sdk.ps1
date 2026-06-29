# Vérifie la présence du SDK iris pour le Device Bridge (mode device)
$ErrorActionPreference = "Continue"

$binPath = $env:IRIS_BIN_PATH
if (-not $binPath) {
    $settings = Join-Path $PSScriptRoot "..\src\Fgp.DeviceBridge.Api\appsettings.json"
    if (Test-Path $settings) {
        $json = Get-Content $settings -Raw | ConvertFrom-Json
        $binPath = $json.Iris.BinPath
    }
}
if (-not $binPath) {
    $binPath = "C:\Users\HYF\Documents\sdk\iris\bin"
}

Write-Host "Iris BinPath: $binPath" -ForegroundColor Cyan
if (-not (Test-Path $binPath)) {
    Write-Host "KO  Dossier introuvable" -ForegroundColor Red
    exit 1
}

$required = @("IrisDeviceServer.exe", "device_server.json")
$ok = $true
foreach ($f in $required) {
    $p = Join-Path $binPath $f
    if (Test-Path $p) {
        Write-Host "OK  $f" -ForegroundColor Green
    } else {
        Write-Host "KO  $f manquant" -ForegroundColor Red
        $ok = $false
    }
}

$port = 50218
try {
    $json = Get-Content (Join-Path $binPath "device_server.json") -Raw | ConvertFrom-Json
    if ($json.ServerPort) { $port = [int]$json.ServerPort }
} catch { }

Write-Host "Port HTTP attendu: $port"
$tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port $port -WarningAction SilentlyContinue
if ($tcp.TcpTestSucceeded) {
    Write-Host "OK  Port $port ouvert (serveur déjà actif)" -ForegroundColor Green
} else {
    Write-Host "INFO Port $port fermé — le bridge peut démarrer IrisDeviceServer.exe (AutoStartServer)" -ForegroundColor Yellow
}

if (-not $ok) { exit 1 }
