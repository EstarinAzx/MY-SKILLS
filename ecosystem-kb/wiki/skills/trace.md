---
type: skill
updated: 2026-06-21
tags: [skill, code-reading]
source: live inspection 2026-06-12
---

# trace

End-to-end flow tracing across multiple files — "how does login work", "trace the checkout flow", `/trace`. For multi-layer questions only; single-file/function questions are answered normally without it.

**Audience register** (Step 7, added 2026-06-12): default **engineer** (`file:line`-forward, unchanged for direct `/trace`); **plain** register remaps the answer to everyday language with `file:line` demoted to trailing parens + a closing engineer-view offer. The [[preset]] `learn` flow always invokes plain (learning context, never asks). Register changes presentation only — trace methodology, `file:line` capture, and flows.md persistence are unchanged.

Renamed from `read-flow` 2026-06-12; folder is `~/.claude/skills/trace/`.

**Pairs with [[happy-path]]** (built 2026-06-21): the forward-design twin. `/hp`
draws the intended flow as an MVD *before* code exists; trace reads the *built*
flow back. `.context/happy-path.md` (design-time) vs `.context/flows.md`
(built-time) — same project, two files side by side.

**Presentation layer** (2026-07-12): [[drawio]] turns a traced flow into a
deliverable — `seqlayout.py` renders it as a sequence diagram, the code
importers draw the static import graph (complement: trace follows one runtime
flow). `flows.md` stays the source of truth.
