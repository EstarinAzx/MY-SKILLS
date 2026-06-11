---
type: skill
updated: 2026-06-12
tags: [skill, handoff, context]
source: live inspection 2026-06-12
---

# context-handoff

The `.context/` cross-session handoff family — a project-local directory (overview.md, stack.md, active-work.md, decisions.md, …) that lets a fresh agent pick up without re-reading the chat. Obsidian-compatible (frontmatter + wikilinks).

- **context-init** — bootstrap `.context/` in the current project (`/context-init`).
- **context-update** — refresh at any context switch: update active-work.md, append decisions.md (`/context-update`).
- **context-sync** — umbrella skill wrapping both (init + update).

Distinct from the global [[memory-system]] (user-level, cross-project) — `.context/` is per-project and lives in the repo.

Template CLAUDE.md (section 6) enforces the convention in every new project: read active-work.md at session start, `/context-update` at session end/fork, suggest `/context-init` once for multi-session work.
