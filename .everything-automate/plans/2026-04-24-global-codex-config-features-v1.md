---
title: Global Codex Config Feature Guarantees v1
task_id: global-codex-config-features-v1-2026-04-24
status: approved
approval_state: approved
plan_path: .everything-automate/plans/2026-04-24-global-codex-config-features-v1.md
mode: direct
execution_mode: single_owner
execution_unit: AC
recommended_mode: execute
recommended_agents:
  - ea-worker
verification_policy: temp-home-setup-and-doctor
verification_lane: mixed
open_risks:
  - Patching `config.toml` with ad-hoc text handling could break unrelated user config if the update logic is too broad.
  - Deduping only the managed keys must not accidentally rewrite unrelated `features` entries.
  - Doctor output can become noisy if config status is mixed into the current asset-only report without a clear shape.
  - Doctor should fail when the required config flags are incomplete, so the install contract needs to say that clearly.
test_command: python3 scripts/install_global.py setup --codex-home <tmp-dir> && python3 scripts/install_global.py doctor --codex-home <tmp-dir>
---

# Requirements Summary

- Extend Codex global setup so it also manages the required EA feature flags in `~/.codex/config.toml`.
- Guarantee only these three feature flags in v1:
  - `multi_agent = true`
  - `codex_hooks = true`
  - `default_mode_request_user_input = true`
- Keep the change idempotent so rerunning setup does not add duplicate config entries.
- Preserve unrelated user-owned config in `config.toml`; only the `[features]` keys above are managed.

# Desired Outcome

After this work:

- `python3 scripts/install_global.py setup` ensures the three EA feature flags exist in `~/.codex/config.toml`.
- Running setup again does not duplicate those keys or create repeated `[features]` blocks.
- Existing non-EA config remains intact.
- `doctor` and the install docs reflect that `config.toml` is now part of the managed Codex setup surface.
- `doctor` returns a non-zero exit when one of the required config flags is missing, false, or duplicated.

# In Scope

- Add a small `config.toml` patch step to the Codex global installer.
- Create or update the `[features]` table with the three required EA keys.
- Deduplicate those three keys when setup runs against an existing file.
- Preserve unrelated config text as much as practical.
- Update `doctor` so it can report whether the three required feature flags are present and fail when they are incomplete.
- Update docs that currently say `config.toml` is excluded from v0.

# Non-Goals

- Do not take ownership of the whole `config.toml` file.
- Do not manage model, trust, plugin, TUI, or other non-EA settings.
- Do not add `agents.ea-*` config entries.
- Do not solve every possible malformed TOML recovery path.
- Do not expand v1 to plugin enablement or other feature flags.

# Design Direction

Keep the change narrow.

Use the installer to patch only the `[features]` table in `config.toml`.

Rules:

- If `config.toml` does not exist, create the smallest file that contains the required `[features]` table.
- If `[features]` exists, upsert the three required keys to `true`.
- If one of those keys appears more than once, collapse it to one managed value.
- Leave unrelated tables and keys unchanged.

`doctor` should stay simple.
It only needs to confirm whether the required three feature flags are present and true.

# Test Strategy

Strategy: `mixed`

Use install and config verification checks:

- Run setup against a temp Codex home with no preexisting `config.toml`.
- Confirm setup creates `config.toml` with the three required feature flags.
- Confirm setup recognizes a `[features] # keep note` header instead of appending a second block.
- Run setup again against the same temp home.
- Confirm the three keys still appear once and stay `true`.
- Run setup against a temp home that already has unrelated config content.
- Confirm unrelated settings remain after setup.
- Run doctor against the temp home and confirm it reports the managed config state clearly.
- Run doctor against a temp home with a missing or false required flag and confirm it exits non-zero.
- Re-read install docs and confirm they no longer claim `config.toml` is excluded from v0.

# Task

## AC1: Setup Guarantees The Three Required EA Feature Flags

`setup` ensures the required EA feature flags exist in the Codex global config.

### TC1.1

Run setup into an empty temp Codex home:

```bash
python3 scripts/install_global.py setup --codex-home <tmp-dir>
```

Expected evidence:

- `<tmp-dir>/config.toml` exists.
- It contains `[features]`.
- It contains:
  - `multi_agent = true`
  - `codex_hooks = true`
  - `default_mode_request_user_input = true`

### TC1.2

Run setup into a temp Codex home with an existing `config.toml` that already has unrelated settings.

Expected evidence:

- The three required EA keys exist and are `true`.
- Unrelated settings still exist after setup.

## AC2: Setup Stays Idempotent And Avoids Duplicate Managed Keys

Rerunning setup does not create duplicate managed config entries.

### TC2.1

Run setup twice against the same temp Codex home.

Expected evidence:

- The three managed keys each appear once in `config.toml`.
- `[features]` is not duplicated by the installer.

### TC2.2

Run setup against a temp Codex home whose `config.toml` already contains one or more of the managed keys.

Expected evidence:

- The final file keeps one effective copy of each managed key.
- Each managed key ends as `true`.

## AC3: Doctor Reports The Managed Config State

`doctor` reflects the new managed `config.toml` responsibility.

### TC3.1

Run:

```bash
python3 scripts/install_global.py doctor --codex-home <tmp-dir>
```

Expected evidence:

- Doctor output still reports managed asset status.
- Doctor also reports whether the required config feature flags are present.

### TC3.2

Run doctor against a temp Codex home where one required feature flag is missing or false.

Expected evidence:

- Doctor reports the config state as incomplete or missing.

## AC4: Docs Match The New Installer Contract

Docs no longer describe `config.toml` as outside the managed setup surface.

### TC4.1

Read `templates/INSTALL.md`.

Expected evidence:

- It says global setup now manages the required EA feature flags in `~/.codex/config.toml`.
- It no longer says `config.toml` is excluded from v0.

### TC4.2

Read any updated user-facing overview docs touched by the implementation.

Expected evidence:

- They describe the managed setup surface consistently with the installer behavior.

## Execute Handoff

Use `$ea-execute` after approval.

Start with AC1.

Keep the implementation narrow:

- installer logic
- doctor reporting
- install docs

Do not expand into broader global config management during execution.
