---
title: Everything Automate
description: Codex-first reusable agent workflow project with brainstorming, planning, execute, and global Codex setup.
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
$brainstorming
  -> $planning
  -> $execute
```

## What It Does

- `$brainstorming`
  helps turn a vague idea into a clear direction
- `$planning`
  turns a clear request into a plan that `$execute` can use
- `$execute`
  uses an approved plan, does the work, checks the result, and decides what to do next

Under the hood, the project also has:

- runtime state helpers
- a global Codex installer
- design docs and milestone docs

## Current Status

Current active focus:

- Codex workflow surfaces
- Codex global setup
- `M5` execute hardening

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

Current global install writes:

- `~/.codex/AGENTS.md`
- `~/.codex/agents/*.toml`
- `~/.codex/skills/brainstorming/`
- `~/.codex/skills/planning/`
- `~/.codex/skills/execute/`

It also:

- writes an install manifest under `~/.codex/everything-automate/`
- creates backups under `~/.codex/backups/<timestamp>/`

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
- [docs/specs/everything-automate-codex-execute-hardening.md](docs/specs/everything-automate-codex-execute-hardening.md)
  current `M5` working document
- [templates/codex/INSTALL.md](templates/codex/INSTALL.md)
  Codex install shape

## Language Rule

Use simple English by default.

- prefer common words over abstract framework words
- write so non-native English speakers can follow quickly
- keep important contract terms stable, but explain them with simple words around them

If a middle-school-level reader cannot follow the wording, it is too hard.
