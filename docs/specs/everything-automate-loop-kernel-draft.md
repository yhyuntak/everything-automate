---
title: Everything Automate Loop Kernel Draft
description: Draft canonical flow and loop-kernel spec for a reusable agent harness, synthesized from Ralph-loop reference analysis and aligned to everything-automate goals.
doc_type: spec
scope:
  - canonical flow
  - loop kernel
  - agent harness
  - planning
  - verification
covers:
  - docs/research/ralph-loop/00-ralph-loop-concept.md
  - docs/research/ralph-loop/02-oh-my-openagent.md
  - docs/research/ralph-loop/03-oh-my-codex.md
  - docs/research/ralph-loop/04-oh-my-claudecode.md
  - docs/research/ralph-loop/05-superpowers.md
  - docs/research/ralph-loop/06-claude-automate-evaluation.md
---

# Everything Automate Loop Kernel Draft

## Historical Note

This document is kept as design history.

It predates the current `ea-*` workflow and the Codex-only repo direction.
Read it as an early kernel draft, not as the current runtime contract.

## Why This Exists

The reference repos converge on one useful center:

```text
plan -> execute -> verify -> decide
```

That is the real kernel.

Around it, the stronger harnesses add bootstrap, intake, execution-mode choice, and wrap-up so the kernel can run repeatedly without losing context or exiting early.

This draft proposes a canonical flow for `everything-automate` that keeps the best parts of `claude-automate` while extracting a smaller, reusable loop runtime.

## Core Judgment

`claude-automate` should be treated as the main source of product taste and workflow philosophy, but not as the final runtime shape.

The right move is:

- keep `claude-automate`'s strengths
  planning discipline, AC-driven implementation, specialized agents, wrap-up, and verification habit
- replace its weak runtime core
  single `mode` string, no cancel contract, no task-scoped loop state, no shared completion kernel

So this should be a **new cut with selective carry-over**, not a full discard and not a direct port.

## Canonical Flow

### 4-stage kernel

```text
plan -> execute -> verify -> decide
```

- `plan`: define what done means
- `execute`: do the work
- `verify`: produce fresh evidence
- `decide`: continue, complete, fail, or cancel

### 8-stage portable flow

```text
bootstrap
  -> intake
  -> plan
  -> commit
  -> execute
  -> verify
  -> decide
  -> wrap
```

This gives enough structure to support Claude Code, OpenCode, Codex, and OpenCode-like internal runtimes without forcing every environment into the same UX.

## Stage Model

| Stage | Purpose | Reference patterns | What `everything-automate` should do |
| --- | --- | --- | --- |
| `bootstrap` | Inject runtime rules, skills, hooks, tool mapping | `superpowers` plugin/bootstrap, `oh-my-openagent` command templates, `oh-my-codex` generated config | Install runtime overlays, register skills, attach hooks, detect provider capabilities |
| `intake` | Decide whether work is executable now or needs clarification/planning | `claude-automate` planning mode detection, `oh-my-codex` deep-interview, `oh-my-openagent` Prometheus intake | Classify request: direct, clarify, or plan; capture task id and execution intent |
| `plan` | Create or refine spec/PRD/plan/AC | `claude-automate` planning, `oh-my-claudecode` ralplan + PRD refinement, `superpowers` brainstorming + writing-plans | Produce normalized plan artifact with AC, verification expectations, and execution recommendation |
| `commit` | Lock the execution contract | `oh-my-codex` choose `team` vs `ralph`, `oh-my-claudecode` handoff from plan to mode | Choose `single_owner`, `team`, or `subagents`; freeze plan path, owner, and stopping conditions |
| `execute` | Run implementation or investigation | `claude-automate` implement, `oh-my-openagent` Atlas + Ralph loop, `superpowers` subagent-driven-development | Run work according to mode while updating loop state and artifact state |
| `verify` | Gather fresh evidence | `claude-automate` stop hook + test-command, `oh-my-claudecode` reviewer verification, `superpowers` verification-before-completion | Run commands, capture outputs, artifacts, and reviewer verdicts into durable evidence records |
| `decide` | Move to next phase based on evidence | `oh-my-openagent` continuation injection, `oh-my-codex` state transitions, `oh-my-claudecode` stop-hook blocking | Transition to `fixing`, `complete`, `failed`, or `cancelled`; never silently stop in partial state |
| `wrap` | Finalize and persist memory | `claude-automate` wrap, `context-builder`, `superpowers` finishing-a-development-branch | Clean state, summarize work, persist learnings, hand off next steps, archive run data |

## What Each Reference Contributes

### `claude-automate`

Keep:

- strong planning workflow
- AC-driven implementation
- specialized agents
- wrap-up discipline
- practical stop-hook verification idea

Do not keep as-is:

- `mode` as the only runtime state
- grep-based active plan recovery
- workflow semantics spread across skills without a shared state machine

### `oh-my-openagent`

Keep:

- explicit continuation runtime
- state-backed loop resumption
- named command/template surfaces
- clear separation between planner and executor

Be careful with:

- transcript/tag-driven completion as the only terminal signal
- too much logic split across prompt templates and hook conventions

### `oh-my-codex`

Keep:

- explicit state contract
- phase-based loop transitions
- scoped cancel semantics
- observable runtime artifacts

Be careful with:

- contract dispersion across prompts, AGENTS, contracts, and generated config

### `oh-my-claudecode`

Keep:

- PRD/story-driven execution
- strict reviewer verification
- stop-hook enforcement
- composition between persistence and parallelism layers

Be careful with:

- convention-heavy behavior without one typed loop API
- legacy fallback paths that complicate state semantics

### `superpowers`

Keep:

- bootstrap as runtime behavior, not doc-only setup
- skill-gated workflow phases
- fresh subagent per task pattern
- mandatory verification before completion

Be careful with:

- no single orchestration kernel
- workflow truth spread across skills and guides

## Proposed Runtime Concepts

### Stage enum

```text
bootstrap
intake
planning
committed
executing
verifying
fixing
wrapping
complete
cancelled
failed
```

### Execution mode enum

```text
single_owner
team
subagents
```

### Loop state record

```yaml
run_id: string
task_id: string
provider: claude-code | opencode | codex | internal
stage: bootstrap | intake | planning | committed | executing | verifying | fixing | wrapping | complete | cancelled | failed
execution_mode: single_owner | team | subagents
plan_path: string
owner_id: string
iteration: number
max_iterations: number
started_at: string
updated_at: string
completed_at: string | null
terminal_reason: complete | cancelled | failed | max_iterations | superseded | null
current_phase_summary: string
verification_policy: string
```

### Evidence record

```yaml
- kind: test | lint | build | review | browser | manual
  name: string
  command: string
  artifact_path: string | null
  status: pass | fail | unknown
  summary: string
  captured_at: string
```

## Required Kernel Primitives

`everything-automate` should have these as first-class runtime primitives:

1. `loop-state`
   One durable task-scoped state file or state API.

2. `plan-artifact`
   Normalized plan/PRD/spec file with AC and verification expectations.

3. `continuation`
   One reusable continuation rule that can resume work after stop, compaction, or partial progress.

4. `verification`
   A shared evidence contract that stores the command, result, and summary.

5. `decision-engine`
   A single rule set for `continue`, `fix`, `complete`, `cancel`, `fail`.

6. `cancel`
   Explicit user-triggered terminalization with scoped cleanup.

7. `wrap`
   Post-run summary, memory persistence, and operator handoff.

## Recommended Separation

The system should separate three different concerns that the reference repos often blur:

- `planning lane`
  clarify, scope, spec, AC, tradeoffs
- `execution substrate`
  single owner, team runtime, or task-sliced subagents
- `completion discipline`
  verify, decide, continue, cancel, complete

Ralph should sit in the third bucket.

That means:

- `Ralph` is not the planner
- `Ralph` is not the team runtime
- `Ralph` is not the subagent framework
- `Ralph` is the kernel that keeps execution honest until terminal state

## Suggested First Cut

The first implementation should be intentionally small.

### v0 kernel

- one loop-state file
- one plan artifact format
- one execution mode: `single_owner`
- one verification contract
- one cancel command
- one wrap step

### v1 expansion

- add `subagents` execution mode
- add browser/reviewer evidence kinds
- add resumable compaction support
- add run history and lightweight memory persistence

### v2 expansion

- add `team` runtime
- add provider adapters
- add per-provider bootstrap and tool-mapping overlays

## Direct Recommendation For This Repo

Do not start by porting all of `claude-automate`.

Start by extracting a smaller kernel:

1. define the loop-state schema
2. define the plan artifact schema
3. define the verify/evidence schema
4. define the stage transition table
5. adapt `planning`, `implement`, and `wrap` to use that kernel

Only after that should the harness grow new provider adapters or team runtime features.

## Transition Strategy

```text
claude-automate workflow taste
  + oh-my-codex state contract
  + oh-my-openagent continuation logic
  + oh-my-claudecode verification strictness
  + superpowers bootstrap portability
  = everything-automate loop kernel
```

## Open Questions

These need decisions before implementation:

- Should the canonical plan artifact be PRD-first or checklist-first?
- Should verification failures always loop automatically, or sometimes require user confirmation?
- Should `cancel` preserve unfinished evidence and artifacts by default?
- Should `subagents` be part of v0, or delayed until the loop kernel is stable?
- Should provider-specific bootstrap live in adapters or in profile bundles?

## Bottom Line

The common pattern across the reference repos is real.

`everything-automate` should codify it as:

- an 8-stage portable flow
- a 4-stage inner loop
- one shared task-scoped state machine
- one shared verification/evidence contract

And the best strategic move is not to throw away `claude-automate`, but to **extract its taste into a new, smaller loop kernel that other runtimes can actually share**.
