---
type: skill
updated: 2026-06-12
tags: [skill, design, pencil, pipeline]
source: live inspection 2026-06-12
---

# design-pipeline

The Pencil → code pipeline — three skills built 2026-06-12 from the ecosystem
brainstorm (design lens) that finally give the wired-but-dormant pencil MCP
([[mcp-servers]]) consumers. All reach `.pen` files only through the pencil MCP
(encrypted — never Read/Grep), and all defer actual code and design judgment to
impeccable ([[design-skills]]); these skills are the connective wiring, not a
new design engine (so they do not collide with the [[design-skill-lineup]]
one-winner rule).

- **pencil-bridge** (anchor) — `.pen` → structured brief → impeccable codes it.
  Pulls `export_nodes` + `get_variables` + `snapshot_layout` + `get_screenshot`,
  assembles one handoff, invokes impeccable. The other two assume it.
- **token-sync** — design-token round-trip: `get_variables` → CSS custom
  properties + DTCG JSON (extract), code tokens → `set_variables` (inject), or a
  drift diff. Merge-never-clobber.
- **screenshot-diff** — visual regression: pencil `get_screenshot` reference vs
  impeccable browser-script render, severity-ordered fix checklist, loop until
  close.

Status: **authored 2026-06-12, orchestration-only** — no deterministic test
harness, since they drive the live pencil MCP + impeccable. Exercise against a
real `.pen` before relying on them. Honors the no-hooks rule
([[knowledge-base-lineup]]); on-demand, in-session.
