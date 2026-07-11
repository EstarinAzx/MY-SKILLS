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

Content (8 sections as of 2026-07-12 revision): four behavioral guards
(think before coding / simplicity first / surgical changes / goal-driven
execution), then ecosystem wiring — consult [[llm-kb]] ecosystem vault
instead of guessing, [[context-handoff]] handoff via the [[preset]]
pick-up/wrap-up loop (bare `/context-update` demoted: wrap-up wraps it),
plain-language-when-discussing (with the `/trace` answer style folded in),
JS arrow-function preference. Carries a provenance header naming the
canonical path so project copies aren't edited by mistake.
