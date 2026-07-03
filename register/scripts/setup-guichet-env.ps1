# Configure .env.local pour guichet local → VPS distant
param(
    [string]$Vps = "102.68.62.85",
    [int]$RhPort = 8100,
    [string]$SshUser = "adn",
    [string]$RemoteEnvPath = "~/rhonip/.env"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $Root "frontend"
$Example = Join-Path $Frontend ".env.guichet-vps.example"
$EnvLocal = Join-Path $Frontend ".env.local"
$RhUrl = "http://${Vps}:${RhPort}"

Write-Host ""
Write-Host "==> Configuration guichet local -> VPS $RhUrl" -ForegroundColor Cyan

if (-not (Test-Path $Example)) {
    throw "Fichier manquant : $Example"
}

$existingKey = $null
if (Test-Path $EnvLocal) {
    $line = Get-Content $EnvLocal | Where-Object { $_ -match '^NEXT_PUBLIC_GUICHET_INTERNAL_API_KEY=' } | Select-Object -First 1
    if ($line) {
        $existingKey = ($line -split '=', 2)[1].Trim()
    }
}

Copy-Item -Force $Example $EnvLocal
$content = Get-Content $EnvLocal -Raw
$content = $content -replace 'http://102\.68\.62\.85:8100', $RhUrl
$content = $content -replace 'http://102\.68\.62\.85:8201', "http://${Vps}:8201"
$content = $content -replace 'http://102\.68\.62\.85:8200', "http://${Vps}:8200"
$content = $content -replace 'http://102\.68\.62\.85:8210', "http://${Vps}:8210"
Set-Content -Path $EnvLocal -Value $content.TrimEnd() -NoNewline
Add-Content -Path $EnvLocal -Value ""

$remoteKey = $null
try {
    $grep = ssh -o ConnectTimeout=8 -o BatchMode=yes "${SshUser}@${Vps}" "grep '^GUICHET_INTERNAL_API_KEY=' $RemoteEnvPath 2>/dev/null | head -1"
    if ($grep -match '^GUICHET_INTERNAL_API_KEY=(.+)$') {
        $remoteKey = $Matches[1].Trim()
        Write-Host "    Cle guichet lue depuis le VPS." -ForegroundColor Green
    }
} catch {
    Write-Host "    SSH indisponible — cle VPS non lue (editez .env.local manuellement)." -ForegroundColor Yellow
}

$keyToUse = if ($remoteKey) { $remoteKey } elseif ($existingKey) { $existingKey } else { "fgp_guichet_internal_dev" }
(Get-Content $EnvLocal) | ForEach-Object {
    if ($_ -match '^NEXT_PUBLIC_GUICHET_INTERNAL_API_KEY=') {
        "NEXT_PUBLIC_GUICHET_INTERNAL_API_KEY=$keyToUse"
    } else { $_ }
} | Set-Content $EnvLocal

Write-Host "    Ecrit : $EnvLocal"

Write-Host ""
Write-Host "==> Test RH $RhUrl/login/" -ForegroundColor Cyan
try {
    $login = Invoke-WebRequest -Uri "$RhUrl/login/" -TimeoutSec 10 -UseBasicParsing
    Write-Host "    Login RH : HTTP $($login.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "    ERREUR : RH injoignable — $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "    Verifiez reseau / pare-feu vers $RhUrl"
}

Write-Host ""
Write-Host "==> Test API guichet" -ForegroundColor Cyan
try {
    $headers = @{ "X-Guichet-Internal-Key" = $keyToUse }
    $api = Invoke-WebRequest -Uri "$RhUrl/api/guichet/employees/?page=1&page_size=1" -Headers $headers -TimeoutSec 10 -UseBasicParsing
    Write-Host "    Guichet API : HTTP $($api.StatusCode)" -ForegroundColor Green
} catch {
    $status = $null
    if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
    if ($status -eq 403) {
        Write-Host "    ERREUR 403 : cle guichet incorrecte." -ForegroundColor Red
        Write-Host "    Sur le VPS : bash deploy/vps/align-guichet-key.sh"
        Write-Host "    Puis relancez ce script."
    } else {
        Write-Host "    ERREUR API guichet : $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Prochaine etape : register\scripts\start-guichet-local-vps.cmd" -ForegroundColor Cyan
Write-Host "Puis ouvrez http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
