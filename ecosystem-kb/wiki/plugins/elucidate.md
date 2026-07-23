---
type: plugin
updated: 2026-07-17
tags: [plugin, mode, commenting, parked]
source: live inspection 2026-07-17
---

# elucidate

**PARKED 2026-07-17** — user-requested temporary uninstall ("don't need it lately, will reinstall later"). NOT deprecated; still the commenting-lineup winner ([[commenting-mode-lineup]]). Folder moved intact to `~/.claude/_deprecated/elucidate-plugin`; registered plugin uninstalled; `elucidate@elucidate` enabledPlugins entry + directory-marketplace entry removed from settings.json. **Reinstall = move the folder back to `~/.claude/skills/elucidate-plugin`** — skills-dir auto-load picks it up and the statusline badge auto-revives (wrapper checks that path absolutely).

Self-authored commenting-mode plugin; when installed it loaded **by directory**: `~/.claude/skills/elucidate-plugin` registered as a directory marketplace and also auto-loaded as `elucidate-local@skills-dir` (see [[plugin-loading]]).

**Elucidate mode** — code carries its logic as plain-English comments, written together with the code in one pass (no scaffold, no approval gate). House style: title banner + section banners + file-top block (depends-on, data shapes) + per-construct summary + step comments. One axis, MODE: `default` (critical whys only) / `learner` (comment above every action) / `technical` (deep: tradeoffs, perf, edge cases). Was session-start hook driven, active at default.

Commands: `/elucidate:default|:learner|:technical|:off`. Applies to logic-bearing source files only; skips configs/markdown/fixtures. Sync rule: edit a comment whenever the code it describes changes.

Formerly owned the statusline plumbing. At park time the composed wrapper was **relocated to the neutral `~/.claude/hooks/statusline-wrapper.ps1`** (settings.json repointed) so the statusline survives the uninstall — it now renders `[CAVEMAN] [PONYTAIL]`, and the elucidate badge auto-revives on reinstall because the wrapper references the skills path absolutely. Badge shows **identity only** — the `[MODE:…]` bracket was dropped 2026-06-21 by request. ([[settings-and-hooks]], [[ponytail]])
