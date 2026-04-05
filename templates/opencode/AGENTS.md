# Everything Automate for OpenCode

This file is the top-level runtime guidance entry for the OpenCode template.

## Runtime Model

```text
session start
  -> plugin bootstrap
  -> wait for actionable request
  -> intake
  -> direct | clarify | plan
  -> execute
  -> verify
  -> decide
  -> wrap
```

## Core Expectations

- OpenCode runtime bootstrap is expected to happen through plugin/config surfaces
- skill path registration and bootstrap text injection are separate concerns
- the shared loop kernel remains:

```text
plan -> execute -> verify -> decide
```

## Intake Boundary

General conversation does not automatically start the loop.
The loop starts only after the first actionable request is classified.

## Current Status

This file is a scaffold for the distributable OpenCode template.
Concrete plugin wiring and runtime assets will be added after the Claude Code and Codex baselines are stable.
