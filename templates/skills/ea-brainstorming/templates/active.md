---
mode: brainstorming
status: active
stage: code-scan
version: 1
updated_at: YYYY-MM-DDTHH:MM:SS+09:00
owner: user
source_milestone: [path or short source]
source_milestone_name: [chosen code milestone name]
source_north_star: [path to locked North Star archive, if available]
source_north_star_title: [short title, if available]
read_test_required: true
read_test_agents: 3
read_test_style: independent-interpretation
read_test_default_model: gpt-5.4-mini
read_test_default_reasoning: medium
---

# Brainstorming State

## Source Milestone
[The chosen code-related milestone. This is the boundary.]

## Boundary
[What belongs inside this milestone, and what must not expand it.]

## Codebase Context
[Relevant files, modules, patterns, and constraints found during read-only exploration.]

## Senior Engineer Scan
[Important lenses, risks, tradeoffs, and focused questions surfaced by the senior engineer perspective.]

## Current Design Direction
[The working design direction being shaped with the user.]

## Decisions
[Settled design choices and why the user accepted them.]

## Learning Notes
[Short notes that help the user understand important concepts or tradeoffs for this milestone.]

## Open Questions
[Questions that still block a good planning handoff.]

## Parking Lot
[Useful ideas outside the current milestone.]

## Integrated Design Note
[The planning-readable final design note once accepted.]

## Planning Handoff
[What `$ea-planning` should read next, and what it should not guess.]

## Read-Test Notes
[Summaries of read-test results and divergence, if any.]

## Anchor Message
Brainstorming mode is active. Keep the discussion inside the chosen code milestone. Classify new ideas as Code Design Material, Learning Question, Decision, Open Question, or Parking Lot before following them. Do not implement or write an execution plan in this mode.
