# Export PostgreSQL ONIP (Windows PowerShell)
# Usage : .\deploy\backup\export-db.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$BackupDir = Join-Path $RepoRoot "deploy\backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Output = Join-Path $BackupDir "onip_rh_production.sql"
$OutputStamped = Join-Path $BackupDir "onip_rh_$Timestamp.sql"

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

$EnvFile = Join-Path $RepoRoot ".env"
if (Test-Path $EnvFile) {
    foreach ($line in Get-Content $EnvFile) {
        if ($line -match '^\s*([^#=]+)=(.*)$') {
            Set-Item -Path "env:$($Matches[1].Trim())" -Value $Matches[2].Trim()
        }
    }
}

$Db = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "onip_db" }
$User = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "onip_user" }
$Container = if ($env:ONIP_POSTGRES_CONTAINER) { $env:ONIP_POSTGRES_CONTAINER } else { "onip_postgres" }

$running = docker ps --format "{{.Names}}" | Select-String -Pattern "^$([regex]::Escape($Container))$"
if (-not $running) {
    Write-Error "Conteneur '$Container' non démarré. Lancez : docker compose --profile rh up -d"
}

Write-Host "==> Export $Db depuis $Container..."
docker exec $Container pg_dump -U $User -d $Db --no-owner --no-acl --clean --if-exists | Set-Content -Encoding utf8 $Output

Copy-Item -Force $Output $OutputStamped

$size = [math]::Round((Get-Item $Output).Length / 1MB, 1)
Write-Host "==> Sauvegarde GitHub : $Output ($size MB)"
Write-Host "    Copie horodatée   : $OutputStamped ($size MB)"
