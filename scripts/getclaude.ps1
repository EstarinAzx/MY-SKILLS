# ----------------- getclaude.ps1 — drop template CLAUDE.md into current dir ----------------- #

# Copies the canonical CLAUDE.md from the template folder into whatever directory
# you're standing in. Refuses to clobber an existing CLAUDE.md unless -Force.

[CmdletBinding()]
param(
    # Overwrite an existing CLAUDE.md in the target dir without this, an existing file aborts.
    [switch]$Force
)

# --------------------------------- paths --------------------------------- #

$source = 'C:\Users\S.D\.claude\template\IN USE\CLAUDE.md'
$dest   = Join-Path (Get-Location).Path 'CLAUDE.md'

# --------------------------------- copy --------------------------------- #

# Bail early if the template went missing rather than copying nothing silently.
if (-not (Test-Path -LiteralPath $source)) {
    Write-Error "Template not found: $source"
    return
}

# Guard against silently destroying a project-specific CLAUDE.md.
if ((Test-Path -LiteralPath $dest) -and -not $Force) {
    Write-Warning "CLAUDE.md already exists here. Re-run 'getclaude -Force' to overwrite."
    return
}

Copy-Item -LiteralPath $source -Destination $dest -Force
Write-Host "CLAUDE.md -> $dest" -ForegroundColor Green
