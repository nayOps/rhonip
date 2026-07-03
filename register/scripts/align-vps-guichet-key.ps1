# Aligne la cle guichet sur le VPS puis recree le frontend Docker local
param(
    [string]$VpsUser = "adn",
    [string]$VpsHost = "102.68.62.85",
    [string]$RemotePath = "/home/adn/onip-rh"
)

Write-Host ""
Write-Host "==> VPS : alignement cle guichet" -ForegroundColor Cyan
Write-Host "    Connexion SSH (mot de passe adn si demande)..."
ssh -o StrictHostKeyChecking=accept-new "${VpsUser}@${VpsHost}" "cd ${RemotePath} && bash deploy/vps/align-guichet-key.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR SSH ou script VPS" -ForegroundColor Red
    exit 1
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

Write-Host ""
Write-Host "==> Local : recreation frontend Docker" -ForegroundColor Cyan
docker compose --profile register up -d --force-recreate frontend
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
& (Join-Path $PSScriptRoot "check-guichet-docker.ps1")
