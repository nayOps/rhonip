# Ajoute rh.onip.gouv.local au fichier hosts Windows
# Usage (PowerShell en administrateur) :
#   .\scripts\rh-local-hosts.ps1                  # 127.0.0.1 — poste serveur
#   .\scripts\rh-local-hosts.ps1 -Ip 192.168.1.79 # IP LAN — postes agents

param(
    [string]$Ip = "127.0.0.1",
    [string]$HostName = "rh.onip.gouv.local"
)

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
$line = "$Ip`t$HostName"
$content = Get-Content -Path $hostsPath -ErrorAction Stop

$filtered = $content | Where-Object { $_ -notmatch [regex]::Escape($HostName) }
$newContent = @($filtered) + $line
Set-Content -Path $hostsPath -Value $newContent -Encoding ASCII

Write-Host "OK : $line ajoute dans $hostsPath"
Write-Host "Test : http://$HostName/"
