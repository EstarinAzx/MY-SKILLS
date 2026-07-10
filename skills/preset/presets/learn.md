# learn — trace a flow and crystallize its vocabulary in one pass

One-shot. Off-loop — runs anytime, not part of the handoff cycle. Argument is the flow question: `/preset learn <how does X work>`. Bare invocation → defer to trace's own bare handling (list known flows, or ask which flow).

## Steps

1. **Trace — plain register.** Invoke the `trace` skill with the argument as the question, and tell it to answer in **plain / approachable register** — learn is always a learning context, so never ask: lead with the plain-English version (everyday words, a real-world analogy when it helps), and keep `file:line` as an engineer view offered in one closing line. Run trace fully per its own SKILL — flows.md recall, lens classification, subagent zoom-out, data trace, plain-layout answer, persist to `.context/flows.md`.
2. **Collect term candidates while tracing.** Exactly three mismatch types qualify:
   - the user's word ≠ the code's name for the same thing ("reservation" vs `Booking`)
   - a term in the code or the question is fuzzy or overloaded — one word, two meanings
   - the code contradicts an existing `CONTEXT.md` glossary entry

   Nothing else qualifies; aligned vocabulary is not a candidate.
3. **Gate.** No candidates → report "vocabulary aligned — no terms to resolve" and stop. `CONTEXT.md` untouched.
4. **Mini-grill.** Grill the candidates only — one term at a time, a recommended answer with each question (grill-with-docs interview style). No plan stress-test, no design-tree walk.
5. **Record.** As each term resolves, update `CONTEXT.md` inline per grill-with-docs' `CONTEXT-FORMAT.md`. Create the file lazily on the first resolved term. Glossary only — zero implementation detail.
6. **ADRs.** Inherited rule: offer one only when hard-to-reverse + surprising-without-context + real trade-off, all three. Expect ~never in a terminology session.

Store boundary: trace owns `.context/flows.md`; the grill half owns `CONTEXT.md`. Neither writes the other's file.
