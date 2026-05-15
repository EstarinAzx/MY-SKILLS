---
name: skeleton
description: Plan code as plain-English logic blueprints before writing real code. AI drafts one .md per source file under blueprints/, mirroring the src tree. Each blueprint reads like prose ("If... then...", "Loop through...", "Send back..."). User approves blueprints batch, then code lands per-file with separate approval each. Source-of-truth: blueprint updates before code. Use when user runs /skeleton, says "blueprint this", "skeleton first", "plan in prose before coding", or wants logic written in English before syntax.
---

# Skeleton

Write the logic in plain English first. Code second. Blueprints are the source of truth — code is one valid rendering of them.

This skill is **not** docstrings, **not** code comments, **not** a README. It is a parallel `.md` tree under `blueprints/` that mirrors your source tree, where each file describes its sibling code file's behavior as numbered English steps.

## When to invoke

User runs:
- `/skeleton <natural language task>` — forward mode. AI plans files, drafts blueprints, asks approval, writes code per-file with approval gates.
- `/skeleton backfill <path-or-glob>` — reverse mode. AI reads existing code, generates blueprint(s), user fixes/approves. No code changes.

Skill is **manual only**. Do not auto-trigger on every Write/Edit.

## Layout

- All blueprints live at `blueprints/` at repo root.
- Mirror the source tree exactly. `src/auth/login.ts` → `blueprints/auth/login.md`. `test/auth/login.test.ts` → `blueprints/test/auth/login.test.md`.
- One blueprint per code file. Always `.md`.
- File extension on source dropped, replaced with `.md`. Path segments below `src/` (or repo root if no `src/`) are preserved.

### What files get blueprints

Logic-bearing source only:

```
.py .ts .tsx .js .jsx .mjs .cjs .go .rs .java .kt .swift .rb .php .c .cpp .cc .h .hpp .cs .scala .ex .exs .clj .dart .lua .m .mm
```

Skip: `.md .txt .json .yaml .yml .toml .ini .css .scss .html .svg .sql .csv .lock .gitignore`, dotfiles, configs, fixtures, generated code, vendored deps.

## Blueprint file format

```markdown
---
code_file: src/auth/login.ts
last_synced: 2026-05-16
status: draft
---

## Depends on
- express (web framework)
- bcrypt (password hashing)
- [users db module](../db/users.md)

## Data shapes

User has: id (number), email (string), passwordHash (string), createdAt (date).

LoginResult has: token (string) and expiresAt (date).

## function login(email, password)

1. Look up user by email in the users table.
2. If user is missing, send back 404 "not found".
3. Otherwise, compare the supplied password to the stored hash using bcrypt.
4. If the comparison fails, send back 401 "invalid credentials".
5. Create a new session token tied to the user id.
6. Store the token in the sessions table with a 24-hour expiry.
7. Send back a LoginResult containing the token and its expiry.

## function logout(token)

1. Look up the session by token.
2. If not found, send back 204 (idempotent).
3. Otherwise, delete the session row.
4. Send back 204.
```

### Frontmatter fields

- `code_file` — relative path from repo root to the source file this blueprint describes.
- `last_synced` — ISO date (YYYY-MM-DD) when blueprint and code were last known in sync.
- `status` — one of:
  - `draft` — AI wrote it, awaiting user approval
  - `approved` — user approved, code currently being written
  - `synced` — code matches blueprint
  - `stale` — code edited after blueprint last_synced (set by `/skeleton-check`)

### Section order (always)

1. Frontmatter
2. `## Depends on` — bullet list. External libs noted with one-line role. Internal references use markdown links to the other blueprint (`[name](relative/path.md)`).
3. `## Data shapes` — types in prose. "User has: id (number), email (string)...". Skip if file has none.
4. One `## function <name>(<args>)` or `## class <Name>` section per top-level construct, in source order.
5. Numbered steps inside each section. One step per logical block.

If file has no functions/classes (e.g. a module-level script), use `## main` as the single section.

## Phrasing guidelines

Write English a smart non-programmer could read. Use these natural patterns:

| Code concept              | English phrasing                                    |
|---------------------------|-----------------------------------------------------|
| `if cond { ... }`         | "If [cond], then [...]"                             |
| `else`                    | "Otherwise, ..."                                    |
| `for x in xs`             | "For each x in [xs], ..." / "Loop through [xs], ..."|
| `while cond`              | "As long as [cond], ..."                            |
| `return x`                | "Send back x"                                       |
| `let x = ...`             | "Store this as x" / "Remember x as ..."             |
| `new Foo(...)`            | "Create a new Foo with ..."                         |
| `foo.bar(args)`           | "Call bar on foo with args" / "Ask foo to bar ..."  |
| Callback / promise / event | "This runs LATER when [trigger]: ..."              |
| `try / catch`             | "Attempt ... If it fails, ..."                      |
| `throw`                   | "Stop and report ..."                               |
| `async / await`           | "Wait for ... before continuing"                    |
| Early return / guard      | "First check ... if so, send back ... and stop."    |

Granularity: **logical block, not line-by-line**. One numbered step per if-branch, loop, try-block, or short sequence of related assignments. Variable bookkeeping is grouped, not split per line.

These are guidelines not gates. Use natural prose. Don't twist sentences to hit exact keywords. The point is readability.

## Workflow: forward mode (`/skeleton <task>`)

1. **Plan files.** From the task description, list every code file you will create or modify. Group into a plan.
2. **Reverse-engineer existing files.** For any file in the plan that already exists and lacks a blueprint, write its current-state blueprint first (silently) so the diff makes sense.
3. **Write blueprints.** Create one `.md` per code file under `blueprints/` mirroring the planned path. Frontmatter `status: draft`. Use markdown links to other blueprints in the batch under `## Depends on`.
4. **Batch approve.** Present the full set in chat. List paths created + a one-line summary each. Ask the user to approve, reject, or describe edits.
   - If user describes edits: rewrite affected blueprints, re-ask.
   - If user edits `.md` files directly: re-read and proceed.
   - On approval: bump all status to `approved`, set `last_synced` to today.
5. **Write code per file, gated.** For each file in the approved batch, write the code, then pause and ask user to approve that specific file's code before moving to the next. After approval of each file, set its blueprint `status: synced` and update `last_synced`.
6. **Mid-code discrepancy.** If while writing code you realize the blueprint is wrong, stop, update the blueprint, re-ask approval for that one file. Do not silently diverge.

## Workflow: backfill mode (`/skeleton backfill <path-or-glob>`)

1. Resolve target files. Skip non-logic-bearing extensions (see allowlist above).
2. For each target, read the code, generate a blueprint at the mirrored `blueprints/` path with `status: draft`.
3. After writing all, present the list and ask user to review/edit/approve.
4. On approval, bump status to `synced` and set `last_synced` to today.
5. No code is touched in backfill mode.

## Sync rule

Blueprint is the source of truth. **Always update the blueprint before the code.**

When the user asks for a code change to a file that has a blueprint:
1. Update the blueprint first.
2. Bump `last_synced` and set `status: approved`.
3. Ask the user to approve the blueprint change.
4. Then make the code change.
5. Set `status: synced` after.

If user insists on a quick code-only edit (typo, rename), still update the blueprint after — never leave it stale silently. Set `status: synced` and bump `last_synced`.

## Cross-file references

Inside `## Depends on`, link to other blueprints with relative markdown links: `[validateToken](../auth/token.md#function-validatetoken)`.

Inside numbered steps, refer to functions by name only. The dependency list at top establishes the resolved targets. Don't inline long paths in the middle of prose.

## What this skill does NOT do

- Does not write code comments or docstrings — those go in the code, this skill writes a parallel doc tree.
- Does not auto-trigger on every Write/Edit. Manual only.
- Does not blueprint configs, markup, styles, or data files.
- Does not skip the approval gate. The whole point is human review of logic before syntax.
- Does not silently diverge — if reality requires a change, update the blueprint first.

## See also

- `/skeleton-check` — drift detector. Walks `blueprints/`, compares `code_file` mtime vs blueprint mtime, prints a table of file / status / last_synced / drift_reason.
- `example/login.md` — full reference blueprint shipped with this skill.
