---
name: ea-doctor
description: Check whether the Codex EA runtime is ready without changing anything.
argument-hint: "check"
---

# ea-doctor

Use this when the user wants a read-only EA health check.

## Purpose

Use this in a Codex session that already has the EA source checkout open.
`ea-doctor` is the read-only route to `python3 scripts/install_global.py doctor`.
It checks whether the EA runtime is ready.

Its job is to:

- inspect the expected global EA assets
- inspect the required Codex config feature flags
- report what is missing or broken
- say whether the runtime is ready
- avoid any install or repair work

## Flow

```text
[Read state]
  |
  v
[Check assets]
  |
  v
[Check config]
  |
  v
[Report ready or missing]
```

## Safety

- Read only.
- Do not install anything.
- Do not repair anything.
- Do not change config files.
- Do not hide failures behind a pass.
- Do not replace the installer check with a script preflight claim.

## Output

Report:

- managed assets found
- missing assets
- config feature flag state
- latest manifest status
- ready or not ready
