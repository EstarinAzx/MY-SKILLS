---
type: skill
updated: 2026-07-15
tags: [skill, handoff, context]
source: live inspection 2026-06-12
---

# context-handoff

The `.context/` cross-session handoff family — a project-local directory (overview.md, stack.md, active-work.md, decisions.md, …) that lets a fresh agent pick up without re-reading the chat. Obsidian-compatible (frontmatter + wikilinks).

- **context-init** — bootstrap `.context/` in the current project (`/context-init`).
- **context-update** — refresh at any context switch: update active-work.md, record a decision (`/context-update`).
- **context-sync** — umbrella skill wrapping both (init + update).

Distinct from the global [[memory-system]] (user-level, cross-project) — `.context/` is per-project and lives in the repo.

Template CLAUDE.md (section 6) enforces the convention in every new project: read active-work.md at session start, `/context-update` at session end/fork, suggest `/context-init` once for multi-session work.

## Folded folders (2026-07-15)

The two append-only files fold from a single monolith into a **thin index + entry folder** — the shape [[llm-kb]] uses for its wiki, borrowed to stop `decisions.md` growing to a 2000-line wall:

- `decisions.md` (index) + `decisions/YYYY-MM-DD-<slug>.md` (one file per decision)
- `gotchas.md` (index) + `gotchas/<slug>.md` (one file per trap)

The index is the wikilink target, so `overview.md`'s wikilink to the decisions index is unchanged (it resolves to `decisions.md`); entries back-link their index so they are never orphans. Everything else stays a flat file (`history.md` is a terse table that resists bloat). Recording an item = write the entry file, prepend one link line to the index.

`scripts/lint.py` is a **self-contained stdlib health check** (broken links, orphans, index↔entry drift, `--stale`) run during `update` — deliberately **not** coupled to llm-kb's scripts (context-sync must install standalone). This is the one place context-sync borrows llm-kb's structure while staying a handoff system, not a wiki: no SCHEMA.md, no log.md, no ingest, no search. Legacy flat `.context/` migrates on the same-machine `/context-update` path — offered when bloated, never forced. Design + plan live in `skills/context-sync/design/`.
