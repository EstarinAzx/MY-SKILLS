---
name: ecosystem-audit
description: Deterministic health check for the ~/.claude ecosystem — reconciles the skills/ folder against the ecosystem-kb vault and flags the skills-dir footgun. Use when user types /ecosystem-audit, says "audit the ecosystem", "check for skill drift", "lint my skills", "find stray skill folders", or before/after a consolidation. Read-only; never deletes.
---

# /ecosystem-audit — ecosystem health check

You reconcile what is *installed* under `~/.claude/skills/` against what the
[[ecosystem-kb]] vault *says* is installed, and surface the silent footguns of
the skills-dir loader. The script does the detection; you interpret the findings
and propose fixes — you never delete or move anything without confirmation.

## Routing

`/ecosystem-audit` (or "audit the ecosystem", "check skill drift"): run the
helper, then read its findings back as a short punch list grouped by category,
worst-first, each with a one-line recommended action. Offer to act on the
fixable ones (document a skill in the vault, remove a stray folder) — one
confirmation per destructive step.

```
python "<this skill's dir>\scripts\audit.py" [claude-root]
```

`claude-root` defaults to the `~/.claude` derived from the script's own
location; pass it only to audit a different tree.

## Findings

| Category | Means | Typical fix |
|---|---|---|
| `stray-folder` | child of `skills/` with no SKILL.md — not loadable, just clutter in the one dir that auto-loads its children | move it out of `skills/` (e.g. to `~/.claude/`), or delete |
| `plugin-autoload` | child of `skills/` with `.claude-plugin/` — loads as `<x>@skills-dir` with no registry entry | informational; confirm it is intended (e.g. elucidate-plugin) |
| `name-collision` | two skill folders declare the same `name:` | rename one or deprecate the loser ([[knowledge-base-lineup]] pattern) |
| `vault-undocumented` | a skill folder named nowhere in ecosystem-kb | write its `wiki/skills/` page + index.md line |
| `vault-stale-path` | a `~/.claude/skills/<name>/` path the vault asserts no longer exists | fix the path, or record the rename/removal |

`stale-path` deliberately ignores `wiki/decisions/` and `log.md` — those narrate
history, so they name removed paths on purpose.

## Template drift (template_sync.py)

`template/IN USE/` is the copy pushed to the MY-SKILLS remote; it lags live
unless synced. The companion script reports (and, on request, mirrors) that
drift:

```
python "<this skill's dir>\scripts\template_sync.py" [claude-root] [--apply]
```

Same output contract as audit.py. Categories: `drift` (content differs),
`live-only`, `template-only`. Mirror rules are asymmetric: `skills/` is a
curated list — `--apply` only refreshes folders present on *both* sides, and
one-sided folders stay findings for a human call; `ecosystem-kb/` is a full
mirror — `--apply` copies new/changed pages and deletes pages deleted live.
Newlines are normalized, so git CRLF churn is never drift; `.obsidian/` is
ignored. `--apply` mutates only the template copy, never live — run it, review
`git status` in the template repo, then commit/push there.

## Hard rules

1. **Read-only and deterministic.** The script makes no network or LLM calls,
   mutates nothing, and only runs when invoked in-session. No hooks, no
   background watcher — drift is checked on demand ([[knowledge-base-lineup]]).
2. **Confirm before any move/delete.** A finding is a recommendation, not a
   mandate; the user decides what is intentional.
3. **Close the loop.** When a fix resolves drift (new skill documented, folder
   removed), update the ecosystem-kb vault in the same session so the next audit
   is clean.

## Helper script

- `python "<this skill's dir>\scripts\audit.py"` — emits `category<TAB>location<TAB>detail`
  per finding then a count; exit 0 clean, 1 findings, 2 usage error. Tests in
  `scripts/tests/`.
