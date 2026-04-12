---
name: qa
description: Review finished work with fresh eyes before commit by using a cold reviewer subagent.
argument-hint: "[plan path, execute result, or ready-for-review task]"
---

# qa

Use this after `$execute` and before `commit`.

`qa` may be entered automatically after a normal successful `$execute`.
It may also be run again explicitly when a rerun is needed.

## Purpose

`qa` is the final review gate before commit.

Its job is to:

- review finished work with fresh eyes
- catch important code, test, behavior, and contract problems
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
  -> main LLM judges findings
  -> decide
     -> pass
     -> fix and return to execute
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
- behavior goal
- LLM reads or decision inputs
- LLM-owned decisions
- script-owned validation
- contract changes
- open risks

This packet is the review input.

Use the installed helper in this skill:

- `scripts/build_handoff.py`

Build the packet before spawning the cold reviewer.

The helper should fail if the packet is missing the basics needed for a real review.

## Cold Reviewer Rule

`qa` should use one cold reviewer subagent.

"Cold" means:

- not the implementer
- not heavily biased by the full working conversation
- given only the focused review packet

## Reviewer Focus

The reviewer should check two lenses:

- code lens
  - code quality
  - architecture fit
  - security or risk smells
  - test quality
- behavior and contract lens
  - mismatch with the intended goal
  - whether the LLM will see the right inputs
  - whether judgment ownership stays with the LLM where it should
  - whether scripts only validate and persist state instead of deciding behavior

Focus on important problems.
Do not nitpick style.

## QA Judgment

The cold reviewer finds problems.

The main LLM running `qa` must still judge those findings.

That means:

- decide which findings are true blockers
- separate real defects from weaker concerns
- judge code defects
- judge behavior-shaping defects
- judge contract and ownership defects
- decide whether the work should:
  - `pass`
  - `fix`
  - rarely return to `$planning`

`qa` is not only a reviewer call.
It is the final review-and-judgment stage before commit.

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
- After a normal successful `$execute`, continue into `$qa` in the same LLM-led workflow when the review inputs are ready.
- Do not describe this as a runtime-enforced script transition in this version.
- Use simple English.
- Put the verdict first.
- Keep findings grouped and easy to scan.
- If you explain the review flow, use a real ASCII flow chart instead of a simple arrow list.

## Installed Helper

This skill ships its own helper script:

- `scripts/build_handoff.py`

Do not depend on a repo-only runtime helper for the review packet.

## Completion

`qa` is complete when:

- the review verdict is clear
- the important findings are clear
- the next step is clear
- the work is either ready for commit or clearly sent back for fixes
