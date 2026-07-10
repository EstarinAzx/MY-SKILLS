---
type: decision
updated: 2026-07-10
tags: [decision, lineup, mattpocock]
source: mattpocock/skills v1.1.0 curation, 2026-07-10
---

# mattpocock-skills-lineup

**2026-07-10** — mattpocock/skills v1.1.0 installed as a *curated* set, not verbatim. In: to-spec, to-tickets, wayfinder, research, prototype, implement, triage, grilling, domain-modeling, codebase-design, ask-matt, setup-matt-pocock-skills, resolving-merge-conflicts + updates to grill-me, grill-with-docs, improve-codebase-architecture, teach.

**Excluded, and why:**

- **handoff** — user call: [[context-handoff]] (context-sync) already owns cross-session handoff.
- **tdd** — [[tdd-lineup]] hard rule: superpowers TDD is sole.
- **code-review** — name-collides with the built-in code-review skill; built-in covers it.
- **diagnosing-bugs** — superpowers systematic-debugging + [[bugs-begone]] cover it.
- **writing-great-skills** — superpowers writing-skills covers it.

**How to apply:** on future `mattpocock/skills` updates, re-copy the curated list only, then reapply the two local patches (implement → superpowers TDD; ask-matt "Local ecosystem note"). Old pre-v1.1.0 folders backed up in `~/.claude/_deprecated/mp-pre-v1.1-backup/`.
