---
name: token-sync
description: Round-trip design tokens between a Pencil (.pen) design and code — extract pencil variables to CSS custom properties + DTCG JSON, push code tokens back into pencil, or diff the two for drift. Use when user says "sync design tokens", "export pencil variables to CSS", "pull tokens from the design", "push my CSS variables to pencil", or "check token drift". .pen via pencil MCP only.
---

# /token-sync — design-token round-trip

Keep the design's variables and the codebase's tokens in agreement. Three
directions: extract, inject, diff.

## Preconditions

- pencil MCP available; schema loaded (`get_editor_state(include_schema: true)`
  if it is not already in context).
- A project token target: a CSS file of custom properties, or a tokens JSON.
  Ask which if it is not obvious.

## Directions

**Extract (pencil → code)** — the default:
1. `get_variables` — pull the design's variable set.
2. Normalize each to a kebab CSS custom property (`--color-…`, `--space-…`,
   `--font-…`) and a W3C DTCG token entry; preserve groups and aliases.
3. Merge into the project token file. **Never clobber** unrelated tokens — merge
   by name and report additions vs. changes.

**Inject (code → pencil):**
1. Read the project's CSS custom properties / token JSON.
2. Map names to pencil variables; `set_variables` to update the design.
3. Report what changed; leave design-only variables untouched.

**Diff:**
- Compare `get_variables` against the code tokens and print a drift table
  (design-only, code-only, value-mismatch). No writes.

## Hard rules

1. **MCP-only access to .pen.**
2. **Merge, never clobber** — name collisions and value mismatches are reported;
   the user resolves them.
3. Deterministic mapping (kebab-case, fixed prefixes); no hooks; on-demand only.

## See also

- `/pencil-bridge` — full design→code; calls this for tokens.
- [[design-skills]] — impeccable consumes the tokens this lands.
