# Relay Background-Agent Spawn Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dispatch every new Relay leg as a native Claude Code background session, visible through `claude agents`, while preserving Relay's existing state, permission, handoff, and stop behavior.

**Architecture:** Relay remains prompt-ware: `skills/relay/SKILL.md` tells the active session how to rebuild and launch the next leg. Add the native `--background` CLI flag to the existing PowerShell `Start-Process` argument list; keep the quoted `/relay ...` command as one positional prompt. Sync historical design language and current vault pages, then record the change in the append-only vault log.

**Tech Stack:** Claude Code CLI 2.1.209+, PowerShell `Start-Process`, Markdown skills/specs, llm-kb vault, deterministic ecosystem audit/lint scripts.

## Global Constraints

- Approved design: `skills/docs/superpowers/specs/2026-07-15-relay-background-agent-design.md`.
- Spawn with `claude --background <relay prompt>`; `claude agents` is management UI, not the spawn command.
- Launch from target project root so the background leg inherits the cwd and reads `.claude/relay/<slug>.md`.
- Keep `mode=bypass` default (`--dangerously-skip-permissions`) and `mode=accept` behavior unchanged.
- Keep state frontmatter, Handoff, Breadcrumbs, leg fencing, `stop: true`, `max_legs: 20`, PushNotification, and body completion unchanged.
- After successful spawn, old leg's final user-facing line must be exactly `[relay: leg <k> scheduled loop is running in claude agents]`.
- Never print that bracketed success line when spawning fails.
- No scripts, hooks, wrappers, schedulers, state keys, dependencies, or changes to plain `/loop`.
- Do not edit immutable `ecosystem-kb/raw/`.
- Working tree already contains unrelated changes. Stage and commit only clean paths named by each task; never use `git add -A`, `git add .`, reset, checkout, clean, or stash.
- Pre-existing modifications exist in `ecosystem-kb/index.md`, `ecosystem-kb/log.md`, and `ecosystem-kb/wiki/syntheses/loop-engineering.md`. Current index/synthesis wording remains accurate, so do not edit either file. Prepend the required entry to dirty `log.md`, preserve its existing diff, and leave it unstaged for the user rather than bundling unrelated work into this change.
- Existing design commits `8007963` and `d30e180` are already complete; do not rewrite or amend them.

---

### Task 1: Update Relay's executable spawn contract

**Files:**
- Modify: `C:\Users\S.D\.claude\skills\relay\SKILL.md:8-12,95-114,124-137`

**Interfaces:**
- Consumes: state frontmatter fields `spawn_flags`, `interval`, `n`, and `body`; Claude Code CLI syntax `claude [options] [prompt]`.
- Produces: canonical Relay spawn command and exact post-spawn final line consumed by all future Relay legs and mirrored in Task 2.

- [ ] **Step 1: Capture the pre-change assertions**

Run from any directory:

```powershell
$path = 'C:\Users\S.D\.claude\skills\relay\SKILL.md'
$text = Get-Content -Raw $path
if ($text -notmatch 'Start-Process claude') { throw 'missing spawn instruction' }
if ($text -match "'--background'") { throw 'expected pre-change skill without --background' }
if ($text -match '\[relay: leg <k> scheduled loop is running in claude agents\]') { throw 'expected pre-change skill without final status line' }
'RED: background spawn contract is absent'
```

Expected:

```text
RED: background spawn contract is absent
```

- [ ] **Step 2: Replace Relay sequence steps 3–5 with the background-session contract**

In `skills/relay/SKILL.md`, replace current relay-sequence steps 3–5 with this exact Markdown:

````markdown
3. Spawn the next leg as a native background agent (PowerShell tool, from the
   project root — the new session must inherit this cwd). Rebuild args from
   frontmatter (`spawn_flags` + `interval` + `n` + `body`); `--background`
   registers the session in `claude agents`, and the quoted final element keeps
   the `/relay` command a single prompt argument:

   ```powershell
   Start-Process claude -ArgumentList @('--background','--dangerously-skip-permissions','"/relay 10m N=8 /preset ticket-loop"')
   ```

4. If spawning fails (`claude` missing from PATH, invalid arguments, or process
   launch error), PushNotification `"relay: <slug> background spawn failed"`,
   set `stop: true`, stop the loop, and do not retry. Do not print the success
   line below.
5. After a successful spawn, PushNotification
   `"relay: leg <k> spawned for <slug>"` (load the tool via ToolSearch if
   deferred), stop own loop, and end the user-facing response with exactly:

   ```text
   [relay: leg <k> scheduled loop is running in claude agents]
   ```
````

Also change the opening description at lines 9–12 from generic fresh-session wording to:

```markdown
file, spawns a fresh Claude background session whose injected first prompt is
this same `/relay` command, and stops its own loop. The next leg appears in
`claude agents`; its context is just startup hooks + this skill + the handoff.
```

In `## Sharp edges`, replace the window-specific permission sentence:

```markdown
  leg on its first permission prompt until a human looks at its window
```

with:

```markdown
  background leg on its first permission prompt until a human opens
  `claude agents`
```

- [ ] **Step 3: Run deterministic content checks**

```powershell
$path = 'C:\Users\S.D\.claude\skills\relay\SKILL.md'
$text = Get-Content -Raw $path
$required = @(
  "'--background'",
  'registers the session in `claude agents`',
  '[relay: leg <k> scheduled loop is running in claude agents]',
  'Do not print the success',
  'set `stop: true`',
  'do not retry'
)
foreach ($needle in $required) {
  if (-not $text.Contains($needle)) { throw "missing: $needle" }
}
if ($text.Contains('idle husk')) { throw 'stale foreground-window wording remains' }
'PASS: Relay skill specifies background spawn and success/failure messaging'
```

Expected:

```text
PASS: Relay skill specifies background spawn and success/failure messaging
```

- [ ] **Step 4: Inspect only this file's diff**

```powershell
git -C 'C:\Users\S.D\.claude' diff -- skills/relay/SKILL.md
```

Expected: one focused Markdown diff; no state-machine or permission-default changes.

- [ ] **Step 5: Commit only the Relay skill**

```powershell
git -C 'C:\Users\S.D\.claude' add -- skills/relay/SKILL.md
git -C 'C:\Users\S.D\.claude' commit -m 'feat(relay): spawn legs as background agents'
```

Expected: commit succeeds with only `skills/relay/SKILL.md` staged.

---

### Task 2: Amend Relay design history for native background agents

**Files:**
- Modify: `C:\Users\S.D\.claude\skills\docs\superpowers\specs\2026-07-11-relay-design.md:1-8,20-28,63-68,104-114,127-141,167-174`

**Interfaces:**
- Consumes: Task 1's canonical `Start-Process claude -ArgumentList @('--background', ...)` command and exact bracketed final line.
- Produces: historical design amended to describe current behavior without erasing the original 2026-07-11 rationale.

- [ ] **Step 1: Add a dated status amendment**

Extend the `**Status:**` block with:

```markdown
Amended 2026-07-15 — spawned legs now use Claude Code's native `--background`
mode and are managed through `claude agents`; `claude agents` itself is not the
spawn command because it accepts no initial Relay prompt.
```

- [ ] **Step 2: Correct foreground-terminal claims and relay sequence**

Make these exact semantic replacements:

- `spawns a fresh Claude session in a new terminal window` → `spawns a fresh Claude background session`
- `Spawn a new terminal in the same cwd:` → `Spawn a native background agent in the same cwd:`
- Replace old shorthand command with:

```powershell
Start-Process claude -ArgumentList @('--background','--dangerously-skip-permissions','"/relay 10m N=8 /preset ticket-loop"')
```

- After successful spawn, document this exact final line:

```text
[relay: leg <k> scheduled loop is running in claude agents]
```

- State explicitly: spawn failure sets `stop: true`, notifies, stops without retry, and never prints the success line.
- Delete the obsolete v2 suggestion to use `wt -w 0 nt`; native agent view replaces terminal-tab accumulation.
- Update success criterion `new window opens` to `new background session appears in claude agents`.

Do not rewrite historical permission amendment: `--dangerously-skip-permissions` remains the current default.

- [ ] **Step 3: Check design consistency**

```powershell
$path = 'C:\Users\S.D\.claude\skills\docs\superpowers\specs\2026-07-11-relay-design.md'
$text = Get-Content -Raw $path
if (-not $text.Contains("'--background'")) { throw 'background flag missing' }
if (-not $text.Contains('[relay: leg <k> scheduled loop is running in claude agents]')) { throw 'final line missing' }
if ($text.Contains('new terminal window')) { throw 'stale terminal claim remains' }
if ($text.Contains('wt -w 0 nt')) { throw 'obsolete terminal-tab idea remains' }
'PASS: original Relay design reflects 2026-07-15 amendment'
```

Expected:

```text
PASS: original Relay design reflects 2026-07-15 amendment
```

- [ ] **Step 4: Commit only historical design amendment**

```powershell
git -C 'C:\Users\S.D\.claude' add -- skills/docs/superpowers/specs/2026-07-11-relay-design.md
git -C 'C:\Users\S.D\.claude' commit -m 'docs(relay): amend design for background agents'
```

Expected: one-file documentation commit.

---

### Task 3: Sync Relay's current knowledge page and append history

**Files:**
- Modify: `C:\Users\S.D\.claude\ecosystem-kb\wiki\skills\relay.md:1-44`
- Modify without staging: `C:\Users\S.D\.claude\ecosystem-kb\log.md:5-7` (already dirty before this task)
- Do not modify: `C:\Users\S.D\.claude\ecosystem-kb\index.md`
- Do not modify: `C:\Users\S.D\.claude\ecosystem-kb\wiki\syntheses\loop-engineering.md`

**Interfaces:**
- Consumes: Task 1's current behavior and Task 2's decision history.
- Produces: queryable `[[relay]]` current-state page and append-only timeline entry. Existing index/synthesis summaries remain broad enough to stay correct.

- [ ] **Step 1: Update `wiki/skills/relay.md` current state**

Set frontmatter:

```yaml
updated: 2026-07-15
```

Replace the current `Start-Process claude` sentence with:

```markdown
spawns a fresh background session via `Start-Process claude` with
`--background` and the same `/relay` command injected as its first prompt, then
stops its own loop. The leg is visible and manageable through `claude agents`;
that command opens the manager and is not itself used to spawn the prompted
leg. Fresh leg = startup hooks + skill + handoff only — context rot and
uncached full-history re-reads (5-min cache TTL) reset every leg.
```

Add to the kill-switch/behavior paragraph:

```markdown
After a successful spawn, the old leg ends with
`[relay: leg <k> scheduled loop is running in claude agents]`; spawn failures
set `stop: true`, notify, and never print that success line.
```

Keep existing permission-risk and no-watchdog paragraphs unchanged except replacing any visible-window wording with `claude agents` management wording.

- [ ] **Step 2: Commit the clean Relay page before touching dirty `log.md`**

```powershell
git -C 'C:\Users\S.D\.claude' add -- ecosystem-kb/wiki/skills/relay.md
git -C 'C:\Users\S.D\.claude' commit -m 'docs(ecosystem-kb): record Relay background agents'
```

Expected: one-file vault commit. `index.md`, `log.md`, and `loop-engineering.md` remain unstaged.

- [ ] **Step 3: Prepend the append-only log entry without staging it**

Insert immediately before the current topmost `## [` entry in `ecosystem-kb/log.md`:

```markdown
## [2026-07-15] update | relay legs move to native background agents

[[relay]] now dispatches each new leg with `Start-Process claude` plus
`--background`, keeping the reconstructed `/relay` command as the initial
prompt and the target project as cwd. `claude agents` is the inspection and
management surface, not the spawn command. Successful old legs end with
`[relay: leg <k> scheduled loop is running in claude agents]`; spawn failures
set `stop: true`, notify, and omit that success line. State, fencing, caps,
permission modes, and no-watchdog policy remain unchanged. Synced [[relay]].

```

Do not edit or reorder the 2026-07-12 build entry. Do not stage `log.md`: it already contains unrelated user changes that must not be bundled into this task's commit.

- [ ] **Step 4: Run vault content checks**

```powershell
$vault = 'C:\Users\S.D\.claude\ecosystem-kb'
$relay = Get-Content -Raw "$vault\wiki\skills\relay.md"
$log = Get-Content -Raw "$vault\log.md"
if (-not $relay.Contains('--background')) { throw 'relay page missing background flag' }
if (-not $relay.Contains('[relay: leg <k> scheduled loop is running in claude agents]')) { throw 'relay page missing final line' }
if (-not $log.Contains('## [2026-07-15] update | relay legs move to native background agents')) { throw 'log entry missing' }
'PASS: Relay vault page and append-only log synchronized'
```

Expected:

```text
PASS: Relay vault page and append-only log synchronized
```

- [ ] **Step 5: Confirm shared dirty files stayed unstaged**

```powershell
$staged = git -C 'C:\Users\S.D\.claude' diff --cached --name-only
foreach ($path in @('ecosystem-kb/index.md','ecosystem-kb/log.md','ecosystem-kb/wiki/syntheses/loop-engineering.md')) {
  if ($staged -contains $path) { throw "unexpected staged shared file: $path" }
}
'PASS: shared pre-existing changes remain unstaged'
```

Expected:

```text
PASS: shared pre-existing changes remain unstaged
```

---

### Task 4: Verify native background dispatch without starting a Relay chain

**Files:**
- None.

**Interfaces:**
- Consumes: installed `claude.exe`, Task 1 command shape, native `claude agents --json` management surface.
- Produces: observed evidence that background dispatch returns, uses expected cwd, and becomes visible to agent manager.

- [ ] **Step 1: Verify installed CLI surfaces**

```powershell
$rootHelp = claude --help | Out-String
$agentsHelp = claude agents --help | Out-String
if ($rootHelp -notmatch '--bg, --background') { throw 'Claude CLI lacks --background' }
if ($agentsHelp -notmatch '--json') { throw 'Claude CLI lacks agents --json' }
'PASS: installed Claude CLI supports background dispatch and agent inspection'
```

Expected:

```text
PASS: installed Claude CLI supports background dispatch and agent inspection
```

- [ ] **Step 2: Launch one harmless bounded background session from repo root**

Use `--permission-mode manual`, not bypass, because this smoke prompt needs no tools. Give it a unique name so it can be identified without confusing it with unrelated sessions:

```powershell
$cwd = 'C:\Users\S.D\.claude'
$name = 'relay-bg-smoke-20260715'
$prompt = 'Reply with exactly relay-background-ok. Do not use tools.'
Start-Process claude -WorkingDirectory $cwd -ArgumentList @('--background','--permission-mode','manual','--name',$name,'"' + $prompt + '"') -Wait
'PASS: background dispatch process returned'
```

Expected:

```text
PASS: background dispatch process returned
```

This does not start `/relay`, schedule `/loop`, edit state, or use bypass permissions.

- [ ] **Step 3: Confirm agent registration and inherited cwd**

Run immediately after Step 2:

```powershell
$agents = @(claude agents --json --all | ConvertFrom-Json)
$session = $agents | Where-Object { $_.name -eq 'relay-bg-smoke-20260715' } | Select-Object -First 1
if ($null -eq $session) { throw 'background smoke session not visible in claude agents --json' }
if ($session.cwd -ne 'C:\Users\S.D\.claude') { throw "wrong cwd: $($session.cwd)" }
"PASS: $($session.name) registered with cwd $($session.cwd) and status $($session.status)"
```

Expected prefix:

```text
PASS: relay-bg-smoke-20260715 registered with cwd C:\Users\S.D\.claude and status
```

`status` may already be `completed` because the prompt is intentionally cheap.

- [ ] **Step 4: Verify docs contain no stale foreground-terminal contract**

```powershell
$paths = @(
  'C:\Users\S.D\.claude\skills\relay\SKILL.md',
  'C:\Users\S.D\.claude\skills\docs\superpowers\specs\2026-07-11-relay-design.md',
  'C:\Users\S.D\.claude\ecosystem-kb\wiki\skills\relay.md',
  'C:\Users\S.D\.claude\ecosystem-kb\wiki\syntheses\loop-engineering.md'
)
$stale = Select-String -Path $paths -Pattern 'new terminal window|new window opens|idle husk|wt -w 0 nt'
if ($stale) { $stale | ForEach-Object { "{0}:{1}: {2}" -f $_.Path,$_.LineNumber,$_.Line.Trim() }; throw 'stale foreground-terminal claims remain' }
'PASS: no stale foreground-terminal contract remains'
```

Expected:

```text
PASS: no stale foreground-terminal contract remains
```

- [ ] **Step 5: Run ecosystem audit and vault lint**

```powershell
python 'C:\Users\S.D\.claude\skills\ecosystem-audit\scripts\audit.py'
python 'C:\Users\S.D\.claude\skills\llm-kb\scripts\lint.py' 'C:\Users\S.D\.claude\ecosystem-kb'
```

Expected: neither command reports a Relay-specific error. Existing accepted findings outside Relay scope may remain; record them without fixing them.

- [ ] **Step 6: Verify clean task paths and preserved shared changes**

```powershell
$clean = git -C 'C:\Users\S.D\.claude' status --short -- skills/relay/SKILL.md skills/docs/superpowers/specs/2026-07-11-relay-design.md ecosystem-kb/wiki/skills/relay.md
if ($clean) { $clean; throw 'committed task paths remain dirty' }
$shared = git -C 'C:\Users\S.D\.claude' status --short -- ecosystem-kb/index.md ecosystem-kb/log.md ecosystem-kb/wiki/syntheses/loop-engineering.md
if ($shared -notmatch 'ecosystem-kb/log.md') { throw 'expected unstaged log.md with pre-existing + appended history' }
'PASS: task paths clean; shared user changes preserved unstaged'
```

Expected:

```text
PASS: task paths clean; shared user changes preserved unstaged
```

- [ ] **Step 7: Report acceptance evidence**

Report these facts exactly:

```text
- Relay spawn instruction uses `claude --background`, not `claude agents`.
- Harmless background smoke session appeared in `claude agents --json` with the expected cwd.
- Successful old legs end with `[relay: leg <k> scheduled loop is running in claude agents]`.
- Spawn failures set `stop: true`, notify, and do not print the success line.
- No full Relay chain was started during verification.
```

No commit: this task changes no files.
