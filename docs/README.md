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

## Draft Specs

- `docs/specs/everything-automate-loop-kernel-draft.md`
  Draft canonical flow, runtime state, and kernel primitives for a reusable `everything-automate` harness.
- `docs/specs/everything-automate-planning-workflow.md`
  Canonical planning workflow for Codex-first in-session use, including the 4-agent roster and system prompt contract for Ralph-ready execution handoff.
- `docs/specs/everything-automate-operating-principles.md`
  Korean operating principles for writing and maintaining `everything-automate` documents as durable, time-independent sources of truth.
- `docs/specs/everything-automate-implementation-milestones.md`
  Current milestone plan for rebuilding Everything Automate around the user-facing flow: `brainstorming -> planning -> execute -> qa -> commit`.
- `docs/specs/everything-automate-loop-state-contract.md`
  M1 contract for the shared task-scoped loop state used by the v0 kernel.
- `docs/specs/everything-automate-plan-artifact-contract.md`
  M1 contract for the minimum executable plan artifact with AC and verification structure.
- `docs/specs/everything-automate-evidence-contract.md`
  M1 contract for fresh verification evidence and completion-facing records.
- `docs/specs/everything-automate-stage-transition-contract.md`
  M1 contract for stage transitions and the v0 decision engine.
- `docs/specs/everything-automate-runtime-flow.md`
  M2 document connecting the v0 contracts into an actual outer flow and inner loop runtime sequence.
- `docs/specs/everything-automate-codex-execution-model.md`
  Codex-first operating model defining in-session planning, external EA launcher execution, and the initial `ea codex ...` command surface.
- `docs/specs/everything-automate-codex-execute-hardening.md`
  Current M5 working document for validating and strengthening the Codex `execute` contract, especially handoff consumption, verify/decide semantics, retry, and state/runtime gaps.
- `docs/specs/everything-automate-provider-entry-bootstrap-mapping.md`
  M3 document defining provider-specific install surfaces, entry files, bootstrap mechanisms, and the shared intake boundary.
- `docs/specs/everything-automate-resume-cancel-contract.md`
  M4 contract for resumable runs, explicit cancellation semantics, terminal-reason separation, and artifact preservation.
- `docs/specs/everything-automate-claude-m4-pause-notes.md`
  Decision note capturing what was learned from Claude Code M4 exploration and why implementation order is temporarily shifting to Codex first.
