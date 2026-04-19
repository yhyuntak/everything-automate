---
name: execute
description: Use an approved plan to finish the work through a TC-first loop, then hand off to `$qa`.
argument-hint: "[plan path or approved task]"
---

# execute

Use an approved plan to finish the work without reopening planning.

## Purpose

`execute` is the main work phase after `$planning`.

Its job is to:

- read an approved plan
- turn `Task -> AC -> TC` into a working checklist
- keep the main LLM as the controller for the loop
- route bounded implementation work to the `worker` subagent lane when useful
- route hard execution decisions to the `advisor` subagent lane when needed
- let the worker raise escalation signals without calling the advisor directly
- move through the task one AC at a time
- use TC-first work when possible
- use the earliest valid check first when strict test-first is not possible
- keep progress visible
- finish execution and continue into `$qa` when review inputs are ready

## Position In The Main Flow

```text
$brainstorming
  -> $planning
  -> $execute
  -> $qa
  -> commit
```

`execute` is not the final acceptance step.
That is what `$qa` is for.

## Use When

Use `execute` when:

- an approved plan already exists
- the plan contains `Task -> AC -> TC`
- the user wants implementation now
- the handoff is strong enough to start real work

## Do Not Use When

Do **not** use `execute` when:

- the direction is still fuzzy
- the plan is still draft
- scope and non-goals are still unclear
- the plan still forces guessing
- the user still needs brainstorming or planning

If any of the above are true, stop and go back to `$planning`.

## Input Contract

`execute` reads an approved plan.

At minimum, it needs:

- `task_id`
- `plan_path`
- `approval_state`
- `execution_unit`
- `test_strategy`
- `open_risks`
- one `Task`
  - with `AC`s
  - and `TC`s under each `AC`

Default `execution_unit` is `AC`.

## Entry Check

Before real work starts, make sure:

- the plan is present
- `approval_state` is `approved`
- the task goal is clear
- scope and non-goals are visible
- design direction is clear enough
- test strategy is explicit
- `Task -> AC -> TC` is present and usable

If the entry check fails:

- do not start implementation
- explain what is missing
- return to `$planning`

## Core Flow

```text
[Approved Plan]
   |
   v
[Entry Check]
   |
   +---- fail ----> [Return To Planning]
   |
   v
[Make Checklist]
   |
   v
[Controller Picks AC]
   |
   v
[Controller Picks TC]
   |
   v
[Run Earliest Valid Check]
   |
   v
[Controller Chooses Work Mode]
   |
   +---- small direct work ----> [Controller Implements]
   |
   +---- bounded work ---------> [Worker Implements]
   |                                |
   |                                v
   |                           [Worker Report]
   |                                |
   +<-------------------------------+
   |
   v
[Controller Decides]
   |
   +---- pass ----------------> [Mark TC Done]
   |
   +---- clear retry ---------> [Retry]
   |
   +---- unclear/escalated ---> [Advisor Handoff]
   |                                |
   |                                v
   |                           [Advisor Advice]
   |                                |
   +<-------------------------------+
   |
   +---- blocked -------------> [Stop And Report]
   |
   +---- scope drift ---------> [Return To Planning]
   |
   v
[Repeat Until All ACs Pass]
   |
   v
[QA Entry Gate]
   |
   +---- ready ---------------> [$qa]
   |
   +---- missing input -------> [Stay In Execute]
```

## Step Meanings

### 1. Make Execution Checklist

The first real action is to turn the approved plan into a live working checklist.

Use the installed helper in this skill:

- `scripts/checklist.py execute-start`

Example shape:

```text
Task
  -> AC1 [pending]
     -> TC1 [pending]
     -> TC2 [pending]
  -> AC2 [pending]
     -> TC1 [pending]
```

This checklist is what you actually work from.

### 2. Pick The Next AC

Work one AC at a time.

Do not try to finish the whole task at once.

When an AC becomes active, update the checklist with:

- `scripts/checklist.py ac-start`

### 3. Pick The Next TC

Inside the current AC, pick the next unfinished TC.

This is the heart of the loop.

When a TC becomes active, update the checklist with:

- `scripts/checklist.py tc-start`

### 4. Choose TC Type

Not every TC is the same.

Use the best fit:

- `automated`
  - a real automated test or check
- `manual`
  - a human-run scenario check
- `doc`
  - a document quality or content check
- `config`
  - a config, parse, startup, or smoke check

Keep this list small.
Detailed routing, such as UI browser checks or prompt scenarios, should come from the approved plan.

## Controller, Worker, Advisor

`execute` uses one owner for the loop.

That owner is the main LLM running `$execute`.
Treat that main LLM as the `controller`.

The supporting lanes are real subagent lanes:

- `worker`
  - bounded implementation lane
  - works on the active AC and TC
  - reports pass, fail, blocked, or escalation_needed
- `advisor`
  - high-reasoning decision lane
  - receives a focused handoff from the controller
  - recommends a path but does not implement

The roles are:

- `controller`
  - read the plan
  - pick AC and TC
  - decide whether direct work is enough
  - delegate bounded implementation work to a worker when useful
  - read worker reports and escalation signals
  - decide whether advisor help is needed
  - decide whether to retry, stop, or return to `$planning`
- `worker`
  - read the code for the active AC and TC
  - make bounded changes
  - run checks
  - report what happened clearly
  - raise escalation signals when continuing would be unsafe or speculative
- `advisor`
  - diagnose a hard execution moment
  - compare options
  - recommend a path and next steps

Important rules:

- the worker does **not** call the advisor directly
- the worker may ask the controller to escalate
- the controller owns advisor use
- the controller owns the final execution decision

## Worker Escalation Rule

The worker should continue when:

- the next fix is clear
- the fix stays inside approved scope
- the check result points to a concrete next step
- the risk of continuing is low

The worker should raise escalation when:

- the same check fails again and the next move is not clear
- the root cause is unclear after a reasonable attempt
- there is a design or architecture fork
- the likely fix crosses scope or non-goals
- a workflow or skill contract may need to change
- continuing would be guessing
- the risk of a wrong fix is high

Escalation does not automatically mean advisor.
The controller decides one of these:

- retry directly with a clearer instruction
- adjust the worker task boundary
- call the advisor
- stop as blocked
- return to `$planning`

Use these `escalation_type` values:

- `none`
- `controller_decision`
- `advisor_candidate`
- `planning_boundary`
- `blocked`

## TC-First Rule

When possible, use TC-first work.

That means:

```text
pick TC
  -> make the check fail first if possible
  -> implement
  -> make the TC pass
```

Do not default to "code first, tests later" when a useful check can come first.
TDD is not mandatory; the goal is the earliest useful verification loop for the active TC.

## If Strict TDD Is Not Practical

Do not skip the check.

Instead, use the earliest valid check you can:

- for UI work, that may be a manual scenario
- for docs work, that may be a doc checklist
- for config work, that may be a parse or smoke check

Rule:

```text
prefer test-first
if not possible, use check-first
but always anchor the work in a TC
```

## If The TC Is Weak Or Unclear

Do not silently redesign the TC inside `$execute`.

Return to `$planning` when a TC is:

- unclear
- too weak to prove the AC is done
- mismatched with its AC
- not executable by the controller or worker
- only checking internal calls without a result that matters

Example:

```text
TC: "check it works"
  -> return to $planning

TC: "verify private helper X was called once"
  -> return to $planning unless that call is the public contract
```

## Decision Loop

After rerunning the current TC, decide:

- `pass`
  - mark the TC done
  - if all TCs in the AC pass, mark the AC done
- `fail`
  - retry directly if the next move is still clear
  - use the advisor if the execution path is no longer clear
- `blocked`
  - stop and report the blocker clearly
  - return to `$planning` if the TC itself is unclear, too weak, mismatched, or not executable
- `scope_drift`
  - stop and return to `$planning` if the work crosses the plan boundary

Record the result with:

- `scripts/checklist.py tc-result`

## Advisor Trigger Rules

Do not call the advisor for every failure.

Use the advisor when the controller sees one of these:

- the same TC fails again and the next move is no longer clear
- execution reaches a real design fork
- the likely fix crosses the approved plan boundary
- the worker report shows repeated effort with weak progress
- the worker raises `advisor_candidate` and the controller agrees
- the task is near completion and needs one last risk pass before `$qa`

If the next step is still obvious, retry directly first.

## Retry Rules

Retry is bounded.

Per TC:

- allow up to 3 fix-and-retry cycles
- if the same failure keeps coming back without a meaningfully new approach, stop retrying
- if a retry is no longer clear, switch to an advisor handoff instead of guessing
- if the plan itself is too weak, return to `$planning`

Do not loop forever.

When an AC is complete, update the checklist with:

- `scripts/checklist.py ac-complete`

## Checklist Progress

Progress should stay visible through the checklist.

At minimum, keep track of:

- current AC
- current TC
- completed ACs
- completed TCs
- blocked items
- latest evidence or latest check result

This is what makes resume and restart understandable.

## Artifact Policy

Use a hybrid rule for execution context:

- keep short local retries in memory
- write files only at important execution boundaries

In v1, the important boundaries are:

- durable worker report
- advisor handoff
- controller retry packet
- checklist progress

Do not dump the full conversation into these files.

Keep them short and task-bound.

The latest durable packet files live under the task state root.

The main files are:

- `worker-report.json`
- `advisor-handoff.json`
- `retry-packet.json`
- `execute-progress.json`

Use `worker-report.json` for the latest durable worker boundary:

- summary
- what_tried
- candidate_next_steps
- optional files_touched
- optional checks_run
- optional failure_or_blocker
- optional escalation_needed
- optional escalation_type
- optional escalation_question
- optional uncertainty_reason
- optional risk_if_continue

Use `advisor-handoff.json` only when the controller calls the advisor:

- open_question
- recent_attempts
- candidate_options
- optional relevant_files
- optional failing_check
- optional worker_report_ref
- optional escalation_question
- optional uncertainty_reason
- optional risk_if_continue

Use `retry-packet.json` after the controller reads the advisor result and decides the next move:

- controller_decision
- recommended_path
- next_steps
- optional advisor_summary
- optional risks_to_watch
- optional advisor_handoff_ref

## QA Entry Gate

When all ACs are complete, do not stop at "implementation done".

Check whether QA can start now.

Normal execute completion should only move forward when:

- changed files exist
- test or check results exist
- a focused QA handoff can be built

If those are true:

- build the QA handoff with `qa/scripts/build_handoff.py`
- continue into `$qa` in the same LLM-led workflow

If those are not true:

- stay in `execute`
- say clearly what is still missing before QA

## Installed Helper

This skill ships its own helper script:

- `scripts/checklist.py`

Use it for:

- `execute-start`
- `ac-start`
- `tc-start`
- `tc-result`
- `ac-complete`
- `worker-report`
- `advisor-handoff`
- `retry-packet`

Do not depend on a repo-only runtime helper for live checklist updates.

## End Of Execute

When all ACs are complete and QA entry conditions are satisfied:

```text
task complete
  -> build QA handoff
  -> enter $qa
```

`execute` does not go straight to commit.
After a normal successful execute run, the main LLM should continue into `$qa` without a separate user-side command.
This is a skill-level workflow rule in this version, not a runtime-enforced script handoff.

## Constraints

- Do not brainstorm inside `execute`.
- Do not replan inside `execute`.
- Do not treat "looks done" as done.
- Do not silently widen scope.
- Do not silently redesign weak TCs.
- Do not let the worker own the whole loop.
- Do not let the worker call the advisor directly.
- Do not skip TC thinking just because strict TDD is hard.
- When you report progress or completion, say the result first.
- Keep updates clean and easy to scan.
- If you explain the loop, use a real ASCII flow chart instead of a simple arrow list.

## Completion

`execute` is complete only when:

- the approved plan has been followed
- all required ACs are complete
- all required TCs are resolved
- progress is visible enough to understand what happened
- the next step is direct `$qa` in the same workflow or an explicit QA rerun when needed
