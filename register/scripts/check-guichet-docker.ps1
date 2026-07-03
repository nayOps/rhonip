# Vérifie le guichet register lancé en Docker (localhost:3000)
param(
    [string]$Base = "http://localhost:3000",
    [string]$GuichetKey = "fgp_guichet_internal_dev"
)

$ErrorActionPreference = "Continue"
Write-Host ""
Write-Host "==> Conteneurs register" -ForegroundColor Cyan
$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
    Write-Host "    docker introuvable dans PATH" -ForegroundColor Red
} else {
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1 |
        Select-String -Pattern "fgp_|onip_|NAMES" | ForEach-Object { Write-Host "    $_" }
}

Write-Host ""
Write-Host "==> Frontend $Base" -ForegroundColor Cyan
try {
    $page = Invoke-WebRequest -Uri $Base -TimeoutSec 10 -UseBasicParsing -MaximumRedirection 5
    Write-Host "    HTTP $($page.StatusCode) -> $($page.BaseResponse.ResponseUri)" -ForegroundColor Green
} catch {
    Write-Host "    ERREUR : $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "    Demarrez : docker compose --profile register up -d frontend"
}

Write-Host ""
Write-Host "==> Proxy RH $Base/api/rh/api/guichet/refs/" -ForegroundColor Cyan
try {
    $refs = Invoke-WebRequest -Uri "$Base/api/rh/api/guichet/refs/" -Headers @{
        "X-Guichet-Internal-Key" = $GuichetKey
    } -TimeoutSec 15 -UseBasicParsing
    Write-Host "    HTTP $($refs.StatusCode)" -ForegroundColor Green
} catch {
    $status = $null
    if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
    if ($status -eq 403) {
        Write-Host "    HTTP 403 — cle guichet incorrecte (GUICHET_INTERNAL_API_KEY)" -ForegroundColor Red
    } elseif ($status -eq 502) {
        Write-Host "    HTTP 502 — conteneur frontend ne joint pas le RH" -ForegroundColor Red
        Write-Host "    Ajoutez dans .env : RH_INTERNAL_API_URL=http://102.68.62.85:8100"
        Write-Host "    Puis : docker compose --profile register up -d --force-recreate frontend"
    } else {
        Write-Host "    ERREUR : $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==> API gateway $Base/api/health/ (rewrite enrollment)" -ForegroundColor Cyan
try {
    $gw = Invoke-WebRequest -Uri "$Base/api/health/" -TimeoutSec 10 -UseBasicParsing
    Write-Host "    HTTP $($gw.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "    ERREUR gateway : $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
