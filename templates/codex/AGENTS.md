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

If a middle-school-level reader cannot follow the wording, it is too hard.

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
