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
- move through the task one AC at a time
- use TC-first work when possible
- use the earliest valid check first when strict test-first is not possible
- keep progress visible
- finish the task and hand off to `$qa`

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
approved plan
  -> entry check
  -> make execution checklist
  -> pick next AC
  -> pick next TC
  -> choose TC type
     -> automated
     -> manual
     -> doc
     -> config
  -> run the earliest valid check first
  -> implement
  -> rerun the TC
  -> decide
     -> pass
     -> fail
     -> blocked
     -> scope_drift
  -> repeat
  -> when all ACs pass
     -> move to $qa
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

## Decision Loop

After rerunning the current TC, decide:

- `pass`
  - mark the TC done
  - if all TCs in the AC pass, mark the AC done
- `fail`
  - fix and retry inside the current AC
- `blocked`
  - stop and report the blocker clearly
- `scope_drift`
  - stop and return to `$planning` if the work crosses the plan boundary

Record the result with:

- `scripts/checklist.py tc-result`

## Retry Rules

Retry is bounded.

Per TC:

- allow up to 3 fix-and-retry cycles
- if the same failure keeps coming back without a meaningfully new approach, stop retrying
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

## Installed Helper

This skill ships its own helper script:

- `scripts/checklist.py`

Do not depend on a repo-only runtime helper for live checklist updates.

## End Of Execute

When all ACs are complete:

```text
task complete
  -> move to $qa
```

`execute` does not go straight to commit.

## Constraints

- Do not brainstorm inside `execute`.
- Do not replan inside `execute`.
- Do not treat "looks done" as done.
- Do not silently widen scope.
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
- the next step is clearly `$qa`
