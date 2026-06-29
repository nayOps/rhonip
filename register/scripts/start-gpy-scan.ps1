# Demarre GPYScan / CameraGP si possible, puis verifie le port 9002
# Usage: powershell -ExecutionPolicy Bypass -File scripts/start-gpy-scan.ps1

$port = 9002
$names = @('GPYScan', 'GPYScanOffice', 'CameraGP', 'GPScan', 'ScanOffice', 'eloam', 'Eloam')

function Test-PortOpen {
    param([int]$P)
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $ar = $c.BeginConnect('127.0.0.1', $P, $null, $null)
        if ($ar.AsyncWaitHandle.WaitOne(1500) -and $c.Connected) {
            $c.Close()
            return $true
        }
        $c.Close()
    } catch {}
    return $false
}

if (Test-PortOpen $port) {
    Write-Host "[OK] Port $port deja ouvert — service CameraGP actif." -ForegroundColor Green
    exit 0
}

Write-Host "Recherche GPYScan / CameraGP..." -ForegroundColor Cyan

$started = $false
$searchRoots = @(
    "${env:ProgramFiles}",
    "${env:ProgramFiles(x86)}",
    "C:\GPYScan",
    "C:\CameraGP"
)

foreach ($root in $searchRoots) {
    if (-not (Test-Path $root)) { continue }
    Get-ChildItem $root -Recurse -Filter "*.exe" -ErrorAction SilentlyContinue | ForEach-Object {
        foreach ($n in $names) {
            if ($_.BaseName -like "*$n*") {
                Write-Host "Lancement: $($_.FullName)"
                Start-Process -FilePath $_.FullName -WindowStyle Normal
                $started = $true
                Start-Sleep -Seconds 4
                if (Test-PortOpen $port) {
                    Write-Host "[OK] Port $port ouvert apres lancement." -ForegroundColor Green
                    exit 0
                }
            }
        }
    }
}

if (-not $started) {
    Write-Host "[INFO] Executable GPYScan introuvable automatiquement." -ForegroundColor Yellow
    $setup = Join-Path $PSScriptRoot "..\..\..\gpy\SDK\_extracted\CameraGPSDKsetup.exe"
    if (Test-Path $setup) {
        Write-Host "Installez d'abord: $setup"
        Write-Host "Puis lancez GPYScan depuis le menu Demarrer (icone barre des taches)."
    }
}

Write-Host "[KO] Port $port toujours ferme. Lancez GPYScan manuellement puis: scripts\check-gpy-ws.ps1" -ForegroundColor Red
exit 1
