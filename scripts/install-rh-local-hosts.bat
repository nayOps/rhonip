@echo off
:: Ajoute rh.onip.gouv.local dans le fichier hosts (elevation admin requise)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Elevation administrateur requise...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0rh-local-hosts.ps1"
echo.
pause
