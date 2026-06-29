# Prépare le SDK FAP60 et démarre le Device Bridge
$ErrorActionPreference = "Stop"

$apiDir = Join-Path $PSScriptRoot "..\src\Fgp.DeviceBridge.Api"

& (Join-Path $PSScriptRoot "copy-fap60-sdk.ps1")
& (Join-Path $PSScriptRoot "verify-iris-sdk.ps1")

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "ERREUR: .NET SDK non installé." -ForegroundColor Red
    Write-Host "Téléchargez .NET 8 SDK: https://dotnet.microsoft.com/download/dotnet/8.0"
    Write-Host "Redémarrez PowerShell après installation."
    exit 1
}

Write-Host ".NET $(dotnet --version)"
Write-Host "Device Bridge: http://127.0.0.1:8765 (FAP60 + iris JD5 + camera GPY)"
Write-Host "Iris Device Server: port 50218 (démarré auto si Iris:Mode=device)"
Write-Host "Sidecar caméra x86: http://127.0.0.1:8766 (démarré auto si Camera:Mode=gpy)"
Write-Host "Dans un 2e terminal: .\probe-devices.ps1"
Write-Host ""

$env:ASPNETCORE_ENVIRONMENT = "Development"
Set-Location (Resolve-Path $apiDir)
dotnet run
