---
name: screenshot-diff
description: Visual regression between a Pencil (.pen) design reference and the live rendered UI — capture the design via pencil get_screenshot, capture the running page via impeccable's browser scripts, diff them, and produce a prioritized fix checklist. Use when user says "compare the design to the build", "visual diff", "does it match the mockup", or "pixel-check against pencil". .pen via pencil MCP only.
---

# /screenshot-diff — design vs build visual regression

Close the loop between the Pencil reference and what the browser actually
renders.

## Preconditions

- pencil MCP (schema loaded) with the reference node, AND a running or
  renderable build of the page.
- impeccable's live browser scripts available for the actual-state capture.

## Flow

1. **Reference** — `get_screenshot` of the target `.pen` node (load schema first
   if needed); `snapshot_layout` for the expected measurements.
2. **Actual** — drive impeccable's browser script to screenshot the rendered
   page at the same viewport.
3. **Diff** — compare structurally (spacing, alignment, type scale, color) and
   visually. Emit a checklist ordered by severity: blocker (layout/contrast) →
   major (spacing/type) → minor (subpixel).
4. **Remediate** — apply fixes via impeccable or hand the checklist back; re-run
   until the delta is acceptable.

## Hard rules

1. **MCP-only access to .pen.**
2. Synchronous and in-session — no background watcher, no hooks.
3. The `.pen` is the reference; the build conforms to it, not the reverse,
   unless the user says otherwise.

## See also

- `/pencil-bridge`, `/token-sync` — the rest of the pencil pipeline.
- [[design-skills]] — impeccable (browser scripts and fixes).
