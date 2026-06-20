---
name: trace
description: Use when the user asks how a flow works end-to-end across multiple files in a codebase, why a multi-step behavior fails, or where to add a feature touching several layers — "how does login work", "trace the checkout flow", "walk me through X", "/trace". Not for single-file or single-function questions; answer those normally.
---

# /trace

Read one flow of an unfamiliar codebase with a question-first methodology, answer with verifiable references, persist what was learned so the next pass is cheaper.

**Core discipline: follow the data, not the directory.** Never read every file in scope — enter at the edge, trace one key piece of data inward, skip plumbing. If you notice you are reading files "to be thorough", stop and return to the trace.

## Step -1: Recall before reading

Check `.context/flows.md` in the project root.

- **Flow already recorded** → cheap verify: open the stored entry point and 1–2 key files; if `git log --since=<entry's updated date> -- <key files>` shows no commits and the code matches the stored summary, answer from the entry in seconds. Drift → re-trace and update the entry, telling the user the flow changed.
- **Adjacent flow recorded** → use its entry point and key files as a head start.
- **Bare invocation, no question** → if flows.md exists, list its flows + summaries and ask "which flow, or a new question?". If not, ask one question: "understand a flow, hunt a bug, or plan a change — and which feature?"

## Step 0: Classify the question

| Type | Signal | Stretch | Compress |
|---|---|---|---|
| **Understand** | "how does X work" | full happy path + failure paths | — |
| **Bug hunt** | "why does X fail/break" | failure paths FIRST, happy path as baseline only | zoom-out |
| **Change plan** | "where would I add X" | zoom-out, data model, extension points | failure paths |

Bug hunt boundary: stop at *understanding* where the bug can leak in. Do not fix — hand off to the user's debugging/fix workflow.

## Step 1: Zoom out — delegate it

Bulk orientation reading does not belong in main context. Dispatch one subagent (`cavecrew-investigator` if available, else `Explore`): README, folder map, data model / main entities, and the likely entry point for the question. Conclusions only.

No subagent available → cap zoom-out at README + folder listing + schema glance. No implementation files yet.

## Steps 2–6: Trace inline

Read the flow yourself — follow-ups are the point, and inline keeps the trace hot in context.

2. **Enter at the edge.** Route handler, CLI entry, event handler — whatever meets the outside world for this question. Never open random files hoping they're relevant.
3. **Tests as contract — 2-minute cap.** A clear happy-path test gives input/output faster than the implementation. Tests absent, stale, or abstract → skip without guilt, infer the contract from the entry point's request/response shape.
4. **Follow the data.** Pick the key object (the order, the payload, the user) and trace enter → transform → exit. Functions it passes through matter; functions it doesn't, don't.
5. **Skip the noise on pass one:** logging, metrics, middleware, rate limiters, retry wrappers, serializers, ancient TODOs — unless the question is about them.
6. **Failure paths, through the lens.** After the happy path makes sense, read error handling with the question-type lens: bug hunt → where could the observed behavior leak in; security → enumeration, leaked errors, missing authz; reliability → swallowed errors, partial failure.

Record `file:line` for every hop as you go — the answer needs them.

**Reading budget:** full-file reads are the exception, not the method. Grep for the symbol, then read the function range (offset/limit), not the file. More than ~6 full-file reads means you are reading the directory, not the data — "end to end" in the question does not repeal this; the journey still runs through specific functions.

## Step 7: Answer format

Four sections, in order:

1. **Summary** — ONE concrete sentence, **50 words max**. It must name actual mechanisms, and it must select: pick the mechanisms that answer the question, not every hop. A semicolon-chained mega-sentence is a fail — needing semicolons means you haven't compressed yet.
   - ❌ "It handles login."
   - ❌ 100+ words chained with semicolons covering all twelve hops.
   - ✅ "Login takes email+password, looks up the user by email, verifies with bcrypt, and issues a 7-day JWT as an httpOnly cookie — failures return a generic 401 to avoid leaking which field was wrong."
   - Can't write that sentence → you have a gap; re-read that piece before answering.
2. **Data journey** — numbered hops, each with `file:line` and the transformation named.
3. **Failure paths** — lens-matched findings.
4. **Gaps** — what you did NOT verify (assumed configs, unread branches, generated code). Never omit; honesty beats fake completeness.

### Register — who the answer is for

Default **engineer**: the four sections above, `file:line`-forward. When invoked
with a **plain register** (the `learn` preset, or the user asks to keep it
non-technical / "without the jargon"), change the *presentation only* — the
trace itself, the data discipline, the `file:line` capture, and flows.md
persistence are all unchanged. Plain remap of Step 7:

1. **Summary** → 1–2 everyday-language sentences, no jargon, no paths; a concrete
   real-world analogy is welcome when it clarifies.
2. **Data journey** → the same hops in plain words; each may carry its `file:line`
   in trailing parentheses, never leading with it.
3. **Failure paths** → "when it goes wrong", in plain terms.
4. **Gaps** → unchanged.

Then offer the engineer view (the `file:line` call path) in one closing line —
and if the answer came out map- or graph-shaped, offer to save it as its own
`.md` (beyond the terse flows.md entry). Do not write that file unasked.

## Step 8: Persist to flows.md

Append the flow to `.context/flows.md` (create `.context/` and the file if missing):

```markdown
---
type: flows
project: <name>
updated: <today>
tags: [flows]
---
# Flows

## <flow name>
- **Question:** <original question>  **Lens:** <understand|bug|change>
- **Summary:** <the one sentence>
- **Entry:** <file:line>
- **Key files:** <3–5 paths>
- **Updated:** <date>
```

If `.context/overview.md` exists, add `[[flows]]` to its Map section once.

## Red flags — stop and correct

- Reading files alphabetically or "all of scripts/" → return to the data trace.
- Past ~6 full-file reads → switch to Grep + ranged reads.
- A journey hop without `file:line` → go get the line.
- Summary needs semicolons or exceeds 50 words → compress; select mechanisms, drop hops.
- Answer drafted without a Gaps section → list what you skipped.
- Flow answered but flows.md not updated → the next session pays full price again.
