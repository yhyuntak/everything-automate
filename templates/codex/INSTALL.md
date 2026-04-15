# Codex Template Install

This document tracks the current Codex install shape.

## Intended Install Shape

```text
python3 scripts/install_global.py setup --provider codex
  -> ~/.codex/*

start Codex session
  -> use in-session workflow skills
  -> handoff execution intent internally
  -> runtime support prepares state/instructions underneath
```

## Current Surfaces

- top-level `AGENTS.md`
- in-session workflow guidance
- agent prompts under `templates/codex/agents/`
- workflow skills under `templates/codex/skills/`
- global installer: `scripts/install_global.py`
- runtime state tool: `runtime/ea_state.py`
- Codex runtime helper: `runtime/ea_codex.py`
- authoring-time wrapper: `templates/codex/overlays/ea-codex.sh`

## Current Workflow Shape

- `$brainstorming`
- `$planning`
- `$execute`
- `$qa`

## Local Repo Test Path

For local testing inside this repository:

1. install project-local skills and agents into `./.codex/`
2. keep the root `AGENTS.md` as the authoring contract
3. treat `templates/codex/AGENTS.md` as the runtime guidance reference for the test
4. run a planning-only Codex session that writes a plan artifact to `.everything-automate/plans/`

Current helper scripts:

- `python3 scripts/install_codex_local_test.py`
- `python3 scripts/install_global.py setup --provider codex --codex-home <tmp-dir>`
- `python3 scripts/install_global.py doctor --provider codex --codex-home <tmp-dir>`
- `bash scripts/test_codex_planning.sh [slug]`

Note:

- In this GPU server environment, Codex `workspace-write` sandbox can fail with `bwrap: loopback: Failed RTM_NEWADDR`.
- The local planning test currently uses `--dangerously-bypass-approvals-and-sandbox` so Codex can actually read and write repo files during the test.

Internal support tools currently present in the authoring repo:

```bash
python3 runtime/ea_codex.py ...
templates/codex/overlays/ea-codex.sh ...
```

The wrapper stays in the source repo as authoring-time glue.
The current global setup does not materialize it into `~/.codex/`.

## Verification Goal

After setup, the Codex path should:

- make `$brainstorming`, `$planning`, `$execute`, and `$qa` the active in-session workflow surfaces
- let approved plans hand off into `$execute` cleanly
- keep state and recovery underneath the UX
- support `status`, `cancel`, and `resume` without forcing the user into a wrapper-first workflow
- back up replaced global assets before overwriting them
- expose a minimal `doctor` surface for managed assets

## Status

This is now a partial implementation guide.
The current runtime helper exists, and the active user-facing Codex workflow skills right now are `$brainstorming`, `$planning`, `$execute`, and `$qa`.
The current global setup v0 is:

- `setup`
  - materialize `~/.codex/AGENTS.md`
  - materialize `~/.codex/agents/*.toml`
  - materialize `~/.codex/skills/{brainstorming,planning,execute,qa}/`
  - write a managed install manifest under `~/.codex/everything-automate/`
  - back up replaced assets under `~/.codex/backups/<timestamp>/`
- `doctor`
  - report managed install root
  - report found and missing managed assets
  - report latest manifest path and status

`~/.codex/config.toml` is intentionally excluded from v0.
Other workflow surfaces and provider adapters should be added only after their contracts are explicitly agreed.
