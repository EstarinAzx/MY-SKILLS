---
type: synthesis
updated: 2026-07-12
tags: [synthesis, overview]
---

# ecosystem-overview

Entry point. The setup has four layers:

**1. Session modes (always on, hook-driven)** — [[caveman]] full (terse output, ~75% token cut) + [[elucidate]] default (plain-English comment style in code) + [[ponytail]] full (code minimalism, YAGNI/stdlib-first). All load every session via [[settings-and-hooks]]; statusline `[CAVEMAN] [ELUCIDATE] [PONYTAIL]`.

**2. Plugins** — [[superpowers]] (workflow discipline: brainstorming, TDD, debugging, verification), [[codex]] (second-opinion/rescue via local Codex CLI), [[drawio]] (polished exportable diagrams, skills-only — presentation layer over hp/trace Mermaid, installed 2026-07-12), plus the three mode plugins above. Loading mechanics in [[plugin-loading]] — note the skills-dir auto-load trap.

**3. Standalone skills** (`~/.claude/skills/`) — [[design-skills]] (impeccable-led family), [[llm-kb]] (knowledge vaults, built this one), [[context-handoff]] (.context/ per-project handoff), [[grill-skills]] → [[github-planning]] (plan → spec → tickets chain), [[improve-codebase-architecture]], [[mcp-tooling]] (Unity MCP + mcp2cli), [[bugs-begone]], [[output-skill]], [[preset]], [[trace]], [[happy-path]] (`/hp` — trace's forward-design twin, built 2026-06-21: draws the golden-path MVD before code exists), [[teach]] (`/teach` — stateful multi-session teaching workspace producing HTML lessons, added 2026-06-24), [[slot]] (`/slot` — Wisp Slot dance: rebind a sacrificial family route, spawn Agent through it, guarded restore; added 2026-07-17).

**3a. Dev lifecycle (mattpocock/skills v1.1.0, curated 2026-07-10)** — [[mattpocock-lifecycle]]: wayfinder → to-spec → to-tickets → implement, with model-invoked helpers (grilling, research, prototype, domain-modeling, codebase-design, resolving-merge-conflicts) and router ask-matt. Curation + exclusions in [[mattpocock-skills-lineup]]; updates via `/preset mp-update`.

**3b. Meta self-maintenance** — [[ecosystem-audit]] (built 2026-06-12): deterministic, read-only reconciler of `skills/` against this vault, and linter for the [[plugin-loading]] skills-dir footgun. First build of the meta layer the ecosystem brainstorm proposed. Grew `template_sync.py` 2026-07-10 (live ↔ `template/IN USE` drift + mirror); `/preset health` rolls all the checkers into one command.

**3c. Design→code pipeline** — [[design-pipeline]] (built 2026-06-12): pencil-bridge + token-sync + screenshot-diff, the first consumers of the formerly-dormant pencil MCP ([[mcp-servers]]); connective wiring around impeccable, not a new design engine.

**4. Infrastructure** — [[mcp-servers]] (UnityMCP, pencil), [[memory-system]] (auto-memory + lineup pattern).

**Decision history** (all 2026-06-11, the great consolidation): [[design-skill-lineup]], [[knowledge-base-lineup]], [[tdd-lineup]], [[commenting-mode-lineup]]. Common pattern: one winner per niche, losers to `~/.claude/_deprecated/` (or deleted when pushed to GitHub), memory file + this vault record the why.

**Standing hard rules:** no hooks/background processes/out-of-session LLM calls for knowledge tooling; user instructions > superpowers > defaults.
