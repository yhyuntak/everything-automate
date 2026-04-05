# Claude Code Template Install

This document will become the installation guide for the Claude Code template.

## Intended Install Shape

```text
install template assets
  -> connect plugin and hook surfaces
  -> activate CLAUDE.md guidance
  -> start session
  -> bootstrap
```

## Planned Surfaces

- Claude Code plugin install flow
- setup command or equivalent initialization step
- hook registration
- skill availability verification

## Current M4 Hookup

The current Claude Code template includes minimal runtime glue for recovery semantics:

- `hooks/hooks.json`
- `hooks/scripts/session-start-init.sh`
- `hooks/scripts/stop-suspend.sh`
- `hooks/scripts/cancel-current.sh`
- `hooks/scripts/resume-check.sh`

Expected environment inputs:

- `EA_TASK_ID`
- `EA_PLAN_PATH` for first initialization
- optional `EA_STATE_ROOT`
- optional `EA_OWNER_ID`

## Verification Goal

After installation, a new Claude Code session should:

- read the template guidance entry
- have bootstrap assets available
- wait for an actionable request before intake begins
- initialize loop state only when task metadata is available
- suspend active work conservatively on stop

## Status

This guide is intentionally skeletal.
Concrete setup commands and verification steps will be filled in when the Claude-specific runtime assets are wired into a real plugin/setup path.
