# elucidate — statusline badge script for Claude Code (PowerShell).
# Reads the single-axis mode flag and prints the elucidate badge:
#   active -> [ELUCIDATE]   (full color; [MODE:…] bracket dropped by request 2026-06-21)
#   off    -> [ELUCIDATE]   (dimmed)
#
# Written WITHOUT `exit`, so a composing wrapper can dot-source it in-process.
# Also works standalone if settings.json points "statusLine" directly here.

$ClaudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$Flag = Join-Path $ClaudeDir ".elucidate-active"
$Esc = [char]27

# Parse the flag. $Mode stays empty if the flag is missing, malformed, or 'off'
# — in which case the off badge is shown.
$Mode = ""
if (Test-Path -LiteralPath $Flag) {
    try {
        $Item = Get-Item -LiteralPath $Flag -Force -ErrorAction Stop
        # Refuse reparse points (symlink / junction) and oversized files.
        if (-not ($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -and
            $Item.Length -le 64) {
            $Raw = Get-Content -LiteralPath $Flag -TotalCount 1 -ErrorAction Stop
            if ($null -ne $Raw) {
                $val = ([string]$Raw).Trim().ToLowerInvariant()
                if (@('default','learner','technical') -contains $val) { $Mode = $val }
            }
        }
    } catch { }
}

# $Mode is whitelisted above, so the interpolation below can only emit fixed
# literals — no injection risk from the flag's bytes.
if ($Mode -ne "") {
    # Active — identity badge only; [MODE:…] dropped by request, mode still parsed for color.
    [Console]::Write("${Esc}[38;5;141m[ELUCIDATE]${Esc}[0m")
} else {
    # Off — identity badge only, dimmed grey.
    [Console]::Write("${Esc}[38;5;240m[ELUCIDATE]${Esc}[0m")
}
