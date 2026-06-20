---
type: plugin
updated: 2026-06-12
tags: [plugin, mode, commenting]
source: live inspection 2026-06-12
---

# elucidate

Self-authored commenting-mode plugin, loaded **by directory** (not marketplace): `~/.claude/skills/elucidate-plugin` is registered as a directory marketplace and also auto-loads as `elucidate-local@skills-dir` (see [[plugin-loading]]). Sole survivor of the commenting-mode consolidation — see [[commenting-mode-lineup]].

**Elucidate mode** — code carries its logic as plain-English comments, written together with the code in one pass (no scaffold, no approval gate). House style: title banner + section banners + file-top block (depends-on, data shapes) + per-construct summary + step comments. One axis, MODE: `default` (critical whys only) / `learner` (comment above every action) / `technical` (deep: tradeoffs, perf, edge cases). Currently **active at default**, session-start hook driven.

Commands: `/elucidate:default|:learner|:technical|:off`. Applies to logic-bearing source files only; skips configs/markdown/fixtures. Sync rule: edit a comment whenever the code it describes changes.

Also owns the statusline plumbing: `settings.json` points at `elucidate-plugin/src/hooks/statusline-wrapper.ps1`, the single composed entry. As of 2026-06-21 it renders `[CAVEMAN] [ELUCIDATE] [PONYTAIL]`. Elucidate's badge shows **identity only** — the `[MODE:…]` bracket was dropped by request (mode/color still parsed from the flag, just not displayed). ([[settings-and-hooks]], [[ponytail]])
