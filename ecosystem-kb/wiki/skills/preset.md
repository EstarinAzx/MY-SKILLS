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
