#!/usr/bin/env node
// elucidate — Claude Code SessionStart activation hook.
//
// Runs on every session start:
//   1. Resolves the mode: a valid saved flag persists across sessions; only the
//      first-ever run falls back to env / config / 'off'.
//   2. Writes the flag file at $CLAUDE_CONFIG_DIR/.elucidate-active.
//      The flag is ALWAYS written — even for 'off' — because the statusline
//      renders a permanent badge.
//   3. When the mode is active, emits the full elucidate workflow as
//      SessionStart context so the model has the rules from turn one.

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultState, parseState, safeWriteFlag, readFlag } = require('./elucidate-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.elucidate-active');

// Persist the mode across sessions: a valid saved flag wins, so reopening
// Claude Code keeps whatever mode was last set. The env var / config default
// only seeds the first-ever run, when no flag file exists yet.
let state = readFlag(flagPath);
if (state === null) {
  state = getDefaultState();
}

// Write the flag every session — the badge needs it present even when off.
safeWriteFlag(flagPath, state);

const { active, mode } = parseState(state);

// Off — elucidate is dormant. Write the flag (done above), say nothing
// behavioral. Injecting workflow rules while off would only confuse the model.
if (!active) {
  process.stdout.write('OK');
  process.exit(0);
}

// Active — emit the full workflow. Read SKILL.md as the single source of truth
// so edits to it propagate automatically with no hardcoded duplication.
// Plugin layout: __dirname = <plugin_root>/src/hooks/, skill two levels up.
let skillContent = '';
try {
  skillContent = fs.readFileSync(
    path.join(__dirname, '..', '..', 'skills', 'elucidate', 'SKILL.md'), 'utf8'
  );
} catch (e) { /* fall back to the short ruleset below */ }

let output;

if (skillContent) {
  // Strip YAML frontmatter — the model only needs the workflow body.
  const body = skillContent.replace(/^---[\s\S]*?---\s*/, '');
  output = 'ELUCIDATE MODE ACTIVE (mode=' + mode + ')\n\n' + body;
} else {
  // Fallback when SKILL.md cannot be read — minimum viable ruleset.
  const modeLine = {
    default: 'MODE default — inside bodies add only the few most critical ' +
      'why-comments. Keep it sparse.',
    learner: 'MODE learner — a one-sentence comment above every logical ' +
      'action; say what it does, not how the language works; no dash prefix.',
    technical: 'MODE technical — comment wherever there is technical ' +
      'substance and go deep: the why plus tradeoffs, complexity, perf, edge ' +
      'cases, failure modes, in expert voice.'
  }[mode];
  output =
    'ELUCIDATE MODE ACTIVE (mode=' + mode + ')\n\n' +
    'Every code-writing task carries its logic in plain-English comments.\n\n' +
    'NEW function/class/file → write the commented code directly, in one pass: ' +
    'no scaffold phase, no approval gate. Still include the banners, file-top ' +
    'block, and one-line summary above each construct.\n\n' +
    'EDIT to existing code: write the plain-English comment and the code ' +
    'together in one pass — no approval gate.\n\n' +
    modeLine + '\n\n' +
    'Section the file with one-line banner comments: a title banner at the ' +
    'top, and a section banner before each logical group of constructs (a ' +
    'banner is one line — the title set in a run of dashes).\n\n' +
    'Logic-bearing source files only. When code later changes, update the ' +
    'matching comment in the same edit. Toggle off with /elucidate:off.';
}

process.stdout.write(output);
