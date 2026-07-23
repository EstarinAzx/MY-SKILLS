---
type: skill
updated: 2026-07-20
tags: [skill, wisp, routing, plugin]
source: built 2026-07-17; spec Wisp repo docs/superpowers/specs/2026-07-17-slot-skill-design.md (#110); session-awareness Wisp #124; CLI-native rewrite Wisp #131 (PR #137, merged 2026-07-20, plugin v1.3.0)
---

# slot

`/slot` — the Wisp Slot dance: snapshot a family route, rebind a sacrificial
family (default `haiku`) to any Wisp Target, spawn the Agent tool with that
family word, hold until every Slot-driven agent finishes, then revert the row.
**CLI-native since v1.3.0 (Wisp #131, merged 2026-07-20):** the hold/restore
primitive is the wisp-router CLI's own **`wisp snapshot <family>`** /
**`wisp snapshot revert <family>`** (row-based Routing-map snapshots, shipped
in #127), recorded in a snapshot store under `~/.wisp`. The old hand-written
lease files (`~/.claude/slot/lease-<family>.json`) are **gone** — the snapshot
store *is* the recovery record. **Requires wisp-router ≥ 2.0.24.**

**Crash recovery (changed mechanic):** a crash or force-kill leaves the family
rebound with its **snapshot still held** — the store survives the session. Next
session the SessionStart hook warns about held rows; recover each with
`wisp snapshot revert <family>` (confirm no agent on that family is still
running first). Never hand-edit the store or `wisp routing set` over a held
snapshot without reverting first — the held snapshot is the only recovery
record. Revert is **unconditional** (writes the recorded value back over
whatever's live, prints the overwritten value, clears the snapshot) — **no
compare-and-set**; the skill re-reads `wisp routing` first if it wants a guard.
Trying to snapshot an already-held row errors `'<family>' already snapshotted
(<value>)` → STOP, surface it, revert-then-resnapshot only after the user
confirms the family is idle.

**Parallel Slots:** up to **4 distinct Targets at once** (only 4 family words:
`haiku`/`sonnet`/`opus`/`fable`). Each family is its own Slot with its own
snapshot, held and reverted independently — restoring `haiku` can't disturb a
live `sonnet` agent. Agents sharing a Target share one family (one snapshot,
many agents); a 5th distinct concurrent Target waits for a family to free (no
queue built). Reserve `fable` if the session's own default model rides it.

**Delivery (unchanged): the plugin is the one copy.** Installed as
`wisp-slot@wisp-router` from a **local directory marketplace** pointing at the
Wisp checkout (`D:/.claude/claude projects/autocomplete_extension`). The old
personal skills-dir copy is retired to `~/.claude/_deprecated/slot/`. Trap:
directory marketplaces install into a **versioned cache**
(`~/.claude/plugins/cache/wisp-router/wisp-slot/<ver>/`), so repo edits reach
the live skill/hook only after `claude plugin update wisp-slot@wisp-router` —
the FULL id; bare `wisp-slot` fails "not found" (bump the plugin version for a
new cache dir — v1.3.0 for the CLI-native rewrite).

**Triage fast path (unchanged):** a plain "route X to family Y" ask with no
subagent to run is a persistent routing edit — one `wisp routing set`, surface
warnings, report the prior value, stop. No snapshot, no checklist, no restore.
The full snapshot/hold/revert procedure applies only when a subagent runs
through a temporary rebind.

**Session-awareness (Wisp #124, unchanged shape):** the plugin also ships a
SessionStart hook (all sources) — bridged sessions get a Wisp announcement,
live family-route snapshot (`wisp routing --json`, fail-soft), the headless CLI
cheat sheet (`wisp routing` / `wisp providers` / `wisp models <provider>`), and
a **held-snapshot** warning (formerly stale-lease); silent when unbridged. Plus
a node statusline badge (`[WISP fable→gpt-5.6-terra]`, live per-refresh
resolution, held-snapshot marker, degrades to `[WISP]`). Bridged detection =
`ANTHROPIC_BASE_URL` set AND Wisp home exists (`WISP_HOME` honored) — env alone
lies (profile trap). The badge is wired into elucidate's composed
`statusline-wrapper.ps1`, pointing at the checkout path (stable across
versions, unlike the cache).

Iron rule (unchanged): the Bridge resolves routing per request, so early
revert silently reroutes a live agent — a returned task id proves launch, not
completion. Hold each family's binding until every agent launched through
*that* family finishes. Aliases never work as Agent model values; family words
only. Spawn labels the agent's `description` with the real backend
(`<target model>: <task>`) since the family word misleads in the UI. History:
pre-2.0.11 globals needed a source-checkout fallback (`bun
packages/tui/src/index.tsx routing …`) — retired; lease files replaced by CLI
snapshots in v1.3.0 (#131).

Built TDD-style: baseline agents failed the early-restore trap ("binding only
matters at spawn"); skill counters it; 3/3 pressure re-tests green; verified
live end-to-end through a bridged `claude-wisp` session (`[bridge] route family
'claude-haiku-4-5…' -> codex model=gpt-5.6-terra`).
