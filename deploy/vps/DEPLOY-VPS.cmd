@echo off
REM Lance le deploiement VPS (SSH : entrez le mot de passe adn quand demande)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-from-windows.ps1"
pause
