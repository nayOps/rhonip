# Vérifie le service WebSocket CameraGP (GPY / XHY) — port 9002
# Usage: powershell -ExecutionPolicy Bypass -File scripts/check-gpy-ws.ps1

$port = 9002
$hostName = "127.0.0.1"

Write-Host "=== CameraGP / GPY — diagnostic port $port ===" -ForegroundColor Cyan

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    $pid = $listener.OwningProcess | Select-Object -First 1
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    Write-Host "[OK] Port $port en ecoute (PID $pid — $($proc.ProcessName))" -ForegroundColor Green
} else {
    Write-Host "[KO] Rien n'ecoute sur le port $port" -ForegroundColor Red
    Write-Host ""
    Write-Host "La camera USB peut etre detectee par Windows sans le service SDK." -ForegroundColor Yellow
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  1. Installer: sdk\gpy\SDK\_extracted\CameraGPSDKsetup.exe"
    Write-Host "  2. Lancer l'application GPYScan / CameraGP (menu Demarrer ou barre des taches)"
    Write-Host "  3. Relancer ce script"
    Write-Host ""
    $setup = Join-Path $PSScriptRoot "..\..\..\gpy\SDK\_extracted\CameraGPSDKsetup.exe"
    if (Test-Path $setup) {
        Write-Host "Installateur trouve: $setup"
    }
    $demo = Join-Path $PSScriptRoot "..\..\..\gpy\SDK\_extracted\Sample\html\newEaxmpleOneSimple.html"
    if (Test-Path $demo) {
        Write-Host "Test manuel (Edge): file:///$($demo -replace '\\','/')"
    }
}

Write-Host ""
Write-Host "Test WebSocket rapide..." -ForegroundColor Cyan
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $async = $tcp.BeginConnect($hostName, $port, $null, $null)
    $ok = $async.AsyncWaitHandle.WaitOne(2000, $false)
    if ($ok -and $tcp.Connected) {
        Write-Host "[OK] Connexion TCP $hostName`:$port reussie" -ForegroundColor Green
        $tcp.Close()
    } else {
        Write-Host "[KO] Connexion TCP $hostName`:$port impossible (timeout)" -ForegroundColor Red
        $tcp.Close()
    }
} catch {
    Write-Host "[KO] $($_.Exception.Message)" -ForegroundColor Red
}
