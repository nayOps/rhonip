# Raccourci — le service ICAO vit sous fgp\fgp\scripts\
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Main = Join-Path $Root "scripts\start-icao-face-service.ps1"
if (-not (Test-Path $Main)) {
    Write-Host "Script introuvable : $Main" -ForegroundColor Red
    exit 1
}
& $Main @args
