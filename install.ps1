<#
.SYNOPSIS
  Install agent-workflow-kit skills into Claude Code, Codex and Antigravity.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun
  powershell -ExecutionPolicy Bypass -File .\install.ps1
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Targets codex,antigravity -Force
#>
[CmdletBinding()]
param(
    [ValidateSet('claude', 'codex', 'antigravity')]
    [string[]]$Targets,
    [string[]]$Skills = @('agent-kit', 'project-init', 'startup', 'shutdown', 'office-docs', 'grilling'),
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$kitSkills = Join-Path $PSScriptRoot 'skills'
$userHome = $env:USERPROFILE
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $userHome ".agent-kit-backup\$stamp"

# Platform -> (config folder that proves it is installed, global skills folder)
$platforms = [ordered]@{
    claude      = @{ probe = Join-Path $userHome '.claude'; skills = Join-Path $userHome '.claude\skills' }
    codex       = @{ probe = Join-Path $userHome '.codex'; skills = Join-Path $userHome '.codex\skills' }
    antigravity = @{ probe = Join-Path $userHome '.gemini\antigravity'; skills = Join-Path $userHome '.gemini\antigravity\skills' }
}

if (-not $Targets) {
    $Targets = @($platforms.Keys | Where-Object { Test-Path -LiteralPath $platforms[$_].probe })
    if (-not $Targets) { throw 'No Claude Code / Codex / Antigravity config folder found under your home directory.' }
}

function Get-TreeHash([string]$Dir) {
    $files = Get-ChildItem -LiteralPath $Dir -Recurse -File | Sort-Object FullName
    ($files | ForEach-Object {
        $_.FullName.Substring($Dir.Length) + ':' + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    }) -join "`n"
}

$summary = @()
foreach ($t in $Targets) {
    $dest = $platforms[$t].skills
    Write-Output "== $t -> $dest"
    if (-not $DryRun -and -not (Test-Path -LiteralPath $dest)) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
    }
    foreach ($s in $Skills) {
        $src = Join-Path $kitSkills $s
        if (-not (Test-Path -LiteralPath $src)) { throw "Skill not found in kit: $s" }
        $target = Join-Path $dest $s
        $status = 'install'
        if (Test-Path -LiteralPath $target) {
            if ((Get-TreeHash $src) -eq (Get-TreeHash $target)) {
                $status = 'same'
            } elseif ($Force) {
                $status = 'replace'
            } else {
                $status = 'skip-differs'
            }
        }
        switch ($status) {
            'same' { Write-Output "   = $s (already identical)" }
            'skip-differs' { Write-Output "   ! $s exists and differs - skipped (use -Force to back up and replace)" }
            default {
                if ($DryRun) {
                    Write-Output "   ~ $s would $status"
                } else {
                    if ($status -eq 'replace') {
                        $bk = Join-Path $backupRoot "$t\$s"
                        New-Item -ItemType Directory -Path (Split-Path $bk) -Force | Out-Null
                        Move-Item -LiteralPath $target -Destination $bk
                        Write-Output "   backup: $bk"
                    }
                    Copy-Item -LiteralPath $src -Destination $target -Recurse
                    Write-Output "   + $s ($status)"
                }
            }
        }
        $summary += [pscustomobject]@{ Platform = $t; Skill = $s; Result = $(if ($DryRun -and $status -in 'install', 'replace') { "would $status" } else { $status }) }
    }
}

$summary | Format-Table -AutoSize | Out-String | Write-Output
if ($DryRun) { Write-Output 'Dry run only - nothing was changed.' }
else { Write-Output 'Done. Restart each Agent so the new skills are loaded.' }
