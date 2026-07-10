---
type: skill
updated: 2026-07-10
tags: [skill, learning, teaching]
source: mattpocock/skills v1.1.0, refreshed 2026-07-10 (structure unchanged)
---

# teach

Stateful, multi-session teaching skill — `/teach <topic>` turns the current
directory into a **teaching workspace** and produces beautiful self-contained
HTML lessons grounded in a mission. User-invoked only
(`disable-model-invocation: true`); never auto-fires. Folder
`~/.claude/skills/teach/`.

Workspace files: `MISSION.md` (the *why*, grounds all teaching) + `RESOURCES.md`
(trusted external sources — never trust parametric knowledge) +
`./lessons/*.html` (primary unit — one tightly-scoped HTML lesson,
`0001-<name>.html`, incrementing) + `./reference/*.html` (compressed cheat
sheets, print-friendly) + `./learning-records/*.md` (ADR-style insight log,
`0001-...`, drives zone-of-proximal-development) + `./assets/*` (reusable
components — shared stylesheet first; reuse is the default) + `NOTES.md`
(user teaching preferences). Format specs ship beside SKILL.md:
`MISSION-FORMAT.md`, `RESOURCES-FORMAT.md`, `LEARNING-RECORD-FORMAT.md`,
`GLOSSARY-FORMAT.md`.

Pedagogy: knowledge → skills → wisdom; storage-strength over fluency via
desirable difficulty (retrieval practice, spacing, interleaving). Mission grounds
every lesson; if unclear, question the user first. Wisdom delegates to
real-world communities.

**Routing vs neighbors:** teaches the *user a subject* — orthogonal to
[[preset]] `learn` (which traces a *codebase* flow + glossary-grills vocabulary
into CONTEXT.md) and to [[llm-kb]] (which builds *source-fed wiki vaults* for the
LLM). teach produces interactive HTML lessons for a human learner over many
sessions; the others produce reference docs for code comprehension.
