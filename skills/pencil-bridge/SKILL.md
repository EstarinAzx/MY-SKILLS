---
name: pencil-bridge
description: Turn a Pencil (.pen) design into production code — extract the node tree, tokens, layout, and a screenshot via the pencil MCP, assemble a design brief, then hand it to impeccable to build. Use when user says "code this pencil design", "build from the .pen file", "implement my pencil mockup", or "pencil to code/React/HTML". Reads .pen only through the pencil MCP, never the filesystem.
---

# /pencil-bridge — Pencil design → code

Connector skill. The pencil MCP holds the design, impeccable writes the code;
this skill moves the structured design from one to the other. It does not
generate code itself and does not override impeccable's judgment — it is the
wiring that was missing while the pencil MCP sat with zero consumers.

## Preconditions

- pencil MCP available and the target `.pen` document identified.
- `.pen` files are **encrypted** — only ever touched via pencil MCP tools,
  never Read/Grep.

## Flow

1. **Schema first.** If this conversation has no current `.pen` schema, call
   `get_editor_state(include_schema: true)` — the schema is required before any
   other pencil tool works. Identify the node(s) to build.
2. **Pull the design** (batch via `batch_get` where possible):
   - `export_nodes` — the component/layout tree of the target.
   - `get_variables` — design tokens (color, type, spacing).
   - `snapshot_layout` — spatial structure and measurements.
   - `get_screenshot` — a pixel reference of the target node.
   - `get_guidelines` — any design guidelines the document carries.
3. **Assemble one brief** — component tree + named tokens + spacing/type scale +
   the reference screenshot, as a single handoff. State the target stack
   (framework, styling approach); ask if it is not already known.
4. **Hand to impeccable** — invoke the `impeccable` skill with the brief as the
   source of truth; it produces the component code honoring tokens, layout, and
   accessibility. pencil-bridge stays out of the code decisions.
5. **Sync tokens (optional)** — if the project keeps a token file, run
   `/token-sync` so the generated code references real custom properties instead
   of hardcoded values.
6. **Verify (optional)** — `/screenshot-diff` compares the built UI against the
   step-2 reference.

## Hard rules

1. **MCP-only access to .pen** — never Read/Grep an encrypted design file.
2. **Schema before tools** — `get_editor_state(include_schema: true)` first
   whenever the schema is not already in context.
3. **impeccable owns the code** — this skill assembles inputs; it neither
   invents design nor bypasses impeccable.
4. No hooks, no background — on-demand, in-session only.

## See also

- [[design-skills]] — impeccable (the code engine) and the rest of the family.
- `/token-sync` — design-token round-trip.
- `/screenshot-diff` — visual regression against the `.pen` reference.
