---
title: Everything Automate Docs Index
description: Entry point for current project docs, Codex workflow specs, milestone notes, and docs maintenance.
doc_type: guide
scope:
  - project docs
  - codex
  - workflow
  - specs
covers:
  - docs/specs/
  - docs/docs-maintenance.md
---

# Everything Automate Docs

This index points to current docs first.
Stale operational content should be removed or reduced to a short tombstone.

The current user-facing flow is:

```text
$brainstorming
  -> $planning
  -> $execute
  -> $qa
  -> commit
```

Support skills such as `$issue-capture` and `$issue-pick` feed work into this flow.

Current source-of-truth order:

1. `templates/codex/AGENTS.md`
   top-level Codex workflow contract
2. `templates/codex/skills/*/SKILL.md`
   stage and support-skill behavior
3. `scripts/install_global.py`
   managed global install shape

Older research and early specs are not current guidance.

## Current Project Docs

- [`../README.md`](../README.md)
  Main project overview and global Codex setup command.
- [`docs-maintenance.md`](docs-maintenance.md)
  Source-of-truth order, docs inventory, and stale-doc checks.
- [`../templates/codex/INSTALL.md`](../templates/codex/INSTALL.md)
  Current Codex install shape and managed global assets.
- [`../templates/codex/AGENTS.md`](../templates/codex/AGENTS.md)
  Runtime guidance installed as the top-level Codex contract.
- [`../templates/codex/skills/README.md`](../templates/codex/skills/README.md)
  Current workflow and support skills.
- [`../templates/codex/agents/README.md`](../templates/codex/agents/README.md)
  Current narrow Codex agent roster.
- [`../runtime/README.md`](../runtime/README.md)
  Shared runtime helper overview.

## Current Specs

- `docs/specs/everything-automate-implementation-milestones.md`
  Current milestone and status map for the Codex-first flow.
- `docs/specs/everything-automate-codex-execute-hardening.md`
  Short current summary for `$execute` and `$qa` hardening.
- `docs/specs/everything-automate-planning-workflow.md`
  Tombstone for removed superseded planning design.
- `docs/specs/everything-automate-operating-principles.md`
  Writing and maintenance principles for durable project docs.
- `docs/specs/everything-automate-codex-execution-model.md`
  Support note explaining why the project moved to a Codex-first operating model.
- `docs/specs/everything-automate-provider-entry-bootstrap-mapping.md`
  Tombstone for removed provider entry/bootstrap mapping.
- `docs/specs/everything-automate-resume-cancel-contract.md`
  Resume and cancel semantics for runtime support.
- `docs/specs/everything-automate-claude-m4-pause-notes.md`
  Tombstone for removed Claude exploration notes.

## Support Contracts

These documents describe lower-level state and artifact ideas.
They are useful when changing runtime helpers, but they are not the main user workflow.

- `docs/specs/everything-automate-loop-kernel-draft.md`
  Tombstone for removed early shared kernel draft.
- `docs/specs/everything-automate-loop-state-contract.md`
  Shared task-scoped loop state contract.
- `docs/specs/everything-automate-plan-artifact-contract.md`
  Minimum executable plan artifact contract.
- `docs/specs/everything-automate-evidence-contract.md`
  Verification evidence and completion record contract.
- `docs/specs/everything-automate-stage-transition-contract.md`
  Stage transition and decision engine contract.
- `docs/specs/everything-automate-runtime-flow.md`
  Tombstone for removed earlier runtime flow.

## Removed Research

Old Ralph loop research reports were removed from current docs.
The remaining index is only a tombstone:

- `docs/research/ralph-loop/README.md`
