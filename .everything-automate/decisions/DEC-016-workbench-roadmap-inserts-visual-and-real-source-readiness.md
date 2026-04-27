---
title: Workbench Roadmap Adds Visual And Real Source Readiness Steps
status: accepted
date: 2026-04-28
decision_id: DEC-016
---

# Workbench Roadmap Adds Visual And Real Source Readiness Steps

## Context

The locked Workbench roadmap moved from:

```text
M1 source and graph contract
  -> M2 read-only visual map
  -> M3 timestamped work package safety
```

The first M2.5 UI pass showed that this jump was too large.

The Workbench did load a graph, but the first graph UI did not match the accepted visual direction.
It also broke at small widths and used a hand-built graph camera that was too fragile.

The Cytoscape reset fixed the graph engine direction, but it also showed that visual quality and real source readiness need to be explicit milestones before safe editing.

## Decision

Keep the original locked roadmap as historical record.

Add the current Workbench roadmap amendment:

```text
M1: Source And Graph Contract
  -> M2: Read-Only Visual Map V1
  -> M2.5A: Graph Engine Reset
  -> M2.5B: Visual Parity And Workbench Shell UX
  -> M2.6: Real Codex Source Readiness
  -> M3: Timestamped Work Package Safety Core
```

M2.5A is complete enough to treat as the new baseline:

- Cytoscape is the graph engine.
- Nodes render as circular skill and agent graph nodes.
- Pan, zoom, fit, node click, and inspector selection work.
- The first broken responsive shell has been replaced.

M2.5B is the next milestone:

- Treat the whole Workbench screen as the UX target, not only the graph.
- Align the top bar, icon rail, source panel, graph canvas, minimap, inspector, empty states, error states, and responsive drawers with the accepted reference direction.
- Use Browser screenshots as an explicit acceptance check.
- Keep the Workbench read-only.

M2.6 follows M2.5B:

- Load real global `~/.codex`, local repo `.codex`, and custom Codex-home-like sources.
- Keep layout, fit, filters, inspector, and performance usable when the node count grows.
- Decide what search, grouping, and large-graph fallback are needed before editing starts.

## Consequences

- Do not start M3 work package editing until the read-only Workbench can be trusted visually and against real local Codex sources.
- M2.5B should start with a short UX frame discussion before implementation.
- M2.6 should test actual user sources, not only fixtures.
- The Workbench remains Codex-first and read-only through M2.6.
- Editing, apply-back, work packages, and agent scenario tests remain later milestones.

## Related Artifacts

- `.everything-automate/state/milestone/archive/20260426-105927-codex-workbench-roadmap.md`
- `.everything-automate/decisions/DEC-015-workbench-m25-graph-first-interaction.md`
- `docs/workbench-roadmap.md`
- `docs/workbench-implementation-plan.md`
