---
type: log
---

# Log

## [2026-07-23] pattern | relay-leg — one-ticket-per-leg + slot-delegated grunt

Captured the most refined use of the loop stack seen so far, from a live run:
`/relay N=1 read and follow .claude/relay-leg.md` draining a whole spec's
tracer-bullet tickets, fully unattended. Not a new skill — a **composition** of
existing pieces, each an existing rule taken to its limit: **N=1** one ticket
per leg (cache-fresh context per unit); the **body is a versioned file the leg
reads** (`read and follow .claude/relay-leg.md`), so the loop-body contract
lives in-repo not in the `/relay` command (files-not-sessions applied to the
*body*); **external-state** (GitHub issues + native deps + `.context/`) collapses
the relay Handoff to a one-line `state:` pointer; **gateless unattended wrap-up**
(`/context-update` per leg, `.context/` on main only); **spec-batch drainer**
that self-stops on queue-empty and closes the delivered spec. One **optional**
move — a per-body user choice this run, *not* a relay default: a leg delegated
its mechanical grunt to a cheap Wisp Target (grok-4.5) via [[slot]] (temporary
`haiku` Slot; Iron Rule — restore after every grunt finishes, before the gate),
the leg's own model leading and reviewing. That opt-in is the **relay×slot
composition** — a relay leg as slot *driver* — which neither [[relay]] nor
[[slot]] noted before.

Live proof: claude-wrapper spec #9, legs 1–5 landing #10 → #14, every leg
gate-green (typecheck · tests · build), one reviewed grunt per leg, zero human
touches. **Gotcha recorded:** a slot-driving body must use the current CLI
mechanic (`wisp snapshot` / `wisp snapshot revert`, [[slot]] v1.3.0) — the
retired `lease-<family>.json` files are gone; a stale body file still naming
leases misleads a cold leg (follow the live skill, not the body). Edits:
[[loop-engineering]] gains a "relay-leg pattern" section + decision-history line;
[[relay]] gains a relay×slot composition note; [[index]] relay line + dates
bumped. Doc-only — no skill/plugin change, no new kill switch or cap.

## [2026-07-18] update | slot gains parallel per-family Slots (wisp-slot 1.2.0)

[[slot]]'s "one lease at a time" limit lifted at user request — subagents can
now run on several Wisp Targets at once. Single `~/.claude/slot/lease.json` →
**per-family** `lease-<family>.json`; each family (`haiku`/`sonnet`/`opus`/
`fable`) is an independent Slot with its own lease, held and restored on its
own agents' completion. Safe, not reckless: the four family routes resolve
independently through the Bridge, so the load-bearing invariant (never restore
under a live agent) is per-family — restoring `haiku` can't disturb a `sonnet`
agent. The old constraint was mechanical (one lease file = one recovery
record), reversing design-spec #110 §98's "concurrent leases out of scope" once
the per-family split gave each Slot its own recovery record. **Hard ceiling: 4
distinct Targets concurrently** (only 4 family words); agents sharing a Target
share a family; no queue for a 5th (add if ever hit — ponytail). SKILL.md
rewrite (step 2 per-family lease check, step 7 parallel hold, new "Running
Slots in parallel" section, Limits + rationalization rows); `session-start.js`
+ `wisp-statusline.js` glob `lease*.json` (back-compat with legacy singular;
badge `!LEASE×N`); plugin.json 1.1.2 → **1.2.0**; README updated. Edited the
Wisp checkout source (`plugins/slot/`), pushed to cache via
`claude plugin update wisp-slot@wisp-router` — 1.2.0 cache verified identical
to source. JS logic tested green (temp HOME, 2 fake leases → hook lists both,
badge `!LEASE×2`/`!LEASE`/none). Live 2-Target E2E deferred (needs Bridge up +
two credentialed Targets). New decision doc in the Wisp `.context/decisions/`;
synced [[slot]] + index date.

**Follow-up (1.2.1):** the printed 9-box "Slot Progress" checklist was noise —
worse under parallel families (reprints per step). SKILL.md now says track the
steps **silently** (harness task tools, not the transcript), surfacing only
warnings/spawns/restores. Checklist block removed; step sequence kept as a
one-line reference above the detailed steps. Bumped 1.2.0 → 1.2.1, plugin
update verified (checklist gone, "track silently" present). Triage fast-path
was already checklist-free.

## [2026-07-17] update | slot goes plugin-only + session-awareness (Wisp #124)

[[slot]] delivery flipped: personal skills-dir copy retired to
`_deprecated/`, the `wisp-slot@wisp-router` plugin (local directory marketplace
= the Wisp checkout) is now the one copy on this machine. Plugin grew
session-awareness (Wisp #124, v1.1.0): SessionStart hook announcing the Bridge
(routing snapshot, headless CLI cheat sheet, stale-lease warning; silent
unbridged) + node statusline badge (`[WISP fable→<model>]` live per refresh,
`!LEASE` marker) wired into elucidate's composed wrapper at the checkout path.
Detection = env + Wisp-home (env alone lies — profile trap). Cache gotcha:
directory marketplaces install a versioned snapshot; repo edits need
`claude plugin update wisp-slot@wisp-router` (full id — bare name fails).
Source-checkout fallback for old globals retired (global 2.0.13). Same-day
follow-ups (v1.1.1): triage fast path — a bare "route X to family Y" ask is one
`wisp routing set`, no lease/checklist (a live run danced all 9 steps for a
plain rebind); badge lease marker went ASCII `!LEASE` (wide ⚠ overlapped the
next cell); badge colored cyan. All pushed to origin. Vault + index synced.

## [2026-07-17] add | slot skill (Wisp #110)

New personal skill [[slot]] — Claude Code drives its own Wisp routing:
snapshot → lease → rebind Slot family → spawn Agent via family word →
hold until agents finish → guarded restore. Built TDD-style (baseline
early-restore failure observed, countered, 3/3 re-tests green); verified live
end-to-end through a bridged claude-wisp session (serve log:
`route family 'claude-haiku-4-5…' -> codex model=gpt-5.6-terra`). Two gaps
found live and fixed: checkout path hardcoded (no filesystem hunting), lease
path made absolute (a run wrote it cwd-relative). Accidental TUI open during
the hunt rewrote all family routes to anthropic — repaired same session.
Vault + routing sheet synced.

## [2026-07-16] update | relay gains binary resolution (claude-wisp support)

[[relay]] now tracks which launcher started the chain so every leg respawns
with the **same binary** — a `claude-wisp` / local-gateway wrapper otherwise
silently falls back to the real `claude` and bypasses the router. New `binary:`
state field, resolved once (stored value → `$env:CLAUDE_BINARY` →
"wisp"-in-command-line autodetect → default `claude`) and persisted for resumes
and future legs. Wrapper binaries (`wisp` / `.cmd` / `.ps1`) spawn through
`cmd.exe /c` because direct `Start-Process claude-wisp --background` is flaky
and often registers no visible leg; the spawn block also now rebuilds the full
`/relay` command string from state instead of a hardcoded example. Doc-only
change to the skill — no new kill switch, cap, or fencing; state/permission/
no-watchdog policy unchanged. User-authored edit to live `skills/relay/SKILL.md`;
mirrored into `template/IN USE` (0 drift) and synced [[relay]].

[[context-handoff]]'s two append-only files now fold into a **thin index +
entry folder** (llm-kb's shape, borrowed): `decisions.md`/`gotchas.md` become
newest-first link indexes over `decisions/`·`gotchas/` one-file-per-entry
folders — killing the `decisions.md` 2000-line wall. Index is the wikilink
target so `overview.md` is unchanged; entries back-link their index (never
orphans); `history.md` and all bounded files stay flat. New
`scripts/lint.py` — a **self-contained** stdlib health check (broken-link /
orphan / entry-not-indexed / index-dangling / `--stale`), deliberately NOT
coupled to llm-kb's scripts so context-sync installs standalone; 7 unit tests
green. Search dropped as overkill at ~a dozen files. Legacy flat `.context/`
migrates on the `/context-update` path — offered when bloated, never forced.
Brainstorm→spec→plan→build inline (superpowers); design + plan in
`skills/context-sync/design/`. FF-merged to main (with the finished relay
commits). Mirrored into `template/IN USE` (context-sync + relay → 0 drift).
Synced [[context-handoff]]; `/preset health` gates the template push.

## [2026-07-15] update | relay legs move to native background agents

[[relay]] now dispatches each new leg with `Start-Process claude` plus
`--background`, keeping the reconstructed `/relay` command as the initial
prompt and the target project as cwd. `claude agents` is the inspection and
management surface, not the spawn command. Successful old legs end with
`[relay: leg <k> scheduled loop is running in claude agents]`; spawn failures
set `stop: true`, notify, and omit that success line. State, fencing, caps,
permission modes, and no-watchdog policy remain unchanged. Synced [[relay]].

## [2026-07-14] curate | template adopts 4 live-only skills

User opted to mirror the standing `live-only` rows into MY-SKILLS:
elucidate-plugin (skills-dir autoload copy — nested `.git` stripped to avoid
the [[template-plugins-snapshot]] gitlink rot; template also keeps its own
root copy), pencil-bridge, screenshot-diff, token-sync. `template_sync.py`
now reports 0 findings — template mirrors the full live skills lineup.
Pushed as `9aa068c` (after `187fb4f`, the wayfinder-wiring + mp-flag-flip
mirror).

## [2026-07-14] wire | wayfinder routed (sheet row + init fog fork)

Wayfinder was in the ecosystem but chained to nothing — only reachable by
typing `/wayfinder` or via ask-matt; sole preset mention was mp-update's
install list. Two wires added: (1) `~/.claude/CLAUDE.md` situation→invoke row
"Effort too big for one session / needs investigation map → `/wayfinder` →
to-spec → to-tickets → implement"; (2) [[preset]] init step 5 fog fork —
grill hits investigation-shaped unknowns (research/spikes/prototypes needed
before deciding) → offer `/wayfinder`, steps 6–8 wait, funnel re-enters at
step 6 after the map clears. Synced [[mattpocock-lifecycle]] + [[preset]].

## [2026-07-13] patch | model-invocation enabled on 3 mattpocock skills

`disable-model-invocation: true → false` on grill-with-docs, to-spec,
to-tickets (user-directed, during Wisp's routing-map `/preset init` run —
the funnel invokes all three mid-flow and upstream's user-only flag stalled
it each time). Now a standing local patch: mp-update preset step 5 lists the
flips for reapply after refresh; noted on [[grill-skills]] +
[[github-planning]]. Template mirror pending this session's
`/preset health`.

## [2026-07-13] decision | template drops plugins/cache (gitlink rot)

Investigated the recurring ` M plugins/cache/...superpowers/5.1.0` status
noise in the template repo. Root cause: the 2026-06-11 plugins snapshot
committed the superpowers cache dir with its embedded `.git` → gitlink
(160000), dangling on GitHub, unclonable; whole snapshot also frozen at
5.1.0 vs live 6.1.1 (template_sync only covers skills/ + ecosystem-kb/).
Decision [[template-plugins-snapshot]]: keep registries + marketplaces
(rebuildable installs), untrack + .gitignore `plugins/cache/**`; rejected a
third sync root. Standing ⚠️: registry/marketplace snapshots still manual.

## [2026-07-13] build | global CLAUDE.md routing sheet

Closed the push/pull gap: skill descriptions route single skills every
session, but chains/pairings/standing-rules lived vault-only (pull). New
`~/.claude/CLAUDE.md` (user-level memory, auto-loads every session, every
dir) — 4-layer map, situation→invoke table, standing rules, vault pointer.
Contract: routing only (~50 lines), vault stays the encyclopedia; division
vs [[getclaude]] IN USE copy = machine-wide routing vs per-project behavior.
Sync duty added: lineup changes update the sheet same session. Open
follow-ups: file unversioned; claude-md-stale-ref lint doesn't cover it.
New [[global-claude-md]] config page; index updated.

## [2026-07-12] install | drawio plugin (365-skills marketplace)

Added marketplace `Agents365-ai/365-skills`, installed plugin `drawio` —
skill `drawio-skill` v1.28.2 (.drawio XML gen + desktop-CLI export, 28
scripts: shapesearch/autolayout/code+IaC importers/seqlayout/c4/diff/heatmap
etc.). Skills-only: no hooks, no MCP — no-hooks rule clean. Assessed fit:
inline Mermaid in `.context/` stays source of truth for [[happy-path]] /
[[trace]]; drawio is the presentation/export layer (Mermaid→drawio CLI
conversion on ≥v30 makes promotion zero-rework; `seqlayout.py` suits traced
flows). Niche "polished exportable diagram" was vacant — no lineup conflict;
sibling mermaid/plantuml/excalidraw/tldraw plugins deliberately skipped.
Deps gap: draw.io CLI + Graphviz not installed (winget `JGraph.Draw` 30.2.6,
`Graphviz.Graphviz`) — browser-fallback/XML-only until then. No skill edits
to hp/trace (speculative wiring rejected); pairing documented in [[drawio]],
cross-linked from both pages. Also fixed [[ecosystem-overview]] layer 1
staleness: ponytail was missing from the session-modes list.

## [2026-07-12] doc | getclaude page (rediscovered wiring)

User forgot where `getclaude` lives — rediscovered and vaulted: profile
function (line 1 of the WindowsPowerShell profile on D:) →
`~/.claude/scripts/getclaude.ps1` → copies `template/IN USE/CLAUDE.md` into
cwd, `-Force` to overwrite. New [[getclaude]] config page; canonical-edit
rule recorded (edit the template copy, re-drop with -Force). Exactly the
archaeology the vault exists to prevent — now it can't be forgotten twice.
Same pass revised the universal CLAUDE.md itself: provenance header (edit
the canonical copy, not project copies), section 6 rewired to the [[preset]]
pick-up/wrap-up loop instead of bare `/context-update`, /trace style merged
into plain-language (9 → 8 sections), "User Preference" renamed
"JavaScript Style".

## [2026-07-12] synthesis | harness-engineering page

Named the umbrella: new [[harness-engineering]] synthesis — the
prompt→context→harness ladder (pick-up/wrap-up as the context-engineering
gateway the whole setup grew from), the six harness components here
(hooks/modes, contracts, state files, enforcement, session lifecycle,
reproducibility), the pain→ritual→codify→generalize practice, and why a
harness compounds where skill-hoarding doesn't (graph vs islands; the vault
as the load-bearing piece). [[loop-engineering]] filed as subsystem.
Doc-only sync: page + index.

## [2026-07-12] synthesis | loop-engineering page

Named the loop stack as a concept: new [[loop-engineering]] synthesis —
runner (`/loop`) / lifecycle ([[relay]]) / body ([[preset]] loop bodies) /
contract, the files-not-sessions principle (stop is pull, not push), the
composability ladder (one-shot → looped → relayed), and the consolidated
decision history incl. the bypass-permissions flip. Doc-only sync: page +
index; no skill changes.

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

## [2026-07-17] remove | elucidate parked (temporary uninstall, user request)

User-requested temporary uninstall of [[elucidate]] ("don't need it lately,
will reinstall later") — parked, NOT deprecated; [[commenting-mode-lineup]]
winner unchanged. Steps: `claude plugin uninstall elucidate-local@elucidate`;
folder moved intact `~/.claude/skills/elucidate-plugin` →
`~/.claude/_deprecated/elucidate-plugin` (kills the skills-dir auto-load +
its SessionStart/UserPromptSubmit hooks); settings.json cleaned
(enabledPlugins `elucidate@elucidate` + directory-marketplace entry removed).
Statusline gotcha: the composed wrapper lived INSIDE the plugin folder —
relocated to neutral `~/.claude/hooks/statusline-wrapper.ps1` and settings
repointed; elucidate badge referenced by absolute skills path so it
auto-revives on reinstall. Verified: wrapper renders `[CAVEMAN] [PONYTAIL]`,
plugin list clean. Reinstall = move folder back to
`~/.claude/skills/elucidate-plugin`. Synced [[elucidate]],
[[settings-and-hooks]], index, routing sheet.
