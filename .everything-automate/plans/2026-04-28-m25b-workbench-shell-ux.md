---
title: M2.5B Workbench Shell UX
task_id: m25b-workbench-shell-ux-2026-04-28
plan_path: .everything-automate/plans/2026-04-28-m25b-workbench-shell-ux.md
approval_state: approved
source_brainstorming: .everything-automate/state/brainstorming/archive/20260428-003245-m25b-workbench-shell-ux.md
source_roadmap: docs/workbench-roadmap.md
test_strategy: mixed
execution_unit: AC
---

# M2.5B Workbench Shell UX

## Task Summary

Polish the current read-only Codex Workbench shell so the first desktop screen looks and behaves like the accepted reference direction.

This is a visual and interaction UX pass over the existing M2.5A Cytoscape baseline.

## Desired Outcome

The Workbench feels like one coherent graph workbench:

- desktop first screen has the reference structure
- graph is visually dominant
- skill and agent nodes look intentional, not provisional
- side panels are useful and ordered
- selected-node inspector is readable
- narrow width does not break the graph
- only real read-only controls are visible

## In Scope

- `src/workbench/static/index.html`
- `src/workbench/static/styles.css`
- `src/workbench/static/app.js`
- source panel content structure, labels, density, and status area
- inspector content structure and selected-node hierarchy
- topbar and read-only action layout
- left icon rail as visual shell with Graph Map as the only active item
- Cytoscape node and edge visual styling
- desktop loaded graph screenshot state
- desktop selected-node inspector screenshot state
- narrow-width graph-first drawer behavior
- one empty or error screenshot state
- docs updates if visible Workbench behavior changes

## Non-Goals

- no graph API changes
- no node or edge schema changes
- no new graph data types
- no hooks, runtime, setup, or non-Codex provider nodes
- no real global `~/.codex` scale work beyond visual fixture checks
- no editing
- no work packages
- no apply-back
- no export
- no agent-run or scenario-test controls
- no fake buttons for future features
- no persistent saved layout state

## Design Direction

Keep Cytoscape as the graph engine.

Make the static shell closer to the reference desktop image:

```text
[Topbar]
   |
   v
[Icon Rail] [Sources + Filters] [Graph Canvas + Minimap] [Inspector]
```

Use the current fixture source for visual checks.

The graph should use:

- green circular skill nodes
- blue circular agent nodes
- icon inside each node
- label below each node
- stronger selected-node ring
- readable edges with enough contrast
- central/high-degree node emphasis
- non-noisy hover or focus highlighting

The source panel should show:

- Global, Local, Custom tabs
- current source card/status
- load/refresh affordance only where real
- Skills filter section
- Agents filter section
- compact visible node rows or counts
- clear loaded/error/empty status

The inspector should show:

- selected node icon, name, kind
- identity/path/aliases first
- incoming and outgoing detected edges second
- source preview last
- empty state when no node is selected

The icon rail should not become real navigation.
It should show Graph Map as active and hide, disable, or visually mute future items.

Responsive behavior should fold the same screen:

- graph remains the primary area
- Sources becomes a drawer
- Inspector becomes a drawer or sheet
- topbar remains usable
- graph controls do not overlap important content

## Test Strategy

Use a mixed strategy:

- syntax checks for changed frontend JS and Python entry points
- existing Workbench unit tests for source/graph/server behavior
- static search checks to prevent fake future controls
- Browser Use screenshot checks for visual states
- Browser Use interaction checks for fit, zoom, node click, hover/focus, filters, and drawers

## Task

Implement M2.5B Workbench Shell UX.

### AC1: Desktop Shell Matches The Reference Structure

The first loaded desktop screen has the same structural shape as the reference image.

It should show a topbar, visual icon rail, source/filter panel, graph-dominant canvas, minimap, and inspector.

#### TC1.1

Open:

```text
http://127.0.0.1:8765/?source=custom&path=/Users/yoohyuntak/.codex/worktrees/42b3/everything-automate/tests/fixtures/workbench/custom-codex-home
```

Use Browser screenshot.

Pass when the first loaded desktop screen visibly contains:

- topbar
- left visual rail
- source/filter panel
- graph canvas with grid
- minimap
- right inspector
- graph-dominant center area

#### TC1.2

Check the DOM or visible text for fake future actions.

Pass when there are no live controls for:

```text
Export
Edit
Apply
Test
Work package
Agent run
Scenario test
```

Historical docs may mention these terms only as non-goals.

#### TC1.3

Check the left icon rail.

Pass when Graph Map is the only active meaning, and other future rail items are absent, disabled, or visually muted.

### AC2: Graph Nodes Look Like A Polished Map

The graph no longer looks like a provisional Cytoscape demo.

Nodes, labels, edges, selection, and hover/focus states should match the reference direction.

#### TC2.1

Use Browser screenshot on the loaded fixture graph.

Pass when:

- skill nodes are green circular nodes
- agent nodes are blue circular nodes
- each node has an icon-like center mark
- labels are below nodes
- selected node has stronger visual weight
- edges are visible but not noisy
- high-degree nodes feel more central or visually important

#### TC2.2

Click a node in Browser.

Pass when:

- the node becomes selected
- the selected node gets a stronger ring or visual emphasis
- connected edges or neighborhood focus become clearer
- the inspector updates to the clicked node

#### TC2.3

Use zoom in, zoom out, and fit controls.

Pass when:

- zoom value changes after zoom in/out
- fit recenters the graph without `NaN` or blank canvas behavior
- graph controls remain readable and do not resize the layout

### AC3: Source Panel Is Reference-Like And Useful

The source panel should feel like a real left work panel, not a rough form.

#### TC3.1

Use Browser screenshot on the loaded fixture graph.

Pass when the source panel shows:

- Global, Local, Custom source choice
- current source card or status
- load or refresh control only where real
- Skills section
- Agents section
- compact node rows or counts
- clear loaded/error/empty status

#### TC3.2

Toggle Skills and Agents filters.

Pass when:

- the graph updates visibly
- visible node and edge counts or status update
- the panel does not visually collapse or overlap

#### TC3.3

Load an invalid custom source.

Pass when:

- the error state is visible and intentional
- the graph area does not break
- no stale successful source state is presented as current

### AC4: Inspector Prioritizes Node Identity And Relationships

The right inspector should read like the reference direction.

It should make the selected node easy to understand.

#### TC4.1

Click a node and inspect the right panel.

Pass when the inspector shows, in this order:

- selected node icon, name, and kind
- selection identity or display id
- path
- aliases
- degree or simple graph facts
- incoming detected edges
- outgoing detected edges
- source preview

#### TC4.2

Clear selection or reload into no-selection state.

Pass when the inspector empty state is calm and useful, without suggesting edit/test/apply actions.

### AC5: Narrow Width Uses Graph-First Drawers

The Workbench must not collapse into a broken one-column layout.

At narrow width, the graph remains primary and panels fold away.

#### TC5.1

Use Browser screenshot at a narrow viewport or the current in-app browser narrow size.

Pass when:

- graph remains visible and usable
- source panel is hidden behind a Sources drawer or equivalent
- inspector is hidden until node selection or inspector action
- topbar actions remain reachable
- graph controls do not overlap node labels badly

#### TC5.2

Open Sources and Inspector in narrow width.

Pass when:

- each drawer/sheet opens above the graph without layout breakage
- backdrop and close behavior work
- the graph returns to usable state after closing

### AC6: Checks And Docs Stay Consistent

The visual redesign should keep existing behavior healthy and docs honest.

#### TC6.1

Run:

```bash
python3 -m unittest discover -s tests -p 'test_workbench*.py'
```

Pass when all tests pass.

#### TC6.2

Run:

```bash
python3 -m py_compile src/workbench/server.py src/workbench/graph.py scripts/ea_workbench.py
node --check src/workbench/static/app.js
git diff --check
```

Pass when all checks pass.

#### TC6.3

Search current UI/docs for accidental live future controls:

```bash
rg -n "Export|export|Edit|edit|Apply|apply|Test|test|Work package|work package|Agent run|agent run|Scenario test|scenario test" src/workbench/static docs/workbench-implementation-plan.md docs/workflow-map.md docs/workbench-roadmap.md README.md
```

Pass when matches are either absent from live UI or clearly documented as non-goals or future milestones.

#### TC6.4

If visible behavior changed enough to make docs stale, update:

- `docs/workbench-implementation-plan.md`
- `docs/workflow-map.md`
- `docs/workbench-roadmap.md` only if the milestone meaning changes

Pass when docs describe the current read-only M2.5B behavior without claiming editing, apply-back, agent-run, export, work packages, live force simulation, or saved layouts.

## Execution Order

```text
[Review current shell]
   |
   v
[Polish desktop shell]
   |
   v
[Polish graph node visuals]
   |
   v
[Polish source panel]
   |
   v
[Polish inspector]
   |
   v
[Fix narrow-width drawers]
   |
   v
[Run checks and Browser screenshots]
   |
   +---- fail ----> [Revise focused area]
   |
   v
[Ready for QA]
```

## Open Risks

- Visual parity is partly judgment-based, so Browser screenshots are required evidence.
- The in-app browser viewport may not exactly match the reference image size.
- Fixture data is small. M2.6 still needs real-source scale checks later.
- Cytoscape canvas rendering is harder to assert with DOM-only tests.
- Panel content changes can accidentally imply future actions; keep copy read-only.

## EA Execute Handoff

- `task_id`: `m25b-workbench-shell-ux-2026-04-28`
- `plan_path`: `.everything-automate/plans/2026-04-28-m25b-workbench-shell-ux.md`
- `approval_state`: `pending_user_approval`
- `execution_unit`: `AC`
- `test_strategy`: `mixed`
- `open_risks`: visual parity is screenshot-judged; fixture data is small; do not add fake future controls; keep graph API and source contract stable
