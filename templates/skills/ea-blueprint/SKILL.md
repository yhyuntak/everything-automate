---
name: ea-blueprint
description: Turn one chosen milestone into a buildable design spec before planning.
argument-hint: "<locked milestone artifact or blueprint request>"
---

# ea-blueprint

Use this after Milestone and before Planning.

`ea-blueprint` turns one chosen milestone into a buildable design spec, then hands that design to planning.

## State

Use the single workspace active file:

- `.everything-automate/state/active.md`

Use the template at:

- `.codex/skills/ea-blueprint/templates/active.md`

Do not create mode-specific active files.

If `.everything-automate/state/active.md` already exists and belongs to Blueprint, continue from that file instead of creating a second blueprint file.

If the existing active file belongs to another workflow or conflicts with the current blueprint session, stop and ask before overwriting it.

Accepted blueprint outputs archive under:

- `.everything-automate/state/blueprint/archive/`

When the blueprint is accepted, archive the active file as the accepted blueprint output and then remove `.everything-automate/state/active.md` so hooks return to no-op.

## Inputs

Blueprint starts from:

- one chosen milestone from the locked milestone roadmap

It may also read:

- the parent locked North Star archive

The milestone is the primary input.
The parent North Star is supporting context only.

Blueprint should not reopen the final goal unless the user explicitly moves back a stage.

## v0 Target Kinds

Classify the chosen milestone into one of these target kinds:

- `code-change`
- `harness-workflow`
- `docs-knowledge`
- `general`

`docs-knowledge` includes more than maintenance docs. Use it for documentation, guides, research summaries, comparison analyses, decision reports, audit-style writeups, and other reader-facing artifacts where the main output is a knowledge artifact rather than a code change.

Load one matching reference file by default:

- `code-change` -> `references/code-change.md`
- `harness-workflow` -> `references/harness-workflow.md`
- `docs-knowledge` -> `references/docs-knowledge.md`
- `general` -> `references/general.md`

Only load extra reference files when the primary reference is not enough.

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

Blueprint owns:

- design shape
- architecture and boundaries
- ownership
- data and control flow
- abstraction choices
- tradeoffs

Planning owns:

- AC and TC shape
- execution order
- file-level work
- worker handoff
- verification details

`Execution-Shape Sufficiency` means the design is clear enough on components, boundaries, ownership, flows, and decisions that planning does not invent the core shape. It does not require TC slices, file edit order, worker assignment, or verification command details.
