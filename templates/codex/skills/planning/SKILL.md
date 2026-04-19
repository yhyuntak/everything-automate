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
- read relevant accepted decisions when a settled boundary already exists
- create or update a decision note when a meaningful choice becomes accepted during planning
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
  -> read relevant accepted decisions if needed
  -> explore repo if needed
  -> clarify if still unclear
  -> lock task goal
  -> lock scope / non-goals
  -> lock design direction
  -> choose test strategy
  -> if a meaningful choice becomes settled
     -> create or update decision note
  -> write Task
     -> write ACs
        -> attach TCs
  -> use plan-arch for non-trivial plans
  -> revise if needed
  -> use plan-devil for non-trivial plans
  -> revise if needed
  -> write execute handoff
  -> report plan and handoff summary
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

### 2. Read Relevant Accepted Decisions

Before writing a new plan, check whether a settled boundary already exists in:

- `.everything-automate/decisions/`

Read only the decision notes that matter to the current task.

Use accepted decisions to avoid reopening already-settled choices.

Do not read the full decision log when only one or two notes matter.

### 3. Explore Repo If Needed

Use `explorer` only when repo facts matter.

Use it to find:

- current patterns
- likely files
- likely tests
- important constraints already in the codebase

Do not ask the user for repo facts that the repo can tell you.

### 4. Clarify If Still Unclear

Ask the user only if important ambiguity remains after the context check, any needed decision-note reads, and any needed exploration.

Ask one strong question at a time.

### 5. Lock Task Goal

Write down what this task should change when it is done.

This is the "what becomes true after the work" section.

### 6. Lock Scope And Non-Goals

Make clear:

- what is in scope now
- what is out of scope now
- what boundaries `execute` should not cross silently

### 7. Lock Design Direction

Stay at the right level.

Planning should describe:

- the main design direction
- the parts of the system that matter
- the pattern or shape to follow
- what should stay stable

Planning should **not** turn into long code examples or detailed implementation drafts.

### 8. Choose Test Strategy

Every real execution plan needs a test strategy.

Choose the best fit for the task:

- `docs-only`
- `unit-first`
- `integration-first`
- `backend verification`
- `web E2E`
- `mixed`

The chosen test strategy should make sense for the kind of project and change.

### 9. Create Or Update Decision Notes When Needed

`planning` is the main stage that writes decision notes.

Write or update a decision note when:

- a meaningful design or workflow choice becomes accepted
- future sessions would likely need to remember this choice
- the choice is broader than one small implementation detail

Do **not** write a decision note for:

- still-open brainstorming choices
- tiny implementation details
- information that only matters inside one short-lived plan

If an accepted decision is changed later, update or supersede the old decision note instead of silently drifting.

### 10. Write `Task -> AC -> TC`

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
  the evidence that the AC is done

Keep ACs concrete.
Keep TCs tied to their ACs.

#### TC Writing Policy

Write TCs before `$execute`.
`$execute` runs the TC checklist; it should not have to invent better TCs.

Use result-first TCs by default.

That means:

- test or check the result, not private implementation details
- prefer public behavior, outputs, state changes, files, UI changes, and errors
- for code work, use real internal code paths when practical
- mock or fake external boundaries such as network, DB, file system, third-party APIs, time, and paid services
- avoid TCs that only prove private method calls or internal call order, unless that interaction is the public contract

TDD is useful, but it is not mandatory.

Choose the earliest useful verification loop:

- `test-first` when an automated test is practical and valuable
- `check-first` when a UI, doc, config, or scenario check fits better
- `verify-after` when the work is exploratory or visual, but still needs fresh evidence before completion

Every TC should answer:

- what result proves this AC is done?
- what failure would this TC catch?
- is this the cheapest reliable check?
- can `$execute` run or perform it without guessing?

Use this routing guide:

- code behavior
  - automated behavior test, CLI check, fixture check, output check, state check, or error check
- UI behavior
  - component check, browser check, Playwright-style flow, or manual visual check
  - use browser checks when user flow, responsive layout, focus, keyboard, hover, asset loading, canvas, text overflow, or overlap risk matters
  - do not require Playwright for every small UI change
- docs or content
  - doc checklist, link/index check, wording consistency check, or reader-flow check
- config or install
  - parse check, setup check, doctor check, startup check, or smoke check
- runtime or state
  - artifact check, state transition check, resume/cancel check, or terminal summary check
- prompt, skill, or agent behavior
  - scenario check, routing check, refusal check, or handoff check

### 11. Use Planning Reviewers

For non-trivial plans, use both `plan-arch` and `plan-devil` by default.

Non-trivial plans include:

- workflow, runtime, state, skill, or agent changes
- UI behavior changes
- multi-file behavior changes
- unclear test strategy
- AC/TC shape that could force `$execute` to guess

Tiny low-risk work may skip them.

Examples:

- typo fixes
- link fixes
- narrow copy edits
- very small changes with obvious scope, TC, test strategy, and handoff

Use `plan-arch` to check structure and fit.

Use `plan-arch` when:

- the design direction has real tradeoffs
- the task shape is big enough that structure matters
- the `Task -> AC -> TC` structure may be weak
- the test strategy may not fit the work
- TC routing may not fit the work
- UI/browser verification may be under- or over-used
- `$execute` may not be able to follow the plan without guessing

Use `plan-devil` to attack failure risk.

Use `plan-devil` when:

- the risk is high
- the ACs still feel weak
- the TCs feel weak or missing
- TCs check implementation details instead of results
- the plan may over-test or under-test the work
- the handoff may force `$execute` to guess
- the chosen test strategy feels too weak

For tiny low-risk work, explain briefly why reviewers were skipped.

### 12. Write Execute Handoff

End the plan with a simple block that `$execute` can read.

### 13. Report Plan Before Approval

Before asking for approval, give the user a short clean report of the plan.

That report should confirm:

- the main planning conclusion
- the main scope and non-goals
- the design direction
- the test strategy
- the execute handoff
- the open risks

Do not paste the full plan back when a shorter report is enough.

The goal is to let the user confirm the handoff shape before execution starts.

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

If planning settled a meaningful long-lived choice, update or create the related decision note before finishing.

## Plan Artifact Path

During local Everything Automate development, write plan artifacts to:

- `.everything-automate/plans/{YYYY-MM-DD}-{slug}.md`

If a caller already provides a plan path, use that path.

## Decision Artifact Path

During local Everything Automate development, write decision notes to:

- `.everything-automate/decisions/{decision-id}-{slug}.md`

Use short stable ids such as `DEC-001`.

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

## User Report Before Approval

Before approval, summarize the plan in a way that is easier to scan than the full plan file.

That summary should include:

- what the work will change
- what is in scope now
- what stays out of scope now
- the test strategy
- the execute handoff fields
- the main open risks

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
- Do not skip the short user-facing plan report before asking for approval.
- Do not paste the full plan file back when a clean summary is enough.
- Do not create decision notes for every tiny choice.
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
- the user has seen a clean plan summary before approval
- relevant accepted decisions were read when they mattered
- any new meaningful accepted choice was written to a decision note when needed
- the user approves the plan when approval is needed
