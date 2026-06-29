# Copie les DLL FAP60 (Bin64) vers device-bridge/sdk/fap60-x64
$ErrorActionPreference = "Continue"

$root = Split-Path $PSScriptRoot -Parent
$dest = Join-Path $root "sdk\fap60-x64"
$required = @("FAP60-02.dll", "fingerprint.dll", "Driver.dll")

$force = $args -contains "-Force"
$allPresent = ($required | ForEach-Object { Test-Path (Join-Path $dest $_) }) -notcontains $false
if ($allPresent -and -not $force) {
    Write-Host "SDK FAP60 deja present dans: $dest"
    Write-Host "Pour recopier depuis FAP60Demo\Bin64 : copy-fap60-sdk.ps1 -Force"
    Write-Host "Ou lancez verify-fap60-sdk.cmd pour comparer avec la demo."
    exit 0
}

# Priorite : Bin64 de la DEMO, puis copies locales deja preparees (fgp/register, rh-onip)
$srcCandidates = @(
    "C:\Users\HYF\Documents\sdk\FAP60 Windows CSharp SDKV2.0.14C-2025091817\FAP60 Windows CSharp SDKV2.0.14C-2025091817\samplecode\FAP60Demo\Bin64",
    "C:\Users\HYF\Documents\sdk\FAP60 Windows CSharp SDKV2.0.14C-2025091817\FAP60 Windows CSharp SDKV2.0.14C-2025091817\bin\Bin64",
    "C:\Users\HYF\Documents\sdk\fgp\register\device-bridge\sdk\fap60-x64",
    "C:\Users\HYF\Documents\rh-onip\register\device-bridge\sdk\fap60-x64"
)

$src = $srcCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $src) {
    Write-Error "Dossier Bin64 FAP60 introuvable. Ajustez le chemin dans copy-fap60-sdk.ps1"
    exit 1
}

New-Item -ItemType Directory -Force -Path $dest | Out-Null

$locked = 0
$copied = 0
Get-ChildItem -Path $src -File | ForEach-Object {
    $target = Join-Path $dest $_.Name
    try {
        Copy-Item -Path $_.FullName -Destination $target -Force -ErrorAction Stop
        $copied++
    }
    catch {
        if (Test-Path $target) {
            Write-Host "Ignore (fichier verrouille, deja present): $($_.Name)"
            $locked++
        }
        else {
            Write-Warning "Echec copie $($_.Name): $_"
        }
    }
}

$allPresent = ($required | ForEach-Object { Test-Path (Join-Path $dest $_) }) -notcontains $false
if (-not $allPresent) {
    Write-Error "DLL obligatoires manquantes dans $dest"
    exit 1
}

Write-Host "SDK pret: $dest ($copied fichier(s) copies, $locked verrouille(s) ignore(s))"
Get-ChildItem $dest -Filter "*.dll" | Select-Object Name
exit 0
