---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Wrap up

When the grill resolves to a decision, invoke `/context-sync-update` if `.context/` exists in the project. The whole point of grilling is reaching settled decisions — those belong in `.context/decisions.md` so a future agent doesn't re-grill the same questions. Always include the **why** (the constraint or alternative considered) when recording — that's what makes a decision durable, and lets future agents judge edge cases instead of blindly applying the rule.
