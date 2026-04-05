# Codex Overlays

This directory holds Codex-specific runtime glue for the current `M4` path.

Current surface:

- `ea-codex.sh`
  Thin wrapper around `runtime/ea_codex.py`

Role:

- expose an internal Codex runtime helper surface
- keep runtime/state glue separate from the in-session workflow UX
- avoid pretending Codex has Claude-style native lifecycle hooks
