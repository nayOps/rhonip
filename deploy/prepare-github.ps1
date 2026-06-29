# Prépare le push GitHub
# Usage : .\deploy\prepare-github.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent

Write-Host "==> Export base de donnees..."
& (Join-Path $RepoRoot "deploy\backup\export-db.ps1")

Write-Host ""
Write-Host "==> Pret pour GitHub :"
Write-Host "  Code  : rh/, register/, compose/, deploy/, attendanceapk/"
Write-Host "  Dump  : deploy/backups/onip_rh_production.sql"
Write-Host "  Exclus: .env, agents/, node_modules/, build/"
Write-Host ""

Set-Location $RepoRoot
if (Get-Command git -ErrorAction SilentlyContinue) {
    if (Test-Path .git) { git status -sb } else { Write-Host "(git non initialise — en attente de votre remote GitHub)" }
}
