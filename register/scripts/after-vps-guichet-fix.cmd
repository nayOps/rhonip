@echo off
REM Apres correction sur le VPS : recree le frontend et teste localhost:3000
setlocal
cd /d "%~dp0..\.."
echo.
echo  Test RH VPS depuis ce PC...
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://102.68.62.85:8100/api/guichet/employees/?page=1&page_size=1' -Headers @{'X-Guichet-Internal-Key'='fgp_guichet_internal_dev'} -TimeoutSec 15 -UseBasicParsing; Write-Host '  VPS guichet : HTTP' $r.StatusCode -ForegroundColor Green } catch { if ($_.Exception.Response) { Write-Host '  VPS guichet : HTTP' ([int]$_.Exception.Response.StatusCode) '- corrigez la cle sur le VPS d abord' -ForegroundColor Red } else { Write-Host '  ERREUR:' $_.Exception.Message -ForegroundColor Red } }"
echo.
echo  Recreation frontend Docker...
docker compose --profile register up -d --force-recreate frontend
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check-guichet-docker.ps1"
pause
endlocal
