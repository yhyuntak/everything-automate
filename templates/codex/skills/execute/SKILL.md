---
name: execute
description: C-lite execution workflow that consumes an approved plan handoff, works AC-first, and loops through execute, verify, decide, and fix with bounded retry and explicit terminal outcomes.
argument-hint: "[plan path or approved task]"
---

# execute

Consume an approved planning handoff and carry the work to verified completion without reopening upstream design decisions.

## Purpose

`execute` is the primary execution surface after `$planning`.

Its job is to:

- consume an approved plan handoff
- respect planning decisions instead of replanning inside execution
- work AC-first
- require fresh evidence before completion
- keep retry, blocker, and terminal semantics explicit
- leave a usable progress or terminal summary

## Use When

- an approved plan artifact already exists
- the handoff block is present and readable
- acceptance criteria and verification steps are concrete enough to execute
- the user wants implementation, not further ideation or planning

## Do Not Use When

- direction is still vague
- non-goals or decision boundaries are still unclear
- the plan is not explicitly approved
- verification steps are missing or too weak to prove completion
- the work needs brainstorming or planning first

If any of the above are true, stop and return to `$planning`.

## Core Contract

`execute` is a new canonical `C-lite` / Ralph-lite executor for `everything-automate`.

It uses prior systems as references, but it is not a renamed `implement` and it is not a full Ralph runtime.

```text
$planning
  -> approved handoff
  -> $execute
     -> readiness check
     -> context intake
     -> select AC
     -> execute
     -> verify
     -> decide
        -> pass: advance
        -> fail: fix and retry
        -> blocker: stop or escalate
        -> scope drift: fold in if still in-bound, otherwise return to planning
     -> repeat
  -> terminal or partial-progress summary
```

## Input Contract

`execute` consumes the approved plan handoff.

Minimum fields:

- `task_id`
- `plan_path`
- `approval_state`
- `execution_unit`
- `recommended_mode`
- `recommended_agents`
- `verification_lane`
- `open_risks`
- `problem_framing`
- `decision_drivers`
- `viable_options`
- `recommended_direction`
- explicit unit-of-work source: `AC` or `story->AC`

## Entry Readiness Check

Do not start real execution until all of the following are true:

- approved handoff is present
- approval is explicit
- execution unit is explicit
- acceptance criteria exist
- verification steps are concrete enough to run
- non-goals and decision boundaries are visible
- major open risks are understood
- no missing decision context would force execution to reopen already-set direction choices

If readiness fails:

- do not start implementation
- report the missing readiness items clearly
- return the work to `$planning`

## Execution Rules

- Treat the approved plan as source of truth.
- Default unit of work is `AC`.
- Story-shaped work is allowed only if the approved input already resolves stories into verifiable ACs.
- Do not silently widen scope.
- Do not reopen chosen direction if planning already locked it.
- Use runtime/state helpers only as internal support, not as the main user workflow.

## Default Flow

### 1. Context Intake

Before touching code, restate:

- current task
- current AC
- relevant constraints
- relevant risks
- verification path for this AC

This is not replanning.
It is a short execution grounding pass.

### 2. Select the Next Unit

Pick the next unfinished AC.

Allowed statuses for a unit:

- `pending`
- `in_progress`
- `passed`
- `blocked`
- `failed_verification`

### 3. Execute

Implement only the work needed for the current AC.

If small discovered sub-work is still inside the current AC and inside existing non-goals and decision boundaries, it may be folded in.

If discovered work crosses boundaries, stop and return to `$planning`.

### 4. Verify

Fresh evidence is always required.

Preferred evidence includes:

- targeted tests
- build
- lint
- runtime checks
- focused manual verification when automated checks are insufficient

Read the evidence output.
Do not claim completion from expectation or intuition.

### 5. Decide

After each verification pass:

- `pass`
  - mark the AC complete
  - record what evidence proved it
  - move to the next AC
- `fail`
  - fix the issue and retry within bounds
- `blocked`
  - stop and report the blocker clearly
- `scope_drift`
  - if still in-bound, fold it into the current AC
  - otherwise stop and return to `$planning`

## Retry and Escalation

Retry is bounded.

Per AC:

- allow up to 3 fix-and-reverify cycles
- if the same verification failure keeps recurring without a materially new approach, stop escalating locally
- if evidence shows the plan itself is insufficient, return to `$planning`
- if the blocker is external, permission-based, or requirement-based, stop and report it

Do not loop forever.

## Reviewer Verification Floor

Fresh evidence is mandatory for every run.

Reviewer verification is:

- optional for low-risk, narrow changes
- required for high-risk or architecture-sensitive runs

Treat the following as reviewer-required by default:

- security-sensitive work
- auth, migrations, or public API changes
- architecture-shaping changes
- broad multi-file changes where local evidence alone is too weak

## Progress and Summary Contract

Progress must stay visible at the AC level.

At minimum, execution should keep clear track of:

- current AC
- completed ACs
- blocked ACs
- failed-verification ACs
- latest evidence used

## Terminal Outcomes

### `complete`

Allowed only when:

- all required ACs are complete
- fresh evidence proves the result
- reviewer verification has happened when the run requires it

Completion summary must include:

- completed ACs
- evidence used
- remaining open risks, if any

### `cancelled`

Use when the user explicitly stops the run.

Cancellation summary must include:

- ACs already completed
- current AC at stop time
- latest evidence collected
- remaining work

### `failed`

Use when:

- bounded retry is exhausted
- a blocker prevents valid continuation
- execution cannot proceed without invalid assumptions

Failure summary must include:

- failed AC
- failure reason
- evidence gathered
- whether the next step should be retry, replanning, or external unblock

### `suspended/interrupted`

Use when the run stops without clean completion or declared failure.

Interruption summary must include:

- completed ACs
- current AC
- latest evidence state
- best resume point

## Constraints

- Do not brainstorm inside `execute`.
- Do not replan inside `execute`.
- Do not treat “looks done” as completion.
- Do not silently absorb boundary-crossing scope.
- Do not collapse `cancelled`, `failed`, and `suspended/interrupted` into one generic stop state.

## Completion

`execute` is complete only when:

- the approved handoff has been honored
- all required ACs are resolved
- fresh evidence supports the result
- the correct terminal outcome is explicit
- the run leaves a usable terminal or partial-progress summary
