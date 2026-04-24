---
name: ea-setup
description: Install, update, or repair the Codex EA runtime, then run `$ea-doctor`.
argument-hint: "setup | repair | update"
---

# ea-setup

Use this when the user wants the full EA setup or repair flow inside Codex.

## Purpose

Use this in a Codex session that already has the EA source checkout open.
`ea-setup` is the in-session route to `python3 scripts/install_global.py setup`.
It is the real install and repair surface.

Its job is to:

- inspect the current EA source and Codex home state before changing anything
- keep the source checkout open while you run the installer
- decide whether the deterministic setup path is safe to run
- install or repair the full EA runtime when safe
- keep the required config guarantees in place
- stop and explain risky conflicts instead of guessing
- run `$ea-doctor` at the end
- summarize what changed

## What To Check First

Before any write step, check:

- the current Codex home
- the current EA source state
- the installed global assets
- the required Codex config feature flags
- the latest install manifest and backup state

## Flow

```text
[Read state]
  |
  v
[Check safety]
  |
  +---- risky conflict ----> [Stop and explain]
  |
  v
[Run full setup]
  |
  v
[Run $ea-doctor]
  |
  v
[Report result]
```

## Safety

- Use the deterministic installer path in `python3 scripts/install_global.py setup`.
- Do not skip the config guarantee step when a full setup is safe.
- Do not overwrite a risky conflict silently.
- Do not end without `$ea-doctor`.

## Output

Report:

- what state was found
- what was installed or repaired
- what was skipped and why
- whether `$ea-doctor` passed
