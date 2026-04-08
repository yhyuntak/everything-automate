# Everything Automate for Codex CLI

This file is the top-level runtime guidance entry for the Codex template.

## Positioning

Codex CLI is the current `v0` implementation path.
The primary user workflow should stay inside the Codex session.
Runtime helpers and state tools exist to support that workflow, not replace it.

## Runtime Model

```text
inside Codex
  -> $brainstorming
  -> $planning
  -> $execute
  -> $qa

under the hood
  -> handoff
  -> state/runtime preparation
  -> execution/recovery support
```

## Core Expectations

- `AGENTS.md` is the top-level operating contract
- setup installs or generates the runtime overlays Codex needs
- in-session workflow is the primary UX
- durable execution is not assumed to be native to Codex
- runtime helpers are internal support surfaces for state, instructions, and recovery
- the shared kernel remains:

```text
plan -> execute -> verify -> decide
```

## Language Rule

Use simple English by default.

- prefer common words over abstract framework words
- write so non-native English speakers can follow quickly
- keep important terms stable, but explain them in simple words around them
- use the same rule in skill text, setup text, and direct user-facing explanations
- prefer easier words over harder professional English
- English terms are allowed, but do not overuse them
- if a simpler word works, use the simpler word
- do not stack many English terms in one short paragraph

If a middle-school-level reader cannot follow the wording, it is too hard.

## Communication Rule

Put the answer first.

- start with the main conclusion or state change
- do not hide the answer inside a long setup paragraph
- if the user mainly needs a status update, lead with:
  - what finished
  - what changed
  - what is still left

Keep the answer cleanly structured.

- prefer short sections or short paragraphs over one long block
- group content into clear chunks when helpful:
  - conclusion
  - key changes
  - checks
  - next step
- do not mix every detail into one paragraph
- do not flood the main answer with too many file paths

## Flow Chart Rule

When a process or workflow needs to be explained, prefer a real ASCII flow chart.

Good:

```text
[Start]
   |
   v
[Read Plan]
   |
   v
[Pick AC]
   |
   +---- blocked ----> [Stop and Report]
   |
   v
[Pick TC]
   |
   v
[Run Check]
   |
   v
[Implement]
   |
   v
[Check Again]
   |
   +---- fail ----> [Fix and Retry]
   |
   v
[Next]
```

Do not treat this as a flow chart:

```text
plan -> execute -> verify -> decide
```

That is only a short chain, not a real flow chart.

## Current Status

Primary in-session workflow surface:

- `$brainstorming`
- `$planning`
- `$execute`
- `$qa`

Current internal support surface in this source repo:

- `templates/codex/overlays/ea-codex.sh`

This helper is not the intended primary user workflow.
Installed packaging may later hide or replace it behind in-session skill wiring.

Current planning-agent roster:

- `explorer`
- `plan-arch`
- `plan-devil`
- `qa-reviewer`

Current note:

- `$brainstorming` is the idea-shaping surface before planning.
- `$planning` is the execution-planning surface after direction is clear enough.
- `$execute` is the TC-first execution surface after an approved planning handoff and before `$qa`.
- `$qa` is the final cold-review gate before `commit`.
- hidden runtime/state helpers may support the flow, but they are not the main user workflow.
