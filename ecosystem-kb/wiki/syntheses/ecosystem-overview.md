---
type: synthesis
updated: 2026-06-24
tags: [synthesis, overview]
---

# ecosystem-overview

Entry point. The setup has four layers:

**1. Session modes (always on, hook-driven)** — [[caveman]] full (terse output, ~75% token cut) + [[elucidate]] default (plain-English comment style in code). Both load every session via [[settings-and-hooks]]; statusline shows their badges.

**2. Plugins** — [[superpowers]] (workflow discipline: brainstorming, TDD, debugging, verification), [[codex]] (second-opinion/rescue via local Codex CLI), plus the two mode plugins above. Loading mechanics in [[plugin-loading]] — note the skills-dir auto-load trap.

**3. Standalone skills** (`~/.claude/skills/`) — [[design-skills]] (impeccable-led family), [[llm-kb]] (knowledge vaults, built this one), [[context-handoff]] (.context/ per-project handoff), [[grill-skills]] → [[github-planning]] (plan → PRD → issues chain), [[improve-codebase-architecture]], [[mcp-tooling]] (Unity MCP + mcp2cli), [[bugs-begone]], [[output-skill]], [[preset]], [[trace]], [[happy-path]] (`/hp` — trace's forward-design twin, built 2026-06-21: draws the golden-path MVD before code exists), [[teach]] (`/teach` — stateful multi-session teaching workspace producing HTML lessons, added 2026-06-24).

**3b. Meta self-maintenance** — [[ecosystem-audit]] (built 2026-06-12): deterministic, read-only reconciler of `skills/` against this vault, and linter for the [[plugin-loading]] skills-dir footgun. First build of the meta layer the ecosystem brainstorm proposed.

**3c. Design→code pipeline** — [[design-pipeline]] (built 2026-06-12): pencil-bridge + token-sync + screenshot-diff, the first consumers of the formerly-dormant pencil MCP ([[mcp-servers]]); connective wiring around impeccable, not a new design engine.

**4. Infrastructure** — [[mcp-servers]] (UnityMCP, pencil), [[memory-system]] (auto-memory + lineup pattern).

**Decision history** (all 2026-06-11, the great consolidation): [[design-skill-lineup]], [[knowledge-base-lineup]], [[tdd-lineup]], [[commenting-mode-lineup]]. Common pattern: one winner per niche, losers to `~/.claude/_deprecated/` (or deleted when pushed to GitHub), memory file + this vault record the why.

**Standing hard rules:** no hooks/background processes/out-of-session LLM calls for knowledge tooling; user instructions > superpowers > defaults.
