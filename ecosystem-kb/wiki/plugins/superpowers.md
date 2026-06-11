---
type: plugin
updated: 2026-06-12
tags: [plugin, workflow, discipline]
source: live inspection 2026-06-12
---

# superpowers

Workflow-discipline plugin from `claude-plugins-official` marketplace, v5.1.0, installed 2026-06-02. Cache: `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0`.

Injects `using-superpowers` at every session start: if a skill might apply (even 1%), it must be invoked before responding.

Key skills: `brainstorming` (mandatory before creative work), `test-driven-development` (sole TDD skill — see [[tdd-lineup]]), `systematic-debugging`, `writing-plans` / `executing-plans`, `verification-before-completion`, `requesting-/receiving-code-review`, `writing-skills`, `using-git-worktrees`, `dispatching-parallel-agents`, `subagent-driven-development`, `finishing-a-development-branch`.

Priority order it declares: user instructions (CLAUDE.md) > superpowers skills > default system prompt.
