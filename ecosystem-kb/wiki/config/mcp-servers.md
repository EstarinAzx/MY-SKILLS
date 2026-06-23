---
type: config
updated: 2026-06-12
tags: [config, mcp]
source: live inspection 2026-06-12
---

# mcp-servers

MCP servers wired into the setup.

- **UnityMCP** — `~/.claude/mcp.json`: http, `localhost:8080/mcp`. MCP for Unity; driven via [[mcp-tooling]] (unity-mcp-skill, mcp-source).
- **pencil** — .pen design-file editor (encrypted files, MCP-only access). Allowed in permissions (`mcp__pencil`); a `_disabled_pencil` duplicate exists in disabled state. Tools: get_editor_state, get_guidelines, batch_get, batch_design, snapshot_layout, get_screenshot, get_variables, set_variables, export_nodes. As of 2026-06-12 it has consumers — the [[design-pipeline]] skills (was dormant before). Note: actual day-to-day Pencil use is via the Antigravity VSCode extension, not this MCP.
- **skeletongraph** — REMOVED 2026-06-11 with the skeleton plugin ([[commenting-mode-lineup]]). Was `plugin:skeleton:skeletongraph`, a Python dependency-graph server.

Plugin-bundled MCP servers load via their plugin ([[plugin-loading]]); standalone ones via `mcp.json`.
