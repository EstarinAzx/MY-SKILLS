# prompt-writer — turn a rough ask into a clean agent prompt

One-shot, off-loop (invoke anytime). Takes a rough prompt, a task description, or
"prompt the next agent to do X" and returns a **paste-ready** prompt for another
agent or subagent. Argument is the raw prompt/idea:
`/preset prompt-writer <rough prompt or task>`.

The job is **not** to reword — it is to make the prompt *correct, scoped, and
bounded* before it ships. A prompt that reads nicely but points at the wrong slice
is worse than the messy original.

## Principles

- **Verify before you write.** Check the ask against reality — the repo,
  `.context/`, the issues, the code. If the framing is wrong (a slice that isn't
  actually TDD, a file that doesn't exist, a blocker they missed, a dependency out
  of order), fix it. Never propagate the user's error into the prompt. This is the
  step that earns the preset.
- **Goal first, then the specifics each target needs.** Spell out each task's real
  contract so the receiving agent doesn't guess. Vague prompt in → vague work out.
- **Set boundaries.** Say what NOT to do: blocked work, out-of-scope, "stop at X".
  A boundary prevents overreach better than a paragraph of hope.
- **Pin the rules.** Name the skills, conventions (`CLAUDE.md`), and house style the
  agent must follow, so its output matches the project.
- **Right-size.** Flag ceremony the task doesn't earn — a worktree for
  non-colliding work, a subagent for a one-liner, an extra phase. Less is more;
  also say when the ceremony WOULD be worth it.
- **Rehydration first** (for a fresh-session agent). Open the prompt with what to
  read (`.context/active-work.md`, the PRD/issue) before acting.

## Steps

1. **Capture the raw ask.** Argument → that's the prompt to enhance. No argument →
   ask one line: "What should the next agent do?".
2. **Verify against reality.** Check the claims — issue numbers, file/slice names,
   TDD-vs-not, blockers, dependencies, conventions. Correct anything wrong before
   writing a word of the prompt.
3. **Write the prompt.** Produce ONE paste-ready block: a rehydration pointer (if
   cross-session), the goal, each target's explicit contract, hard boundaries
   (don't-do / blocked / out-of-scope), and the skills/conventions to follow. Match
   the receiving runtime — a slash entry like `/preset pick-up` if that's the door,
   plain instructions otherwise.
4. **Explain the diff.** Below the block, a short "what changed + why" — the
   corrections and boundaries you added — so the user trusts the prompt instead of
   pasting it blind.
5. **Cut ceremony.** Call out anything in the original ask that's unnecessary for
   this task, and name when it would actually pay off.

Output = the prompt block + the short rationale. Nothing else.
