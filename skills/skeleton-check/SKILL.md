---
name: skeleton-check
description: Drift detector for the /skeleton workflow. Walks blueprints/ at repo root, compares each blueprint's last_synced and code mtime against its code_file, and prints a table flagging draft / approved / synced / stale blueprints. Read-only — does not modify any file. Use when user runs /skeleton-check, says "check blueprint drift", "are blueprints stale", or wants a sync report after editing code without updating skeletons.
---

# Skeleton-check

Companion to `/skeleton`. Reports which blueprints are out of sync with their code. Read-only — never writes, never auto-fixes.

## What it does

1. Locate `blueprints/` at the repo root. If missing, tell the user "no blueprints/ directory found — run /skeleton first" and stop.
2. Walk every `.md` file under `blueprints/`.
3. For each blueprint, parse the YAML frontmatter. Skip files that have none.
4. For each blueprint, resolve `code_file` relative to repo root.
   - If `code_file` does not exist on disk → mark `missing-code`.
   - Otherwise, get the mtime of the code file.
   - Compare against `last_synced` (date) and the blueprint file's own mtime.
5. Compute status:
   - `code_file` missing → `missing-code`
   - frontmatter `status: draft` → `draft` (awaiting approval)
   - frontmatter `status: approved` and code mtime > blueprint mtime → `approved (writing)` — currently being implemented
   - frontmatter `status: synced` and code mtime > blueprint mtime → `stale` — code changed after blueprint
   - frontmatter `status: stale` → `stale` (already flagged)
   - everything else → `synced`
6. Print a table.

## Output format

Plain markdown table, sorted by status (stale → draft → approved → synced → missing-code), then by path:

```
| file                              | status   | last_synced | drift_reason                          |
|-----------------------------------|----------|-------------|---------------------------------------|
| blueprints/auth/login.md          | stale    | 2026-05-10  | code mtime 2026-05-14 > blueprint     |
| blueprints/db/users.md            | draft    | 2026-05-16  | awaiting approval                     |
| blueprints/util/retry.md          | synced   | 2026-05-15  | —                                     |
| blueprints/legacy/old.md          | missing  | 2026-05-01  | code_file src/legacy/old.ts not found |
```

After the table, print a short summary line: `N stale, M draft, K synced, J missing-code`.

If everything is `synced`, just print `All N blueprints in sync.` and skip the table.

## What this skill does NOT do

- Does not auto-update blueprints. Drift means the user must run `/skeleton` on the affected file to resync.
- Does not edit, move, or delete any file.
- Does not run git commands. mtime from the filesystem is enough.
- Does not bootstrap `blueprints/` — that's `/skeleton`'s job.
