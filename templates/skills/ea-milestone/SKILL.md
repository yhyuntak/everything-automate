---
name: ea-milestone
description: Split a locked North Star into ordered output milestones before code design brainstorming.
argument-hint: "<locked North Star artifact or milestone roadmap request>"
---

# ea-milestone

Use this after a locked North Star and before `ea-brainstorming`.

`ea-milestone` turns one locked final goal into ordered output milestones that later stages can work one by one.

## Purpose

`ea-milestone` exists so large goals do not jump straight from North Star into code design brainstorming.

It creates and maintains:

- `.everything-automate/state/active.md`

This active file is the source of truth while Milestone mode is active.

## Use When

Use this skill when:

- a locked North Star is too large to brainstorm and plan in one step
- the goal has clear stage order, dependencies, or required handoffs
- the user needs output-first milestones before deciding what to design now
- the next `ea-brainstorming` session should start from one milestone rather than from the whole goal

If the user did not explicitly ask for Milestone mode, ask before starting when the change would create or update `active.md`.

## Do Not Use When

Do not use this skill when:

- there is no locked North Star artifact
- the target is already small enough for a one-item roadmap and the user is ready for `ea-brainstorming`
- the user wants open-ended idea generation instead of ordered delivery steps
- the user wants detailed design or implementation planning rather than milestone splitting

## Core Rule

Milestone is roadmap shaping only.

It owns:

- why the goal needs milestone splitting
- ordered output milestones
- current milestone recommendation
- ordering logic
- milestone dependencies
- handoff rule for `ea-brainstorming`

It does not own:

- redefining the final goal
- buildable design details
- AC / TC planning
- implementation
- QA

## State File

When Milestone mode starts, create or update:

- `.everything-automate/state/active.md`

Use the template at:

- `.codex/skills/ea-milestone/templates/active.md`

The active file exists only while Milestone mode is active.

`active.md` is not the final output. It is a live working file for the hook and current session only.

There must be only one active state file in a workspace:

- `.everything-automate/state/active.md`

Do not create mode-specific active files.

If `.everything-automate/state/active.md` already exists and belongs to another workflow, stop and ask before overwriting it.

When the milestone roadmap is locked, archive the accepted output to:

- `.everything-automate/state/milestone/archive/YYYYMMDD-HHMMSS-[slug].md`

Then remove `active.md` from the active path so hooks return to no-op.

## Input Rule

Milestone starts from a locked North Star archive, not from memory alone.

Read:

- the locked North Star archive
- any explicit user constraints about order, urgency, scope, or later deliverables

Do not use the chat transcript as the source of truth when it conflicts with the locked North Star artifact.

## Classification Rule

Classify each important user statement before following it.

```text
Milestone Material
  -> changes or sharpens milestone names, outputs, or grouping

Ordering Question
  -> affects sequence, current milestone, or whether something is early vs later

Dependency Note
  -> adds a prerequisite, blocker, or unlock condition

Parking Lot
  -> useful but outside the roadmap split itself
```

## Artifact-First Rule

Milestones must be output-first, not action-first.

Good:

- investigation summary complete
- beginner guide document v1 complete
- frontend guide design note accepted

Weak:

- investigate
- work on the docs
- make progress

## Pipeline

Follow this pipeline:

```text
locked north-star archive
  -> inspect goal size
  -> propose milestone roadmap
  -> create active.md
  -> user revises split, order, outputs, and dependencies
  -> confirm current milestone recommendation
  -> read-test
  -> lock roadmap
  -> archive accepted output and remove active.md
```

## Step 1: Decide Whether Splitting Is Needed

Read the locked North Star and decide:

- does this need several milestones?
- is one short milestone enough?

The roadmap may still contain one milestone, but that choice must be explicit.

## Step 2: Propose The First Draft

The assistant should propose the first roadmap draft.

That draft should include:

- why milestones are needed
- milestone names
- why each milestone exists
- required inputs
- output artifacts
- what each milestone unlocks next

Do not wait for the user to invent the whole roadmap from scratch.

## Step 3: Create The Active State

Create `active.md` once the first roadmap proposal exists.

Capture:

- parent goal
- milestone list
- current milestone recommendation
- ordering logic
- risks and dependencies
- open questions

## Step 4: Refine Interactively

Use the milestone draft to negotiate with the user.

Good questions:

- Is this split too coarse or too fine?
- Does one milestone need to move earlier?
- Is the output artifact for this milestone correct?
- Is the recommended current milestone the right one to design next?
- Is any milestone actually a later concern and better parked for now?

Use `request_user_input` when the user needs to:

- choose between two milestone orders
- confirm the current milestone
- cut scope
- merge or split milestones

## Step 5: Run Read-Test

Run read-test only after the milestone roadmap looks concrete enough to inspect.

Use three `ea-read-test` agents when available.

Each agent should read:

- `.everything-automate/state/active.md`

Do not paste the full state file into the prompt. Ask each agent to read the file directly and report its natural interpretation.

The read-test prompt should stay simple:

```text
Read the active Milestone file and explain what roadmap you think it communicates, whether the parent goal is preserved, what the milestones produce, which milestone is recommended now, what is clearly excluded, and what still feels unclear.

Focus on the Milestone stage: check whether the parent goal, milestone order, output artifacts, current milestone recommendation, dependencies, and handoff rule read clearly.
```

Pass when:

- all three agents describe the same parent goal
- all three agents describe compatible milestone order
- at least two of three agree on the current milestone recommendation
- at least two of three agree on the main out-of-scope items
- no agent reports that the roadmap changes the North Star

Fail when:

- any agent reads a different parent goal
- agents disagree on the current milestone recommendation
- agents disagree on whether this is milestone splitting, design, planning, or implementation
- more than one agent says the roadmap is too ambiguous to act on

If read-test fails:

- compare the divergent interpretations
- find the smallest unclear point
- ask the user one narrow question
- update `active.md`
- run read-test again when useful

## Step 6: Lock The Roadmap

Lock when:

- the roadmap order is clear enough
- each milestone has an output artifact
- the current milestone recommendation is explicit
- the dependencies are clear enough for `ea-brainstorming` to start
- read-test passes or the user explicitly accepts the remaining risk

Archive the accepted roadmap and remove `active.md`.

## Output Shape

When reporting to the user, keep it short:

- parent goal
- milestone list
- current milestone recommendation
- what changed
- what next stage should read

## Completion

Milestone is complete when:

- a locked North Star was used as input
- the roadmap is artifact-first
- ordering logic is clear
- one current milestone recommendation is explicit
- risks and dependencies are recorded
- read-test passes or the user explicitly accepts the remaining risk
- the accepted milestone output has been archived
- `.everything-automate/state/active.md` has been removed
