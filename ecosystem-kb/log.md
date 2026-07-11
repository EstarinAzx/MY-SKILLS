---
type: log
---

# Log

## [2026-07-12] build | /relay self-relaying loops

Brainstorm build (spec 2026-07-11). New skill `~/.claude/skills/relay/` —
wraps built-in `/loop` in legs of N iterations (default 10); at leg end:
rewrite Handoff in project-local `.claude/relay/<slug>.md`, `Start-Process
claude` a fresh session with the same `/relay` command injected, stop own
loop. Fixes context rot + uncached re-read cost of long single-session
loops (ScheduleWakeup and CronCreate are both session-bound — nothing
in-session can outlive it, hence spawn). Kill switches: `/relay stop`,
`max_legs: 20`, leg-fencing. Spawned legs run unattended → default spawn
flag `--dangerously-skip-permissions` (live test same day: `acceptEdits`
parked leg 2 on the loop skill's permission prompt — bypass or the chain
stalls; `mode=accept` kept as edit-only opt-in). No
watchdog hook by design (standing rule). Conscious partial revisit of the
2026-07-10 "user drives loops explicitly" decision — spawn automated, user
keeps start/stop/caps. [[preset]] loop bodies unchanged, wrappable as-is.
Synced [[relay]] (new), [[preset]], index.

## [2026-07-10] build | loop-body presets: ticket-loop + ci-babysit

Loop-engineering pass. Two [[preset]]s written as bodies for the built-in `/loop` runner, plus a "Loop bodies" section in preset SKILL.md naming the contract (state-check first, one unit per firing, breadcrumbs, explicit stop signal). `ticket-loop`: one unblocked `ready-for-agent` ticket per firing — pick → idempotency guard (existing branch/PR) → `ticket/<id>` branch → `/implement` → test gate → breadcrumb comment + relabel; queue dry → stop the loop; ambiguity/destructive → `ready-for-human`. `ci-babysit`: PR checks per firing — green→stop, pending→one cheap line, red→trivial fix / one flaky rerun / escalate with root-cause comment; never fix-push twice for one failure. Rejected: loop-framework skill (built-in `/loop` is the framework), cron routines (user drives loops). `health` noted loopable as-is. Synced [[preset]], index; template pushed.

## [2026-07-10] build | maintenance layer: template_sync.py + health/mp-update presets

Ecosystem-improvement brainstorm applied (three picks, all rooted in this session's observed pain). (1) [[ecosystem-audit]] grew `scripts/template_sync.py` — deterministic live↔`template/IN USE` drift report (`drift`/`live-only`/`template-only`, newline-normalized, `.obsidian` ignored) with asymmetric `--apply`: skills/ mirrors only common folders (curation stays human), ecosystem-kb/ mirrors fully; tests green; first live run caught real drift (template's stale `skills/llm-kb`). (2) [[preset]] `health` — audit.py + template_sync.py + llm-kb lint --stale in one punch list. (3) [[preset]] `mp-update` — the [[mattpocock-skills-lineup]] procedure codified (curated list, excluded five, two patches, verify, sync); memory updated to point at it. Rejected in brainstorm: retro preset (wrap-up covers), triage/research presets (skills already direct), any hook automation (no-hooks rule). Curation call: `ecosystem-audit` skill added to template — `/preset health` depends on its scripts. Synced [[ecosystem-audit]], [[preset]], [[ecosystem-overview]], index.

## [2026-07-10] install | mattpocock/skills v1.1.0 (curated)

Cloned mattpocock/skills at v1.1.0 and installed a curated set into `~/.claude/skills/`. Renames applied: to-prd → **to-spec**, to-issues → **to-tickets** (old folders + pre-update copies of grill-me/grill-with-docs/improve-codebase-architecture/teach → `_deprecated/mp-pre-v1.1-backup/`). Updated in place: grill-me, grill-with-docs (ADR/CONTEXT formats moved out to domain-modeling), improve-codebase-architecture (now HTML report), teach (structure unchanged). New: grilling (helper — one-question-at-a-time + confirmation gate), wayfinder, research, prototype, implement, triage, domain-modeling, codebase-design, ask-matt, setup-matt-pocock-skills, resolving-merge-conflicts. Excluded per [[mattpocock-skills-lineup]]: handoff (user call — [[context-handoff]] owns it), tdd ([[tdd-lineup]]), code-review (built-in name collision), diagnosing-bugs, writing-great-skills. Local patches: implement/SKILL.md points at superpowers TDD; ask-matt carries a "Local ecosystem note" routing excluded names. Synced [[github-planning]], [[grill-skills]], [[improve-codebase-architecture]], [[teach]]; new [[mattpocock-lifecycle]] + [[mattpocock-skills-lineup]]; index updated. Also fixed stale `/to-prd`/`/to-issues` invocations in [[preset]] init (SKILL.md + init.md). Template `IN USE/` mirrored from live and pushed (EstarinAzx/MY-SKILLS `e5d7687`): same curated set + vault pages. Follow-up same day: [[preset]] init gained conditional step 4 — `docs/agents/` missing → offer `/setup-matt-pocock-skills`, issue-tracker section seeded from the step-2 destination answer (9 steps now); fixed step 2's stale "governs steps 4 and 5" cross-ref; template re-synced and pushed.

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

## [2026-06-24] add | teach skill (multi-session teaching workspace)

New standalone skill `~/.claude/skills/teach/` documented. `/teach <topic>` —
user-invoked only (`disable-model-invocation: true`), turns the cwd into a
stateful teaching workspace producing beautiful self-contained HTML lessons
(`./lessons/0001-...html`) grounded in `MISSION.md`, fed by trusted
`RESOURCES.md`, tracked via ADR-style `./learning-records/`, reusing
`./assets/` components (shared stylesheet first). Pedagogy: knowledge→skills→
wisdom, storage-strength over fluency (retrieval/spacing/interleaving). Format
specs ship beside SKILL.md (MISSION/RESOURCES/LEARNING-RECORD/GLOSSARY). Routing
note: orthogonal to [[preset]] `learn` (codebase-vocab) and [[llm-kb]] (source
vaults) — teach instructs a *human learner* over many sessions. Wrote [[teach]],
updated index, [[ecosystem-overview]] layer 3. Doc-only sync (skill authored by
user, not built this session).

## [2026-06-21] build | /hp happy-path skill (forward-design twin of trace)

Fourth brainstorm build. New skill `~/.claude/skills/hp/` — `/hp [idea]` draws an MVD (minimum viable diagram): the one success spine of a user journey *before* code exists, the forward-design inverse of [[trace]] (which reads built code inward). Convey-mode menu asked each invoke (`ux+beat` default / `ux` / `system` / `beats`); box modes render Mermaid `flowchart`, persists to `.context/happy-path.md` (one `##` per flow) mirroring trace's flows.md — design-time vs built-time, two files side by side. Core discipline: success spine only, no error/edge forks (red-flagged); ≤2 clarifying Qs, not a grill. Wired into [[preset]] `init` as a step between grill and PRD (init renumbered to 8 steps; PRD embeds the MVD). GREEN application test (clean subagent, recipe-app idea with two planted error-branch temptations) passed 4/4 — resisted both forks, 0 clarifying Qs, correct `ux+beat` semantics, valid Mermaid. Synced [[happy-path]] (new), [[trace]], [[preset]], index, [[ecosystem-overview]]. Skipped the full RED pressure-gauntlet as disproportionate for a personal technique skill (ponytail).
