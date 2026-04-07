---
name: execute
description: Carry an approved plan through implementation, verification, and completion with clear retry and stop rules.
argument-hint: "[plan path or approved task]"
---

# execute

Use an approved plan to finish the work without reopening decisions that planning already settled.

## Purpose

`execute` is the main work phase after `$planning`.

Its job is to:

- read an approved plan
- follow the plan instead of drifting back into planning
- work AC-first
- require fresh evidence before completion
- keep retry, blocker, and end-state rules explicit
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

## Core Flow

`execute` is the standard execution skill for `everything-automate`.
It is lighter than a full Ralph runtime, but stricter than a plain "implement this" step.

```text
$planning
  -> approved plan
  -> $execute
     -> entry check
     -> quick context recap
     -> select AC
     -> execute
     -> verify
     -> decide
        -> pass: advance
        -> fail: fix and retry
        -> blocker: stop or escalate
        -> scope drift: fold in if still in-bound, otherwise return to planning
     -> repeat
  -> final or partial summary
```

## Input Contract

`execute` reads the approved plan.

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

## Entry Check

Do not start real execution until all of the following are true:

- the approved plan is present
- approval is explicit
- execution unit is explicit
- acceptance criteria exist
- verification steps are concrete enough to run
- non-goals and decision boundaries are visible
- major open risks are understood
- no missing context would force execution to reopen decisions that planning already made

If the entry check fails:

- do not start implementation
- report the missing items clearly
- return the work to `$planning`

Typical entry failures include:

- `approval_state` is not `approved`
- the final handoff block exists but one or more required fields are missing
- acceptance criteria exist but are not concrete enough to execute
- verification steps are too weak to prove completion
- decision boundaries are missing, so execution would be forced to re-open planning

## If Entry Fails

If `execute` refuses to start, say so clearly instead of drifting into partial work.

At minimum, report:

- `status: refused`
- refusal reason
- missing or failing entry checks
- whether the work should return to `$planning`

Example shape:

```text
execute status: refused
reason: approval_state is draft
missing items:
  - explicit approval
next action:
  - return to $planning
```

Do not soften this into "can probably continue."
If the entry check fails, execution does not begin.

## Execution Rules

- Treat the approved plan as source of truth.
- Default unit of work is `AC`.
- Story-shaped work is allowed only if the approved input already resolves stories into verifiable ACs.
- Do not silently widen scope.
- Do not reopen chosen direction if planning already locked it.
- Use runtime/state helpers only as internal support, not as the main user workflow.

## Default Flow

### 1. Quick Context Recap

Before touching code, restate:

- current task
- current AC
- relevant constraints
- relevant risks
- verification path for this AC

This is not replanning.
It is a short recap before doing the work.

### 2. Pick the Next AC

Pick the next unfinished AC.

Allowed statuses for a unit:

- `pending`
- `in_progress`
- `passed`
- `blocked`
- `failed_verification`

### 3. Do the Work

Implement only the work needed for the current AC.

If small discovered sub-work is still inside the current AC and inside existing non-goals and decision boundaries, it may be folded in.

If discovered work crosses boundaries, stop and return to `$planning`.

### 4. Check the Result

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

## Branch Examples

Use the following examples to keep branch semantics concrete.

### `pass`

Example:

- current AC: add `setup` and `doctor` subcommands to the global installer
- evidence:
  - `python3 -m py_compile scripts/install_common.py scripts/install_global.py`
  - temp install root setup succeeds
  - temp install root doctor output succeeds

Decision:

```text
decide: pass
reason: required AC behavior is present and fresh evidence proves it
next action: mark the AC complete and move to the next AC
```

### `fail`

Example:

- current AC: doctor reports missing managed assets correctly
- evidence:
  - script runs
  - doctor crashes on a missing manifest path

Decision:

```text
decide: fail
reason: implementation exists but fresh evidence shows the AC is not satisfied
next action: fix and re-verify within retry bounds
```

Use `fail` when the current AC is still the right target and a local fix is plausible.

### `blocked`

Example:

- current AC: verify installed skill usability against the real global Codex environment
- evidence:
  - local files are present
  - the needed external environment, permission, or dependency is unavailable

Decision:

```text
decide: blocked
reason: valid continuation depends on an external prerequisite that local fixing cannot supply
next action: stop the run and report the blocker clearly
```

In v0, `blocked` stops the current run rather than skipping ahead to unrelated ACs.

### `scope_drift`

Example:

- current AC: add explicit refusal behavior when `approval_state != approved`
- discovered work:
  - a small wording fix in the same refusal section
    -> still in-bound
  - redesigning planning approval semantics across multiple upstream skills
    -> out-of-bound

Decision:

```text
decide: scope_drift
reason: newly discovered work crosses the current execution boundary
next action: return to $planning unless the discovered work is clearly still in-bound
```

## Retry and Escalation

Retry is bounded.

Per AC:

- allow up to 3 fix-and-reverify cycles
- if the same verification failure keeps recurring without a meaningfully new approach, stop retrying locally
- if evidence shows the plan itself is insufficient, return to `$planning`
- if the blocker is external, permission-based, or requirement-based, stop and report it

Do not loop forever.

### Retry / Escalation Example

Example:

- current AC: doctor reports missing managed assets correctly
- first attempt fails because doctor ignores one missing directory
- second attempt fails for the same reason with only cosmetic code changes
- third attempt still fails and no materially new approach exists

Decision:

```text
decide: failed
reason: bounded retry exhausted without a materially new path to success
next action: stop local retry and report whether replanning or external help is needed
```

If repeated failure reveals that the plan itself is underspecified, return to `$planning` instead of forcing `failed` immediately.

## Scope Drift Examples

### In-Bound Scope Drift

Example:

- current AC: install Codex skills into `~/.codex/skills/`
- discovered work: create the missing parent directory before copying files

Decision:

```text
scope_drift: in-bound
action: fold into the current AC
```

This is still in-bound because it is a small enabling step required to satisfy the same AC without changing the plan boundary.

### Out-of-Bound Scope Drift

Example:

- current AC: harden `execute` readiness and branch semantics
- discovered work: invent a new progress artifact format and wire it into runtime helpers

Decision:

```text
scope_drift: out-of-bound
action: stop execution and return to $planning
```

This is out-of-bound because it changes the next design slice rather than completing the current AC.

## When Reviewer Verification Is Required

Fresh evidence is mandatory for every run.

Reviewer verification is:

- optional for low-risk, narrow changes
- required for high-risk or architecture-sensitive runs

Treat the following as reviewer-required by default:

- security-sensitive work
- auth, migrations, or public API changes
- architecture-shaping changes
- broad multi-file changes where local evidence alone is too weak

## Progress and Summary

Progress must stay visible at the AC level.

At minimum, keep clear track of:

- current AC
- completed ACs
- blocked ACs
- failed-verification ACs
- latest evidence used

For v0, keep progress in a separate structured artifact rather than overloading run-level state.

Recommended artifact split:

```text
.everything-automate/state/tasks/{task_id}/loop-state.json
  -> run-level state only

.everything-automate/state/tasks/{task_id}/execute-progress.json
  -> AC-level progress

.everything-automate/state/tasks/{task_id}/terminal-summary.json
  -> final derived summary
```

### `execute-progress.json`

Treat `execute-progress.json` as the canonical AC-progress artifact.

Minimum top-level fields:

- `schema_version`
- `task_id`
- `run_id`
- `plan_path`
- `status`
- `current_ac`
- `completed_acs`
- `blocked_acs`
- `failed_verification_acs`
- `acs`
- `latest_evidence`
- `best_resume_point`
- `updated_at`

Minimum per-AC fields:

- `ac_id`
- `title`
- `status`
- `retry_count`
- `latest_evidence`

Artifact rules:

- update `execute-progress.json` in place as the run advances
- keep run lifecycle and terminal reason in `loop-state.json`
- keep AC progress and evidence snapshots in `execute-progress.json`
- keep a top-level cached `latest_evidence` pointer and the relevant per-AC evidence

### Partial-Progress Output

A partial-progress snapshot should make it obvious:

- which AC is active now
- which ACs are already complete
- whether any AC is blocked or failed verification
- what the latest evidence says
- where the next resume point is

Example shape:

```json
{
  "schema_version": 1,
  "task_id": "example-task",
  "run_id": "uuid",
  "plan_path": ".everything-automate/plans/example.md",
  "status": "in_progress",
  "current_ac": {
    "ac_id": "AC3",
    "title": "Define partial-progress output"
  },
  "completed_acs": ["AC1", "AC2"],
  "blocked_acs": [],
  "failed_verification_acs": [],
  "latest_evidence": {
    "ac_id": "AC3",
    "kind": "doc-review",
    "summary": "draft exists, final check pending"
  },
  "best_resume_point": "resume current AC from verify"
}
```

## End States

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

For v0, write end-state output to `terminal-summary.json`.

Rules:

- `terminal-summary.json` is derived from the final progress snapshot and final run-level state
- it is written only for:
  - `complete`
  - `cancelled`
  - `failed`
  - `suspended/interrupted`
- it must not replace `loop-state.json`
- it must not become a second live progress source during normal execution

## Constraints

- Do not brainstorm inside `execute`.
- Do not replan inside `execute`.
- Do not treat “looks done” as completion.
- Do not silently absorb boundary-crossing scope.
- Do not collapse `cancelled`, `failed`, and `suspended/interrupted` into one generic stop state.

## Completion

`execute` is complete only when:

- the approved plan has been honored
- all required ACs are resolved
- fresh evidence supports the result
- the correct terminal outcome is explicit
- the run leaves a usable terminal or partial-progress summary
