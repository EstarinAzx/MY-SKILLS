---
type: decision
updated: 2026-07-13
tags: [decision, template, plugins]
source: live inspection 2026-07-13
---

# template-plugins-snapshot

**2026-07-13 — MY-SKILLS keeps plugin *sources*, drops plugin *caches*.**

The template repo (`template/IN USE` → MY-SKILLS) has carried a full
`plugins/` snapshot since the 2026-06-11 consolidation (`f071d1c`):
marketplaces + caches + registry JSONs. Found two rots: (1) the superpowers
cache dir contained an embedded `.git`, so it committed as a **gitlink**
(mode 160000) — zero files on GitHub, a dangling pointer no clone can
resolve, and perpetual ` M` status noise; (2) the whole snapshot was frozen
at 2026-06-11 vintage (superpowers 5.1.0 vs live 6.1.1) because
[[ecosystem-audit]] `template_sync.py` maintains only `skills/` +
`ecosystem-kb/` — nothing refreshed `plugins/`.

**Kept:** `plugins/installed_plugins.json`, `known_marketplaces.json`,
registry JSONs, and the `plugins/marketplaces/` clones — enough to rebuild
any install.

**Cut:** `plugins/cache/**` untracked (`git rm --cached`) and `.gitignore`d
in the template repo — caches are re-derivable from the kept pieces, and
cache dirs can embed `.git` repos that break as gitlinks. Working-tree copy
left in place (ignored, harmless).

**Rejected:** refreshing the cache snapshot each update — would need a third
`template_sync.py` root and re-rots between syncs; the registry+marketplace
pair already carries the reproducibility.

⚠️ Registry JSONs and marketplace clones in the template still snapshot
manually — they too can lag live (no checker covers them). Accepted for now;
revisit if a restore-from-repo ever bites.
