---
name: brainstorming
description: Standalone idea-shaping workflow for early design thinking, option comparison, and scope clarification before planning.
argument-hint: "<idea, feature direction, or vague request>"
---

# brainstorming

Turn a vague idea into a clearer product or design direction before formal planning.

## Purpose

Use brainstorming when the user needs help shaping the work, not yet sequencing the work.

Brainstorming should:

- clarify user intent
- surface constraints and non-goals early
- explore multiple plausible directions
- recommend a direction with tradeoffs
- leave behind a clean design brief that can later feed `$planning`

Brainstorming is upstream of planning.
It is not implementation and it is not execution planning.

## Use When

- the user has an idea but not yet a concrete execution shape
- the user wants to compare approaches before planning
- the request is exploratory, product-oriented, or design-oriented
- scope feels fuzzy enough that planning would be premature
- the user explicitly asks to brainstorm

## Do Not Use When

- the request is already concrete enough for `$planning`
- the user already has a clear approved design and wants an execution plan
- the task is only to review an existing plan

## Interaction Policy

Brainstorming is interactive by default.

- Ask one question at a time.
- Prefer high-leverage questions over broad questionnaires.
- Do not ask the user for codebase facts that can be explored directly.
- If the request is brownfield, ground yourself first with `explorer`.
- Once enough clarity exists, stop interviewing and move into option generation and recommendation.

## Default Flow

```text
request
  -> quick context intake
  -> explorer if codebase grounding helps
  -> one-question-at-a-time clarification
  -> identify intent / constraints / non-goals
  -> propose 2-3 directions
  -> compare tradeoffs
  -> recommend one direction
  -> user reacts
  -> revise if needed
  -> finalize brainstorm brief
  -> recommend next step: stop or move to $planning
```

## Rules

- Do not implement during brainstorming.
- Do not jump into execution-order details too early.
- Clarify why the user wants the change before narrowing how to build it.
- Ask about scope boundaries and non-goals before polishing solution details.
- Explore the codebase before asking technical questions the repository can answer.
- Offer 2-3 options unless the space is obviously binary or heavily constrained.
- Lead with your recommended option and explain why.
- Keep the conversation collaborative, but converge toward a final recommendation.

## Suggested Question Order

When clarification is needed, prefer this order:

1. intent
2. desired outcome
3. scope
4. non-goals
5. constraints
6. decision boundaries

Do not mechanically ask all categories if the answer is already discoverable or implied with high confidence.

## Output

Brainstorming should end with a concise brainstorm brief containing:

- problem or opportunity statement
- user intent
- desired outcome
- in-scope
- non-goals
- constraints
- options considered
- recommended direction
- open questions, if any
- recommended next step

## Handoff Boundary

Brainstorming does not produce the final execution plan.

If the user wants to proceed after the direction is chosen:

```text
brainstorming
  -> approved direction
  -> $planning
```

If the user only wanted ideation or comparison, stop after the brainstorm brief.

## Completion

Brainstorming is complete when:

- the user understands the viable options
- one direction is recommended clearly
- scope and non-goals are visible enough to avoid premature planning mistakes
- the next step is explicit: stop, refine further, or move to `$planning`
