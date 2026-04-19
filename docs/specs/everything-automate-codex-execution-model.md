---
title: Everything Automate Codex Execution Model
description: Current Codex-first execution model summary.
doc_type: guide
status: current
scope:
  - codex
  - workflow
  - execution model
covers:
  - templates/codex/AGENTS.md
  - templates/codex/skills/
  - runtime/README.md
---

# Codex Execution Model

Codex is the active implementation path.

The user-facing workflow is:

```text
$brainstorming
  -> $planning
  -> $execute
  -> $qa
  -> commit
```

Runtime helpers support this flow.
They are not the main user workflow.

Current source of truth:

- `templates/codex/AGENTS.md`
- `templates/codex/skills/*/SKILL.md`
- `templates/codex/INSTALL.md`
- `runtime/README.md`

Older command names such as `$deep-interview`, `$ralplan`, `$ralph`, and `$cancel` were removed from this document because they are no longer the current Codex UX.
