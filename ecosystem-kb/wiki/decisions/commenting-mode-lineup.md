---
type: decision
updated: 2026-06-12
tags: [decision, lineup, commenting]
source: live inspection 2026-06-12
---

# commenting-mode-lineup

**2026-06-11** — [[elucidate]] is the sole commenting-mode plugin; the skeleton plugin was **fully deleted** (not just deprecated).

**Why:** skeleton and elucidate were near-duplicate plain-English-comment modes; elucidate kept (simpler — one axis, no scaffold/approval ceremony).

**What was removed:** `~/.claude/skills/skeleton plugin/` (folder), the skeletongraph MCP server ([[mcp-servers]]), `~/.claude/skeletongraph/` cache, `.skeleton-active` markers. Source preserved at https://github.com/EstarinAzx/Skeleton (was fully pushed).

**Operational lesson:** the plugin auto-loaded via skills-dir mechanism, so deletion = uninstall, but its running MCP server locked `.venv\Scripts\python.exe` — processes had to be killed before the folder would delete ([[plugin-loading]]).

**How to apply:** never recommend skeleton skills/commands or skeletongraph tools — gone.
