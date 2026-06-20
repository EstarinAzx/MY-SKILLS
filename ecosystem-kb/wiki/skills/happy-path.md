---
type: skill
updated: 2026-06-21
tags: [skill, design, code-reading]
source: live inspection 2026-06-21
---

# happy-path

Forward-design twin of [[trace]] — `/hp` draws the **MVD** (minimum viable
diagram): the one success spine of a user journey, *before* any code exists.
Triggers: "/hp", "happy path", "map the happy path / user journey", "MVD",
"sketch the flow before building". Folder `~/.claude/skills/hp/`. Built
2026-06-21.

**Discipline:** one success spine only — no error / edge / alternate branches
(those are build-time, red-flagged in the skill). At most 1–2 clarifying
questions, not a grill.

**Convey-mode menu** (asked each invoke): `ux+beat` (default — screen nodes,
action+system-beat edges) / `ux` (screens + actions) / `system` (components +
calls, the literal mirror of trace's data hops) / `beats` (numbered prose). Box
modes render Mermaid `flowchart`; persists to `.context/happy-path.md` (one `##`
per flow), mirroring how [[trace]] persists `.context/flows.md` — design-time
MVD vs built-time flow, two files side by side.

**Routing:** existing code → [[trace]]; new idea, no code yet → `/hp`. Heavy
interrogation → [[grill-skills]]. Wired into [[preset]] `init`: drawn after the
grill, embedded in the PRD before [[github-planning]] hands off.
