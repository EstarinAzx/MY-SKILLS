#!/usr/bin/env node
// elucidate — shared configuration resolver and hardened flag-file helpers.
//
// The symlink-safe flag read/write logic is adapted verbatim from the skeleton
// plugin's skeleton-config.js — battle-tested, reused rather than rewritten.
//
// Unlike skeleton, elucidate has a SINGLE axis:
//   mode — 'default'   (only the few most critical why-comments)
//        | 'learner'   (a one-sentence comment above every action)
//        | 'technical' (deepest — why plus tradeoffs, complexity, perf,
//                       edge cases, in expert voice)
//
// There is no METHOD axis: new code is always implemented directly, in one
// pass — no comment-only scaffold phase, no approval gate.
//
// The flag file holds ONE string: 'off', or a mode ('default'/'learner'/
// 'technical'). Like skeleton, the flag is never deleted — 'off' is a stored,
// displayed state so the statusline can always render a badge.

const fs = require('fs');
const path = require('path');
const os = require('os');

const VALID_MODES = ['default', 'learner', 'technical'];

// Every legal flag value. readFlag whitelists against this.
const VALID_STATES = ['off', 'default', 'learner', 'technical'];

// Used when activating from a cold 'off' state with no explicit mode.
const DEFAULT_MODE = 'default';

function getConfigDir() {
  if (process.env.XDG_CONFIG_HOME) {
    return path.join(process.env.XDG_CONFIG_HOME, 'elucidate');
  }
  if (process.platform === 'win32') {
    return path.join(
      process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'),
      'elucidate'
    );
  }
  return path.join(os.homedir(), '.config', 'elucidate');
}

function getConfigPath() {
  return path.join(getConfigDir(), 'config.json');
}

// Parse a flag value into { active, mode }. Anything malformed resolves to
// inactive — never trust the flag's bytes.
function parseState(raw) {
  if (!raw || raw === 'off') {
    return { active: false, mode: null };
  }
  const mode = String(raw).trim().toLowerCase();
  if (VALID_MODES.includes(mode)) {
    return { active: true, mode: mode };
  }
  return { active: false, mode: null };
}

// Resolve the state a new session should start in. Returns 'off' or a mode.
// Env var > config file > 'off'.
function getDefaultState() {
  let cfg = {};
  try {
    cfg = JSON.parse(fs.readFileSync(getConfigPath(), 'utf8'));
  } catch (e) { /* no config — fall through to defaults */ }

  const valid = ['off'].concat(VALID_MODES);
  const envMode = (process.env.ELUCIDATE_DEFAULT_MODE || '').toLowerCase();
  const cfgMode = (cfg.defaultMode ? String(cfg.defaultMode) : '').toLowerCase();
  if (valid.includes(envMode)) return envMode;
  if (valid.includes(cfgMode)) return cfgMode;
  return 'off';
}

// Symlink-safe flag file write. Writes atomically via temp + rename with 0600
// permissions and O_NOFOLLOW. Protects against a local attacker replacing the
// predictable flag path (~/.claude/.elucidate-active) with a symlink. When the
// parent dir is a symlink (legitimate: ~/.claude symlinked elsewhere) it
// resolves through and verifies ownership. Silent-fails on any FS error.
function safeWriteFlag(flagPath, content) {
  const debug = process.env.ELUCIDATE_DEBUG === '1';
  try {
    const flagDir = path.dirname(flagPath);
    fs.mkdirSync(flagDir, { recursive: true });

    let realFlagDir;
    try {
      const lstat = fs.lstatSync(flagDir);
      if (lstat.isSymbolicLink()) {
        realFlagDir = fs.realpathSync(flagDir);
        const realStat = fs.statSync(realFlagDir);
        if (!realStat.isDirectory()) {
          if (debug) process.stderr.write(`[elucidate] safeWriteFlag: symlink target ${realFlagDir} is not a directory\n`);
          return;
        }
        if (typeof process.getuid === 'function') {
          if (realStat.uid !== process.getuid()) {
            if (debug) process.stderr.write(`[elucidate] safeWriteFlag: symlink target ${realFlagDir} owned by uid ${realStat.uid}\n`);
            return;
          }
        } else {
          const normalizedReal = path.resolve(realFlagDir).toLowerCase();
          const normalizedHome = path.resolve(os.homedir()).toLowerCase();
          if (!normalizedReal.startsWith(normalizedHome + path.sep) && normalizedReal !== normalizedHome) {
            if (debug) process.stderr.write(`[elucidate] safeWriteFlag: symlink target ${normalizedReal} is outside home\n`);
            return;
          }
        }
      } else {
        realFlagDir = flagDir;
      }
    } catch (e) {
      return;
    }

    // The flag file itself must never be a symlink — that's the clobber vector.
    const realFlagPath = path.join(realFlagDir, path.basename(flagPath));
    try {
      if (fs.lstatSync(realFlagPath).isSymbolicLink()) return;
    } catch (e) {
      if (e.code !== 'ENOENT') return;
    }

    const tempPath = path.join(realFlagDir, `.elucidate-active.${process.pid}.${Date.now()}`);
    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
    const flags = fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | O_NOFOLLOW;
    let fd;
    try {
      fd = fs.openSync(tempPath, flags, 0o600);
      fs.writeSync(fd, String(content));
      try { fs.fchmodSync(fd, 0o600); } catch (e) { /* best-effort on Windows */ }
    } finally {
      if (fd !== undefined) fs.closeSync(fd);
    }
    fs.renameSync(tempPath, realFlagPath);
  } catch (e) {
    // Silent fail — flag is best-effort
  }
}

// Symlink-safe, size-capped, whitelist-validated flag file read. Refuses
// symlinks, caps the read, rejects anything not in VALID_STATES. Returns null
// on any anomaly so callers never inject untrusted bytes into model context or
// the terminal. MAX_FLAG_BYTES is a hard cap — the longest legal value is
// 'technical' (9 bytes); 64 leaves slack without enabling exfil.
const MAX_FLAG_BYTES = 64;

function readFlag(flagPath) {
  try {
    let st;
    try {
      st = fs.lstatSync(flagPath);
    } catch (e) {
      return null;
    }
    if (st.isSymbolicLink() || !st.isFile()) return null;
    if (st.size > MAX_FLAG_BYTES) return null;

    const O_NOFOLLOW = typeof fs.constants.O_NOFOLLOW === 'number' ? fs.constants.O_NOFOLLOW : 0;
    let fd;
    let out;
    try {
      fd = fs.openSync(flagPath, fs.constants.O_RDONLY | O_NOFOLLOW);
      const buf = Buffer.alloc(MAX_FLAG_BYTES);
      const n = fs.readSync(fd, buf, 0, MAX_FLAG_BYTES, 0);
      out = buf.slice(0, n).toString('utf8');
    } finally {
      if (fd !== undefined) fs.closeSync(fd);
    }

    const raw = out.trim().toLowerCase();
    if (!VALID_STATES.includes(raw)) return null;
    return raw;
  } catch (e) {
    return null;
  }
}

module.exports = {
  getDefaultState, getConfigDir, getConfigPath, parseState,
  VALID_STATES, VALID_MODES, DEFAULT_MODE,
  safeWriteFlag, readFlag
};
