---
title: Ea Upstream Uses Global Install For Shared Harness Fixes
status: accepted
date: 2026-04-23
decision_id: DEC-009
---

## Context

Everything Automate harness problems are often discovered inside another project session.
That project session has the useful context: what failed, what the user expected, and how the prompt or skill behaved.

Moving to a separate Everything Automate session splits that context and makes the fix loop slower.

## Decision

Add an `ea-upstream` Codex skill.

The skill guides the current project session through fixing Everything Automate source-of-truth files directly, installing the result into the global Codex home, retesting from the original project context, then committing and pushing the Everything Automate change.

The default runtime update path is global install:

```bash
python3 scripts/install_global.py setup
python3 scripts/install_global.py doctor
```

The skill does not make project-local `.codex` cleanup, sync, or link mode the main workflow.

## Consequences

- Everything Automate remains the source of truth for shared harness assets.
- A project session can fix shared harness behavior without losing context.
- The workflow must keep two contexts visible:
  - problem context = current project
  - edit context = Everything Automate source
- The skill needs gates before global install, before accepting retest evidence, and before commit/push.
- Push is included by default after the final evidence gate passes.

## Related Plans Or Files

- .everything-automate/plans/2026-04-23-ea-upstream-skill.md
- templates/skills/ea-upstream/SKILL.md
- templates/skills/README.md
- templates/INSTALL.md
