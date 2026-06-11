---
type: plugin
updated: 2026-06-12
tags: [plugin, second-opinion, codex]
source: live inspection 2026-06-12
---

# codex

OpenAI Codex companion plugin from `openai/codex-plugin-cc`, v1.0.4, installed 2026-05-06. Cache: `~/.claude/plugins/cache/openai-codex/codex/1.0.4`. Heaviest-used plugin (353 uses as of 2026-06-11).

Bridges Claude Code to the local Codex CLI for second-opinion and rescue work:

- `codex:rescue` skill + `codex-rescue` agent — hand off investigation, deep root-cause diagnosis, or substantial coding tasks to Codex via shared runtime; use proactively when Claude is stuck or wants a second implementation pass.
- `codex:setup` — check local Codex CLI readiness; toggle stop-time review gate.
- Internal guidance skills: `codex-cli-runtime` (helper contract), `codex-result-handling` (presenting output), `gpt-5-4-prompting` (composing Codex/GPT-5.4 prompts).

Requires Codex CLI installed locally.
