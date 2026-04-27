---
title: M2.5C Graph Readability Refactor
task_id: m25c-graph-readability-refactor-2026-04-28
plan_path: .everything-automate/plans/2026-04-28-m25c-graph-readability-refactor.md
approval_state: approved
source_plan: .everything-automate/plans/2026-04-28-m25b-workbench-shell-ux.md
test_strategy: mixed
execution_unit: AC
---

# M2.5C Graph Readability Refactor

## Task Summary

Refactor the Workbench graph rendering so real global Codex sources stay readable.

The current graph can look acceptable for a tiny fixture, but global source scale creates node overlap, label overlap, and noisy edges.

## Desired Outcome

The Workbench graph should still look good for the small fixture and should not collapse for the global source.

Users should be able to see:

- which nodes matter most
- which node is selected
- which edges relate to the selected or hovered node
- enough labels to orient without turning the map into text noise

## In Scope

- graph layout policy
- dense graph mode
- node size scaling
- edge visual weight
- label visibility policy
- hover and selection focus behavior
- minimap consistency
- Browser Use checks for custom and global sources

## Non-Goals

- no graph API changes
- no backend schema changes
- no new node or edge types
- no editing controls
- no work package controls
- no agent-run or scenario-test controls
- no saved layout persistence
- no new graph library

## Design Direction

Keep Cytoscape as the graph engine.

Add a scale-aware view policy:

```text
[Load Graph]
   |
   v
[Count Nodes And Edges]
   |
   +-- small graph --> [show richer labels and normal edges]
   |
   +-- dense graph --> [larger spacing + lighter edges + fewer labels]
   |
   v
[Render]
   |
   v
[Hover Or Select]
   |
   v
[Show local neighborhood more strongly]
```

The dense graph mode should:

- use wider deterministic rings
- reduce node size extremes
- keep labels only for important nodes by default
- show labels for selected, hovered, and nearby nodes
- make default edges quiet
- make focused edges clear

## Test Strategy

Mixed:

- JavaScript syntax check
- existing Workbench unit tests
- Python compile check for stable entry points
- diff whitespace check
- Browser Use visual checks on both custom fixture and global source
- Browser Use interaction checks for fit, selection, filter, and dense graph readability

## Task

Implement M2.5C Graph Readability Refactor.

### AC1: Dense Graphs Do Not Collapse

Global source should not render as a pile of overlapping nodes and labels.

#### TC1.1

Open:

```text
http://127.0.0.1:8765/?source=global
```

Pass when the graph shows separated nodes with readable spacing, not a central pile.

#### TC1.2

Use Browser screenshot.

Pass when the default global view has quiet edges and only a useful subset of labels.

### AC2: Small Fixture Still Looks Like A Map

The custom fixture should keep the visual direction from M2.5B.

#### TC2.1

Open:

```text
http://127.0.0.1:8765/?source=custom&path=/Users/yoohyuntak/.codex/worktrees/42b3/everything-automate/tests/fixtures/workbench/custom-codex-home
```

Pass when all four nodes are visible, labels are visible, and the graph is not over-muted.

### AC3: Focus Makes Relationships Clear

Hover or selection should show the local neighborhood without redrawing the whole graph.

#### TC3.1

Click a visible node in the global graph.

Pass when:

- selected node is visually stronger
- unrelated nodes and edges are muted
- selected node label is visible
- inspector updates to that node

### AC4: Filters And Fit Still Work

Existing graph controls should not regress.

#### TC4.1

Toggle Agents off and on.

Pass when counts and visible graph update correctly.

#### TC4.2

Use zoom and fit.

Pass when the graph remains visible and does not blank or jump into a broken state.

### AC5: Checks Pass

#### TC5.1

Run:

```text
python3 -m unittest discover -s tests -p 'test_workbench*.py'
python3 -m py_compile src/workbench/server.py src/workbench/graph.py scripts/ea_workbench.py
node --check src/workbench/static/app.js
git diff --check
```

Pass when all checks succeed.

## Execution Order

1. Add graph view policy for small vs dense graphs.
2. Replace the fixed small-ring layout with spacing-aware deterministic rings.
3. Add dense edge and label classes.
4. Update overlay label policy.
5. Verify custom fixture.
6. Verify global source.
7. Run automated checks.

## Open Risks

- Dense graph layout is still deterministic and simple, not a full graph-layout solver.
- More advanced label collision may still be needed later for much larger graphs.
- This task should not add editing or scenario testing behavior.

## ea-execute Handoff

task_id: m25c-graph-readability-refactor-2026-04-28
plan_path: .everything-automate/plans/2026-04-28-m25c-graph-readability-refactor.md
approval_state: approved
execution_unit: AC
test_strategy: mixed
open_risks: deterministic dense layout may need a stronger solver later for much larger graphs
