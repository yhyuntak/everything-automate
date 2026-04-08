---
name: planning
description: Turn a clear direction into a file-based plan that `$execute` can follow.
argument-hint: "<task, approved direction, or implementation request>"
---

# planning

Use this when the direction is clear enough and the user now wants execution planning.

## Purpose

`planning` is an execution-prep skill.

Its job is to:

- turn a clear direction into a file-based plan
- lock the task goal
- lock scope and non-goals
- lock the design direction at the right level
- choose a test strategy
- write a plan that `$execute` can follow without guessing

`planning` is not:

- brainstorming
- implementation
- code writing
- a place to dump long code examples

## Position In The Main Flow

```text
$brainstorming
  -> direction becomes clear enough
  -> $planning
  -> $execute
  -> $qa
  -> commit
```

If the direction is still fuzzy, stop and go back to `$brainstorming`.

## Use When

Use `planning` when:

- the user wants a real execution plan
- a file-based plan would help
- the work should move toward implementation
- scope is clear enough to lock
- the user needs ACs, TCs, and test strategy before coding

## Do Not Use When

Do **not** use `planning` when:

- the user is still choosing between broad directions
- the request is still mostly idea shaping
- the user only wants comparison or thought cleanup
- the user already has an approved plan and wants implementation

If any of the above are true, move to `$brainstorming` or `$execute` instead.

## Interaction Policy

`planning` is mostly non-interactive.

Ask the user questions only when needed.

That usually means:

- the goal is still unclear
- scope is still unclear
- a boundary matters and the repo cannot answer it

Do not keep asking for confirmation in the middle once the plan is clear enough to write.

## Core Flow

```text
input
  -> quick context check
  -> explore repo if needed
  -> clarify if still unclear
  -> lock task goal
  -> lock scope / non-goals
  -> lock design direction
  -> choose test strategy
  -> write Task
     -> write ACs
        -> attach TCs
  -> use plan-arch if needed
  -> revise if needed
  -> use plan-devil if needed
  -> revise if needed
  -> write execute handoff
  -> user approval
```

## Step Meanings

### 1. Quick Context Check

Start by restating:

- what the task is
- what outcome is wanted
- what is already known
- what is still unknown

Keep this short.

### 2. Explore Repo If Needed

Use `explorer` only when repo facts matter.

Use it to find:

- current patterns
- likely files
- likely tests
- important constraints already in the codebase

Do not ask the user for repo facts that the repo can tell you.

### 3. Clarify If Still Unclear

Ask the user only if important ambiguity remains after the context check and any needed exploration.

Ask one strong question at a time.

### 4. Lock Task Goal

Write down what this task should change when it is done.

This is the "what becomes true after the work" section.

### 5. Lock Scope And Non-Goals

Make clear:

- what is in scope now
- what is out of scope now
- what boundaries `execute` should not cross silently

### 6. Lock Design Direction

Stay at the right level.

Planning should describe:

- the main design direction
- the parts of the system that matter
- the pattern or shape to follow
- what should stay stable

Planning should **not** turn into long code examples or detailed implementation drafts.

### 7. Choose Test Strategy

Every real execution plan needs a test strategy.

Choose the best fit for the task:

- `docs-only`
- `unit-first`
- `integration-first`
- `backend verification`
- `web E2E`
- `mixed`

The chosen test strategy should make sense for the kind of project and change.

### 8. Write `Task -> AC -> TC`

This is the backbone of the plan.

```text
Task
  -> AC1
     -> TC1
     -> TC2
  -> AC2
     -> TC1
  -> AC3
     -> TC1
     -> TC2
```

Meaning:

- `Task`
  the whole piece of work
- `AC`
  what must be true for that part to count as done
- `TC`
  how that AC will be tested or checked

Keep ACs concrete.
Keep TCs tied to their ACs.

### 9. Use `plan-arch` If Needed

Use `plan-arch` when:

- the design direction has real tradeoffs
- the task shape is big enough that structure matters
- the `Task -> AC -> TC` structure may be weak
- the test strategy may not fit the work

`plan-arch` is not required for every plan.

### 10. Use `plan-devil` If Needed

Use `plan-devil` when:

- the risk is high
- the ACs still feel weak
- the TCs feel weak or missing
- the handoff may force `$execute` to guess
- the chosen test strategy feels too weak

`plan-devil` is also not required for every plan.

### 11. Write Execute Handoff

End the plan with a simple block that `$execute` can read.

## Required Plan Output

Every plan should contain:

- task summary
- desired outcome
- in-scope
- non-goals
- design direction
- test strategy
- one task with ACs and TCs
- execution order
- open risks
- execute handoff

## Plan Artifact Path

During local Everything Automate development, write plan artifacts to:

- `.everything-automate/plans/{YYYY-MM-DD}-{slug}.md`

If a caller already provides a plan path, use that path.

## Execute Handoff

Keep the handoff simple and useful.

Every approved plan must end with:

- `task_id`
- `plan_path`
- `approval_state`
- `execution_unit`
- `test_strategy`
- `open_risks`

Default `execution_unit` is `AC`.

## Output Shape

Use a structure like this:

```text
Task Summary
Desired Outcome
In Scope
Non-Goals
Design Direction
Test Strategy
Task
  -> ACs
     -> TCs
Execution Order
Open Risks
Execute Handoff
```

## Rules

- Do not brainstorm inside `planning`.
- Do not implement inside `planning`.
- Do not dump long code-level examples.
- Do not leave test strategy implicit.
- Do not leave ACs without TCs.
- Do not hand off to `$execute` if the plan still forces guessing.
- Use simple English.
- Put the main planning conclusion first when reporting the result.
- Keep plan explanations clean and easy to scan.
- If you explain a flow, use a real ASCII flow chart instead of a simple arrow list.

## Completion

`planning` is complete only when:

- the direction is clear enough for execution
- the plan file exists
- scope and non-goals are visible
- design direction is clear enough
- test strategy is explicit
- `Task -> AC -> TC` is present and usable
- the execute handoff is present
- the user approves the plan when approval is needed
