---
type: skill
updated: 2026-07-13
tags: [skill, github, planning]
source: mattpocock/skills v1.1.0, installed 2026-07-10
---

# github-planning

Turning plans into tracker artifacts (mattpocock/skills):

- **to-spec** — synthesize the current conversation into a publishable spec (renamed from **to-prd** in v1.1.0; old folder in `_deprecated/mp-pre-v1.1-backup/`).
- **to-tickets** — break a plan/spec into tracer-bullet tickets with blocking edges (v1.1.0 merge of **to-issues** + to-plan; old folder in `_deprecated/mp-pre-v1.1-backup/`).
- **triage** — move issues *and external PRs* through state-machine roles.
- **setup-matt-pocock-skills** — one-time config of tracker labels + doc locations the suite reads.

Natural chain: [[grill-skills]] (stress-test) → to-spec → to-tickets → implement (see [[mattpocock-lifecycle]]).

**Local patch (2026-07-13):** `to-spec` + `to-tickets` frontmatter `disable-model-invocation: true → false` — upstream ships them user-only, which stalled the `/preset init` funnel (init invokes both mid-flow). Same flip on grill-with-docs ([[grill-skills]]). Reapply after any mp-update refresh (listed in the mp-update preset's patch step).
