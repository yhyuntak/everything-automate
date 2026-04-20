# Codex Overlays

Status: support.

This directory holds Codex-specific runtime glue for the authoring repo.
It is not the primary user workflow.

Current source-repo surface:

- `ea-codex.sh`
  Thin wrapper around `runtime/ea_codex.py`

This wrapper is authoring-time glue.
The current global Codex setup does not install it into `~/.codex/`.

Role:

- expose an internal Codex runtime helper surface
- keep runtime/state glue separate from the in-session workflow UX
- avoid pretending Codex has Claude-style native lifecycle hooks
