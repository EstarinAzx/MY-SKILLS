---
name: codespeak
description: Generate a shared LEXICON.md at repo root that defines canonical names for load-bearing files, modules, and recurring code patterns. Establishes a vocabulary both the user and AI use when talking about this codebase. Auto-loads via CLAUDE.md so future sessions inherit the shared language. Use when the user runs /codespeak, says "build a lexicon", "shared vocab", "name the codebase", or asks for a glossary of file roles and code patterns.
---

# Codespeak

Produce `LEXICON.md` at repo root: a small, dense list of canonical names for the structural pieces of this codebase. The lexicon becomes shared language — when the user says "the dispatcher", both user and AI resolve to the same file. Loaded into every future Claude session via `@LEXICON.md` in `CLAUDE.md`.

This skill is **not** `/chunk-it`. `/chunk-it` writes inline comments inside source files. `/codespeak` writes one external doc that names the architecture.

## What goes in LEXICON.md

Only two categories:

1. **File / module roles** — load-bearing files or folders. Inclusion bar: referenced from ≥3 other places, OR every non-trivial change must touch it. Skip leaves, tests, fixtures, build configs.
2. **Code-pattern shorthand** — recurring patterns that show up in ≥3 places (a retry wrapper, a validator chain, a dispatcher pattern, a state-store convention).

Target ~10–40 entries even for large codebases. A bloated lexicon is a useless lexicon.

Do **not** include: domain/business concepts, user nicknames, in-jokes, low-level utility functions, single-use helpers.

## Entry format

```
**dispatcher**
role: routes events to handlers
say: "the dispatcher" (also: "the router", "the entry")
at: `src/router.ts`
```

Fields:
- **bold-name** — the canonical name. Functional/literal. No metaphors. kebab-case or single lowercase noun.
- `role:` — one line, ≤12 words, describes what it does.
- `say:` — canonical phrase in quotes, optionally `(also: "...", "...")` with 1–2 aliases.
- `at:` — backticked path. File for code, folder with trailing `/` for modules.

Blank line between entries.

## Preamble

Top of `LEXICON.md` always starts with:

```markdown
# Lexicon

Shared vocabulary for this codebase. When the user uses one of these names, resolve it via this file. When proposing or describing changes, refer to things by their canonical name (the bold one). Aliases listed under `say:` are accepted but the canonical name is preferred.

Extend by running `/codespeak` again — re-runs only add new load-bearing items, they don't touch existing entries.

---
```

Then entries. Group order: file/module roles first, then code-pattern shorthand. No section headers within — flat list, easier to scan.

## Workflow

### First run (no LEXICON.md)

1. Survey the repo. Read `README.md`, top-level folder structure, and any existing `CLAUDE.md` for hints about what matters.
2. For each candidate file/folder, check load-bearing criteria: import count, breadth of references, whether changes to it ripple. Use Grep for import counts when needed.
3. For code patterns, scan for ≥3-occurrence shapes (retry wrappers, validation chains, factory patterns, etc.).
4. Draft 10–40 entries. Names must be functional/literal. Propose 1–2 aliases per entry only when an obvious alternative exists.
5. Write `LEXICON.md` to repo root with the preamble + entries.
6. Check for `CLAUDE.md` at repo root:
   - If exists: append the line `@LEXICON.md` at the bottom (or near other `@` imports if any).
   - If absent: create minimal `CLAUDE.md` containing only `@LEXICON.md` on one line.
7. Print the drafted entries inline in the chat as a code block.
8. Ask the user one question: **"rename any? drop any? add any?"** Apply edits with the Edit tool — don't rewrite the whole file.

### Re-run (LEXICON.md exists)

1. Read existing `LEXICON.md`. Treat every existing entry as immutable.
2. Re-survey repo for load-bearing items.
3. Diff against existing entries' `at:` paths and pattern names. Identify only items not yet in the lexicon.
4. If nothing new: tell the user "no new load-bearing items found" and stop.
5. If new items: draft additions, append to `LEXICON.md`, print added entries inline, ask "rename any? drop any?".
6. Never edit, rename, re-role, or re-path existing entries during a re-run. The user's edits are sacred.

### CLAUDE.md handling

- Never duplicate the `@LEXICON.md` line if it already exists.
- Place the import on its own line so it's obvious.
- Do not bootstrap a full CLAUDE.md (stack, conventions, etc.). One line is enough — that's another skill's job.

## Naming rules

- Functional/literal. ✅ `dispatcher`, `retry-wrapper`, `state-store`. ❌ `the bouncer`, `the loom`, `the brain`.
- Single-word noun or kebab-case compound. No camelCase, no spaces.
- Match plurality to reality: `handlers/` not `handler` if the entry points to a folder of N handlers.
- Avoid generic names that say nothing: not `utils`, not `helpers`, not `core`. If a folder really is named `utils/`, name the lexicon entry after what it actually contains: `string-utils`, `date-helpers`.
- Aliases (under `say:`) only when an obvious alternate phrasing is already in use somewhere (a comment, a doc, a function name).

## Inclusion checklist

For each candidate, before adding:
- Does it have ≥3 callers / importers / references? Or is it a folder that every non-trivial change must touch?
- Would referring to it by a short name actually save the user from re-explaining "the file that does X"?
- Is it stable architecture, not transient scaffolding?

If any answer is no → skip it. Better to ship 15 high-value entries than 80 noisy ones.

## What this skill does NOT do

- Does not comment source files. That's `/chunk-it`.
- Does not refactor or rename anything in code. Only names them in the lexicon.
- Does not include domain/business glossary. Only structural code vocabulary.
- Does not rebuild from scratch on re-run. Always additive.
- Does not write more than one line into a fresh `CLAUDE.md`.
- Does not propose metaphorical names. Functional only.

## Example output

`LEXICON.md` after first run on a hypothetical small backend:

```markdown
# Lexicon

Shared vocabulary for this codebase. When the user uses one of these names, resolve it via this file. When proposing or describing changes, refer to things by their canonical name (the bold one). Aliases listed under `say:` are accepted but the canonical name is preferred.

Extend by running `/codespeak` again — re-runs only add new load-bearing items, they don't touch existing entries.

---

**dispatcher**
role: routes incoming events to handlers
say: "the dispatcher" (also: "the router")
at: `src/router.ts`

**handlers**
role: per-event business logic, one file per event type
say: "a handler" / "the handlers folder"
at: `src/handlers/`

**state-store**
role: single source of truth for session state
say: "the state store"
at: `src/state/`

**retry-wrapper**
role: exponential backoff around any async fn
say: "the retry wrapper"
at: `src/util/retry.ts`

**validator-chain**
role: composable input checks; each step short-circuits on failure
say: "the validator chain"
at: `src/validation/chain.ts`
```

Then in chat:

> Drafted 5 entries to `LEXICON.md` and added `@LEXICON.md` to `CLAUDE.md`. Rename any? drop any? add any?
