---
name: ea-north-star
description: Lock a fuzzy user goal into one clear North Star before brainstorming, blueprinting, planning, backlog work, or execution.
argument-hint: "<fuzzy goal, product idea, feature idea, issue, or unclear target>"
---

# ea-north-star

Use this when the user wants their real target made clear before later work starts.

`ea-north-star` is stricter than brainstorming. Its job is to stop drift, extract the user's concrete goal, and create a file-backed North Star that other agents can read the same way.

## Purpose

`ea-north-star` helps turn fuzzy intent into one clear shared target.

It creates and maintains:

- `.everything-automate/state/active.md`

This active file is the source of truth while North Star mode is active.

## Use When

Use this skill when:

- the user asks for North Star, goal lock, target clarification, or a very clear goal
- the user has a fuzzy service, product, feature, issue, or work target
- the user says they are drifting, spreading out, or losing the point
- a later workflow would be risky because the goal is not clear yet

If the user did not explicitly ask for North Star mode, ask before starting when the change would create or update `active.md`.

## Do Not Use When

Do not use this skill when:

- the user only wants casual conversation
- the task is already clear enough for implementation
- the user wants execution planning from an already locked target
- the user wants open-ended idea expansion
- the user wants a code review or QA review

## Core Rule

North Star is target clarification only.

It does not own:

- blueprinting
- execution planning
- backlog shaping
- implementation
- QA

Design ideas may appear during North Star. Do not discard them, and do not let them redefine the goal. Put them in `Spec Seeds`.

## State File

When North Star mode starts, create or update:

- `.everything-automate/state/active.md`

Use the template at:

- `.codex/skills/ea-north-star/templates/active.md`

The active file exists only while North Star mode is active.

`active.md` is not the final output. It is a live working file for the hook and current session only.

There must be only one active state file in a workspace:

- `.everything-automate/state/active.md`

Do not create mode-specific active files such as:

- `.everything-automate/state/north-star/active.md`
- `.everything-automate/state/blueprint/active.md`

Use the `mode` front matter to say which workflow owns the current active state.

When the North Star is locked, treat the locked file as the North Star output and archive it. Do not leave a locked North Star at the active path.

When North Star mode closes, archive the active file to:

- `.everything-automate/state/north-star/archive/YYYYMMDD-HHMMSS-[slug].md`

Then remove `active.md` from the active path so hooks return to no-op.

## Classification Rule

Classify each important user statement before following it.

```text
Goal Material
  -> clarifies the North Star itself
  -> write into the main North Star sections

Spec Seed
  -> may help later build the target
  -> write into Spec Seeds

Parking Lot
  -> useful but outside the current target
  -> write into Parking Lot
```

Do not let Spec Seeds or Parking Lot items change the locked goal unless the user explicitly chooses to change the North Star.

## Pipeline

Follow this pipeline:

```text
raw intent
  -> user mental picture
  -> one-sentence North Star draft
  -> scope and non-goals
  -> concrete success/failure picture
  -> read-test
  -> refine or lock
  -> archive locked output and remove active.md
```

## Step 1: Capture Raw Intent

Create `active.md` early. Do not wait until the goal is polished.

Capture:

- the user's rough words
- the current stage
- what is known
- what is still unclear

Keep the file useful, not perfect.

## Step 2: Extract The Mental Picture

Do not accept abstract goals at face value.

The user chose North Star because they want the real target made clear, even if they cannot explain it cleanly yet.

Ask firm, narrow questions such as:

- What exists when this succeeds?
- What does the user see, feel, decide, or do differently?
- What result would make the user say, "yes, that is it"?
- What result would look plausible but still be wrong?
- What must be included for this to count?
- What must be excluded even if it sounds useful?
- What would another agent likely misunderstand?

Reflect the picture back in concrete words before treating it as settled.

## Step 3: Draft The North Star

Write a one-sentence North Star.

Good shape:

```text
[who or what] can [do or know what] in [what situation], so that [clear result].
```

Avoid vague goals such as:

- make it better
- improve the workflow
- build a good system
- make the app useful

## Step 4: Lock Boundaries

Write:

- `Scope`
- `Non-Goals`
- `Decision Filter`

Use the Decision Filter to classify new ideas before following them.

If an idea does not clarify the current North Star, park it or capture it as a Spec Seed.

## Step 5: Use Structured Input Selectively

Use `request_user_input` only when the user needs to choose, classify, confirm, or cut scope.

Good uses:

- choose between clear options
- classify a new idea
- confirm a boundary
- cut scope
- pick which ambiguity to resolve first
- confirm lock or refine

Do not use `request_user_input` when the user needs to:

- describe their mental picture freely
- explain context, emotion, or pain
- speak before the agent has enough context to create meaningful choices

Free-form conversation extracts the raw picture. Structured input narrows it.

## Step 6: Run Read-Test

Run read-test only after the North Star looks concrete enough to inspect.

Use three `ea-north-star-read-test` agents when available.

Each agent should read:

- `.everything-automate/state/active.md`

Do not paste the full state file into the prompt. Ask each agent to read the file directly and report its natural interpretation.

The read-test prompt should stay simple:

```text
Read the active North Star file and explain what you think the user wants, what success looks like, what is clearly included, what is clearly excluded, and what still feels unclear.
```

## Read-Test Pass/Fail

Pass when:

- all three agents describe the same core user intent
- all three agents describe compatible success pictures
- at least two of three agree on the main in-scope items
- at least two of three agree on the main out-of-scope items
- no agent reports a different primary target

Fail when:

- any agent reads a different main target
- agents disagree on whether this is goal clarification, planning, or implementation
- agents disagree on the main artifact or result
- more than one agent says the target is too ambiguous to act on

Do not judge only by unanimous `ready_to_lock` votes. Read the reasons.

## Step 7: Refine Or Lock

If read-test fails:

- compare the divergent interpretations
- find the smallest unclear point
- ask the user one narrow question
- update `active.md`
- run read-test again when useful

If read-test passes:

- mark the active file as locked
- summarize the locked North Star
- archive the locked file as the North Star output
- remove `active.md` from the active path so hooks return to no-op
- tell the user where the locked output was archived
- only keep `active.md` if the user explicitly says to keep North Star mode active for more refinement

Do not leave a locked `active.md` in place by default. A locked North Star at the active path keeps the hook active and can incorrectly constrain normal conversation or the next workflow.

## Output Shape

When reporting to the user, keep it short:

- current North Star
- what became clearer
- what was parked
- what still blocks lock, if anything
- next step

## Completion

North Star is complete when:

- the target is concrete enough to picture
- scope and non-goals are clear
- a Decision Filter exists
- read-test passes or the user explicitly accepts the remaining risk
- the locked North Star has been archived
- `.everything-automate/state/active.md` has been removed
- Spec Seeds are separate from the goal
- Parking Lot items are separate from the goal
- the next step is clear
