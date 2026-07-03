@echo off
REM Sync Register local -> VPS (sessions + photos RH)
set SSHPASS=ADNKinshasa**2024
cd /d "%~dp0..\.."
python deploy\vps\sync_local_register_to_vps.py %*
