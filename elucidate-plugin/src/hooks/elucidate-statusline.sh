#!/bin/bash
# elucidate — statusline badge script for Claude Code (bash).
# Reads the single-axis mode flag and prints the elucidate badges:
#   active -> [ELUCIDATE] [MODE:DEFAULT|LEARNER|TECHNICAL]
#   off    -> [ELUCIDATE]   (dimmed)

FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.elucidate-active"

# Parse the flag. MODE stays empty if the flag is missing, malformed, or 'off'
# — in which case the off badge is shown.
MODE=""
if [ -f "$FLAG" ] && [ ! -L "$FLAG" ]; then
  RAW=$(head -c 64 "$FLAG" 2>/dev/null | tr -d '\n\r' | tr '[:upper:]' '[:lower:]')
  case "$RAW" in default|learner|technical) MODE="$RAW" ;; esac
fi

# MODE is whitelisted above, so the output below can only be fixed literals —
# no injection risk from the flag's bytes.
if [ -n "$MODE" ]; then
  printf '\033[38;5;141m[ELUCIDATE]\033[0m'
  MLABEL=$(printf '%s' "$MODE" | tr '[:lower:]' '[:upper:]')
  printf ' \033[38;5;108m[MODE:%s]\033[0m' "$MLABEL"
else
  # Off — identity badge only, dimmed grey.
  printf '\033[38;5;240m[ELUCIDATE]\033[0m'
fi
