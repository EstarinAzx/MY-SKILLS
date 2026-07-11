---
type: synthesis
updated: 2026-07-12
tags: [synthesis, harness, meta]
---

# harness-engineering

The umbrella discipline this whole setup practices: building persistent
machinery that shapes every session, instead of crafting individual prompts.
[[loop-engineering]] is one subsystem of it; [[ecosystem-overview]] is its
inventory.

## The ladder

- **Prompt engineering** — craft one message; dies with the message.
- **Context engineering** — control what a session's window contains.
  [[preset]] `pick-up`/`wrap-up` live here: they decide what a session
  starts with and what it leaves behind (`.context/`,
  [[context-handoff]]). Historically the gateway: pick-up/wrap-up were the
  first pieces built (token burn + context rot pain), and everything else
  grew from that pattern.
- **Harness engineering** — persistent machinery that acts without being
  asked, session after session.

## What the harness is made of (here)

- **Hooks / modes** — [[caveman]], [[ponytail]], [[elucidate]] fire before
  a word is typed; they shape output, code style, and build philosophy in
  every session. See [[settings-and-hooks]].
- **Contracts** — the loop-body contract, the elucidate house style, the
  preset one-shot rule: written rules a session obeys mechanically.
- **State files** — `.context/`, relay chain files, tracker tickets, the
  vault itself. Everything durable lives in files; sessions are disposable
  workers (the files-not-sessions principle, [[loop-engineering]]).
- **Enforcement** — [[ecosystem-audit]] `audit.py` + `template_sync.py`,
  [[llm-kb]] `lint.py`: deterministic scripts that check map-matches-
  territory, rolled up by `/preset health`. No background LLM, on-demand
  only ([[knowledge-base-lineup]] standing rule).
- **Session lifecycle** — [[relay]]: the harness deciding when a session
  dies and how its successor is born.
- **Reproducibility** — `template/IN USE` mirrored to MY-SKILLS; the
  harness is a repo, not a machine's accident.

## The practice

Pain → ritual → codify → generalize. Token burn and context rot became the
pick-up/wrap-up ritual (built with Claude's help); the ritual became preset
files; the pattern generalized into [[context-handoff]] for projects and
[[relay]] for loops. Each round the vault records the decision
([[design-skill-lineup]], [[knowledge-base-lineup]], the loop decisions), so
the harness explains itself and future sessions extend it without
archaeology.

## Why it compounds where skill-hoarding doesn't

Installed skills are islands; a harness is a graph. Relationships are
authored (wikilinks here), overlaps are consolidated (lineup decisions),
layers chain instead of colliding ([[relay]] slotted between `/loop` and
[[preset]] bodies without touching either). The vault is the load-bearing
piece: skills you can install, relationships you must write.
