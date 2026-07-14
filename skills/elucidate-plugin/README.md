# Elucidate

A lightweight Claude Code plugin that makes Claude automatically comment its
logic in plain language as it writes code — at varying levels of depth — with
each file sectioned by **banner comments**.

## What it is

ELUCIDATE is a *session mode*. When on, every coding task is written in a house
style: a title banner, a file-top block, section banners, a one-line summary
above each construct, and step comments inside bodies. New code is **implemented
directly, in one pass** — there is no comment-only scaffold phase and no
approval gate.

One axis shapes the output:

| Axis | Values | Controls |
|---|---|---|
| **MODE** | `DEFAULT` / `LEARNER` / `TECHNICAL` | how deep the step comments go |

- **default** — sparsest: only the few most critical why-comments.
- **learner** — a one-sentence comment above every logical action; says *what*
  the code does, never *how the language works*.
- **technical** — deepest: why plus tradeoffs, complexity, performance, edge
  cases, in an expert voice.

It is a **depth** ladder — `default` says least per comment, `technical` most;
`learner` comments most often (every block) but simplest.

## Straight implementation

Code is written **directly**, with its comments, in one pass. There is no
comment-first scaffold phase and no approval gate — that ceremony was an
unnecessary token expense. The comment layer and the code arrive together,
every time.

## Commands

| Command | Sets |
|---|---|
| `/elucidate:default` | MODE → default |
| `/elucidate:learner` | MODE → learner |
| `/elucidate:technical` | MODE → technical |
| `/elucidate:off` | mode off |

A fresh session starts **off**. Any mode command turns it on. Pin a first-run
default with the `ELUCIDATE_DEFAULT_MODE` env var (`default` | `learner` |
`technical` | `off`) or a `config.json` (see below). After the first run the
saved flag persists across sessions.

The skill is also invokable directly as `/elucidate:elucidate`.

## How it works

- Flag file `$CLAUDE_CONFIG_DIR/.elucidate-active` holds one value — `off` or a
  mode. Always present, never deleted (so the badge always renders).
- The `SessionStart` hook resolves the state (a valid saved flag persists; env /
  config seed only the first-ever run), writes the flag, and injects the
  `SKILL.md` workflow when the mode is on.
- The `UserPromptSubmit` hook tracks `/elucidate:*` toggles and re-injects a
  short reminder each turn.
- The statusline renders `[ELUCIDATE] [MODE:…]`, or a dimmed `[ELUCIDATE]` when
  off.

## Install

`/plugin marketplace add` only accepts a local source as `./path` **relative to
the current session's working directory** — anything else is treated as a
GitHub `owner/repo` and cloned over SSH. So open *this* directory
(`elucidate-plugin`) as the Claude Code workspace, then:

1. `/plugin marketplace add ./`
2. `/plugin install elucidate@elucidate`
3. Wire the statusline (see below).
4. `/reload-plugins`

(Avoid spaces in the directory name — they break the marketplace path parser.)

### Statusline

Claude Code allows only **one** `statusLine` in `settings.json`. Two ways to
wire elucidate's badge:

**Standalone** — point `statusLine` directly at the badge script:

```jsonc
// settings.json
"statusLine": {
  "type": "command",
  "command": "pwsh -NoProfile -File \"${CLAUDE_PLUGIN_ROOT}/src/hooks/elucidate-statusline.ps1\""
}
```

(On macOS / Linux use `bash .../elucidate-statusline.sh`.)

**Composed with other badges** — if you already run a statusline wrapper for
another plugin, add elucidate's badge by dot-sourcing `elucidate-statusline.ps1`
(it is written `exit`-free for exactly this) or calling `elucidate-statusline.sh`
after the others. Each badge script is independent — if a plugin is absent, its
badge is simply skipped.

## Env vars

- `ELUCIDATE_DEFAULT_MODE` — `default` | `learner` | `technical` | `off`.
  First-run seed.
- `CLAUDE_CONFIG_DIR` — directory holding the flag file (defaults to
  `~/.claude`). Read, never set, by this plugin.
- Config-file alternative: `%APPDATA%\elucidate\config.json` (Windows) or
  `~/.config/elucidate/config.json` — `{ "defaultMode": "..." }`.

Resolution: the saved flag (`.elucidate-active`) persists across sessions and
wins. Env var > config file seed only the first-ever run; final fallback `off`.

## Layout

- `.claude-plugin/` — `plugin.json` (the two hooks) + `marketplace.json`
- `commands/` — 4 Markdown slash commands: `default`, `learner`, `technical`,
  `off`
- `skills/elucidate/` — `SKILL.md` (the workflow — single source of truth) +
  `example/` (one filled file per mode)
- `src/hooks/` — 3 Node hooks (`elucidate-config.js`, `elucidate-activate.js`,
  `elucidate-mode-tracker.js`) + 2 statusline scripts (`.ps1` / `.sh`)

The hooks are dependency-free Node (stdlib only); the statusline is PowerShell +
Bash. No build step, no Python, no MCP server.
