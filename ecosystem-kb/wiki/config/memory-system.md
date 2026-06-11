---
type: config
updated: 2026-06-12
tags: [config, memory]
source: live inspection 2026-06-12
---

# memory-system

Claude Code auto-memory (enabled in [[settings-and-hooks]]): persistent file-based memory at `~/.claude/projects/C--Users-S-D--claude/memory/`, one fact per file with frontmatter (`name`, `description`, `type: user|feedback|project|reference`), indexed by `MEMORY.md` (loaded each session).

House pattern: **lineup memories** — one file per consolidation decision, each with **Why** and **How to apply** sections. The wiki decision pages ([[design-skill-lineup]], [[knowledge-base-lineup]], [[tdd-lineup]], [[commenting-mode-lineup]]) mirror these; memory is the per-session recall layer, this vault is the durable knowledgebase (entry point: [[ecosystem-overview]]).

Distinct from per-project [[context-handoff]] (`.context/` in each repo).

**Reach caveat:** auto-memory is scoped per project directory — sessions in other projects don't see these files. Cross-project vault awareness travels via the template CLAUDE.md at `~/.claude/template/IN USE/CLAUDE.md` (copied into every new project; section 5 points agents at this vault).
