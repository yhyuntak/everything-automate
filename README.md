---
title: Everything Automate
description: Codex-first workflow project with bootstrap install and in-session setup.
doc_type: guide
scope:
  - project overview
  - first-time setup
  - codex workflow
covers:
  - templates/
  - scripts/
  - docs/
---

# Everything Automate

Everything Automate is a Codex-only workflow project.

The main user experience is inside the Codex session.
The workflow starts in Codex and continues with EA skills.

Current main workflow:

```text
$ea-north-star
  -> $ea-milestone
  -> $ea-brainstorming
  -> $ea-planning
  -> $ea-execute
  -> $ea-qa
```

## What This Project Is

Everything Automate gives you:

- a clear in-session workflow
- reusable EA skills
- reusable EA agents
- setup and doctor support for Codex

The goal is not to push the user into wrappers or hidden runtime tools.
The goal is to make the main workflow work inside Codex.

## First-Time Setup

For a first-time user, setup happens in four steps:

1. run bootstrap outside Codex
2. open Codex in this EA source checkout
3. run `$ea-setup`
4. let `$ea-doctor` confirm the result

```text
[Get Everything Automate source]
   |
   v
[Run bootstrap]
   |
   v
[Open Codex]
   |
   v
[Run $ea-setup]
   |
   v
[Install or repair full EA runtime when safe]
   |
   v
[Run $ea-doctor]
   |
   v
[Ready to use EA workflow]
```

### Step 1. Get the source

Clone this repository first.

```bash
git clone <repo-url>
cd everything-automate
```

### Step 2. Run bootstrap

Run one bootstrap command from this repository.

```bash
python3 scripts/bootstrap.py
```

Bootstrap installs only the minimum global setup surface.
Its job is to install `AGENTS.md`, `$ea-setup`, and `$ea-doctor`.

Bootstrap does not do the full install.

### Step 3. Open Codex

Start a normal Codex session in this EA source checkout.

### Step 4. Run `$ea-setup`

Inside Codex, with this checkout open, run:

```text
$ea-setup
```

`ea-setup` is the in-session route to:

```bash
python3 scripts/install_global.py setup
```

It checks your environment and decides whether it can:

- install
- update
- repair
- or stop and explain a problem

It should inspect the current EA source and Codex home before changing anything.

When the environment is safe, `ea-setup` installs or repairs the full EA runtime.
It then runs `$ea-doctor` automatically.

That includes:

- global EA guidance
- global EA skills
- global EA agents
- required EA Codex feature flags

If the environment is risky, `ea-setup` explains the problem and stops.

### Step 5. Start normal EA workflow

After setup is ready, use the normal EA workflow inside Codex.

## What Bootstrap Installs

Bootstrap installs only the smallest setup surface needed to continue in Codex.

That minimum surface should include:

- `AGENTS.md`
- the `ea-setup` skill
- the `ea-doctor` skill

Bootstrap should stay small.
It should not try to own the full runtime install.

## What `$ea-setup` Does

`$ea-setup` is the main setup workflow inside Codex.
It maps to `python3 scripts/install_global.py setup`.

It should:

- inspect the current environment
- find missing or broken EA global assets
- run the full install when safe
- run repair when possible
- explain and stop when a risky conflict exists
- run `$ea-doctor` at the end
- summarize the result

## What `$ea-doctor` Does

`$ea-doctor` checks whether EA is ready inside Codex.
It maps to `python3 scripts/install_global.py doctor`.

It should:

- check the expected global EA assets
- check the required Codex feature flags
- report pass or fail
- explain what is still missing or broken
- stay read-only

`$ea-doctor` checks state.
It does not install or repair by itself.

## What Ready Means

EA is ready when:

- required global EA assets are installed
- required Codex feature flags are present
- doctor passes
- the main EA workflow skills are available in Codex

## Main Workflow Skills

- `$ea-north-star`
  bootstraps a dedicated worktree, then locks a fuzzy target into one clear goal
- `$ea-milestone`
  splits a locked goal into one or more ordered code milestones
- `$ea-brainstorming`
  turns one chosen code milestone into bounded Grace-led design brainstorming
- `$ea-planning`
  turns a clear request into a plan that `$ea-execute` can use
- `$ea-execute`
  uses an approved plan, does the work, checks the result, and decides what to do next
- `$ea-qa`
  reviews finished work before commit

`$ea-north-star`, `$ea-milestone`, and `$ea-brainstorming` use the shared `ea-read-test` agent to check that the current artifact reads clearly before lock or handoff.

Current support skills:

- `ea-setup`
- `ea-doctor`
- `ea-docs`
- `ea-issue-capture`
- `ea-issue-pick`
- `ea-map`
- `ea-upstream`

`ea-map` reads the EA skill and agent graph and points to the read-only M2.5 Workbench when a graph view helps.

## Current Status

Current active focus:

- Codex workflow surfaces
- Codex global setup
- code-only `ea-brainstorming` redesign

Not current active scope here:

- full Claude adaptation
- internal service adapter

## Current Direction

The install direction is:

- small bootstrap first
- real setup inside Codex
- workflow-first user experience
- runtime helpers underneath, not as the main UX

## Project Layout

- `templates/`
  distributable template source of truth
- `scripts/`
  bootstrap, install, and doctor helpers
- `runtime/`
  runtime and state helpers
- `docs/`
  design notes, specs, and milestone docs

## Main Docs

- [docs/README.md](docs/README.md)
  docs index
- [docs/specs/everything-automate-implementation-milestones.md](docs/specs/everything-automate-implementation-milestones.md)
  current milestone map
- [docs/workflow-map.md](docs/workflow-map.md)
  visual workflow map and read-only Workbench guide
- [docs/workbench-roadmap.md](docs/workbench-roadmap.md)
  current amended Workbench milestone map
- [docs/workbench-implementation-plan.md](docs/workbench-implementation-plan.md)
  current read-only Workbench plan for `src/workbench/`
- [docs/specs/everything-automate-codex-execute-hardening.md](docs/specs/everything-automate-codex-execute-hardening.md)
  current `M5` working document
- [templates/INSTALL.md](templates/INSTALL.md)
  current Codex install shape

## Language Rule

Use simple English by default.

- prefer common words over abstract framework words
- write so non-native English speakers can follow quickly
- keep important contract terms stable, but explain them with simple words around them

If a middle-school-level reader cannot follow the wording, it is too hard.
