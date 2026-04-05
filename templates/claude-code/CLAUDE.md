# Everything Automate for Claude Code

This file is the top-level runtime entry for the Claude Code template.

## What This File Does

- defines the session operating contract
- establishes the shared loop kernel expectations
- hands off to Claude Code-specific bootstrap assets

## Runtime Model

Do not treat session start as task start.

Use this sequence:

```text
session start
  -> bootstrap
  -> wait for actionable request
  -> intake
  -> direct | clarify | plan
  -> execute
  -> verify
  -> decide
  -> wrap
```

## Core Loop

The shared kernel is:

```text
plan -> execute -> verify -> decide
```

`fixing` is a re-entry path after failed verification, not a separate planning mode.

## Claude Code Template Intent

- `CLAUDE.md` is the top-level guidance entry
- hooks and plugin assets perform runtime bootstrap after installation
- the first actionable request triggers intake classification
- `SessionStart` and `Stop` hooks are the first concrete M4 surfaces for state init and suspend

## Current Status

This template now includes an initial M4 hookup:

- `SessionStart` can initialize task-scoped loop state
- `Stop` can suspend the current task conservatively
- explicit helper scripts handle cancel and resume-check

Provider-specific runtime assets will continue to grow incrementally.
