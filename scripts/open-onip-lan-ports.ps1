# Ouvre les ports requis pour l'acces RH des agents sur le LAN
# Executer en PowerShell administrateur :
#   .\scripts\open-onip-lan-ports.ps1

$rules = @(
    @{ Name = 'ONIP RH direct (port 8100)'; Port = 8100 },
    @{ Name = 'ONIP RH HTTP (Traefik)'; Port = 80 },
    @{ Name = 'ONIP RH DNS (CoreDNS)'; Port = 53 }
)

foreach ($rule in $rules) {
    $existing = Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "Regle deja presente : $($rule.Name)"
        continue
    }
    New-NetFirewallRule `
        -DisplayName $rule.Name `
        -Direction Inbound `
        -LocalPort $rule.Port `
        -Protocol TCP `
        -Action Allow | Out-Null
    if ($rule.Port -eq 53) {
        New-NetFirewallRule `
            -DisplayName "$($rule.Name) UDP" `
            -Direction Inbound `
            -LocalPort 53 `
            -Protocol UDP `
            -Action Allow | Out-Null
    }
    Write-Host "OK : $($rule.Name) (port $($rule.Port))"
}

Write-Host ""
Write-Host "Lien agents : http://VOTRE_IP:8100/login/"
