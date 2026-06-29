# Déploie les correctifs RH sur le VPS (SSH mot de passe demandé une fois)
$ErrorActionPreference = "Stop"
$Vps = "adn@102.68.62.85"
$Remote = "/home/adn/onip-rh"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")

Write-Host ""
Write-Host "=== 1/2 Copie des fichiers modifies vers le VPS ===" -ForegroundColor Cyan

$files = @(
    @{ Local = "deploy\vps\run-on-vps-all.sh"; Remote = "$Remote/deploy/vps/run-on-vps-all.sh" },
    @{ Local = "deploy\vps\load-geography.sh"; Remote = "$Remote/deploy/vps/load-geography.sh" },
    @{ Local = "rh\api\views\auto_complete.py"; Remote = "$Remote/rh/api/views/auto_complete.py" },
    @{ Local = "rh\employee\models\employee.py"; Remote = "$Remote/rh/employee/models/employee.py" },
    @{ Local = "rh\static\assets\js\onip-form-select2.js"; Remote = "$Remote/rh/static/assets/js/onip-form-select2.js" },
    @{ Local = "rh\template\base.html"; Remote = "$Remote/rh/template/base.html" },
    @{ Local = "rh\payday\settings.py"; Remote = "$Remote/rh/payday/settings.py" }
)

foreach ($f in $files) {
    $src = Join-Path $Root $f.Local
    if (-not (Test-Path $src)) {
        Write-Host "  SKIP (absent): $($f.Local)" -ForegroundColor Yellow
        continue
    }
    Write-Host "  -> $($f.Local)"
    scp -o StrictHostKeyChecking=accept-new $src "${Vps}:$($f.Remote)"
}

Write-Host ""
Write-Host "=== 2/2 Execution sur le VPS (mot de passe SSH) ===" -ForegroundColor Cyan
ssh -o StrictHostKeyChecking=accept-new $Vps "chmod +x $Remote/deploy/vps/run-on-vps-all.sh $Remote/deploy/vps/load-geography.sh 2>/dev/null; bash $Remote/deploy/vps/run-on-vps-all.sh"

Write-Host ""
Write-Host "=== 3/3 Frontend guichet local (optionnel) ===" -ForegroundColor Cyan
Set-Location $Root
docker compose --profile register up -d --force-recreate frontend 2>$null

Write-Host ""
Write-Host "Termine. Testez http://localhost:3000 et http://102.68.62.85:8100" -ForegroundColor Green
Write-Host ""
