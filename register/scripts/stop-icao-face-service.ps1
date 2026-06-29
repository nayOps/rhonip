param(
    [int]$Port = $(if ($env:ICAO_FACE_PORT) { [int]$env:ICAO_FACE_PORT } else { 50270 })
)

$killed = @()
Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object {
        $procId = $_.OwningProcess
        if ($procId -and ($killed -notcontains $procId)) {
            $killed += $procId
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }

if ($killed.Count -gt 0) {
    Write-Host "  Processus arretes : $($killed -join ', ')"
} else {
    Write-Host "  Aucun processus en ecoute sur le port $Port."
}

Start-Sleep -Milliseconds 500

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2 | Out-Null
    Write-Host "  Port encore actif - fermez la fenetre Python manuellement."
    exit 1
} catch {
    Write-Host "  Port $Port libre."
    exit 0
}
