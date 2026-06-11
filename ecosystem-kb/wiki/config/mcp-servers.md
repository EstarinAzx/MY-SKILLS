---
type: config
updated: 2026-06-12
tags: [config, mcp]
source: live inspection 2026-06-12
---

# mcp-servers

MCP servers wired into the setup.

- **UnityMCP** — `~/.claude/mcp.json`: http, `localhost:8080/mcp`. MCP for Unity; driven via [[mcp-tooling]] (unity-mcp-skill, mcp-source).
- **pencil** — .pen design-file editor (encrypted files, MCP-only access). Allowed in permissions (`mcp__pencil`); a `_disabled_pencil` duplicate exists in disabled state.
- **skeletongraph** — REMOVED 2026-06-11 with the skeleton plugin ([[commenting-mode-lineup]]). Was `plugin:skeleton:skeletongraph`, a Python dependency-graph server.

Plugin-bundled MCP servers load via their plugin ([[plugin-loading]]); standalone ones via `mcp.json`.
