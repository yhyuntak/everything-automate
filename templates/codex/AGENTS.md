# Everything Automate for Codex CLI

This file is the top-level runtime guidance entry for the Codex template.

## Positioning

Codex CLI is a follow-up adaptation target after the Claude Code baseline is stable.
Do not lower the shared kernel design just to fit Codex-specific limits.

## Runtime Model

```text
session start
  -> guidance and overlay bootstrap
  -> wait for actionable request
  -> intake
  -> direct | clarify | plan
  -> execute
  -> verify
  -> decide
  -> wrap
```

## Core Expectations

- `AGENTS.md` is the top-level operating contract
- setup installs or generates the runtime overlays Codex needs
- the shared kernel remains:

```text
plan -> execute -> verify -> decide
```

## Current Status

This file is an initial scaffold for the Codex template.
Codex-specific gaps should be handled later with overlays and degrade paths rather than by weakening the common kernel early.
