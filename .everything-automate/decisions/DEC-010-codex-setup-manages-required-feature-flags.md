---
title: Codex Setup Manages Required EA Feature Flags In Global Config
status: accepted
date: 2026-04-24
decision_id: DEC-010
---

## Context

Everything Automate already installs global Codex agents, hooks, and skills under `~/.codex`.

The required EA feature flags can still exist only because the user set them manually in `~/.codex/config.toml`.

That leaves a gap between:

- what the installer claims to manage
- what the runtime actually needs to work cleanly

## Decision

Extend Codex global setup so it also manages only the required EA feature flags in the `[features]` table of `~/.codex/config.toml`.

The managed v1 scope is limited to:

- `multi_agent = true`
- `codex_hooks = true`
- `default_mode_request_user_input = true`

The installer should preserve unrelated user config and avoid adding duplicate managed keys on rerun.

## Consequences

- EA setup becomes responsible for the minimum feature flags the installed workflow needs.
- Only the three named `[features]` keys become part of the managed Codex setup surface.
- The rest of `config.toml` stays user-owned.
- The installer must patch `config.toml` carefully instead of overwriting user config.
- The first version stays narrow and does not take ownership of broader Codex config.

## Related Plans Or Files

- .everything-automate/plans/2026-04-24-global-codex-config-features-v1.md
- scripts/install_global.py
- templates/codex/INSTALL.md
