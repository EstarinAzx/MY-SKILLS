---
type: config
updated: 2026-06-12
tags: [config, settings, hooks, statusline]
source: live inspection 2026-06-12
---

# settings-and-hooks

State of `~/.claude/settings.json` as of 2026-06-12.

**Core settings:** model `claude-fable-5[1m]`, effort `xhigh`, permissions `bypassPermissions` (allow `mcp__pencil`), theme dark, TUI fullscreen, auto-memory on, auto-updates latest, `includeCoAuthoredBy: false`, worktree baseRef `fresh`.

**Hooks (node-driven, in `~/.claude/hooks/`):**
- SessionStart → `caveman-activate.js` — injects caveman-mode instructions every session ([[caveman]]).
- SessionStart → `.claude-manager/session-start-tap.js` — claude-manager session tap.
- UserPromptSubmit → `caveman-mode-tracker.js` — re-asserts caveman + elucidate mode state per prompt.

**Statusline:** PowerShell wrapper from the [[elucidate]] plugin (`elucidate-plugin/src/hooks/statusline-wrapper.ps1`) — renders mode badges.

**Enabled plugins:** codex@openai-codex, caveman@caveman, elucidate@elucidate (directory marketplace), superpowers@claude-plugins-official. Loading mechanics: [[plugin-loading]].

> Hook caution: the [[knowledge-base-lineup]] no-hooks rule applies to *knowledge tooling*, not these mode hooks — caveman/elucidate hooks are accepted because they only inject static instructions, never call an LLM.
