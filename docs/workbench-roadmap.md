---
title: Codex Workbench Roadmap
description: Current amended milestone roadmap for the Codex-first Workbench.
doc_type: roadmap
scope:
  - workbench
  - milestones
  - codex
  - visual map
covers:
  - docs/workbench-source-contract.md
  - docs/workbench-implementation-plan.md
  - docs/workflow-map.md
---

# Codex Workbench Roadmap

This is the current Workbench milestone map.

The original locked roadmap is still preserved as history:

- `.everything-automate/state/milestone/archive/20260426-105927-codex-workbench-roadmap.md`

This document records the current amendment after the graph UI reset.

## Parent Goal

Build a Codex-first visual personal harness workbench for the user's local Codex setup.

The Workbench should help the user:

- choose a global, local, or custom Codex source
- see the actual skill and agent graph
- understand the harness without remembering every file
- select nodes or flows
- later edit safely in timestamped work packages
- later test changes with local Codex agents
- later apply approved changes back to the connected source

## Current Roadmap

```text
[M1 Source And Graph Contract]
   |
   v
[M2 Read-Only Visual Map V1]
   |
   v
[M2.5A Graph Engine Reset]
   |
   v
[M2.5B Visual Parity And Workbench Shell UX]
   |
   v
[M2.6 Real Codex Source Readiness]
   |
   v
[M3 Timestamped Work Package Safety Core]
   |
   v
[M4 Node And Flow Editing]
   |
   v
[M5 Codex Agent Scenario Test And Path Trace]
   |
   v
[M6 Approved Apply-Back And Recovery]
   |
   v
[M7 Personal Codex Workbench Beta Loop]
```

## M1: Source And Graph Contract

Output:

- `docs/workbench-source-contract.md`

Purpose:

- define what a Codex-home-like source is
- define skill and agent nodes
- define detected edges
- define stable node identity
- keep hooks, runtime, editing, and tests out of the first contract

Status:

- Done enough for M2.

## M2: Read-Only Visual Map V1

Output:

- official `src/workbench/` source area
- read-only server and graph API
- first static Workbench UI
- fixture-backed tests

Purpose:

- replace the old POC path
- load global, local, or custom Codex-home-like sources
- render discovered skills, agents, and detected edges
- inspect nodes without any write path

Status:

- Done enough to expose UI problems.

## M2.5A: Graph Engine Reset

Output:

- Cytoscape-based graph engine in the static Workbench UI
- circular skill and agent nodes
- working pan, zoom, fit, minimap, node selection, and inspector
- snapshot commit before the rebuild and a follow-up graph engine commit

Purpose:

- replace the fragile hand-built graph camera
- move away from card-shaped nodes
- create a usable graph baseline before deeper UX work

Status:

- Current baseline.

Not this milestone:

- full visual parity with the reference image
- real global source polish
- editing
- work packages
- agent tests

## M2.5B: Visual Parity And Workbench Shell UX

Output:

- accepted screen contract for the whole Workbench shell
- polished top bar, icon rail, source panel, graph canvas, minimap, inspector, empty state, error state, and responsive drawer behavior
- Browser screenshot evidence for desktop and narrow widths

Purpose:

- make the Workbench feel like the accepted reference direction
- treat the full product UX as the target, not only the graph
- stop visual drift before adding editing or testing behavior

Status:

- Next milestone to brainstorm.

Not this milestone:

- real source scale decisions beyond what is needed for visual checks
- editing files
- work package creation
- apply-back
- agent-run or scenario-test flows

## M2.6: Real Codex Source Readiness

Output:

- verified loading for real `~/.codex`
- verified loading for local repo `.codex` when present
- verified custom source behavior
- large-graph usability notes for filters, fit, search, grouping, and performance

Purpose:

- prove the map works on the user's actual local Codex harness, not only fixtures
- decide what the read-only map needs before editing starts

Status:

- After M2.5B.

Not this milestone:

- changing live files
- applying patches
- running Codex agents from the Workbench

## M3: Timestamped Work Package Safety Core

Output:

- a Workbench-owned timestamped work package format
- copied source snapshots
- selected node or flow references
- proposed change metadata
- stale-source and approval fields

Purpose:

- create the safe layer before any edit UI writes to live files

Status:

- Do not start until M2.5B and M2.6 are good enough.

## Later Milestones

M4 adds editing inside work packages.

M5 adds Codex agent scenario tests and visual path traces.

M6 adds approved apply-back with recovery.

M7 proves the full personal beta loop before public packaging.

## Current Recommendation

Start `ea-brainstorming` on:

- `M2.5B: Visual Parity And Workbench Shell UX`

The next discussion should decide the UX frame before implementation:

- first screen structure
- top bar actions
- left rail meaning
- source panel behavior
- graph canvas proportions
- inspector priority
- responsive behavior
- Browser screenshot acceptance bar
