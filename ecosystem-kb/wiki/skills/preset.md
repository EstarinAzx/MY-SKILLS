---
type: skill
updated: 2026-07-10
tags: [skill, prompts]
source: live inspection 2026-06-12
---

# preset

Personal prompt-preset library — `/preset <name>` loads a named reusable instruction block instead of retyping it; bare `/preset` lists them.

Presets live in `~/.claude/skills/preset/presets/`: the session-handoff loop (`init`, `pick-up`, `catch-up`, `scope`, `review`, `wrap-up`, `ship`) plus off-loop `learn` (added 2026-06-12) — runs [[trace]] on a flow question in **plain register** (learning context, never asks; jargon/`file:line` demoted), then mini-grills vocabulary mismatches via [[grill-skills]] grill-with-docs machinery into `CONTEXT.md`. Grill fires only on mismatch (user word ≠ code name, fuzzy term, code-vs-glossary conflict); aligned vocabulary skips it.

`init` gained a [[happy-path]] MVD step 2026-06-21: after the grill settles decisions, `/hp` draws the golden-path diagram to `.context/happy-path.md`, embedded in the PRD before [[github-planning]] `to-spec`/`to-tickets` (skills renamed from to-prd/to-issues in mattpocock v1.1.0, 2026-07-10; init renumbered to 8 steps).

2026-07-10: init gained conditional step 4 (now 9 steps) — `docs/agents/` missing → offer `/setup-matt-pocock-skills`, seeding its issue-tracker section from step 2's destination answer (labels/domain-docs default); declined → tracker skills use defaults. Also fixed step 2's stale "governs steps 4 and 5" cross-ref (pre-dated the /hp renumber) to steps 4/7/8.

Same day, off-loop maintenance pair added: `health` (runs [[ecosystem-audit]] audit.py + template_sync.py + [[llm-kb]] lint --stale across registered vaults → one punch list; only template mirroring may be offered proactively) and `mp-update` (the [[mattpocock-skills-lineup]] update procedure made mechanical: curated list, excluded five, the two local patches, verify, sync).

Same day, loop bodies added — presets written for the built-in `/loop` runner (`/loop [interval] /preset <name>`), each honoring the loop-body contract (state-check first / one unit per firing / breadcrumbs / explicit stop signal): `ticket-loop` (one `ready-for-agent` ticket per firing via [[mattpocock-lifecycle]] `/implement`; consumes the triage labels `/setup-matt-pocock-skills` configures) and `ci-babysit` (PR checks: green→stop, pending→cheap, red→smallest fix or escalate; one action per distinct failure). Rejected: a loop framework skill (`/loop` is the framework) and cron routines (user drives loops explicitly).
