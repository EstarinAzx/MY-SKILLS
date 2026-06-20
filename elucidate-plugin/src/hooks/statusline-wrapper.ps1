# elucidate — composed statusline (PowerShell).
#
# settings.json "statusLine" points HERE. Renders the caveman, elucidate, and
# ponytail badges side by side on one line:
#
#   [CAVEMAN] [ELUCIDATE] [PONYTAIL]
#
# Each plugin keeps its own independent badge script — none knows about the
# others. If a plugin is absent, its badge is simply skipped. The elucidate
# badge shows identity only — its [MODE:…] bracket was dropped 2026-06-21.

# Caveman badge — caveman-statusline.ps1 uses `exit`, which would terminate this
# wrapper if dot-sourced. Run it in a child process instead.
$Caveman = Join-Path $HOME ".claude\hooks\caveman-statusline.ps1"
if (Test-Path -LiteralPath $Caveman) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $Caveman
    [Console]::Write(" ")
}

# Elucidate badge — exit-free, dot-source in-process; add a trailing space so the
# ponytail badge that follows isn't glued to it.
$Elucidate = Join-Path $PSScriptRoot "elucidate-statusline.ps1"
if (Test-Path -LiteralPath $Elucidate) {
    . $Elucidate
    [Console]::Write(" ")
}

# Ponytail badge — uses `exit` like caveman, so run in a child process, not dot-sourced.
$Ponytail = Join-Path $HOME ".claude\plugins\marketplaces\ponytail\hooks\ponytail-statusline.ps1"
if (Test-Path -LiteralPath $Ponytail) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $Ponytail
}
