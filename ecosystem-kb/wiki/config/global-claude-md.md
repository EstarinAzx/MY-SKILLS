---
type: config
updated: 2026-07-13
tags: [config, claude-md, context]
source: live inspection 2026-07-13
---

# global-claude-md

`~/.claude/CLAUDE.md` — user-level memory, auto-loaded into **every** session
in **every** directory (stacks with any project CLAUDE.md). Created 2026-07-13
to close the push/pull gap: skill *descriptions* already route single skills
each session, but the graph — chains, pairings, standing rules — lived only in
this vault and reached a session only when something nudged it to read
(pull). The sheet pushes a compressed routing layer instead.

**Content contract:** routing sheet ONLY — 4-layer map, situation→invoke
table, standing rules, pointer here for the why. It is deliberately not an
encyclopedia; the vault stays the deep source. Keep it ~50 lines.

**Division of labor vs [[getclaude]]'s universal CLAUDE.md:** global =
ecosystem routing (machine-wide); IN USE = per-project behavior guards +
handoff loop. They stack in getclaude'd projects; overlap kept minimal.

**Sync duty:** lineup or skill-lineup changes must update this sheet in the
same session (wrap-up / `/preset health` moment) — it is a second
map-vs-territory surface after the vault itself. ⚠️ Not yet version-controlled
(lives outside template/IN USE and outside any repo with a remote) and not yet
linted by [[ecosystem-audit]]'s claude-md-stale-ref check — both are candidate
follow-ups.
