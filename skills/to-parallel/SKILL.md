---
name: to-parallel
description: Generate a parallel agent workflow with copy-paste prompts for each spawned agent. Use when user wants to split work across multiple agents, mentions "parallel agents", "worktrees", "spawn agents", or has a large task that benefits from concurrent work.
---

# To Parallel

Generate a project-specific workflow MD file containing ready-to-paste prompts for parallel agents, plus the coordination rules and merge strategy to keep them from colliding.

## When to use

- User has a large task that can be split into non-overlapping vertical slices
- User wants to spawn multiple Claude Code / terminal agents
- User asks "how do I parallelize this" or "make me agent prompts"

## Process

### 1. Understand the work

Read `.context/overview.md` and `.context/active-work.md` if they exist. Otherwise explore the codebase to understand:

- Current project structure (directories, key files)
- Tech stack and conventions
- What needs to be built or changed

Identify the full scope of work the user wants parallelized.

### 2. Slice into non-overlapping agents

Break the work into agent-sized slices. Rules:

- **Zero file overlap** — no two agents touch the same file. This is the #1 rule.
- **Vertical slices** — each agent delivers complete, demoable functionality, not horizontal layers.
- **Dependency ordering** — identify which agents block others. Foundation/shared work goes first.
- **Minimize agents** — don't create an agent for 2 files of work. Merge small slices.

Typical patterns:

```
Foundation agent (phase 0) → parallel agents (phase 1) → integration (phase 2)
```

```
3-5 agents is the sweet spot. More than 6 creates merge overhead that eats the gains.
```

### 3. Draft the workflow document

Create an MD file in the project's `specicifactions/` or `docs/` directory. The file MUST contain these sections in order:

#### Header
- Title describing the work
- One-line summary
- Core rule: "Parallel agents work best when each agent owns a non-overlapping vertical slice"

#### Current state
- What exists right now (files, components, infrastructure)
- What needs to be built

#### Phase 0: Foundation agent (if needed)
- Copy-paste prompt in a fenced `md` code block
- Scope list (numbered, specific)
- "Avoid" list (what NOT to touch)
- Coordination rules block
- "Stop after X is complete" instruction

#### Phase 1: Parallel agents
For each agent:
- Section heading with agent name and scope summary
- Issue references (if `tailwind-ui-issues.md` or similar exists)
- Copy-paste prompt in a fenced `md` code block containing:
  1. **Role line**: "You are building [scope] for [project]."
  2. **Read list**: Specific files to read first (use `.context/` files if they exist)
  3. **Scope**: Numbered list of exactly what to build
  4. **Avoid**: What NOT to touch (other agents' territory)
  5. **Coordination rules**: Standard block (see template below)

#### Worktree commands
```bash
git worktree add ../project-agent-name -b agent/name
```

#### Merge order
- Numbered list with reasoning

#### Post-merge integration tasks
- What needs wiring together after all agents merge

#### Files inventory
- What gets created, modified, and deleted — by agent

### 4. Prompt template

Every agent prompt MUST follow this structure:

````md
```md
You are building [SCOPE DESCRIPTION] for [PROJECT NAME].

Read these files first:
- `.context/overview.md` — Project overview
- `.context/[relevant-section].md` — [Why this section]
- [Any other project-specific files the agent needs]

Scope:
1. [Specific deliverable with file path]
2. [Specific deliverable with file path]
3. [Specific deliverable with file path]

Avoid:
- [Other agent's files/scope]
- [Shared components unless this is the foundation agent]
- [Backend if this is a frontend agent, etc.]

Coordination rules:
- Work only on your assigned scope.
- Read relevant files before editing.
- Do not refactor unrelated code.
- Do not rename shared contracts without checking dependent code.
- Prefer small, testable changes.
- Run [verification command] and verify before stopping.
- If blocked by another issue, stop and report the blocker.
- Do not commit unless explicitly instructed.

[SKILL HOOKS — only if applicable]
When finished, run `/context-sync-update` if `.context/` exists.
```
````

### 5. Confirm with user

Present:
- Number of agents proposed
- What each agent owns (1-line summary)
- Dependency/merge order
- Any phase 0 blocker

Ask: "Does this split look right? Should any agents be merged or split further?"

After approval, write the file.

### 6. Wrap up

If `.context/` exists, run `/context-sync-update` to record the parallel work plan in `active-work.md`.

## Anti-patterns

- **Don't create 1-file agents** — merge small slices into a neighbor.
- **Don't let agents share files** — if two agents need the same file, one builds it in phase 0.
- **Don't skip the "Avoid" section** — agents WILL wander without explicit boundaries.
- **Don't put implementation details in prompts** — tell agents WHAT to build, not HOW. Let them read the codebase.
- **Don't forget merge order** — unordered merges = conflict hell.

## Example output reference

See `specicifactions/parallel-tailwind-ui-workflow.md` in the Night City Market prototype for a complete real-world example of this skill's output.
