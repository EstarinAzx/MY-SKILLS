---
type: skill
updated: 2026-07-13
tags: [skill, planning, interrogation]
source: mattpocock/skills v1.1.0, installed 2026-07-10
---

# grill-skills

Plan stress-testing by relentless interview.

- **grilling** — model-invoked reusable interview loop (new in v1.1.0) powering both user-facing skills. One question at a time (multiple at once is bewildering); facts come from exploring the codebase, only *decisions* go to the human; ends with a **confirmation gate** — restate the shared understanding before any implementation.
- **grill-me** — interrogate the user about a plan/design until shared understanding, resolving every branch of the decision tree.
- **grill-with-docs** — same, but challenges the plan against the project's domain model. v1.1.0 moved ADR/CONTEXT.md formats out to the **domain-modeling** skill (old `ADR-FORMAT.md`/`CONTEXT-FORMAT.md` aux files removed). Pairs with [[improve-codebase-architecture]], which consumes the same docs. See [[mattpocock-lifecycle]].

**Local patch (2026-07-13):** `grill-with-docs` frontmatter `disable-model-invocation: true → false` — upstream ships it user-only, which stalled the `/preset init` funnel (init invokes it mid-flow). Same flip applied to to-spec/to-tickets ([[github-planning]]). Reapply after any mp-update refresh (listed in the mp-update preset's patch step).
