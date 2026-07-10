---
type: skill
updated: 2026-07-10
tags: [skill, meta, health, deterministic]
source: live inspection 2026-06-12; template_sync added 2026-07-10
---

# ecosystem-audit

Self-maintenance skill — the first of the meta layer. Reconciles what is
installed under `~/.claude/skills/` against what this vault claims, and surfaces
the skills-dir loader's footguns. Built 2026-06-12 from the ecosystem brainstorm
(the meta lens' top pick).

Deterministic, read-only, stdlib-only helper `scripts/audit.py` (same shape as
[[llm-kb]]'s search.py/lint.py: TAB output, exit 0/1/2, no network/LLM). Runs
only on demand — honors the no-hooks rule ([[knowledge-base-lineup]]).

Findings: `stray-folder` (child of skills/ with no SKILL.md), `plugin-autoload`
(child with `.claude-plugin/` — the silent `<x>@skills-dir` load described in
[[plugin-loading]]), `name-collision` (two skills, one `name:`),
`vault-undocumented` (skill named nowhere here), `vault-stale-path` (a
`~/.claude/skills/<name>/` path this vault asserts but disk lacks; `decisions/`
and `log.md` exempt — they narrate history).

Second script `scripts/template_sync.py` (added 2026-07-10): drift between live
`skills/`+`ecosystem-kb/` and `template/IN USE` (the copy pushed to MY-SKILLS).
Categories `drift`/`live-only`/`template-only`; newline-normalized (CRLF churn
never drifts), `.obsidian/` ignored. `--apply` mirrors asymmetrically —
`skills/` refreshes only folders on both sides (curation stays human),
`ecosystem-kb/` mirrors fully including deletes; mutates the template copy
only. Tests in `scripts/tests/`. Rolled up by `/preset health`.

Pairs with the deferred `skill-usage-report` idea (telemetry → next
consolidation) and is the audit input a future guided `consolidate` skill would
drive. Trigger: `/ecosystem-audit`, "check skill drift", "find stray folders".
