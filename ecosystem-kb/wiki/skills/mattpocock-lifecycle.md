---
type: skill
updated: 2026-07-10
tags: [skill, planning, lifecycle, mattpocock]
source: mattpocock/skills v1.1.0, installed 2026-07-10
---

# mattpocock-lifecycle

The dev-lifecycle suite from mattpocock/skills v1.1.0 (curated install — see [[mattpocock-skills-lineup]] for what was excluded and why). Main flow: **wayfinder** (plan) → **to-spec** (define) → **to-tickets** (break down) → **implement** (build) → review.

User-invoked:

- **wayfinder** — plan work too big for one session as a shared map of investigation tickets on the issue tracker (tracker-native in v1.1.0; four ticket types: decision, task, spike, grilling; fog vs out-of-scope distinction).
- **implement** — build from spec/tickets. Patched locally: drives superpowers TDD (not Matt's `/tdd`) and the built-in code-review skill.
- **ask-matt** — router over the suite; carries a "Local ecosystem note" mapping excluded skills to our equivalents.

Model-invoked:

- **research** — background agent investigates against primary sources, captures cited Markdown in the repo.
- **prototype** — throwaway prototype (UI or logic) to answer a design question.
- **domain-modeling** — sharpen project terminology, update ADRs (formats moved here from grill-with-docs).
- **codebase-design** — deep-module vocabulary (module/interface/seam/depth); spoken by [[improve-codebase-architecture]].
- **resolving-merge-conflicts** — in-progress git merge/rebase conflict resolution.

Planning entry points: [[grill-skills]], [[github-planning]]. Cross-session context stays with [[context-handoff]], not Matt's handoff.
