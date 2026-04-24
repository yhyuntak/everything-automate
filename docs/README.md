---
title: Research Docs Index
description: Entry point for research documents collected in this workspace, including Ralph loop reference analysis across external agent harness projects.
doc_type: reference
scope:
  - research
  - ralph loop
  - agent harness
covers:
  - docs/research/ralph-loop/
  - docs/specs/
---

# Research Docs

This index now separates current reference docs from older design drafts.

Use the historical section for context only.
Those notes can mention older paths, older skill names, or pre-Codex-only design ideas.

## Ralph Loop Analysis

- `docs/research/ralph-loop/00-ralph-loop-concept.md`
  Cross-repo definition of Ralph loop, its lifecycle, and the reusable harness primitives it requires.
- `docs/research/ralph-loop/01-everything-claude-code.md`
  Analysis of autonomous-loop, hook, memory, and operator patterns in `everything-claude-code`.
- `docs/research/ralph-loop/02-oh-my-openagent.md`
  Analysis of the explicit `ralph-loop` command, hook runtime, state storage, and planning surfaces in `oh-my-openagent`.
- `docs/research/ralph-loop/03-oh-my-codex.md`
  Analysis of `ralplan -> ralph -> team` style workflow, prompt contracts, and state/runtime mechanisms in `oh-my-codex`.
- `docs/research/ralph-loop/04-oh-my-claudecode.md`
  Analysis of PRD-driven Ralph persistence, team composition, and hook/state enforcement in `oh-my-claudecode`.
- `docs/research/ralph-loop/05-superpowers.md`
  Analysis of Ralph-adjacent planning, subagent execution, verification, and plugin bootstrap patterns in `superpowers`.
- `docs/research/ralph-loop/06-claude-automate-evaluation.md`
  Evaluation of `claude-automate` against the Ralph loop concept and its missing runtime primitives.

## Current Reference Specs

- `docs/specs/everything-automate-operating-principles.md`
  Korean operating principles for writing and maintaining `everything-automate` documents as durable, time-independent sources of truth.
- `docs/specs/everything-automate-implementation-milestones.md`
  Current milestone view for the Codex-only EA direction.

## Historical Draft Specs

These docs are kept for design history.
They are not the current runtime contract.

- `docs/specs/everything-automate-loop-kernel-draft.md`
  Early kernel draft for a reusable harness before the current EA workflow and Codex-only narrowing.
- `docs/specs/everything-automate-loop-state-contract.md`
  M1 contract for the shared task-scoped loop state used by the v0 kernel.
- `docs/specs/everything-automate-plan-artifact-contract.md`
  M1 contract for the minimum executable plan artifact with AC and verification structure.
- `docs/specs/everything-automate-evidence-contract.md`
  M1 contract for fresh verification evidence and completion-facing records.
- `docs/specs/everything-automate-stage-transition-contract.md`
  M1 contract for stage transitions and the v0 decision engine.
- `docs/specs/everything-automate-runtime-flow.md`
  M2 runtime-flow draft from the earlier provider-era design phase.
- `docs/specs/everything-automate-codex-execution-model.md`
  Earlier Codex execution-model draft from the pre-`ea-*` workflow stage.
- `docs/specs/everything-automate-codex-execute-hardening.md`
  Earlier execute-hardening draft from the pre-`ea-execute` workflow stage.
- `docs/specs/everything-automate-planning-workflow.md`
  Earlier planning-workflow draft from the pre-`ea-planning` workflow stage.
- `docs/specs/everything-automate-provider-entry-bootstrap-mapping.md`
  Provider-entry mapping draft kept as history after the repo became Codex-only.
- `docs/specs/everything-automate-resume-cancel-contract.md`
  Resume/cancel draft from the earlier provider-neutral analysis phase.
- `docs/specs/everything-automate-claude-m4-pause-notes.md`
  Claude exploration pause note kept only for historical context.
