---
name: ea-execute
description: Use an approved plan to finish the work through a TC-first loop, then hand off to `$ea-qa`.
argument-hint: "[plan path or approved task]"
---

# ea-execute

Use an approved plan to finish the work without reopening ea-planning.

## Purpose

`ea-execute` is the main work phase after `$ea-planning`.

Calling `$ea-execute` is an explicit request to use the `ea-worker` subagent for implementation work.

The main LLM is the controller.
The controller owns the loop, but it should not do normal implementation itself.
The controller should spawn the `ea-worker` for each AC/TC implementation unit after the entry check and checklist setup.

Only skip the ea-worker for controller bookkeeping, such as checklist updates, QA handoff files, or a clearly read-only verification step.

Its job is to:

- read an approved plan
- turn `Task -> AC -> TC` into a working checklist
- keep the main LLM as the controller for the loop
- route implementation work to the `ea-worker` subagent lane by default
- route hard execution decisions to the `ea-advisor` subagent lane when needed
- let the ea-worker raise escalation signals without calling the ea-advisor directly
- move through the task safely, using serial work by default and parallel work when ACs or TCs are independent
- use TC-first work when possible
- use the earliest valid check first when strict test-first is not possible
- keep progress visible
- finish execution and continue into `$ea-qa` when review inputs are ready

## Position In The Main Flow

```text
$ea-brainstorming
  -> $ea-planning
  -> $ea-execute
  -> $ea-qa
  -> commit
```

`ea-execute` is not the final acceptance step.
That is what `$ea-qa` is for.

## Use When

Use `ea-execute` when:

- an approved plan already exists
- the plan contains `Task -> AC -> TC`
- the user wants implementation now
- the handoff is strong enough to start real work

## Do Not Use When

Do **not** use `ea-execute` when:

- the direction is still fuzzy
- the plan is still draft
- scope and non-goals are still unclear
- the plan still forces guessing
- the user still needs ea-brainstorming or ea-planning

If any of the above are true, stop and go back to `$ea-planning`.

## Input Contract

`ea-execute` reads an approved plan.

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
- return to `$ea-planning`

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
[Controller Checks Parallel Safety]
   |
   +---- independent work ----> [Spawn Bounded Workers In Parallel]
   |                                  |
   |                                  v
   |                            [Collect Worker Reports]
   |                                  |
   +<---------------------------------+
   |
   v
[Controller Picks AC Or TC Batch]
   |
   v
[Controller Picks TC]
   |
   v
[Run Earliest Valid Check]
   |
   v
[Controller Builds Worker Task]
   |
   v
[Worker Implements]
   |
   v
[Worker Report]
   |
   v
[Controller Reads Report]
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
   +---- ready ---------------> [$ea-qa]
   |
   +---- missing input -------> [Stay In Execute]
```

## Step Meanings

### 1. Make Execution Checklist

The first real action is to turn the approved plan into a live working checklist.

Use the installed helper in this skill:

- `scripts/checklist.py ea-execute-start`

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

### 2. Check Parallel Safety

After the checklist exists, scan the pending ACs and TCs for independence.

Use parallel worker calls only when all of these are true:

- the plan gives clear AC/TC boundaries
- each worker can own a disjoint file, module, doc, prompt, or config scope
- the work does not require another active worker's result
- the checks can run without racing on the same mutable state
- the expected merge path is simple enough for the controller to review

Stay serial when:

- file or module ownership overlaps
- one AC decides the shape for another AC
- the worker would need to coordinate with another worker mid-task
- a shared generated file, lockfile, migration, or state file may be edited by more than one worker
- the plan is weak and parallel work would hide design confusion

Parallelism is a tool for independent work, not a reason to split unclear work.

### 3. Pick The Next AC

Work one AC at a time unless the parallel safety check finds independent work.

Do not try to finish the whole task at once. If running parallel work, spawn small bounded workers for independent ACs or TC groups.

When an AC becomes active, update the checklist with:

- `scripts/checklist.py ac-start`

### 4. Pick The Next TC

Inside the current AC, pick the next unfinished TC.

This is the heart of the loop.

When a TC becomes active, update the checklist with:

- `scripts/checklist.py tc-start`

### 5. Choose TC Type

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

`ea-execute` uses one owner for the loop.

That owner is the main LLM running `$ea-execute`.
Treat that main LLM as the `controller`.

The supporting lanes are real subagent lanes:

- `ea-worker`
  - default implementation lane
  - works on the active AC and TC
  - reports pass, fail, blocked, or escalation_needed
- `ea-advisor`
  - high-reasoning decision lane
  - receives a focused handoff from the controller
  - recommends a path but does not implement

The roles are:

- `controller`
  - read the plan
  - pick AC and TC
  - build the ea-worker task
  - delegate implementation work to a ea-worker by default
  - read ea-worker reports and escalation signals
  - decide whether ea-advisor help is needed
  - decide whether to retry, stop, or return to `$ea-planning`
- `ea-worker`
  - read the code for the active AC and TC
  - make bounded changes
  - run checks
  - report what happened clearly
  - raise escalation signals when continuing would be unsafe or speculative
- `ea-advisor`
  - diagnose a hard execution moment
  - compare options
  - recommend a path and next steps

Important rules:

- the ea-worker does **not** call the ea-advisor directly
- the ea-worker may ask the controller to escalate
- the controller owns ea-advisor use
- the controller owns the final execution decision
- the controller should not implement directly during normal `$ea-execute`
- direct controller edits are only for tiny harness bookkeeping, such as checklist or handoff files

## Advisor Escalation Rule

The controller must not silently solve hard execution calls by itself.

Call the ea-advisor when the ea-worker reports `escalation_needed: true` with `escalation_type: advisor_candidate`, unless the controller can point to a concrete reason that the ea-worker report is wrong.

Also call the ea-advisor when any of these appear:

- a design or architecture fork
- a likely fix that crosses approved scope or non-goals
- repeated failure where the next move is not obvious
- a workflow, skill, hook, or agent contract may need to change
- the controller would need to invent a new approach not already covered by the plan

The controller may summarize facts, prepare the handoff, and decide after advice.
The controller may not replace the advisor by making the hard design call itself.

## Parallel Worker Rule

When using parallel workers, the controller must make ownership explicit.

Each ea-worker prompt should say:

- which AC or TC group it owns
- which files, modules, docs, prompts, or config surfaces it may edit
- which related surfaces it may read
- which checks it should run
- that other workers may be editing the repo at the same time
- that it must not revert or overwrite changes outside its scope
- that it must adapt to existing changes instead of undoing them

The controller should spawn typed ea-workers with explicit task context.
Do not combine `fork_context: true` with an explicit `agent_type`, model, or reasoning override.
If the controller needs the `ea-worker` lane, either spawn `agent_type: ea-worker` without forking full context, or fork context without overriding the agent type.

Pause new parallel spawns when any active ea-worker reports:

- `blocked`
- `escalation_needed`
- a scope conflict
- overlapping file ownership
- a check failure that could invalidate another active worker's work

After parallel workers finish, the controller must:

- read every report
- inspect or summarize the combined diff
- run the shared verification checks
- update the checklist for each completed AC/TC
- decide whether any failed or escalated work needs retry, advisor help, or return to planning

## Worker Escalation Rule

The ea-worker should continue when:

- the next fix is clear
- the fix stays inside approved scope
- the check result points to a concrete next step
- the risk of continuing is low

The ea-worker should raise escalation when:

- the same check fails again and the next move is not clear
- the root cause is unclear after a reasonable attempt
- there is a design or architecture fork
- the likely fix crosses scope or non-goals
- a workflow or skill contract may need to change
- continuing would be guessing
- the risk of a wrong fix is high

Escalation does not automatically mean ea-advisor.
The controller decides one of these:

- retry directly with a clearer instruction
- adjust the ea-worker task boundary
- call the ea-advisor
- stop as blocked
- return to `$ea-planning`

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

Do not silently redesign the TC inside `$ea-execute`.

Return to `$ea-planning` when a TC is:

- unclear
- too weak to prove the AC is done
- mismatched with its AC
- not executable by the controller or ea-worker
- only checking internal calls without a result that matters

Example:

```text
TC: "check it works"
  -> return to $ea-planning

TC: "verify private helper X was called once"
  -> return to $ea-planning unless that call is the public contract
```

## Decision Loop

After rerunning the current TC, decide:

- `pass`
  - mark the TC done
  - if all TCs in the AC pass, mark the AC done
- `fail`
  - retry directly if the next move is still clear
  - use the ea-advisor if the execution path is no longer clear
- `blocked`
  - stop and report the blocker clearly
  - return to `$ea-planning` if the TC itself is unclear, too weak, mismatched, or not executable
- `scope_drift`
  - stop and return to `$ea-planning` if the work crosses the plan boundary

Record the result with:

- `scripts/checklist.py tc-result`

## Advisor Trigger Rules

Do not call the ea-advisor for every failure.

Use the ea-advisor when the controller sees one of these:

- the same TC fails again and the next move is no longer clear
- execution reaches a real design fork
- the likely fix crosses the approved plan boundary
- the ea-worker report shows repeated effort with weak progress
- the ea-worker raises `advisor_candidate` and the controller agrees
- the task is near completion and needs one last risk pass before `$ea-qa`

If the next step is still obvious, retry directly first.

## Retry Rules

Retry is bounded.

Per TC:

- allow up to 3 fix-and-retry cycles
- if the same failure keeps coming back without a meaningfully new approach, stop retrying
- if a retry is no longer clear, switch to an ea-advisor handoff instead of guessing
- if the plan itself is too weak, return to `$ea-planning`

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

- durable ea-worker report
- ea-advisor handoff
- controller retry packet
- checklist progress

Do not dump the full conversation into these files.

Keep them short and task-bound.

The latest durable packet files live under the task state root.

The main files are:

- `ea-worker-report.json`
- `ea-worker-report-[ac-or-tc-id].json` when several workers run in parallel
- `ea-advisor-handoff.json`
- `retry-packet.json`
- `ea-execute-progress.json`

Use `ea-worker-report.json` for the latest durable ea-worker boundary:

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

Use `ea-advisor-handoff.json` only when the controller calls the ea-advisor:

- open_question
- recent_attempts
- candidate_options
- optional relevant_files
- optional failing_check
- optional worker_report_ref
- optional escalation_question
- optional uncertainty_reason
- optional risk_if_continue

Use `retry-packet.json` after the controller reads the ea-advisor result and decides the next move:

- controller_decision
- recommended_path
- next_steps
- optional advisor_summary
- optional risks_to_watch
- optional advisor_handoff_ref

## QA Entry Gate

When all ACs are complete, do not stop at "implementation done".

Check whether QA can start now.

Normal ea-execute completion should only move forward when:

- changed files exist
- test or check results exist
- a focused QA handoff can be built

If those are true:

- build the QA handoff with `ea-qa/scripts/build_handoff.py`
- continue into `$ea-qa` in the same LLM-led workflow

If those are not true:

- stay in `ea-execute`
- say clearly what is still missing before QA

## Installed Helper

This skill ships its own helper script:

- `scripts/checklist.py`

Use it for:

- `ea-execute-start`
- `ac-start`
- `tc-start`
- `tc-result`
- `ac-complete`
- `ea-worker-report`
- `ea-advisor-handoff`
- `retry-packet`

Do not depend on a repo-only runtime helper for live checklist updates.

## End Of Execute

When all ACs are complete and QA entry conditions are satisfied:

```text
task complete
  -> build QA handoff
  -> enter $ea-qa
```

`ea-execute` does not go straight to commit.
After a normal successful ea-execute run, the main LLM should continue into `$ea-qa` without a separate user-side command.
This is a skill-level workflow rule in this version, not a runtime-enforced script handoff.

## Constraints

- Do not brainstorm inside `ea-execute`.
- Do not replan inside `ea-execute`.
- Do not treat "looks done" as done.
- Do not silently widen scope.
- Do not silently redesign weak TCs.
- Do not let the ea-worker own the whole loop.
- Do not let the ea-worker call the ea-advisor directly.
- Do not skip TC thinking just because strict TDD is hard.
- When you report progress or completion, say the result first.
- Keep updates clean and easy to scan.
- If you explain the loop, use a real ASCII flow chart instead of a simple arrow list.

## Completion

`ea-execute` is complete only when:

- the approved plan has been followed
- all required ACs are complete
- all required TCs are resolved
- progress is visible enough to understand what happened
- the next step is direct `$ea-qa` in the same workflow or an explicit QA rerun when needed
