---
title: M2.5 Graph-First Read-Only Workbench
description: Current M2.5 Workbench plan and amended visual-readiness stages for the read-only src/workbench/ map.
doc_type: plan
scope:
  - workbench
  - read-only graph
  - skill and agent surfaces
  - current M2 docs
covers:
  - src/workbench/
  - docs/workflow-map.md
  - README.md
---

# M2.5 Graph-First Read-Only Workbench

## Current Stage

The Workbench roadmap now splits the read-only map work into smaller visual stages:

```text
M2 Read-Only Visual Map V1
  -> M2.5A Graph Engine Reset
  -> M2.5B Visual Parity And Workbench Shell UX
  -> M2.6 Real Codex Source Readiness
  -> M3 Timestamped Work Package Safety Core
```

M2.5A is the current baseline.
It replaced the fragile hand-built graph view with Cytoscape and circular graph nodes.

M2.5B is the next milestone.
It should refine the whole Workbench screen, not only the graph.

M2.6 should verify the map against real Codex sources before any editing milestone starts.

## Goal

Build the current Workbench under `src/workbench/` as a graph-first read-only map for local Codex skill and agent surfaces.

The Workbench is for inspection.
It does not edit files, apply patches, build work packages, or run agents.

## Run Command

Start the M2.5 Workbench with:

```bash
python3 -m src.workbench.server --host 127.0.0.1 --port 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

## M2.5 Limits

The current Workbench is limited to:

- read-only viewing
- skill nodes and agent nodes only
- detected edges only
- one selected source at a time
- local source discovery from Codex-home-like roots
- graph-first camera, hover, selection, filters, minimap, pan, zoom, and fit

The graph is not a general editor.
It does not expose write controls.

## What The Workbench Shows

The current M2.5A baseline shows:

- a narrow icon rail at far left
- a source and filter rail
- a graph-dominant canvas
- a right inspector
- a top toolbar
- graph controls and a minimap inside the canvas
- circular skill and agent nodes only
- edges created from detected text matches

The graph is meant to feel quiet and stable.
It should help a user understand the current source, not change it.

## M2.5B Screen Contract To Decide

Before the next implementation pass, decide the UX frame for the whole screen:

- top bar actions and labels
- left icon rail purpose
- source panel density and source switching flow
- filter behavior when many nodes exist
- graph canvas proportions and default fit
- node icon, label, selected, hover, and edge highlight states
- inspector information order
- empty and error states
- desktop and narrow-width drawer behavior
- Browser screenshot acceptance bar

M2.5B should not start from code polish alone.
It should start from this screen contract.

## Source Rules

The Workbench should read one source at a time:

- Global: expanded `~/.codex`
- Local: repo-root `.codex` when present
- Custom: a user-provided root path

A source is valid only when it is Codex-home-like.
That means it has `skills/` and/or `agents/` directly under the root.

## Historical Note

Older POC drafts described the Workbench as an editing studio with apply, work-package, and agent-run features.
That was the old shape.
It is kept here only as history and is not current behavior.

## Current Doc Links

- `README.md`
  project overview and doc entry point
- `docs/README.md`
  current docs index
- `docs/workbench-roadmap.md`
  current amended Workbench milestone map
- `docs/workflow-map.md`
  current workflow map and Workbench guide
