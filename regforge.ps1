<#
.SYNOPSIS
    RegForge: list, apply, back up and revert documented Windows Registry tweaks.

.EXAMPLE
    .\regforge.ps1 list
    .\regforge.ps1 info explorer/show-file-extensions
    .\regforge.ps1 apply explorer/show-file-extensions
    .\regforge.ps1 revert explorer/show-file-extensions
    .\regforge.ps1 profile essentials
    .\regforge.ps1 apply system/enable-long-paths -Force      # no confirmation prompt
    .\regforge.ps1 apply explorer/classic-context-menu -RestartExplorer
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('list', 'info', 'apply', 'revert', 'backup', 'profile', 'profiles')]
    [string]$Command = 'list',

    [Parameter(Position = 1)]
    [string]$Target,

    [switch]$NoBackup,
    [switch]$Force,
    [switch]$RestartExplorer,
    [string]$BackupRoot = (Join-Path $env:LOCALAPPDATA 'RegForge\backups')
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    ([Security.Principal.WindowsPrincipal]$id).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-AllTweaks {
    Get-ChildItem -Path (Join-Path $Root 'tweaks') -Filter 'tweak.json' -Recurse |
        ForEach-Object {
            $meta = Get-Content $_.FullName -Raw | ConvertFrom-Json
            $meta | Add-Member -NotePropertyName Dir -NotePropertyValue $_.DirectoryName -Force -PassThru
        } | Sort-Object id
}

function Get-Tweak([string]$Id) {
    if (-not $Id) { throw "Specify a tweak id, e.g. explorer/show-file-extensions" }
    $Id = $Id -replace '\\', '/'
    $match = @(Get-AllTweaks | Where-Object { $_.id -eq $Id })
    if ($match.Count -ne 1) { throw "Unknown tweak '$Id'. Run: .\regforge.ps1 list" }
    $match[0]
}

function Get-RegKeys([string]$RegFile) {
    Select-String -Path $RegFile -Pattern '^\[-?(HKEY_[^\]]+)\]' |
        ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -Unique
}

function Backup-Tweak($Tweak, [string]$Stamp) {
    $dest = Join-Path (Join-Path $BackupRoot $Stamp) ($Tweak.id -replace '/', '__')
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    $i = 0
    foreach ($key in Get-RegKeys (Join-Path $Tweak.Dir 'enable.reg')) {
        $i++
        $file = Join-Path $dest ("{0:D2}.reg" -f $i)
        & reg.exe export $key $file /y 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Verbose "Key did not exist before tweak (nothing to back up): $key"
        }
    }
    Write-Host "  Backup: $dest" -ForegroundColor DarkGray
}

function Invoke-RegImport([string]$File) {
    & reg.exe import $File 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "reg import failed for $File (exit $LASTEXITCODE)" }
}

function Confirm-Action([string]$Message) {
    if ($Force) { return $true }
    (Read-Host "$Message [y/N]") -match '^(y|yes)$'
}

function Assert-Admin($Tweak) {
    if ($Tweak.requiresAdmin -and -not (Test-Admin)) {
        throw "'$($Tweak.id)' modifies HKEY_LOCAL_MACHINE. Re-run from an elevated PowerShell."
    }
}

function Invoke-Apply($Tweak, [string]$Stamp) {
    Assert-Admin $Tweak
    Write-Host "Applying $($Tweak.id): $($Tweak.name)" -ForegroundColor Cyan
    if (-not $NoBackup) { Backup-Tweak $Tweak $Stamp }
    Invoke-RegImport (Join-Path $Tweak.Dir 'enable.reg')
    Write-Host "  Done. Restart needed: $($Tweak.restart)" -ForegroundColor Green
}

function Invoke-Revert($Tweak) {
    Assert-Admin $Tweak
    Write-Host "Reverting $($Tweak.id): $($Tweak.name)" -ForegroundColor Cyan
    Invoke-RegImport (Join-Path $Tweak.Dir 'disable.reg')
    Write-Host "  Done." -ForegroundColor Green
}

function Restart-ExplorerIfAsked {
    if ($RestartExplorer) {
        Write-Host 'Restarting Explorer...' -ForegroundColor Yellow
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        if (-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe }
    }
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

switch ($Command) {
    'list' {
        Get-AllTweaks | ForEach-Object {
            [pscustomobject]@{
                Id = $_.id; Name = $_.name; Admin = $_.requiresAdmin; Windows = $_.windows
            }
        } | Format-Table -AutoSize
    }
    'info' {
        $t = Get-Tweak $Target
        Write-Host "$($t.name) [$($t.id)]" -ForegroundColor Cyan
        Write-Host $t.description
        Write-Host "Admin: $($t.requiresAdmin)   Windows: $($t.windows)   Restart: $($t.restart)   Risk: $($t.risk)"
        Write-Host "`n--- enable.reg ---"; Get-Content (Join-Path $t.Dir 'enable.reg')
        Write-Host "`n--- disable.reg ---"; Get-Content (Join-Path $t.Dir 'disable.reg')
    }
    'apply' {
        $t = Get-Tweak $Target
        if (Confirm-Action "Apply '$($t.id)'?") { Invoke-Apply $t $stamp; Restart-ExplorerIfAsked }
    }
    'revert' {
        $t = Get-Tweak $Target
        if (Confirm-Action "Revert '$($t.id)'?") { Invoke-Revert $t; Restart-ExplorerIfAsked }
    }
    'backup' {
        $t = Get-Tweak $Target
        Backup-Tweak $t $stamp
    }
    'profiles' {
        Get-ChildItem (Join-Path $Root 'profiles') -Filter '*.json' | ForEach-Object {
            $p = Get-Content $_.FullName -Raw | ConvertFrom-Json
            [pscustomobject]@{ Profile = $_.BaseName; Description = $p.description; Tweaks = $p.tweaks.Count }
        } | Format-Table -AutoSize
    }
    'profile' {
        $file = Join-Path $Root "profiles\$Target.json"
        if (-not (Test-Path $file)) { throw "Unknown profile '$Target'. Run: .\regforge.ps1 profiles" }
        $p = Get-Content $file -Raw | ConvertFrom-Json
        Write-Host "Profile '$($p.name)': $($p.description)" -ForegroundColor Cyan
        $p.tweaks | ForEach-Object { Write-Host "  - $_" }
        if (Confirm-Action "Apply all $($p.tweaks.Count) tweaks?") {
            foreach ($id in $p.tweaks) { Invoke-Apply (Get-Tweak $id) $stamp }
            Restart-ExplorerIfAsked
        }
    }
}
