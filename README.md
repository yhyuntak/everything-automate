---
title: Everything Automate
description: Codex-first reusable agent workflow project with ea-north-star, ea-blueprint, ea-planning, ea-execute, and global Codex setup.
doc_type: guide
scope:
  - project overview
  - codex
  - setup
  - workflow
covers:
  - templates/codex/
  - scripts/install_global.py
  - docs/
---

# Everything Automate

`everything-automate` is a reusable agent workflow project.

Right now the active implementation path is **Codex-first**.
The current in-session workflow is:

```text
$ea-brainstorming
  -> $ea-north-star
  -> $ea-blueprint
  -> $ea-planning
  -> $ea-execute
  -> $ea-qa
```

## What It Does

- `$ea-brainstorming`
  helps turn a vague idea into a clear direction
- `$ea-north-star`
  bootstraps a dedicated worktree, then locks a fuzzy target into one clear goal
- `$ea-blueprint`
  turns a locked goal into a buildable design spec
- `$ea-planning`
  turns a clear request into a plan that `$ea-execute` can use
- `$ea-execute`
  uses an approved plan, does the work, checks the result, and decides what to do next
- `$ea-qa`
  reviews finished work before commit

Under the hood, the project also has:

- runtime state helpers
- a global Codex installer
- design docs and milestone docs

## Current Status

Current active focus:

- Codex workflow surfaces
- Codex global setup
- `M5` ea-execute hardening

Not current active scope here:

- full Claude adaptation
- internal service adapter

## Global Codex Setup

Install into `~/.codex` with:

```bash
python3 scripts/install_global.py setup --provider codex
```

Check install state with:

```bash
python3 scripts/install_global.py doctor --provider codex
```

Doctor exits non-zero when the required config flags are incomplete or invalid.

Current global install writes:

- `~/.codex/AGENTS.md`
- `~/.codex/hooks.json`
- `~/.codex/hooks/`
- `~/.codex/agents/*.toml`
- `~/.codex/skills/ea-brainstorming/`
- `~/.codex/skills/ea-north-star/`
- `~/.codex/skills/ea-blueprint/`
- `~/.codex/skills/ea-planning/`
- `~/.codex/skills/ea-execute/`
- `~/.codex/skills/ea-qa/`
- `~/.codex/skills/ea-docs/`
- `~/.codex/skills/ea-issue-capture/`
- `~/.codex/skills/ea-issue-pick/`
- `~/.codex/skills/ea-upstream/`

It also:

- writes an install manifest under `~/.codex/everything-automate/`
- creates backups under `~/.codex/backups/<timestamp>/`
- ensures the three required EA feature flags in `~/.codex/config.toml` and leaves the rest of that file user-owned

## Project Layout

- `templates/`
  distributable template source of truth
- `scripts/`
  setup and helper scripts
- `runtime/`
  shared runtime/state helpers
- `docs/`
  research, specs, and milestone tracking

## Main Docs

- [docs/README.md](docs/README.md)
  docs index
- [docs/specs/everything-automate-implementation-milestones.md](docs/specs/everything-automate-implementation-milestones.md)
  current milestone map
- [docs/specs/everything-automate-codex-ea-execute-hardening.md](docs/specs/everything-automate-codex-ea-execute-hardening.md)
  current `M5` working document
- [templates/codex/INSTALL.md](templates/codex/INSTALL.md)
  Codex install shape

## Language Rule

Use simple English by default.

- prefer common words over abstract framework words
- write so non-native English speakers can follow quickly
- keep important contract terms stable, but explain them with simple words around them

If a middle-school-level reader cannot follow the wording, it is too hard.
