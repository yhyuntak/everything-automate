# Everything Automate Runtime

This directory holds the first shared runtime artifacts for `everything-automate`.

The initial implementation is deliberately provider-neutral:

- define a stable file-state root
- create and update loop-state records
- support suspension, resume checks, and explicit cancellation

Current runtime surfaces:

- `ea_state.py`
  Shared file-based loop state engine
- `ea_codex.py`
  Codex runtime helper for `start`, `ralph`, `status`, `cancel`, and `resume`

Provider-specific bootstrap and hook code should adapt to this layer rather than redefining the state semantics.
This layer is implementation support, not the primary end-user workflow surface.
