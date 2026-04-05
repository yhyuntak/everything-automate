# Everything Automate for Internal Runtime

This file is the draft top-level entry for the internal runtime template.

## Current Assumption

The internal runtime is treated as OpenCode-like unless a concrete incompatibility proves otherwise.

That means the first implementation path is:

```text
OpenCode-compatible template
  -> internal adapter overlay
  -> installed runtime bootstrap
```

## Runtime Model

```text
session start
  -> internal bootstrap
  -> wait for actionable request
  -> intake
  -> direct | clarify | plan
  -> execute
  -> verify
  -> decide
  -> wrap
```

## Current Status

This file is a draft source-of-truth entry.
It will stay thin until the Claude Code and Codex baselines are stable and the internal runtime differences are explicit enough to justify a dedicated adapter.
