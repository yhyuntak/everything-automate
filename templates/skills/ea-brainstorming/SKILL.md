---
name: ea-brainstorming
description: Turn one chosen code milestone into a bounded senior-engineer design conversation before planning.
argument-hint: "<chosen code milestone or code design brainstorming request>"
---

# ea-brainstorming

Use this after a code-related milestone is chosen and before Planning.

`ea-brainstorming` is bounded code-design brainstorming. It helps the user and a senior engineer perspective think through one code milestone before any execution plan is written.

## Purpose

`ea-brainstorming` exists because open brainstorming helps thinking, but it can let the scope grow.

Its job is to:

- keep one chosen code milestone as the boundary
- inspect the codebase before design choices are treated as settled
- surface important engineering lenses the user may not know to ask about
- explain tradeoffs in simple English
- help the user ask follow-up questions and make real decisions
- park useful ideas that do not belong to the current milestone
- produce one integrated design note for `$ea-planning`

## Use When

Use `ea-brainstorming` when:

- there is one chosen code-related milestone
- the next step is design thinking, not execution planning
- the user wants to understand options and tradeoffs before coding
- repo context matters and should be read before design choices are made
- the work is app code, scripts, hooks, tests, config, data shape, or product code

If the user did not explicitly ask for `ea-brainstorming`, ask before starting when the change would create or update `active.md`.

## Do Not Use When

Do not use `ea-brainstorming` when:

- there is no locked goal or chosen milestone yet
- the user is still trying to find the broad goal
- the target is documentation, harness workflow, or general process work
- the user already wants a file-based execution plan
- the user already has an approved plan and wants implementation
- the task is only to review finished work

For broad goal clarity, use `$ea-north-star`.
For ordered output splitting, use `$ea-milestone`.
For execution planning, use `$ea-planning`.

## Core Rule

`ea-brainstorming` is not implementation.
It is not hidden `$ea-planning`.
It is not a design document generator that drafts first and asks later.

It is a bounded conversation:

```text
[Chosen Code Milestone]
   |
   v
[Create active.md]
   |
   v
[Senior Engineer Codebase Scan]
   |
   v
[Brief Design Lenses And Tradeoffs]
   |
   v
[User-Steered Design Conversation]
   |
   v
[Integrated Design Note]
   |
   v
[$ea-planning]
```

## State File

When `ea-brainstorming` starts, create or update:

- `.everything-automate/state/active.md`

Use the template at:

- `.codex/skills/ea-brainstorming/templates/active.md`

The active file exists only while `ea-brainstorming` mode is active.

There must be only one active state file in a workspace:

- `.everything-automate/state/active.md`

Do not create mode-specific active files.

If `.everything-automate/state/active.md` already exists and belongs to `ea-brainstorming`, continue from that file.

If `.everything-automate/state/active.md` already exists and belongs to another workflow, stop and ask before overwriting it.

When the integrated design note is accepted, archive it to:

- `.everything-automate/state/brainstorming/archive/YYYYMMDD-HHMMSS-[slug].md`

Then remove `.everything-automate/state/active.md` so hooks return to no-op.

## Input Rule

Start from one chosen code milestone.

Read:

- the chosen milestone artifact or user-provided milestone text
- the locked parent North Star when it is available
- relevant codebase files and patterns

Do not reopen the parent goal unless the user explicitly moves back to North Star.
Do not split milestones inside `ea-brainstorming`; move back to `$ea-milestone` if the milestone is too large.

## Classification Rule

Classify each important user statement before following it.

```text
Code Design Material
  -> clarifies the design for the current code milestone

Learning Question
  -> asks why a design option, pattern, tradeoff, or codebase shape matters

Decision
  -> settles a design choice that Planning should preserve

Open Question
  -> blocks a good design note until answered

Parking Lot
  -> useful, but outside the current milestone
```

Do not let Learning Questions or Parking Lot items expand the milestone.

## Senior Engineer Default Rule

For code-related milestones, run a senior engineer perspective by default.

Use the `ea-senior-engineer` agent when available.
Its job is read-only:

- inspect the relevant codebase area
- identify current patterns and constraints
- surface design lenses that matter for this milestone
- explain tradeoffs and risks
- propose focused questions for the user

It must not implement.
It must not write the plan.
It must not decide for the user.

If subagents are unavailable, the main agent must do the same read-only scan before proposing design options.

## Design Lenses

The senior perspective should consider these lenses and pick the ones that matter for the current milestone.

Do not dump the full list every time.
Do not ask the user to name lenses they do not know.
Brief the user on the important lenses first, then ask focused questions.

- responsibility: which module should own the behavior?
- data flow: where does data come from, change, and leave?
- state: what must be stored, derived, cached, or invalidated?
- errors: what can fail, and what should the user or caller see?
- compatibility: what existing behavior, API, data, or config must stay stable?
- performance: what could become slow, and is that real now?
- cache: would caching help, or would it add stale-data risk too early?
- concurrency: can simultaneous actions race or conflict?
- security and permissions: who can do this, and what should be protected?
- observability: how will a future maintainer debug this?
- testing: what boundary makes the behavior easiest to verify?
- migration: does old data, config, or user behavior need a path forward?
- operations: will this be hard to run, support, or recover?
- rollback: can this be turned off or reverted if wrong?
- team readability: can another developer understand and change it later?

## Interaction Style

Keep the conversation free inside the milestone boundary.

- Start by briefing the senior scan, not by drafting a design note.
- Ask one strong question at a time when a decision is needed.
- Explain tradeoffs in simple English.
- Let the user ask follow-up questions and request deeper senior review.
- Reflect back decisions and why they were made.
- Park side ideas clearly.
- Do not lecture with generic lessons that do not affect this milestone.
- Do not move to `$ea-planning` until the user accepts the integrated design note.

## Required Lifecycle

Follow this lifecycle:

```text
[Read Milestone]
   |
   v
[Create Or Continue active.md]
   |
   v
[Confirm Code Scope]
   |
   v
[Run Senior Engineer Scan]
   |
   v
[Brief Relevant Lenses]
   |
   v
[Bounded Design Conversation]
   |
   v
[Record Decisions And Parking Lot]
   |
   v
[Draft Integrated Design Note]
   |
   v
[Run Read-Test]
   |
   +---- fail ----> [Clarify Design Note And Rerun]
   |
   v
[Ask User To Accept Or Refine]
   |
   +---- refine ----> [Continue Conversation]
   |
   v
[Archive Note And Remove active.md]
   |
   v
[Move To $ea-planning]
```

## Integrated Design Note

The final artifact is one integrated design note.

It should include:

- source milestone
- codebase context
- senior engineer lens summary
- chosen design direction
- key decisions and reasons
- tradeoffs accepted
- important learning notes
- non-goals and parking lot
- planning handoff

Keep it planning-readable.
Do not turn it into a long tutorial.

## Read-Test Gate

Run read-test after the integrated design note is drafted and before asking the user to accept it.

Use three `ea-read-test` agents when available.

Each agent should read:

- `.everything-automate/state/active.md`

Do not paste the full state file into the prompt. Ask each agent to read the file directly and report its natural interpretation.

The read-test prompt should stay simple:

```text
Read the active Brainstorming file and explain what code milestone boundary, design direction, decisions, reasons, parking lot, and planning handoff you think it communicates. Say what Planning should do next and what it must not guess.

Focus on the Brainstorming stage: check whether the integrated design note is clear enough for Planning and whether scope, decisions, reasons, and Parking Lot are separated.
```

Pass when:

- all three agents describe the same code milestone boundary
- all three agents describe compatible design direction
- at least two of three agree on the key decisions and reasons
- at least two of three agree on the main Parking Lot items
- no agent reports that Planning would need to invent the core design

Fail when:

- any agent reads a different milestone boundary
- agents disagree on the main design direction
- agents disagree on whether this is brainstorming, planning, or implementation
- more than one agent says the planning handoff is too ambiguous to act on

If read-test fails:

- compare the divergent interpretations
- find the smallest unclear point
- brief the user on the issue and risk
- update the integrated design note after user direction
- rerun read-test when useful

## When To Move To `$ea-planning`

Move to `$ea-planning` only when:

- the chosen design direction is clear
- important tradeoffs have been discussed enough
- decisions and reasons are captured
- out-of-scope ideas are parked
- read-test passes or the user explicitly accepts the remaining risk
- the user accepts the integrated design note

If the design still feels fuzzy, continue `ea-brainstorming`.
If the milestone is too large, move back to `$ea-milestone`.

## Completion

`ea-brainstorming` is complete when:

- the code milestone boundary is clear
- the senior engineer scan has been briefed
- relevant design lenses and tradeoffs have been discussed
- user decisions are captured with reasons
- Parking Lot items are separate from the current milestone
- read-test passes or the user explicitly accepts the remaining risk
- the integrated design note is accepted and archived
- `.everything-automate/state/active.md` has been removed
- the next step is `$ea-planning`
