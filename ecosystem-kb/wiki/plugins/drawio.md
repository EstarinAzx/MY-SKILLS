---
type: plugin
updated: 2026-07-12
tags: [plugin, diagrams, design]
source: live inspection 2026-07-12
---

# drawio

Diagram-generation plugin from marketplace `Agents365-ai/365-skills`, installed
2026-07-12. One skill: `drawio:drawio-skill` v1.28.2 (upstream
`github.com/Agents365-ai/drawio-skill`, MIT). Marketplace clone at
`~/.claude/plugins/marketplaces/365-skills`. **Skills-only plugin — no hooks,
no MCP, no agents**; honors the no-hooks preference out of the box.

**What it does:** hand-writes or generates `.drawio` XML, exports PNG/SVG/PDF/JPG
via the draw.io desktop CLI, vision self-check loop on the exported PNG, style
presets. 28 bundled Python scripts: `shapesearch.py` (10k+ official shapes),
`autolayout.py` (Graphviz placement), code importers (`pyimports`/`jsimports`/
`goimports`/`rustimports`/`pyclasses`), IaC importers (`tfimports`/`k8simports`/
`composeimports`) + live-infra (`tfstate`/`dockerimports`/kubectl), `seqlayout.py`
(deterministic sequence diagrams), `c4.py` (multi-page C4 with drill-down),
`sqlerd.py`, `openapiimports.py`, `drawiodiff.py`, `heatmap.py`, `timelapse.py`,
`explain.py`, reverse-exports (`drawio2pptx`/`drawiohtml`/`drawio2mermaid`/
`svgflow`), `validate.py`.

**Deps status (2026-07-12, installed same day via winget):** draw.io desktop
v30.2.6 (`JGraph.Draw`) + Graphviz 15.1.0 (`Graphviz.Graphviz`); Python
present. ≥v30 unlocks Mermaid→`.drawio` CLI conversion and ELK `--layout`.
PNG export smoke-tested green. ⚠️ Two Windows quirks: (1) the exe is at
`C:\Users\S.D\AppData\Local\Programs\draw.io\draw.io.exe` (per-user MSI) —
NOT the `C:\Program Files\draw.io\` path the skill's step-1 resolution and
examples assume, so point the skill at the full LocalAppData path; (2)
`--version` prints nothing from PowerShell (Electron detached stdout) — use
`cmd /c "...exe --version > out.txt 2>&1"` to read it; file exports (`-x -f
png -o …`) work normally.

**Routing vs neighbors:** inline Mermaid in `.context/` stays the source of
truth for [[happy-path]] (`happy-path.md`) and [[trace]] (`flows.md`) —
git-rendered, zero-dep; the skill's own routing table agrees (markdown-native
diagrams → mermaid). drawio is the **presentation/export layer** on top:
promote an MVD or traced flow to a polished, editable PNG/SVG/PDF when it
leaves the repo (docs, slides, stakeholders). Mermaid→drawio CLI conversion
(≥v30) makes that promotion zero-rework. `seqlayout.py` fits trace's
sequence-shaped answers; the code importers draw the *static* import graph
(complement, not overlap — trace follows one runtime flow). [[design-skills]]
(UI), dataviz (charts), Excalidraw MCP (hand-drawn) are different niches —
"polished exportable diagram" was vacant, no lineup conflict.

**Deliberately not installed:** the marketplace's sibling diagram plugins
(mermaid, plantuml, excalidraw, tldraw) — inline Mermaid needs no plugin, and
one winner per niche.

⚠️ The skill description says "use proactively when explaining systems with
3+ components" — it can self-invoke in ordinary sessions; with the CLI missing
it falls back to a browser URL rather than failing.
