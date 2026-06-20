---
type: log
---

# Log

## [2026-06-12] init | Claude ecosystem

Vault created at `~/.claude/ecosystem-kb`. Categories: plugins, skills, config, decisions. Ingest style: batch. Primary source: live inspection of ~/.claude.

## [2026-06-12] ingest | initial ecosystem sweep

Full sweep of ~/.claude (settings.json, mcp.json, installed_plugins.json, known_marketplaces.json, skills/ tree, _deprecated/, memory lineups). Wrote 24 pages: 4 plugins, 11 skills, 4 config, 4 decisions, 1 synthesis ([[ecosystem-overview]]).

## [2026-06-12] update | template CLAUDE.md references vault

Added "Ecosystem Knowledgebase" section to `~/.claude/template/IN USE/CLAUDE.md` (copied to all new projects) — consult vault before guessing tooling, check decision pages before installing new skills, sync vault when ecosystem changes. Noted reach caveat in [[memory-system]].

## [2026-06-12] update | template CLAUDE.md adds .context/ convention

Section 6 in template: read active-work.md at session start, /context-update at session end/fork, suggest /context-init once for multi-session work. User Preference renumbered to 7. Recorded in [[context-handoff]].

## [2026-06-12] update | read-flow renamed to trace

Skill folder `~/.claude/skills/read-flow/` → `trace/`; frontmatter name/description, heading, wiki page ([[trace]]), index, [[ecosystem-overview]], [[preset]] links, learn preset, and template copies (`template/IN USE/` skills + ecosystem-kb + CLAUDE.md §7) all updated. Trigger now `/trace`.

## [2026-06-12] update | new `learn` preset bundles read-flow + glossary grill

`/preset learn <flow question>` — full read-flow trace, collect vocabulary mismatches (user word ≠ code name, fuzzy/overloaded term, code-vs-CONTEXT.md conflict), mini-grill only those, write resolved terms to CONTEXT.md per grill-with-docs format. Mismatch-only trigger; plan stress-testing deliberately excluded (manual `/read-flow` → `/grill-with-docs` chain covers it). Updated [[preset]]; page also corrected to list pick-up/wrap-up.

## [2026-06-12] build | ecosystem-audit skill (meta layer)

First build from the ecosystem brainstorm. New skill `~/.claude/skills/ecosystem-audit/` — deterministic stdlib linter `scripts/audit.py` + tests, SKILL.md, [[ecosystem-audit]] vault page. Reconciles skills/ ↔ this vault; categories stray-folder / plugin-autoload / name-collision / vault-undocumented / vault-stale-path. Dogfood run surfaced two standing items: `skills/docs/` is a non-skill folder living under skills/, and `elucidate-plugin` auto-loads via skills-dir (expected). Honors no-hooks rule ([[knowledge-base-lineup]]); read-only, on-demand.

## [2026-06-12] update | trace gains plain/engineer register axis

Transcript autopsy (session e0631f6b, `/preset learn` on REST-prac) showed a learner got a `file:line`-heavy answer and had to nudge "without the technical jargon". Fix: [[trace]] Step 7 gets an audience register — default **engineer** (unchanged for `/trace`), **plain** remaps Summary/journey/failure to everyday language with `file:line` trailing + a closing engineer-view offer; methodology/persistence untouched. [[preset]] `learn` now always sets plain (never asks). Artifacts left manual (one-line offer on map-shaped answers, no silent writes). Verified by clean-context subagent (5/5 checks). Edited `trace/SKILL.md` + `preset/presets/learn.md`; vault pages [[trace]] + [[preset]] synced.

## [2026-06-12] build | llm-kb helper extensions

Second brainstorm build. Extended [[llm-kb]]'s deterministic scripts (one copy serves every vault): `search.py --all` (federated cross-vault search via new `~/.claude/vault-registry.txt`), `search.py --backlinks <vault> <page>` (inbound links; orphans stay in lint — no dup), `lint.py --stale [days]` (page-age + raw-newer-than-page freshness). Backward-compatible (plain `search.py <vault> <terms>` / `lint.py <vault>` unchanged); 22 unit tests green. SKILL.md + ops/lint.md + ops/query.md updated. Registry seeded with this vault.

## [2026-06-21] update | ponytail badge recolored hot pink

`ponytail-statusline.ps1` color `38;5;108` (green) → `38;5;205` (hot pink), both branches. Statusline `[CAVEMAN]`(172) `[ELUCIDATE]`(141) `[PONYTAIL]`(205), verified. Edit is in the plugin-owned marketplace file — a plugin update will overwrite it; reapply after updates. Synced [[ponytail]].

## [2026-06-21] update | statusline = caveman + elucidate (no MODE) + ponytail

Two-step, same day. (1) Wired ponytail's badge into [[elucidate]]'s `statusline-wrapper.ps1` (child-process call to `~/.claude/plugins/marketplaces/ponytail/hooks/ponytail-statusline.ps1`, `exit`-based like caveman). (2) Per follow-up: kept the `[ELUCIDATE]` badge but stripped its `[MODE:…]` bracket — edited `elucidate-statusline.ps1` to print identity only (flag still parsed for active/off color). Final statusline `[CAVEMAN] [ELUCIDATE] [PONYTAIL]`, verified by running the wrapper. Synced [[elucidate]], [[ponytail]], [[settings-and-hooks]].

## [2026-06-21] decision | ponytail stays hook-active, pairs with caveman

User keeps ponytail in always-on hook mode (not skills-only) deliberately: pairs with [[caveman]] for "tokenmaxxing" — caveman cuts prose tokens, ponytail cuts code tokens. Ponytail SKILL.md itself endorses pairing with Caveman. Flipped the ⚠️ note in [[ponytail]] from "mitigate by disabling" to "accepted cost"; future sessions must not suggest `PONYTAIL_DEFAULT_MODE=off`. Corrected page MCP claim too: `ponytail-mcp` ships dormant (plugin.json declares hooks only, reload showed 0 MCP servers).

## [2026-06-21] install | ponytail plugin

Installed `ponytail@ponytail` v4.7.0 from GitHub marketplace `DietrichGebert/ponytail` (commit `0403c4d`, scope user). Code-minimalism / "lazy senior dev" mode (YAGNI, stdlib-first); levels lite/full/ultra. 6 skills: ponytail, -review, -audit, -debt, -gain, -help. Hook-driven like [[caveman]] (SessionStart `ponytail-activate.js` + UserPromptSubmit `ponytail-mode-tracker.js`, Node-gated) + statusline scripts + own `ponytail-mcp`. Node dep satisfied (v22.17.0). Wrote [[ponytail]]; index updated. Standing note: third hook+statusline mode after [[caveman]]/[[elucidate]] — overlaps built-in `/simplify`, only `ponytail-debt` is net-new; recommended `PONYTAIL_DEFAULT_MODE=off` (skills-only) to avoid statusline/prompt-injection stacking. Hooks need `/reload-plugins`.

## [2026-06-12] build | pencil design→code pipeline

Third brainstorm build. Three new skills give the dormant pencil MCP its first consumers: `~/.claude/skills/pencil-bridge/` (anchor — .pen → brief → impeccable), `token-sync/` (variables ↔ CSS/DTCG round-trip), `screenshot-diff/` (pencil reference vs rendered build). SKILL.md only, orchestration around impeccable + the pencil MCP — no deterministic tests, UNVERIFIED against live MCP (need a real .pen to exercise). Documented in [[design-pipeline]]; pencil MCP usage was ~0 (decision to keep made this session — actual Pencil use is the Antigravity VSCode extension, not this MCP). Wiring only, so no [[design-skill-lineup]] one-winner conflict.

## [2026-06-21] build | /hp happy-path skill (forward-design twin of trace)

Fourth brainstorm build. New skill `~/.claude/skills/hp/` — `/hp [idea]` draws an MVD (minimum viable diagram): the one success spine of a user journey *before* code exists, the forward-design inverse of [[trace]] (which reads built code inward). Convey-mode menu asked each invoke (`ux+beat` default / `ux` / `system` / `beats`); box modes render Mermaid `flowchart`, persists to `.context/happy-path.md` (one `##` per flow) mirroring trace's flows.md — design-time vs built-time, two files side by side. Core discipline: success spine only, no error/edge forks (red-flagged); ≤2 clarifying Qs, not a grill. Wired into [[preset]] `init` as a step between grill and PRD (init renumbered to 8 steps; PRD embeds the MVD). GREEN application test (clean subagent, recipe-app idea with two planted error-branch temptations) passed 4/4 — resisted both forks, 0 clarifying Qs, correct `ux+beat` semantics, valid Mermaid. Synced [[happy-path]] (new), [[trace]], [[preset]], index, [[ecosystem-overview]]. Skipped the full RED pressure-gauntlet as disproportionate for a personal technique skill (ponytail).
