---
name: elucidate
description: >
  ELUCIDATE mode — write code carrying its logic in plain-English comments, in
  a house style set by one axis. MODE: default (only the critical why-comments),
  learner (a one-sentence comment above every action), or technical (deepest —
  why plus tradeoffs, complexity, perf, edge cases). New code is implemented
  directly in one pass — no scaffold phase, no approval gate. Files are sectioned
  with banner comments. Toggle with /elucidate:default, :learner, :technical,
  :off. Use when the user runs those commands, says "elucidate this", or wants
  logic in English.
---

# Elucidate

Write code carrying its logic in plain English as comments — comment and code
as **peers**, written together, edited together. The file is sectioned with
**banner comments** so its structure is visible at a glance.

Elucidate is a lightweight commenting mode: it writes the commented code
**directly**, in one pass. There is no comment-only scaffold phase and no
approval gate — just immediate implementation in the house style. How deep the
comments go is set by one axis — **MODE**.

## The mode

Elucidate is a **session mode**, toggled by slash command, shown as statusline
badges: `[ELUCIDATE]` (identity) and `[MODE:…]`.

| Axis | Values | Controls |
|---|---|---|
| **MODE** | `DEFAULT` / `LEARNER` / `TECHNICAL` | how deep the step comments go |

| Command | Sets |
|---|---|
| `/elucidate:default` | MODE → default |
| `/elucidate:learner` | MODE → learner |
| `/elucidate:technical` | MODE → technical |
| `/elucidate:off` | mode off |

- A new session starts **off**. Any mode command turns the mode on. From `off`,
  an activation with no explicit mode takes the default — `default`.
- When the mode is **off**, none of this applies.

## What files get elucidated

Logic-bearing source only:

```
.py .ts .tsx .js .jsx .mjs .cjs .go .rs .java .kt .swift .rb .php .c .cpp .cc .h .hpp .cs .scala .ex .exs .clj .dart .lua .m .mm
```

Skip: `.md .txt .json .yaml .yml .toml .ini .css .scss .html .svg .sql .csv .lock .gitignore`, dotfiles, configs, fixtures, generated code, vendored deps.

## Banner comments

Section every elucidated file with banner comments. A banner is ONE line — the
section title set in a run of dashes, kept to roughly 80 columns:

```
// ---------------------------- Section Title ----------------------------- //
```

Use the language's line-comment syntax (`//`, `#`, `--`). Two kinds:

- **Title banner** — the very first thing in the file. Its title is the file
  name and a one-line purpose: `login.ts — user authentication: sign in and out`.
- **Section banners** — one before each logical group of constructs (all the
  type declarations, the context setup, the hook, the provider, …). A small
  file with a single group needs only the title banner; do not invent sections.

## File structure

Top to bottom, every elucidated file has:

1. **Title banner** — file name + one-line purpose.
2. **File-top block** — a `/* */` (or `"""…"""`, `#`-stack) block with
   **Depends on** (external libs with a one-line role each, plus internal
   modules), **Data shapes** (types in prose; skip if the file has none), and
   — in `learner` mode only — **Concepts** (a one-line list of the language
   features and patterns the file uses, e.g. `dataclass, dependency injection,
   dict-as-map`). That Concepts line is the *only* place the language itself is
   named; inline comments never explain it. The one-line purpose lives in the
   title banner, so it is not repeated here.
3. **Imports**, then the body — each logical group preceded by a **section
   banner**.
4. Within each group, for every top-level function or class: a **one-line
   summary comment** directly above it, and **step comments** inside the body
   (one per logical block). `default` and `technical` write these as dash steps
   (`- …`); `learner` writes plain line-comments with no dash.

The title banner, file-top block, section banners, and per-construct summary
comments are present in **all** modes (the file-top block's Concepts line is
`learner`-only). MODE governs only the **step** comments.

To fill the **Depends on** line, read the file's import statements directly.

## How new code arrives — straight implementation

For a NEW function, class, or file: write the commented code **directly, in one
pass** — no separate skeleton phase, no approval gate. The file still gets the
full house style: banners, file-top block, summaries, step comments. They are
written together with the code, not as a separate approved step.

There is no scaffold method and no comment-first ceremony. The comment layer and
the code are produced in the same edit, every time.

## EDIT to existing code

Editing an existing body — adding a branch, fixing a bug — has nothing to
"approve before coding". Write the plain-English step comment **and** the code
change together, in one pass, no approval gate. A **mixed task** (a new construct
*and* edits): the new construct and the edits both go inline, one batch.

## MODE — how deep the step comments go

Applies to the **step** comments only.

- **default** — sparsest. Inside bodies, keep only the few most critical step
  comments — the *why* behind a non-obvious choice. A competent reader wants
  navigation (the banners) and the essentials, not narration. Voice: concise,
  plain.
- **learner** — a comment directly above **every** logical action (an
  if-branch, a loop, a short related sequence — not every physical line). One
  short sentence each; at most 1-2 comment lines per code line — needing more
  means overexplaining. Say *what* the code does, never *how the language
  works* — no syntax or grammar lessons. Plain line-comments, no `-` prefix.
  Add `⚠️` one-liner callouts where they matter. Voice: plain English naming
  intent. The line above every action is the point.
- **technical** — deepest. Comment **wherever there is technical substance**,
  and when you do, go deep: the *why* plus tradeoffs taken, algorithmic
  complexity, performance, edge cases, failure modes, cross-file constraints.
  Voice: expert — jargon is fine. Skip blocks with no technical substance
  rather than padding them.

The ladder is **depth**, not just count: `default` says least, `technical` says
most per comment, `learner` comments most often (every block) but simplest.

`example/login-default.ts`, `login-learner.ts`, and `login-technical.ts` show
the same file at each mode.

## Phrasing guidelines

The comment **voice** follows MODE:

- **learner** — plain English naming the *intent*: `if (!user)` → "Stop if no
  matching user"; `return { token }` → "Hand back the session token". Never
  explain the language itself — `@dataclass` gets "groups the pickup's fields",
  not "a dataclass bundles named values into one object".
- **default** — concise plain English, one clause: `// 404 not 401 — simpler here`.
- **technical** — terse expert prose, jargon allowed: `// 404 vs 401: avoids
  user-enumeration via response timing/shape`.

Granularity: one step per **logical block** — an if-branch, a loop, a
try-block, a short related sequence — never line-by-line.

## Workflow when the mode is on

1. **Plan files.** List every code file the task creates or modifies.
2. **New constructs** → write the commented code directly, one pass, no
   skeleton and no gate.
3. **Edits** → comment and code together, no gate.
4. **Apply MODE** to the step comments — default keeps only the critical whys,
   learner keeps every block, technical goes deep where there is substance.
5. **Mid-code discrepancy.** If a comment turns out wrong while coding, fix it
   in the same edit. Never silently diverge.

## Sync rule

Comment and code are peers. When a later change touches an elucidated file,
**update the matching comment in the same edit**. Never leave a comment
describing code that no longer exists. This matters most in `learner` mode — a
reader relying on it usually cannot catch a stale comment.

## What this skill does NOT do

- Does not create a separate `blueprints/` tree — the plan lives inline.
- Does not run when the mode is off, or on non-logic files.
- Does not write a comment-only scaffold or add an approval gate — code is
  always implemented directly.
- Does not drop the title banner, file-top block, section banners, or summary
  comments — those are permanent in every mode. MODE governs only dash step
  comments.
- Does not silently diverge — if reality requires a change, fix the comment too.

## See also

- `example/login-default.ts` — sparsest, only the critical whys.
- `example/login-learner.ts` — a one-sentence comment above every action.
- `example/login-technical.ts` — deepest, expert voice with tradeoffs and perf.
