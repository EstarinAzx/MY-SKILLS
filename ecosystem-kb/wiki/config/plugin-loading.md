---
type: config
updated: 2026-06-12
tags: [config, plugins, mechanism]
source: live inspection 2026-06-12
---

# plugin-loading

How plugins get into a session — three paths observed:

1. **Marketplace install** — `~/.claude/plugins/known_marketplaces.json` lists sources (github repos or directories); installs land in `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>` and register in `installed_plugins.json`. Used by [[superpowers]], [[caveman]], [[codex]].
2. **Directory marketplace** — a local path registered as marketplace source; [[elucidate]] loads straight from `~/.claude/skills/elucidate-plugin` (installPath = source, no cache copy).
3. **skills-dir auto-load** — any folder under `~/.claude/skills/` containing `.claude-plugin/` auto-loads as `<name>@skills-dir`, *without* any registry entry. **Deleting the folder is the uninstall.** This is how the skeleton plugin lived and died ([[commenting-mode-lineup]]); elucidate also appears as `elucidate-local@skills-dir`.

Implication: keep non-plugin folders out of `~/.claude/skills/` (this vault deliberately lives at `~/.claude/ecosystem-kb`). Plugin MCP servers spawn per session and **lock their files on Windows** — kill the server processes before deleting a plugin folder.
