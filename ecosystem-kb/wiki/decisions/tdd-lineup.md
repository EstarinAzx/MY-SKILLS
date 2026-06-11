---
type: decision
updated: 2026-06-12
tags: [decision, lineup, tdd]
source: live inspection 2026-06-12
---

# tdd-lineup

**2026-06-11** — `superpowers:test-driven-development` is the sole TDD skill; local `tdd/` moved to `~/.claude/_deprecated/tdd/`.

**Why:** local skill duplicated red-green-refactor and its trigger collided with superpowers' (fires on any feature/bugfix). Superpowers' version is enforcement-shaped (Iron Law, mandatory watch-it-fail, anti-rationalization tables) — better as guardrail. Local skill's unique value (planning gate, wrap-up) is covered by `superpowers:brainstorming` and habit.

**Salvage:** test-design references (deep-modules.md, interface-design.md, mocking.md, refactoring.md, tests.md) remain in `_deprecated/tdd/` for a possible future "test-design" skill.

**How to apply:** never suggest `/tdd`; point handoffs and `.context/` files at [[superpowers]] TDD.
