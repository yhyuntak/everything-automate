# Codex Template Install

This document tracks the current Codex install shape.

## Intended Install Shape

```text
start Codex session
  -> use in-session workflow skills
  -> handoff execution intent internally
  -> runtime support prepares state/instructions underneath
```

## Current Surfaces

- top-level `AGENTS.md`
- in-session workflow guidance
- planning agent prompts under `templates/codex/agents/`
- workflow skills under `templates/codex/skills/`
- runtime state tool: `runtime/ea_state.py`
- Codex runtime helper: `runtime/ea_codex.py`
- authoring-time wrapper: `templates/codex/overlays/ea-codex.sh`

## Current Workflow Shape

- `$planning`

## Local Repo Test Path

For local testing inside this repository:

1. install project-local skills and agents into `./.codex/`
2. keep the root `AGENTS.md` as the authoring contract
3. treat `templates/codex/AGENTS.md` as the runtime guidance reference for the test
4. run a planning-only Codex session that writes a plan artifact to `.everything-automate/plans/`

Current helper scripts:

- `python3 scripts/install_codex_local_test.py`
- `bash scripts/test_codex_planning.sh [slug]`

Note:

- In this GPU server environment, Codex `workspace-write` sandbox can fail with `bwrap: loopback: Failed RTM_NEWADDR`.
- The local planning test currently uses `--dangerously-bypass-approvals-and-sandbox` so Codex can actually read and write repo files during the test.

Internal support tools currently present in the authoring repo:

```bash
python3 runtime/ea_codex.py ...
templates/codex/overlays/ea-codex.sh ...
```

## Verification Goal

After setup, the Codex path should:

- make `$planning` the first active in-session workflow surface
- let approved plans hand off into execution cleanly
- keep state and recovery underneath the UX
- support `status`, `cancel`, and `resume` without forcing the user into a wrapper-first workflow

## Status

This is now a partial implementation guide.
The current runtime helper exists, but the only active user-facing Codex workflow skill right now is `$planning`.
Other workflow surfaces should be added only after their contracts are explicitly agreed.
