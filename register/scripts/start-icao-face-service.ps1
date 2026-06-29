# Démarre le service ICAO Face Quality Assistant (port 50270 par défaut)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$SvcDir = Join-Path $Root "icao-face-service"
$Venv = Join-Path $SvcDir ".venv"

function Get-PythonExe {
    if (Get-Command py -ErrorAction SilentlyContinue) { return @{ Exe = "py"; Args = @("-3") } }
    if (Get-Command python -ErrorAction SilentlyContinue) { return @{ Exe = "python"; Args = @() } }
    return $null
}

$py = Get-PythonExe
if (-not $py) {
    Write-Host "Python 3 introuvable — installez Python 3.10+ puis relancez." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $Venv)) {
    Write-Host "Création de l'environnement virtuel…" -ForegroundColor Cyan
    & $py.Exe @($py.Args + @("-m", "venv", $Venv))
    & (Join-Path $Venv "Scripts\pip.exe") install -r (Join-Path $SvcDir "requirements.txt")
}

$env:ICAO_FACE_PORT = if ($env:ICAO_FACE_PORT) { $env:ICAO_FACE_PORT } else { "50270" }
Write-Host "ICAO Face Service → http://127.0.0.1:$($env:ICAO_FACE_PORT)" -ForegroundColor Green
Set-Location $SvcDir
& (Join-Path $Venv "Scripts\python.exe") -m app.main
