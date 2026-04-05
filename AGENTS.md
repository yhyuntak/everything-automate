# Everything Automate Local Working Rules

## Purpose

This `AGENTS.md` is the local operating contract for building `everything-automate`.
It exists so the session does not have to reconstruct the project's working rules every time.

This file is for the **local authoring layer**.
It is not the distributable template itself.

## Core Model

`everything-automate` has two layers that must stay separate.

### 1. Local authoring layer

This repository is used to:

- research reference harnesses
- design the common loop kernel
- write and test local helper skills/workflows
- generate and package distributable templates

Local operating rules belong here, in this root `AGENTS.md`.

### 2. Distributable template layer

Files intended for external installation or project embedding must live under `templates/` as the source of truth.

That includes future:

- `templates/*/AGENTS.md`
- `templates/*/CLAUDE.md`
- distributable skills
- distributable hooks
- distributable commands
- provider-specific bootstrap files

Do not let repo-local convenience files become the accidental source of truth for distributable behavior.

## Non-Negotiable Rules

### Documents must be durable

Every important document must be understandable later by someone who did not participate in the original discussion.

Write so that:

- the reader can understand the context without hidden background
- the reason for a decision is visible
- the current status vs future intent is distinguishable
- the next action is obvious

Do not write documents as short-lived conversation residue.

### Templates own distributable behavior

If a behavior is meant to ship to users, it should be authored in the template layer.

Local files may:

- describe it
- test it
- generate it
- package it

But local files should not silently become the only implementation of distributable runtime behavior.

### Local rules still belong in local AGENTS

This root `AGENTS.md` must contain the local working rules for evolving the project itself.
That guidance should not depend on reading `docs/` first.

`docs/` may explain and expand the rules.
This file should keep the always-relevant operating contract short and actionable.

### Kernel before adapters

Default build order:

1. loop kernel contracts
2. execution flow
3. minimal bootstrap/intake
4. resume/cancel hardening
5. provider adapters
6. broader expansion

Do not jump to provider-specific polish before the shared kernel is stable.

### Planning discipline is preserved

Keep the best parts of `claude-automate`:

- explicit planning
- AC-driven implementation
- verification discipline
- wrap-up discipline

But do not carry over weak runtime patterns unchanged:

- single-string mode state
- implicit continuation
- no explicit cancel contract
- no shared loop-state kernel

## Current Project Direction

The working design is:

- inner kernel: `plan -> execute -> verify -> decide`
- outer runtime flow: `bootstrap -> intake -> plan -> commit -> execute -> verify -> decide -> wrap`
- initial provider baseline: `Claude Code + Codex`
- design center: `Claude Code`
- Codex should be treated as a constrained adaptation target, not as the feature ceiling
- `OpenCode` and internal runtimes are follow-up targets unless a concrete need pulls them forward

The current priority is to define the reusable loop kernel, not to fully flesh out every runtime surface.

## File Ownership Rules

### Root-level files

Use root-level project files for:

- local operating rules
- local build/generation entry points
- repository-wide configuration

### `docs/`

Use `docs/` for:

- durable design/spec/reference documents
- milestone tracking
- architecture decisions
- research summaries

### `templates/`

Use `templates/` for:

- distributable provider/project templates
- provider-facing `AGENTS.md` / `CLAUDE.md`
- shipping runtime assets

If `templates/` structure is not created yet, treat that as a pending structural task, not as permission to place distributable behavior anywhere convenient.

## What To Do In This Repo By Default

When working on `everything-automate`:

- prefer small structural moves that clarify ownership
- keep local authoring concerns separate from shipping template concerns
- update docs when a design decision becomes important enough to guide later work
- keep `AGENTS.md` focused on always-relevant session rules
- keep implementation milestones sequential and one-step-at-a-time

## What Not To Do

- do not mix local helper behavior with distributable template behavior without marking ownership clearly
- do not implement provider-specific runtime logic first when the shared kernel is still unstable
- do not let detailed docs replace the need for a local session entry contract
- do not scatter the same rule across multiple files with different wording unless one file is clearly the source of truth
