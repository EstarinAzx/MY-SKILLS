---
type: decision
updated: 2026-06-12
tags: [decision, lineup, knowledge-base]
source: live inspection 2026-06-12
---

# knowledge-base-lineup

**2026-06-11** — [[llm-kb]] replaces the old `~/.claude/kb/` system, which was moved to `~/.claude/_deprecated/kb/`.

**Why:** old kb was conversation-capture via hooks with a background flush daemon. User explicitly rejected that failure mode.

**Hard rule established:** no hooks, no background processes, no LLM calls outside the live session — for all knowledge tooling. (Mode hooks like caveman/elucidate are exempt: static instruction injection only — see [[settings-and-hooks]].)

**How to apply:** all knowledge-base work goes through /llm-kb vaults (like this one); never suggest hook-driven capture.
