---
type: skill
updated: 2026-06-12
tags: [skill, knowledge-base, wiki]
source: live inspection 2026-06-12
---

# llm-kb

Personal LLM wiki system — per-topic Obsidian-compatible vaults the LLM builds and maintains from curated sources. The skill that built and maintains *this* vault.

Ops: `init` / `ingest <file|all>` / `query <question>` / `lint`. Vault anatomy: SCHEMA.md (vault law, read first) + index.md + log.md + raw/ (immutable) + wiki/. Deterministic stdlib-only helpers in `scripts/` (search.py, lint.py).

Hard rules (user-set, non-negotiable): no hooks, no background processes, no LLM calls outside the live session — direct rejection of the old `kb/` design ([[knowledge-base-lineup]]).

Design spec: `~/.claude/skills/docs/superpowers/specs/2026-06-11-llm-kb-design.md`.
