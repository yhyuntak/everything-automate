---
name: qa
description: Review finished work with fresh eyes before commit by using a cold reviewer subagent.
argument-hint: "[plan path, execute result, or ready-for-review task]"
---

# qa

Use this after `$execute` and before `commit`.

## Purpose

`qa` is the final review gate before commit.

Its job is to:

- review finished work with fresh eyes
- catch important code, test, risk, and structure problems
- decide whether the work is ready for commit
- send the work back for fixes when needed

`qa` is not:

- implementation
- brainstorming
- full replanning

## Position In The Main Flow

```text
$brainstorming
  -> $planning
  -> $execute
  -> $qa
  -> commit
```

## Use When

Use `qa` when:

- `$execute` has finished enough work to review
- changed files exist
- test or check results exist
- the user wants a commit decision

## Do Not Use When

Do **not** use `qa` when:

- implementation is still actively in progress
- there is no real result to review yet
- there are no changed files
- there are no test or check results to inspect

If that is the case, go back to `$execute`.

## Core Flow

```text
execute result
  -> QA entry check
  -> prepare QA handoff packet
  -> spawn cold qa-reviewer
  -> collect findings
  -> decide
     -> pass
     -> fix and rerun qa
     -> return to planning only if truly needed
```

## Entry Check

Before QA starts, make sure:

- there is finished enough work to review
- changed files or a diff exist
- test or check results exist
- a task summary or plan summary exists

If not, stop and say what is missing.

## QA Handoff Packet

Do not dump the full conversation into the reviewer.

Prepare a focused packet with:

- task summary
- desired outcome
- scope / non-goals
- short plan summary
- changed files or diff
- test or check results
- open risks

This packet is the review input.

## Cold Reviewer Rule

`qa` should use one cold reviewer subagent.

"Cold" means:

- not the implementer
- not heavily biased by the full working conversation
- given only the focused review packet

## Reviewer Focus

The reviewer should check:

- code quality
- architecture fit
- security or risk smells
- test quality
- mismatch with the intended goal

Focus on important problems.
Do not nitpick style.

## Verdicts

Use simple verdicts:

- `pass`
- `fix`

Only recommend going back to `$planning` if the problem is truly at the plan level.

## Output

QA should return:

- verdict
- important findings
- open risks
- recommended next step

## Rules

- Do not implement inside `qa`.
- Do not reopen planning casually.
- Do not block commit for tiny style preferences.
- Do not treat QA like a second execution loop.
- Use simple English.

## Completion

`qa` is complete when:

- the review verdict is clear
- the important findings are clear
- the next step is clear
- the work is either ready for commit or clearly sent back for fixes
