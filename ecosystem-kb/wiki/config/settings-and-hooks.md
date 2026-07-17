---
type: config
updated: 2026-07-17
tags: [config, settings, hooks, statusline]
source: live inspection 2026-07-17
---

# settings-and-hooks

State of `~/.claude/settings.json` as of 2026-07-17.

**Core settings:** model `claude-fable-5[1m]`, effort `xhigh`, permissions `bypassPermissions` (allow `mcp__pencil`), theme dark, TUI fullscreen, auto-memory on, auto-updates latest, `includeCoAuthoredBy: false`, worktree baseRef `fresh`.

**Hooks (node-driven, in `~/.claude/hooks/`):**
- SessionStart → `caveman-activate.js` — injects caveman-mode instructions every session ([[caveman]]).
- SessionStart → `.claude-manager/session-start-tap.js` — claude-manager session tap.
- UserPromptSubmit → `caveman-mode-tracker.js` — re-asserts caveman + elucidate mode state per prompt.
- UserPromptSubmit → `ecosystem-gate.js` (added 2026-07-17) — one-line static echo keeping the [[global-claude-md]] routing gate in attention per prompt; no state, no LLM.

**Statusline:** PowerShell composed wrapper at the neutral `~/.claude/hooks/statusline-wrapper.ps1` (relocated 2026-07-17 from the [[elucidate]] plugin when elucidate was parked; settings.json repointed). Each badge script runs independently; caveman + ponytail use `exit`, so the wrapper runs them in child processes; elucidate's badge is dot-sourced via an absolute skills path, so it is skipped while parked and auto-revives on reinstall. Currently renders `[CAVEMAN] [PONYTAIL]` (+ wisp badge when bridged).

**Enabled plugins:** codex@openai-codex, caveman@caveman, superpowers@claude-plugins-official, ponytail@ponytail, drawio@365-skills, wisp-slot@wisp-router. elucidate removed 2026-07-17 (parked — see [[elucidate]]). Loading mechanics: [[plugin-loading]].

> Hook caution: the [[knowledge-base-lineup]] no-hooks rule applies to *knowledge tooling*, not these mode hooks — caveman/elucidate hooks are accepted because they only inject static instructions, never call an LLM.
