---
type: plugin
updated: 2026-06-12
tags: [plugin, token-efficiency, mode]
source: live inspection 2026-06-12
---

# caveman

Token-compression plugin from `JuliusBrussee/caveman` (GitHub marketplace), installed 2026-05-14. Cache: `~/.claude/plugins/cache/caveman/caveman/63a91ecadbf4`.

**Caveman mode** — ultra-terse response style (~75% token cut, technical substance intact). Levels: lite / full / ultra (+ wenyan variants). Currently **active at full**, auto-loaded every session via SessionStart hook `~/.claude/hooks/caveman-activate.js` and tracked per-prompt by `caveman-mode-tracker.js` (see [[settings-and-hooks]]). Off: "stop caveman" / "normal mode". Code, commits, and security warnings are always written normally.

Skills: `caveman` (the mode), `caveman-commit`, `caveman-review`, `caveman-compress` (compress memory files), `caveman-stats` (real token usage from session log), `caveman-help`, `cavecrew` (delegation guide).

**Cavecrew subagents** — compressed-output agents that keep main context small: `cavecrew-investigator` (read-only code locator), `cavecrew-builder` (surgical 1–2 file edits), `cavecrew-reviewer` (one-line-per-finding diff review).
