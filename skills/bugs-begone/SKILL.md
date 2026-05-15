---
name: bugs-begone
description: Interactive debugging mode that generates hypotheses, instruments code with runtime logs, and iteratively fixes bugs with human-in-the-loop verification. Only for hard-to-diagnose bugs; in those cases, remind the user that debug-mode is available, and never proactively activate this skill.
---

# Debug Mode

You are in **bugs-begone** — a hypothesis-driven debugging workflow. Do NOT jump to fixes. Follow each phase in order.

---

## Phase 1: Understand the Bug

Ask the user (if not already provided): expected vs actual behavior, reproduction steps, error messages.

Read the relevant source code. Understand the call chain and data flow.

## Phase 2: Generate Hypotheses

Generate **testable hypotheses** as a numbered list:

```
Based on my analysis, here are my hypotheses:

1. **[Title]** — [What might be wrong and why]
2. **[Title]** — [Explanation]
3. **[Title]** — [Explanation]
```

Include both obvious and non-obvious causes (race conditions, off-by-one, stale closures, type coercion, etc.).

## Phase 3: Instrument the Code

### Log file

Write to **`{project_root}/.claude/debug.log`** using an absolute path.

**`project_root` = hardcoded constant string** inferred from context (file paths in the conversation). PROHIBITED: `import.meta.dir`, `__dirname`, `process.cwd()`, `Deno.cwd()`, `path.resolve()` or any runtime detection. Exception: remote/CI environments or non-writable local filesystem — use `/tmp/.claude/debug.log` instead.

Before each reproduction: create `.claude/` if needed, then **rotate** the log — if `debug.log` exists, rename it to `debug<ISO-timestamp>.log.` (e.g. `debug-2026-05-13T16-22-11.log.`), then start a fresh empty `debug.log`. **Never clear or delete old rotated logs mid-session** — they preserve evidence so you can compare runs (instrumentation-tweak vs. retry, pre-fix vs. post-fix). Phase 6 cleans them up at the end.

Server-side: file-append API (`fs.appendFileSync`, `open("a")`, etc.). Browser-side: `fetch` POST to a debug API route. **Must work in all environments** (dev/release).

### Region markers

ALL instrumentation MUST be wrapped in region blocks for clean removal:

```
// #region DEBUG       (JS/TS/Java/C#/Go/Rust/C/C++)
# #region DEBUG        (Python/Ruby/Shell/YAML)
<!-- #region DEBUG --> (HTML/Vue/Svelte)
-- #region DEBUG       (Lua)

...instrumentation...

// #endregion DEBUG    (matching closer)
```

### Logging rules

- **NEVER use `console.log`、`print` or any stdout/stderr output.** All debug output MUST go to `debug.log` — server-side via file-append, browser-side via `fetch` to a debug API endpoint.
- Log messages include hypothesis number: `[DEBUG H1]`, `[DEBUG H2]`, etc.
- Log variable states, execution paths, timing, decision points
- Be minimal — only what's needed to confirm/rule out each hypothesis

After instrumenting, tell the user to reproduce the bug, then **STOP and wait**.

## Phase 4: Analyze Logs & Diagnose

When the user has reproduced:

1. **Check log file size first** (e.g. `wc -l` or `ls -lh`). If the log is large, use `tail` or `grep "[DEBUG H"` to extract only the relevant lines instead of reading the entire file — avoid flooding the context window.
2. Map logs to hypotheses — determine which are **confirmed** vs **ruled out**
3. Present diagnosis with evidence:

```
## Diagnosis

**Root cause**: [Explanation backed by log evidence]

Evidence:
- [H1] Ruled out — [why]
- [H2] Confirmed — [log evidence]
```

If inconclusive: new hypotheses → more instrumentation → rotate log (see Phase 3) → ask user to reproduce again.

## Phase 5: Generate a Fix

Write a fix. Keep debug instrumentation in place.

Rotate `.claude/debug.log` (same rule as Phase 3 — rename existing log to a timestamped sibling, start a fresh `debug.log`), ask user to verify the fix works, then **STOP and wait**. The rotated pre-fix log is what lets you compare buggy-run vs. fixed-run if verification fails.

## Phase 6: Verify & Clean Up

**If fixed:** Remove all `#region DEBUG` blocks and contents (use Grep to find them), delete `.claude/debug.log` **and every rotated `.claude/debug.log.*` sibling**, summarize.

**If NOT fixed:** Read new logs, ask what they observed, return to **Phase 2**, iterate.

---

## Rules

- **Never skip phases.** Instrument and verify even if you think you know the answer.
- **Never remove instrumentation before user confirms the fix.**
- **Never use `console.log`、`print` etc.** All debug output goes to `.claude/debug.log` via file-append only.
- **Always rotate (never clear) the log before each reproduction** — preserves cross-run evidence; Phase 6 deletes the whole set at the end.
- **Always wrap instrumentation in `#region DEBUG` blocks.**
- **Always wait for the user** after asking them to reproduce.
