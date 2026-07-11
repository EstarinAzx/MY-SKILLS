---
type: config
updated: 2026-07-12
tags: [config, template, claude-md]
source: live inspection 2026-07-12
---

# getclaude

Universal-CLAUDE.md dropper. Typing `getclaude` in any directory copies the
canonical CLAUDE.md into it; `getclaude -Force` overwrites an existing one
(refuses otherwise).

Wiring (two pieces, easy to forget):

- **Profile function** — line 1 of
  `D:\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`:
  `function getclaude { & 'C:\Users\S.D\.claude\scripts\getclaude.ps1' @args }`
- **Script** — `~/.claude/scripts/getclaude.ps1`: guards missing template and
  existing-file clobber, then plain Copy-Item.

Canonical source: `~/.claude/template/IN USE/CLAUDE.md` — so the universal
CLAUDE.md is version-controlled in MY-SKILLS and rides the same
[[ecosystem-audit]] template mirror as everything else. Edit it THERE, not in
a project copy; projects get updates by re-running `getclaude -Force`.

Content (9 sections as of 2026-07-12): four behavioral guards (think before
coding / simplicity first / surgical changes / goal-driven execution), then
ecosystem wiring — consult [[llm-kb]] ecosystem vault instead of guessing,
[[context-handoff]] `.context/` convention, `/trace` beginner style, plain
language when discussing, JS arrow-function preference.
