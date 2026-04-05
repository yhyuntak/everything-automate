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

## Current Status

Primary in-session workflow surface:

- `$brainstorming`
- `$planning`

Current internal support surface in this source repo:

- `templates/codex/overlays/ea-codex.sh`

This helper is not the intended primary user workflow.
Installed packaging may later hide or replace it behind in-session skill wiring.

Current planning-agent roster:

- `explorer`
- `angel`
- `architect`
- `devil`

Current note:

- `$brainstorming` is the idea-shaping surface before planning.
- `$planning` is the execution-planning surface after direction is clear enough.
- Ralph execution concepts are still under design and should not be treated as installed user-facing skills yet.
