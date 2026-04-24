# Codex Template Install

This document tracks the current Codex install shape.

## Intended Install Shape

```text
git clone <repo-url>
cd everything-automate
python3 scripts/bootstrap.py
start Codex session in this EA source checkout
  -> run $ea-setup
  -> install or repair the full EA runtime when safe
  -> run $ea-doctor
```

Bootstrap is the minimum setup surface.
`$ea-setup` is the full install and repair surface.
`$ea-doctor` is the final check.

Bootstrap only seeds the setup entry points.
Full setup installs the runtime.
Doctor only checks readiness.

## Current Surfaces

- top-level `AGENTS.md`
- in-session workflow guidance
- agent prompts under `templates/agents/`
- workflow skills under `templates/skills/`
- bootstrap setup skills under `templates/skills/ea-setup/` and `templates/skills/ea-doctor/`
- workflow prompt hooks under `templates/hooks.json` and `templates/hooks/`
- global installer: `scripts/install_global.py`
- bootstrap wrapper: `scripts/bootstrap.py`
- runtime state tool: `runtime/ea_state.py`
- Codex runtime helper: `runtime/ea_codex.py`
- authoring-time wrapper: `templates/overlays/ea-codex.sh`

## Bootstrap

Bootstrap should stay small.
It should only install what is needed to continue inside Codex:

- `AGENTS.md`
- the `ea-setup` skill
- the `ea-doctor` skill

Bootstrap does not do the full runtime install.

## `$ea-setup`

`$ea-setup` is the main install and repair surface inside Codex.
It maps to `python3 scripts/install_global.py setup`.

It should:

- inspect the current environment
- inspect the current EA source checkout and Codex home before changing anything
- find missing or broken EA global assets
- install the full runtime when safe
- repair when possible
- explain and stop when a risky conflict exists
- run `$ea-doctor` at the end
- summarize the result

When the environment is safe, it should install or repair:

- global EA guidance
- global EA skills
- global EA agents
- required EA Codex feature flags

If the environment is risky, it should stop and explain why.

## `$ea-doctor`

`$ea-doctor` checks whether EA is ready inside Codex.
It maps to `python3 scripts/install_global.py doctor`.

It should:

- check the expected global EA assets
- check the required Codex feature flags
- report pass or fail
- explain what is still missing or broken
- stay read-only

It does not install or repair by itself.

## Local Repo Test Path

For local testing inside this repository:

1. install project-local skills and agents into `./.codex/`
2. keep the root `AGENTS.md` as the authoring contract
3. treat `templates/AGENTS.md` as the runtime guidance reference for the test
4. run a ea-planning-only Codex session that writes a plan artifact to `.everything-automate/plans/`

Current helper scripts:

- `python3 scripts/install_codex_local_test.py`
- `python3 scripts/bootstrap.py --codex-home <tmp-dir>`
- `python3 scripts/install_global.py bootstrap --codex-home <tmp-dir>`
- `python3 scripts/install_global.py setup --codex-home <tmp-dir>`
- `python3 scripts/install_global.py doctor --codex-home <tmp-dir>`
- `bash scripts/test_codex_planning.sh [slug]`

Note:

- In this GPU server environment, Codex `workspace-write` sandbox can fail with `bwrap: loopback: Failed RTM_NEWADDR`.
- The local ea-planning test currently uses `--dangerously-bypass-approvals-and-sandbox` so Codex can actually read and write repo files during the test.

Internal support tools currently present in the authoring repo:

```bash
python3 runtime/ea_codex.py ...
templates/overlays/ea-codex.sh ...
```

The wrapper stays in the source repo as authoring-time glue.
The current global setup does not materialize it into `~/.codex/`.

## Verification Goal

After setup, the Codex path should:

- make `$ea-north-star`, `$ea-milestone`, `$ea-brainstorming`, `$ea-planning`, `$ea-execute`, and `$ea-qa` the active code-workflow surfaces
- install support skills for docs work, GitHub backlog capture and pick-up, and upstream harness fixes
- install the active-state hook that reads `.everything-automate/state/active.md`
- let approved plans hand off into `$ea-execute` cleanly
- keep state and recovery underneath the UX
- support `status`, `cancel`, and `resume` without forcing the user into a wrapper-first workflow
- back up replaced global assets before overwriting them
- expose a minimal `doctor` surface for managed assets
- keep `ea-setup` and `ea-doctor` available after bootstrap

## Status

This is now a partial implementation guide.
The current runtime helper exists, and the active user-facing Codex code workflow skills right now are `$ea-north-star`, `$ea-milestone`, `$ea-brainstorming`, `$ea-planning`, `$ea-execute`, and `$ea-qa`.
The current installed support skills right now are `ea-setup`, `ea-doctor`, `ea-docs`, `ea-issue-capture`, `ea-issue-pick`, and `ea-upstream`.
The current global setup v0 is:

- `setup`
  - materialize `~/.codex/AGENTS.md`
  - ensure required EA feature flags in `~/.codex/config.toml`:
    - only these `[features]` keys are managed; the rest of `config.toml` stays user-owned
    - `multi_agent = true`
    - `codex_hooks = true`
    - `default_mode_request_user_input = true`
  - ensure required EA agent settings in `~/.codex/config.toml`:
    - only these `[agents]` keys are managed; the rest of `config.toml` stays user-owned
    - `max_threads = 6`
    - `max_depth = 1`
  - materialize `~/.codex/hooks.json`
  - materialize `~/.codex/hooks/`
  - materialize `~/.codex/agents/*.toml`
  - materialize `~/.codex/skills/{ea-brainstorming,ea-north-star,ea-milestone,ea-planning,ea-execute,ea-qa,ea-setup,ea-doctor,ea-docs,ea-issue-capture,ea-issue-pick,ea-upstream}/`
  - write a managed install manifest under `~/.codex/everything-automate/`
  - back up replaced assets under `~/.codex/backups/<timestamp>/`
- `doctor`
  - report managed install root
  - report found and missing managed assets
  - report required EA config feature status and exit non-zero when it is incomplete or invalid
  - report latest manifest path and status
Other workflow surfaces and runtime adapters should be added only after their contracts are explicitly agreed.
