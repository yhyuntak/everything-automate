---
name: ea-blueprint
description: Turn a locked North Star into a buildable design spec before planning.
argument-hint: "<locked North Star artifact or blueprint request>"
---

# ea-blueprint

Use this skill after North Star and before planning.

`ea-blueprint` turns a locked North Star into a buildable design spec, then hands that design to planning.

## State

Use the single workspace active file:

- `.everything-automate/state/active.md`

Use the template at:

- `.codex/skills/ea-blueprint/templates/active.md`

Do not create mode-specific active files.

If `.everything-automate/state/active.md` already exists, read and continue from that file instead of creating a second active blueprint file.

If the existing active file belongs to another workflow or conflicts with the current blueprint session, stop and ask before overwriting it.

Accepted blueprint outputs archive under:

- `.everything-automate/state/blueprint/archive/`

When the blueprint is accepted, archive the active file as the accepted output and then remove `.everything-automate/state/active.md` so hooks return to no-op.

## v0 Target Kinds

Classify the North Star into one of these target kinds:

- `code-change`
- `milestone-roadmap`
- `harness-workflow`
- `docs-knowledge`
- `general`

Load one matching reference file by default:

- `code-change` -> `references/code-change.md`
- `milestone-roadmap` -> `references/milestone-roadmap.md`
- `harness-workflow` -> `references/harness-workflow.md`
- `docs-knowledge` -> `references/docs-knowledge.md`
- `general` -> `references/general.md`

## Blueprint Frame

Use this classification frame while drafting:

- `Blueprint Design Material`
- `Open Question`
- `Handoff Note`
- `Parking Lot`

## Acceptance Gates

Before accepting a blueprint, run two separate gates:

1. `Interpretation Read-Test`
2. `Design Review`

`Interpretation Read-Test` is interpretation-only. Use 3 agents to confirm they read the same target, scope, and design shape from the blueprint. Do not ask them to judge design quality.

`Design Review` is design-only. Use 1 `GPT-5.4` agent with `xhigh` reasoning to check the design itself. Do not ask it for TC breakdowns, file order, worker assignment, or test command sequences.

If either gate finds a problem, feed the feedback back into the blueprint and rerun the needed gate before acceptance.

## Boundary

Blueprint owns design shape, architecture and boundaries, ownership, data and control flow, abstraction choices, and tradeoffs.

Planning owns AC and TC shape, execution order, file-level work, worker handoff, and verification details.

`Execution-Shape Sufficiency` means the design is clear enough on components, boundaries, ownership, flows, and decisions that planning does not invent the core shape. It does not require TC slices, file edit order, worker assignment, or verification command details.
