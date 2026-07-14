#!/usr/bin/env node
// elucidate — UserPromptSubmit hook.
//
// Two jobs every turn:
//   1. Inspect the user's input for /elucidate:* toggles and update the flag.
//      The mode has a SINGLE axis — default / learner / technical — plus off.
//   2. When the mode is active, re-inject a SHORT reminder. The SessionStart
//      hook injects the full workflow once; this keeps it anchored against
//      context compression — but stays terse.

const path = require('path');
const os = require('os');
const {
  safeWriteFlag, readFlag, parseState, VALID_MODES
} = require('./elucidate-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.elucidate-active');

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const lower = (data.prompt || '').trim().toLowerCase();

    // Resolve the mode this prompt asks for — null means "leave the flag
    // untouched". Only ever set when the prompt is clearly a mode intent, so
    // the /elucidate:elucidate SKILL body (which lists every mode, "off"
    // included) can no longer flip the flag off just by being loaded.
    let target = null;
    if (/\belucidate\b/.test(lower)) {
      // A mode COMMAND injects its body, which always declares "…is now
      // <mode>" (off.md → "is now OFF"). The skill doc never says "is now",
      // so this matches the four commands and excludes the skill.
      const directive = /\bis now\b[\s*]*?(default|learner|technical|off)\b/.exec(lower);
      if (directive) {
        target = directive[1];
      } else if (lower.length <= 120) {
        // Otherwise only a SHORT prompt counts — a raw /elucidate:<mode> line
        // or a plain-English toggle. The length gate stops any long injected
        // body (skill or command) from reaching the loose keyword scan.
        const slash = /\/elucidate[-a-z]*[:\s]+(default|learner|technical|off)\b/.exec(lower);
        if (slash) {
          target = slash[1];
        } else if (/\b(off|stop|disable|deactivate|turn off)\b/.test(lower)) {
          target = 'off'; // most specific first — "off" wins ties
        } else if (/\blearner\b/.test(lower)) {
          target = 'learner';
        } else if (/\btechnical\b/.test(lower)) {
          target = 'technical';
        } else if (/\b(default|activate|enable|turn on|start)\b/.test(lower)) {
          target = 'default';
        }
      }
    }
    if (target) safeWriteFlag(flagPath, target);

    // Per-turn reinforcement — only when active.
    const now = parseState(readFlag(flagPath));
    if (now.active) {
      const modeLine = {
        default: 'Comment sparingly — only the few most critical whys.',
        learner: 'One-sentence comment above every action — what it does, not how the language works.',
        technical: 'Comment where there is technical substance; go deep — why, ' +
          'tradeoffs, complexity, perf, edge cases.'
      }[now.mode];
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'UserPromptSubmit',
          additionalContext:
            'ELUCIDATE MODE ACTIVE (mode=' + now.mode + '). ' +
            'NEW function/class/file → write commented code directly in one ' +
            'pass, no scaffold phase and no approval gate. ' +
            'EDIT to existing code → write the English comment and the code ' +
            'together, no approval gate. ' + modeLine +
            ' Section the file with banner comments (title banner + section ' +
            'banners). Logic-bearing source files only.'
        }
      }));
    }
  } catch (e) {
    // Silent fail — never block a prompt over mode tracking.
  }
});
