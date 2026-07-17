#!/usr/bin/env node
// ecosystem — UserPromptSubmit echo: keep the CLAUDE.md routing gate in
// attention every turn (survives compaction + long-session drift).
// Static text only — no LLM calls, no state (standing no-background rule).
process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext:
      "ECOSYSTEM ROUTING ACTIVE. The CLAUDE.md situation→invoke table " +
      "is a gate: a row matches this prompt → invoke that route before " +
      "responding, even for questions."
  }
}));
