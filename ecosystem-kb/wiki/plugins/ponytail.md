---
type: plugin
updated: 2026-06-21
tags: [plugin, code-minimalism, mode]
source: live inspection 2026-06-21
---

# ponytail

Code-minimalism plugin from `DietrichGebert/ponytail` (GitHub marketplace), v4.7.0, installed 2026-06-20 (commit `0403c4d`). Cache: `~/.claude/plugins/cache/ponytail/ponytail/4.7.0`. Marketplace clone at `~/.claude/plugins/marketplaces/ponytail` (multi-harness: also ships Codex, Copilot, Pi, Gemini, OpenCode, Cursor/Windsurf/Cline/Kiro variants).

**Ponytail mode** — "lazy senior dev": forces the simplest, shortest solution that actually works (YAGNI, stdlib before custom, native before dependency, one line before fifty). Levels: lite / full (default) / ultra. Default settable via `PONYTAIL_DEFAULT_MODE` env (lite/full/ultra/off) or `~/.config/ponytail/config.json`. Requires `node` on PATH (verified v22.17.0).

Hook-driven, same architecture as [[caveman]]: `SessionStart` (startup|resume|clear|compact) runs `ponytail-activate.js`; `UserPromptSubmit` runs `ponytail-mode-tracker.js` (both Node-gated, Windows `commandWindows` variants). Ships statusline scripts (`.ps1`/`.sh`); the `.ps1` badge (`[PONYTAIL]`, hot pink 205 — recolored from default green 108) is wired into [[elucidate]]'s `statusline-wrapper.ps1` as of 2026-06-21 — statusline now reads `[CAVEMAN] [ELUCIDATE] [PONYTAIL]`. ⚠️ The color edit lives in the plugin-owned marketplace file (`plugins/marketplaces/ponytail/hooks/ponytail-statusline.ps1`); a `git pull` on plugin update will overwrite it — reapply 205 after updates. Bundles a `ponytail-mcp/` but it stays **dormant** — `plugin.json` declares `hooks` only, no `mcpServers` (reload reported `0 plugin MCP servers`). Hooks confirmed live after `/reload-plugins` (mode-change hook fired).

Skills: `ponytail` (the mode), `ponytail-review` (diff review for over-engineering — what to delete), `ponytail-audit` (whole-repo bloat audit), `ponytail-debt` (harvest `ponytail:` shortcut comments into a debt ledger), `ponytail-gain` (impact scoreboard), `ponytail-help`.

**Target vs neighbors:** ponytail trims **code complexity**; [[caveman]] trims **chat-output tokens** — orthogonal, no conflict. Overlaps the built-in `/simplify` (reuse/simplification/efficiency, same code-minimalism target) and partly `/code-review`; `ponytail-debt`'s shortcut-ledger is the one piece not covered elsewhere. Philosophical tension with [[elucidate]] (adds explanation layer) vs ponytail (strips to minimal) — opposite reflexes, not a hard clash.

**Kept hook-active by choice** (2026-06-21) — user pairs ponytail with [[caveman]] for "tokenmaxxing": caveman trims prose tokens, ponytail trims code tokens, both directions at once. Ponytail's own SKILL.md endorses the pairing ("pair with Caveman for terse prose"). So it's the third hook-driven mode + statusline ([[caveman]], [[elucidate]], ponytail); the per-prompt injection and statusline stacking is accepted cost, not a problem to mitigate. Do **not** suggest `PONYTAIL_DEFAULT_MODE=off`. See [[settings-and-hooks]].
