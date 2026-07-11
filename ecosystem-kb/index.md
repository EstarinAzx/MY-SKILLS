---
type: index
updated: 2026-07-10
---

# Index

## Plugins

- [[superpowers]] — workflow discipline: brainstorming, TDD, debugging, verification (claude-plugins-official v5.1.0)
- [[caveman]] — terse-output mode + cavecrew compressed subagents; hook-activated every session
- [[codex]] — second-opinion/rescue bridge to local Codex CLI (openai/codex-plugin-cc)
- [[elucidate]] — plain-English commenting mode; sole survivor of commenting consolidation; owns statusline
- [[ponytail]] — code-minimalism mode (YAGNI/stdlib-first) + review/audit/debt skills; hook+statusline, third such mode (DietrichGebert/ponytail v4.7.0)

## Skills

- [[design-skills]] — impeccable-led frontend family: redesign, minimalist/brutalist presets, brandkit + imagegen
- [[design-pipeline]] — pencil→code: pencil-bridge + token-sync + screenshot-diff (gives the dormant pencil MCP consumers)
- [[llm-kb]] — per-topic wiki vaults (built this one); no-hooks hard rule
- [[context-handoff]] — .context/ per-project handoff: init / update / sync
- [[grill-skills]] — plan stress-testing: grilling (helper), grill-me, grill-with-docs
- [[github-planning]] — to-spec, to-tickets, triage: plan → spec → tracer-bullet tickets
- [[mattpocock-lifecycle]] — wayfinder → to-spec → to-tickets → implement suite + research/prototype/domain-modeling/codebase-design (v1.1.0, curated)
- [[improve-codebase-architecture]] — CONTEXT.md/ADR-informed refactoring finder
- [[mcp-tooling]] — mcp2cli, unity-mcp-skill, mcp-source
- [[bugs-begone]] — opt-in instrumented debugging for hard bugs
- [[output-skill]] — anti-truncation, complete-output enforcement
- [[preset]] — /preset prompt library: handoff loop (init/pick-up/catch-up/scope/review/wrap-up/ship) + off-loop learn/prompt-writer + maintenance health/mp-update + loop bodies ticket-loop/ci-babysit
- [[relay]] — self-relaying /loop wrapper: legs of N iterations, handoff file, auto-spawned fresh session per leg (kills context rot in long loops)
- [[teach]] — `/teach <topic>` stateful multi-session teaching workspace → beautiful HTML lessons (added 2026-06-24)
- [[trace]] — multi-file end-to-end flow tracing (renamed from read-flow 2026-06-12)
- [[happy-path]] — `/hp` forward-design twin of trace: golden-path MVD before code exists; feeds `/preset init` (built 2026-06-21)
- [[ecosystem-audit]] — meta self-maintenance: skills/ ↔ vault reconciler + skills-dir footgun linter + template_sync.py live↔template drift/mirror

## Config

- [[settings-and-hooks]] — settings.json state: model, hooks, statusline, enabled plugins
- [[mcp-servers]] — UnityMCP, pencil; skeletongraph removed
- [[memory-system]] — auto-memory + lineup-memory pattern
- [[plugin-loading]] — marketplace / directory / skills-dir auto-load paths; deletion = uninstall

## Decisions

- [[design-skill-lineup]] — 2026-06-11: impeccable wins, five skills deprecated
- [[knowledge-base-lineup]] — 2026-06-11: llm-kb replaces kb/; no-hooks hard rule born
- [[tdd-lineup]] — 2026-06-11: superpowers TDD sole; local tdd/ deprecated
- [[commenting-mode-lineup]] — 2026-06-11: elucidate kept, skeleton deleted outright
- [[mattpocock-skills-lineup]] — 2026-07-10: v1.1.0 curated install; handoff/tdd/code-review/diagnosing-bugs/writing-great-skills excluded

## Sources

(none yet — pages derive from live inspection; drop external docs in raw/)

## Syntheses

- [[ecosystem-overview]] — entry point: four layers + decision history + standing rules
